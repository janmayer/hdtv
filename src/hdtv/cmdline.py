# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2019  The HDTV development team (see file AUTHORS)
#
# This file is part of HDTV.
#
# HDTV is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# HDTV is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with HDTV; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

"""
HDTV command line
"""

import argparse
import asyncio
import code
import glob
import os
import platform
import re
import subprocess
import threading
import traceback
from enum import Enum, auto
from pwd import getpwuid

import prompt_toolkit
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters import Condition, emacs_mode
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.shortcuts import CompleteStyle, PromptSession, clear

import __main__
import hdtv.options
import hdtv.util


class CMDType(Enum):
    python = auto()
    shell = auto()
    cmdfile = auto()
    magic = auto()
    hdtv = auto()


class HDTVCommandError(Exception):
    def __init__(self, value=""):
        self.value = value

    def __str__(self):
        return self.value


class HDTVCommandAbort(Exception):
    def __init__(self, value=""):
        self.value = value

    def __str__(self):
        return self.value or ""


class HDTVCommandParserError(HDTVCommandError):
    pass


class HDTVOptionParser(argparse.ArgumentParser):
    def error(self, message):
        raise HDTVCommandParserError(message)

    def exit(self, status=0, message=None):
        if status == 0:
            raise HDTVCommandAbort(message)
        else:
            raise HDTVCommandError(message)


class HDTVCommandTreeNode:
    def __init__(self, parent, title, level):
        self.parent = parent
        self.title = title
        self.level = level
        self.command = None
        self.params = None
        self.childs = []
        self.parent.childs.append(self)

    def FullTitle(self):
        """
        Returns the full title of the node, i.e. all titles of all
        nodes from the root to this one.
        """
        titles = []
        node = self
        while node.parent:
            titles.append(node.title)
            node = node.parent

        titles.reverse()
        return " ".join(titles)

    def FindChild(self, title, use_levels=True):
        """
        Find the nodes child whose title begins with title.    The use_levels
        parameter decides whether to use the level of the node in resolving
        ambiguities (node with lower level take precedence). Returns None
        if there were unresolvable ambiguities or 0 if there were no matching
        childs at all.
        """
        node = 0
        for child in self.childs:
            if child.title.startswith(title):
                if not node:
                    node = child
                elif use_levels and node.level != child.level:
                    if node.level > child.level:
                        node = child
                else:
                    return None
        return node

    def PrimaryChild(self):
        """
        Returns the child with the lowest level, if unambiguous,
        or None otherwise.
        """
        node = None
        for child in self.childs:
            if not node or child.level < node.level:
                node = child
            elif child.level == node.level:
                return None
        return node

    def HasChildren(self):
        """
        Checks if the node has child nodes
        """
        return len(self.childs) != 0

    def RemoveChild(self, child):
        """
        Deletes the child node child
        """
        del self.childs[self.childs.index(child)]


class HDTVCommandTree(HDTVCommandTreeNode):
    """
    The HDTVCommandTree structure contains all commands understood by HDTV.
    """

    def __init__(self):
        self.childs = []
        self.parent = None
        self.command = None
        self.options = None
        self.default_level = 1

    def SetDefaultLevel(self, level):
        self.default_level = level

    def AddCommand(self, title, command, overwrite=False, level=None, **opt):
        """
        Adds a command, specified by title, to the command tree.
        """
        if level is None:
            level = self.default_level

        path = title.split()

        node = self
        # Move down the command tree until the level just above the new node,
        #  creating nodes on the way if necessary
        if len(path) > 1:
            for elem in path[:-1]:
                next = None
                for child in node.childs:
                    if child.title == elem:
                        next = child
                        if next.level > level:
                            next.level = level
                        break
                if not next:
                    next = HDTVCommandTreeNode(node, elem, level)
                node = next

        # Check to see if the node we are trying to add already exists; if it
        # does and we are not allowed to overwrite it, raise an error
        if not overwrite:
            if path[-1] in [n.title for n in node.childs]:
                raise RuntimeError("Refusing to overwrite already existing command")

        # Create the last node
        node = HDTVCommandTreeNode(node, path[-1], level)
        node.command = command
        node.options = opt

    def FindNode(self, path, use_levels=True):
        """
        Finds the command node given by path, which should be a list
        of path elements. All path elements may be abbreviated if
        unambiguous. Returns a tuple consisting of the node found and
        of the remaining elements in the path. The use_levels parameter
        decides whether to use the level of the node in resolving
        ambiguities (node with lower level take precedence).
        """
        # Go down as far as possible in path
        node = self
        while path:
            elem = path.pop(0)
            next_elem = node.FindChild(elem, use_levels)
            if next_elem is None:  # more than one node found
                raise HDTVCommandError("Command is ambiguous")
            elif next_elem == 0:  # no nodes found
                path.insert(0, elem)
                break
            node = next_elem

        return (node, path)

    def ExecCommand(self, cmdline):
        viewport_locked = False
        try:
            fragments, _ = hdtv.util.SplitCmdlines(cmdline)
            if len(fragments) > 1:
                viewport_locked = True
                __main__.spectra.viewport.LockUpdate()
            for path in fragments:
                if not command_line.fKeepRunning:
                    break
                parser = None
                try:
                    (node, args) = self.FindNode(path)
                    while node and not node.command:
                        node = node.PrimaryChild()

                    if not node or not node.command:
                        raise HDTVCommandError("Command not recognized")

                    try:
                        parser = node.options["parser"]
                    except KeyError:
                        parser = None

                    # Parse the commands arguments
                    if parser:
                        args = parser.parse_args(args)

                    # Execute the command
                    node.command(args)
                except HDTVCommandAbort as msg:
                    if str(msg):
                        hdtv.ui.error(str(msg))
                except HDTVCommandParserError as msg:
                    hdtv.ui.error(str(msg))
                    if parser:
                        parser.print_usage()
                except (HDTVCommandError, BaseException) as msg:
                    hdtv.ui.error(str(msg))
                    hdtv.ui.debug(traceback.format_exc())
        except ValueError as msg:
            hdtv.ui.error(str(msg))
        except BaseException as msg:
            hdtv.ui.error(str(msg))
            hdtv.ui.debug(traceback.format_exc())
        finally:
            if viewport_locked:
                __main__.spectra.viewport.UnlockUpdate()

    def RemoveCommand(self, title):
        """
        Removes the command node specified by the string title.
        """
        (node, args) = self.FindNode(title.split(), False)
        if args or not node.command:
            raise RuntimeError("No valid command node specified")

        while not node.HasChildren() and node.parent is not None:
            node.parent.RemoveChild(node)
            node = node.parent

    def GetFileCompleteOptions(self, directory, text, dirs_only=False):
        """
        Returns a list of all filenames in directory <directory> beginning
        with <text>. If dirs_only=True, only (sub)directories are considered.
        """
        directory = os.path.expanduser(directory)

        try:
            files = os.listdir(directory)
        except OSError:
            files = []

        options = []
        for f in files:
            if f.startswith(text):
                if os.path.isdir(directory + "/" + f):
                    options.append(f + "/")
                elif not dirs_only:
                    options.append(f + " ")
        return options

    def GetCompleteOptions(self, document, complete_event):
        """
        Get all possible completions.
        """
        word_before_cursor = document.get_word_before_cursor()
        text_before_cursor = document.text_before_cursor
        cmds, _ = hdtv.util.SplitCmdlines(text_before_cursor)

        try:
            if not word_before_cursor:
                path, last_path = cmds[-1], ""
            else:
                *path, last_path = cmds[-1]
        except IndexError:
            path, last_path = [], ""

        # Find node specified by path. Since we stripped the incomplete part
        # from path above, it now needs to be unambiguous. If is isn't, we
        # cannot suggest any completions.
        try:
            (node, args) = self.FindNode(path)
        except (RuntimeError, HDTVCommandError):
            # Command is ambiguous
            yield from []
            return
        options = []

        default_style = "fg:#000000"
        default_selected_style = "bg:white fg:ansired"

        # If the node found has children, and no parts of the part had to
        # be interpreted as arguments, we suggest suitable child nodes...
        if not args and node.childs:
            l = len(last_path)
            for child in node.childs:
                if child.title[0:l] == word_before_cursor:
                    yield Completion(
                        child.title + " ",
                        -len(word_before_cursor),
                        style=default_style,
                        selected_style=default_selected_style,
                    )
        # ... if not, we use the nodes registered autocomplete handler ...
        elif not hasattr(node, "options") or node.options is None:
            yield from []
        elif "completer" in node.options:
            if isinstance(node.options["completer"], Completer):
                yield from node.options["completer"].get_completions(
                    document, complete_event
                )
            elif callable(node.options["completer"]):
                for option in node.options["completer"](last_path, args):
                    yield Completion(
                        option,
                        -len(word_before_cursor),
                        style=default_style,
                        selected_style=default_selected_style,
                    )
        # ... if that fails as well, we suggest files, but only if the command will
        # take files or directories as arguments.
        elif ("fileargs" in node.options and node.options["fileargs"]) or (
            "dirargs" in node.options and node.options["dirargs"]
        ):
            dirs_only = "dirargs" in node.options and node.options["dirargs"]

            # If the last part of path was incomplete (i.e. did not end
            # in a space), but contains a slash '/', the part before that
            # slash should be taken as a directory from where to suggest
            # files.
            filepath = ""
            if last_path:
                (filepath, word_before_cursor) = os.path.split(last_path)
                # filepath = os.path.split(last_path)[0]

            # Note that the readline library splits at either space ' '
            # or slash '/', so word_before_cursor would be an
            # (incomplete) filename, always without a directory.

            options = self.GetFileCompleteOptions(
                filepath or ".", word_before_cursor, dirs_only
            )

            for option in sorted(options, key=hdtv.util.natural_sort_key):
                yield Completion(
                    option,
                    -len(word_before_cursor),
                    style=default_style,
                    selected_style=default_selected_style,
                )
        else:
            yield from []


class CommandLine:
    """
    Class implementing the HDTV command line, including switching between
    command and Python mode.
    """

    cmds = {}
    cmds["__name__"] = "hdtv"

    def __init__(self, command_tree):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # prompt_toolkit < 3.0.40 brings its own event loop
        ptk_version = prompt_toolkit.__version__
        self.fallback_eventloop = (
            ptk_version.startswith("3.0.") and int(ptk_version[4:].split("-")[0]) < 40
        )

        self.command_tree = command_tree

        self.history = None

        # TODO: Replace by IPython (call InteractiveShell.run_code or similar)
        self._py_console = code.InteractiveConsole(self.cmds)

        self.fPyMode = False
        self.fPyMore = False

        self.session = None
        self.fKeepRunning = True
        self.exit_handlers = []

    def StartEventLoop(self):
        if self.fallback_eventloop:
            return

        def _loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        self.thread = threading.Thread(target=_loop, args=(self.loop,))
        self.thread.start()

    def SetHistory(self, path):
        if not os.access(path, os.W_OK):
            hdtv.ui.error(f"History file '{path}' is read-only, will be discarded")
        self.history = FileHistory(path)

    def RegisterInteractive(self, name, ref):
        self.cmds[name] = ref

    def Unescape(self, s):
        "Recognize special command prefixes"
        s = s.lstrip()
        if len(s) == 0:
            return (CMDType.hdtv, s)

        if s[0] == ":":
            return (CMDType.python, s[1:])
        elif s[0] == "@":
            return (CMDType.cmdfile, s[1:])
        elif s[0] == "!":
            return (CMDType.shell, s[1:])
        elif s[0] == "%":
            return (CMDType.magic, s[1:])
        else:
            return (CMDType.hdtv, s)

    def Clear(self, args):
        """Clear the screen"""
        clear()

    def EnterPython(self, args=None):
        if os.sep == "\\":
            eof = "Ctrl-Z plus Return"
        else:
            eof = "Ctrl-D (i.e. EOF)"
        hdtv.ui.msg(
            f"Python {platform.python_version()}. Return to hdtv with {eof}.",
            end="",
        )
        # self.fPyMode = True

        from traitlets.config import Config

        c = Config()
        c.InteractiveShell.confirm_exit = False
        c.TerminalInteractiveShell.simple_prompt = False
        c.TerminalInteractiveShell.colors = "LightBG"
        c.TerminalInteractiveShell.autoindent = True
        c.TerminalIPythonApp.display_banner = False
        c.InteractiveShell.ipython_dir = "/tmp"

        from IPython import start_ipython

        start_ipython([], config=c, user_ns=self.cmds)

    def EnterShell(self, args=None):
        "Execute a subshell"

        if "SHELL" in os.environ:
            shell = os.environ["SHELL"]
        else:
            shell = getpwuid(os.getuid()).pw_shell

        subprocess.call(shell)

    def Exit(self, args=None):
        self.fKeepRunning = False
        for handler in self.exit_handlers:
            handler()

        # Dirty hack to prevent segfaults because of root garbage collection
        # trying to free the same memory from two threads (asyncio related)
        __main__.spectra.viewport.LockUpdate()
        __main__.spectra.Clear()

    def AsyncExit(self):
        """Asynchronous exit; to be called from another thread"""
        if self.fallback_eventloop:
            self.loop.call_soon_threadsafe(self.Exit)
        else:
            self.Exit()

        self.loop.call_soon_threadsafe(
            lambda: self.session.app.exit(style="class:exiting")
        )
        if not self.fallback_eventloop:
            self.thread.join()

    def EOFHandler(self):
        self.Exit()

    def GetCompleteOptions(self, document, complete_event):
        if self.fPyMode or self.fPyMore:
            cmd_type = CMDType.python
        else:
            (cmd_type, cmd) = self.Unescape(document.text)

        default_style = "fg:#000000"
        default_selected_style = "bg:white fg:ansired"

        if cmd_type == CMDType.hdtv:
            yield from self.command_tree.GetCompleteOptions(document, complete_event)
        elif cmd_type == CMDType.cmdfile:
            (filepath, word_before_cursor) = os.path.split(cmd)
            options = self.command_tree.GetFileCompleteOptions(
                filepath or ".", word_before_cursor
            )
            for option in options:
                yield Completion(
                    option,
                    -len(word_before_cursor),
                    style=default_style,
                    selected_style=default_selected_style,
                )
        else:
            # No completion support for shell and python commands
            return []

    def ExecCmdfile(self, fname):
        """
        Execute a command file with hdtv commands (aka batch file)
        """
        hdtv.ui.msg(f"Execute file: {fname}")

        try:
            file = hdtv.util.TxtFile(fname)
            file.read()
        except OSError as msg:
            hdtv.ui.error("%s" % msg)
        for line in file.lines:
            hdtv.ui.msg("file> " + line)
            self.DoLine(line)
            # TODO: HACK: How should I teach this micky mouse language that a
            # python statement (e.g. "for ...:") has ended???
            if self.fPyMore:
                self.fPyMore = self._py_console.push("")
            if not self.fKeepRunning:
                break

    def ExecCmdfileCmd(self, args):
        for path in args.batchfile:
            for filename in glob.glob(path):
                self.ExecCmdfile(filename)

    def ExecShell(self, cmd):
        subprocess.call(cmd, shell=True)

    def DoLine(self, line):
        """
        Deal with one line of input
        """
        try:
            # In Python mode, all commands need to be Python commands ...
            if self.fPyMode or self.fPyMore:
                cmd_type = CMDType.python
                cmd = line
            # ... otherwise, the prefix decides.
            else:
                (cmd_type, cmd) = self.Unescape(line)

            # Execute as appropriate type
            if cmd_type == CMDType.hdtv:
                self.command_tree.ExecCommand(cmd)
            elif cmd_type == CMDType.python:
                # The push() function returns a boolean indicating
                #  whether further input from the user is required.
                #  We set the python mode accordingly.
                self.fPyMore = self._py_console.push(cmd)
            elif cmd_type == CMDType.shell:
                subprocess.run(cmd, shell=True, check=False)
            elif cmd_type == CMDType.cmdfile:
                self.ExecCmdfile(cmd)
        except KeyboardInterrupt:
            hdtv.ui.warning("Aborted")
        except HDTVCommandError as msg:
            hdtv.ui.error("%s" % str(msg))
        except SystemExit:
            self.Exit()
        except Exception:
            hdtv.ui.error("Unhandled exception:")
            traceback.print_exc()

    def CreateSession(self):
        # self.fPyMode = False
        # self.fPyMore = False

        def message():
            """Choose correct prompt for current mode."""
            if self.fPyMore:
                return "... > "
            elif self.fPyMode:
                return "py>>> "
            else:
                return "hdtv> "

        completer = HDTVCompleter(self.command_tree, self)

        bindings = KeyBindings()

        # @bindings.add(':')
        # def _(event):
        #    if event.app.editing_mode == EditingMode.VI:
        #        event.app.editing_mode = EditingMode.EMACS
        #    else:
        #        event.app.editing_mode = EditingMode.VI

        @bindings.add("pageup")
        def _(event):
            event.current_buffer.enable_history_search = lambda: True
            event.current_buffer.history_backward(count=event.arg)
            event.current_buffer.enable_history_search = lambda: False

        @bindings.add("pagedown")
        def _(event):
            event.current_buffer.enable_history_search = lambda: True
            event.current_buffer.history_forward(count=event.arg)
            event.current_buffer.enable_history_search = lambda: False

        # Code based on prompt_toolkit.key_binding.bindings.auto_suggest.py
        @Condition
        def suggestion_available() -> bool:
            return (
                self.session.app.current_buffer.suggestion is not None
                and len(self.session.app.current_buffer.suggestion.text) > 0
                and self.session.app.current_buffer.document.is_cursor_at_the_end
            )

        # ctrl+right key-binding for partially accepting an auto_suggest.
        # Code based on prompt_toolkit.key_binding.bindings.auto_suggest.py
        @bindings.add("c-right", filter=suggestion_available & emacs_mode)
        def _fill(event: KeyPressEvent) -> None:
            """
            Fill partial suggestion.
            """
            b = event.current_buffer
            suggestion = b.suggestion

            if suggestion:
                t = re.split(r"(\S+\s+)", suggestion.text)
                b.insert_text(next(x for x in t if x))

        self.session = PromptSession(
            message,
            history=self.history,
            completer=completer,
            complete_while_typing=False,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True,
            key_bindings=bindings,
            complete_style=CompleteStyle.MULTI_COLUMN,
        )

    def MainLoop(self):
        try:
            self.CreateSession()
        except UnicodeDecodeError:
            hdtv.ui.debug("Rewriting malformed history file")
            with open(self.history.filename, "r+", errors="replace") as history:
                history_fixed = history.read()
                history.seek(0)
                history.write(history_fixed)
            self.SetHistory(self.history.filename)
            self.CreateSession()

        def set_vi_mode(vi_mode):
            self.session.editing_mode = (
                EditingMode.VI if vi_mode.value else EditingMode.EMACS
            )

        hdtv.options.RegisterOption(
            "cli.vi_mode",
            hdtv.options.Option(
                default=False, parse=hdtv.options.parse_bool, changeCallback=set_vi_mode
            ),
        )

        while self.fKeepRunning:
            # Read a command from the user

            # Read the command
            try:
                line = self.session.prompt()
            except EOFError:
                # Ctrl-D exits in command mode
                self.EOFHandler()
                continue
            except KeyboardInterrupt:
                # The SIGINT signal (which Python turns into a
                # KeyboardInterrupt exception) is used for asynchronous
                # exit, i.e. if another thread (e.g. the GUI thread)
                # wants to exit the application.
                if not self.fKeepRunning:
                    break

                # If we get here, we assume the KeyboardInterrupt is
                # due to the user hitting Ctrl-C.

                # Ctrl-C can be used to abort the entry of a (multi-line)
                # command. If no command is being entered, we assume the
                # user wants to exit and explain how to do that correctly.
                if self.fPyMore:
                    self._py_console.resetbuffer()
                    self.fPyMore = False
                else:
                    hdtv.ui.msg(r"KeyboardInterrupt: Use 'Ctrl-D' to exit")
                continue

            # Execute the command
            if line:
                self.DoLine(line)

        if not self.fallback_eventloop:
            self.loop.call_soon_threadsafe(lambda: self.loop.stop())


class HDTVCompleter(Completer):
    def __init__(self, command_tree, cmdline):
        self.command_tree = command_tree
        self.cmdline = cmdline
        self.loading = 0

    def get_completions(self, document, complete_event):
        yield from self.cmdline.GetCompleteOptions(document, complete_event)


command_tree = HDTVCommandTree()
command_line = CommandLine(command_tree)


def SetInteractiveDict(d):
    command_line.fInteractiveLocals = d


RegisterInteractive = command_line.RegisterInteractive
AddCommand = command_tree.AddCommand
ExecCommand = command_tree.ExecCommand
RemoveCommand = command_tree.RemoveCommand
SetHistory = command_line.SetHistory
AsyncExit = command_line.AsyncExit
MainLoop = command_line.MainLoop
session = command_line.session

RegisterInteractive("gCmd", command_tree)

AddCommand("python", command_line.EnterPython)
AddCommand("exit", command_line.Exit)
AddCommand("quit", command_line.Exit)
AddCommand("clear", command_line.Clear)

prog = "shell"
description = "Start and enter a shell. To return to hdtv, exit the shell."
parser = HDTVOptionParser(prog=prog, description=description)
AddCommand(prog, command_line.EnterShell, level=2, parser=parser)

prog = "exec"
description = "Execute batch file(s) with hdtv commands. Globbing is supported."
parser = HDTVOptionParser(prog=prog, description=description)
parser.add_argument(
    "batchfile", nargs="+", type=str, default=None, help="Path of a batch file"
)
AddCommand(prog, command_line.ExecCmdfileCmd, level=2, parser=parser, fileargs=True)
