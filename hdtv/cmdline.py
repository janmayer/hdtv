# -*- coding: utf-8 -*-

# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2009  The HDTV development team (see file AUTHORS)
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

from __future__ import print_function

import os
import sys
import signal
import platform
import traceback
import code
import atexit
import subprocess
import pwd
import argparse
import shlex
import itertools
import errno

from prompt_toolkit.shortcuts import PromptSession, CompleteStyle
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML


import hdtv.util
import hdtv.options

import ROOT


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


class HDTVCommandTreeNode(object):
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
        l = len(title)
        node = 0
        for child in self.childs:
            if child.title[0:l] == title:
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
        return (len(self.childs) != 0)

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

    def SplitCmdline(self, s):
        """
        Split a string, handling escaped whitespace.
        Essentially our own version of shlex.split, but with only double
        quotes accepted as quotes.
        
        Returns:
            List of command fragments
            Suffix removed from last fragment (quotes)
        """
        try:
            try:
                lex = shlex.shlex(s, posix=True)
                lex.quotes = r'"'
                lex.commenters = '#'
                lex.whitespace_split = True
                return list(lex), ""
            except ValueError:
                lex = shlex.shlex(s + '"', posix=True)
                lex.quotes = r'"'
                lex.commenters = '#'
                lex.whitespace_split = True
                return list(lex), '"'
        except ValueError:
            return []

    def SplitCmdlines(self, s):
        """
        Split line into multiple commands separated by ';'.
        """ 
        seg, last_suffix = self.SplitCmdline(s)
        cmd_sep = [";"]
        return [list(y) for x, y in itertools.groupby(seg, 
            key=lambda x: x not in cmd_sep) if x], last_suffix

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
                raise RuntimeError(
                    "Refusing to overwrite already existing command")

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
            elif next_elem == 0:   # no nodes found
                path.insert(0, elem)
                break
            node = next_elem

        return (node, path)

    def ExecCommand(self, cmdline):
        try:
            fragments, last_suffix = self.SplitCmdlines(cmdline)
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
                except (HDTVCommandParserError) as msg:
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

        l = len(text)

        options = []
        for f in files:
            if f[0:l] == text:
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
        cmds, last_suffix = self.SplitCmdlines(text_before_cursor)

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
            yield
        options = []

        # If the node found has children, and no parts of the part had to
        # be interpreted as arguments, we suggest suitable child nodes...
        if not args and node.childs:
            l = len(last_path)
            for child in node.childs:
                if child.title[0:l] == word_before_cursor:
                    yield Completion(child.title + " ",
                        -len(word_before_cursor))
        # ... if not, we use the nodes registered autocomplete handler ...
        elif not hasattr(node, 'options'):
            yield
        elif "completer" in node.options and callable(node.options["completer"]):
            for option in node.options["completer"](last_path, args):
                yield Completion(option, -len(word_before_cursor))
        # ... if that fails as well, we suggest files, but only if the command will
        # take files or directories as arguments.
        elif ("fileargs" in node.options and node.options["fileargs"]) or \
             ("dirargs" in node.options and node.options["dirargs"]):
            dirs_only = "dirargs" in node.options and node.options["dirargs"]

            # If the last part of path was incomplete (i.e. did not end
            # in a space), but contains a slash '/', the part before that
            # slash should be taken as a directory from where to suggest
            # files.
            filepath = ""
            if last_path:
                (filepath, word_before_cursor) = os.path.split(last_path)
                #filepath = os.path.split(last_path)[0]

            # Note that the readline library splits at either space ' '
            # or slash '/', so word_before_cursor would be an
            # (incomplete) filename, always without a directory.

            options = self.GetFileCompleteOptions(
                filepath or ".", word_before_cursor, dirs_only)
            for option in options:
                yield Completion(option, -len(word_before_cursor))
        else:
            yield


class CommandLine(object):
    """
    Class implementing the HDTV command line, including switching between
    command and Python mode.
    """
    cmds = dict()
    cmds['__name__'] = 'hdtv'

    def __init__(self, command_tree):
        self.command_tree = command_tree

        self.history = None
        
        # TODO: Replace by IPython (call InteractiveShell.run_code or similar)
        self._py_console = code.InteractiveConsole(self.cmds)


        self.fPyMode = False
        self.fPyMore = False

        self.fKeepRunning = True

        if os.sep == '\\':
            eof = 'Ctrl-Z plus Return'
        else:
            eof = 'Ctrl-D (i.e. EOF)'

    def SetHistory(self, path):
        try:
            if not os.path.isfile(path):
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), path)
            self.history = FileHistory(path)
        except FileNotFoundError:
            hdtv.ui.error(r"Could not read history file '{path}', " \
                "history will be discarded.")

    def RegisterInteractive(self, name, ref):
        self.cmds[name] = ref

    def Unescape(self, s):
        "Recognize special command prefixes"
        s = s.lstrip()
        if len(s) == 0:
            return ("HDTV", s)

        if s[0] == ':':
            return ("PYTHON", s[1:])
        elif s[0] == "@":
            return ("CMDFILE", s[1:])
        else:
            return ("HDTV", s)

    def EnterPython(self, args=None):
        if os.sep == '\\':
            eof = 'Ctrl-Z plus Return'
        else:
            eof = 'Ctrl-D (i.e. EOF)'
        hdtv.ui.msg(
            "Python {}. Return to hdtv with {}.".format(
                platform.python_version(), eof), end='')
        #self.fPyMode = True

        from traitlets.config import Config

        c = Config()
        c.InteractiveShell.confirm_exit = False
        c.TerminalInteractiveShell.simple_prompt = False
        c.TerminalInteractiveShell.colors = 'LightBG'
        c.TerminalInteractiveShell.autoindent = True
        c.TerminalIPythonApp.display_banner = False
        c.InteractiveShell.ipython_dir = "/tmp"

        from IPython import start_ipython
        start_ipython([], config=c, user_ns=self.cmds)

    def ExitPython(self):
        print("")
        self.fPyMode = False

    def EnterShell(self, args=None):
        "Execute a subshell"

        if "SHELL" in os.environ:
            shell = os.environ["SHELL"]
        else:
            shell = pwd.getpwuid(os.getuid()).pw_shell

        subprocess.call(shell)

    def Exit(self, args=None):
        self.fKeepRunning = False

    def AsyncExit(self):
        "Asynchronous exit; to be called from another thread"
        self.fKeepRunning = False
        os.kill(os.getpid(), signal.SIGINT)

    def EOFHandler(self):
        print("")
        self.Exit()

    def GetCompleteOptions(self, text):
        if self.fPyMode or self.fPyMore:
            cmd_type = "PYTHON"
        else:
            (cmd_type, cmd) = self.Unescape(text)

        if cmd_type == "HDTV":
            return self.command_tree.GetCompleteOptions(text)
        elif cmd_type == "CMDFILE":
            filepath = os.path.split(cmd)[0]
            return self.command_tree.GetFileCompleteOptions(
                filepath or ".", text)
        else:
            # No completion support for shell and python commands
            return []

    def ExecCmdfile(self, fname):
        """
        Execute a command file with hdtv commands (aka batch file)
        """
        hdtv.ui.msg("Execute file: " + fname)

        try:
            file = hdtv.util.TxtFile(fname)
            file.read()
        except IOError as msg:
            hdtv.ui.error("%s" % msg)
        for line in file.lines:
            hdtv.ui.msg('file> ' + line)
            self.DoLine(line)
            # TODO: HACK: How should I teach this micky mouse language that a
            # python statement (e.g. "for ...:") has ended???
            if self.fPyMore:
                self.fPyMore = self._py_console.push("")
            if not self.fKeepRunning:
                print("")
                break

    def ExecShell(self, cmd):
        subprocess.call(cmd, shell=True)

    def DoLine(self, line):
        """
        Deal with one line of input
        """
        try:
            # In Python mode, all commands need to be Python commands ...
            if self.fPyMode or self.fPyMore:
                cmd_type = "PYTHON"
                cmd = line
            # ... otherwise, the prefix decides.
            else:
                (cmd_type, cmd) = self.Unescape(line)

            # Execute as appropriate type
            if cmd_type == "HDTV":
                self.command_tree.ExecCommand(cmd)
            elif cmd_type == "PYTHON":
                # The push() function returns a boolean indicating
                #  whether further input from the user is required.
                #  We set the python mode accordingly.
                self.fPyMore = self._py_console.push(cmd)
            elif cmd_type == "CMDFILE":
                self.ExecCmdfile(cmd)
        except KeyboardInterrupt:
            hdtv.ui.warn("Aborted")
        except HDTVCommandError as msg:
            hdtv.ui.error("%s" % str(msg))
        except SystemExit:
            self.Exit()
        except Exception:
            hdtv.ui.error("Unhandled exception:")
            traceback.print_exc()

    def MainLoop(self):
        #self.fPyMode = False
        #self.fPyMore = False

        def message():
            """Choose correct prompt for current mode."""
            if self.fPyMore:
                return '... > '
            elif self.fPyMode:
                return 'py>>> '
            else:
                return 'hdtv> '

        completer = HDTVCompleter(self.command_tree, self)
       
        bindings = KeyBindings()
        
        @bindings.add(':')
        def _(event):
            if event.app.editing_mode == EditingMode.VI:
                event.app.editing_mode = EditingMode.EMACS
            else:
                event.app.editing_mode = EditingMode.VI

        session = PromptSession(message,
            enable_system_prompt=True, history=self.history,
            completer=completer, complete_while_typing=False,
            complete_style=CompleteStyle.MULTI_COLUMN)
        
        def set_vi_mode(vi_mode):
            session.editing_mode = (EditingMode.VI
                if vi_mode.value else EditingMode.EMACS)

        hdtv.options.RegisterOption(
            'cli.vi_mode', hdtv.options.Option(
                default=False,
                parse=hdtv.options.parse_bool,
                changeCallback=set_vi_mode))

        while(self.fKeepRunning):
            # Read a command from the user

            # Read the command
            try:
                line = session.prompt()
            except EOFError:
                # Ctrl-D exits in command mode, and switches back to command mode
                #  from Python mode
                if self.fPyMode:
                    self.ExitPython()
                else:
                    self.EOFHandler()
                continue
            except KeyboardInterrupt:
                # The SIGINT signal (which Python turns into a
                # KeyboardInterrupt exception) is used for asynchronous
                # exit, i.e. if another thread (e.g. the GUI thread)
                # wants to exit the application.
                if not self.fKeepRunning:
                    print("")
                    break

                # If we get here, we assume the KeyboardInterrupt is
                # due to the user hitting Ctrl-C.

                # Ctrl-C can be used to abort the entry of a (multi-line)
                # command. If no command is being entered, we assume the
                # user wants to exit and explain how to do that correctly.
                if self.fPyMore:
                    self._py_console.resetbuffer()
                    self.fPyMore = False
                    print("")
                else:
                    print("\nKeyboardInterrupt: Use \'Ctrl-D\' to exit")
                continue

            # Execute the command
            self.DoLine(line)


class HDTVCompleter(Completer):
    def __init__(self, command_tree, cmdline):
        self.command_tree = command_tree
        self.cmdline = cmdline
        self.loading = 0

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        text_before_cursor = document.text_before_cursor
        start = document.current_line_before_cursor.lstrip()
        yield from self.command_tree.GetCompleteOptions(
            document, complete_event)


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

RegisterInteractive("gCmd", command_tree)

AddCommand("python", command_line.EnterPython)
AddCommand("shell", command_line.EnterShell, level=2)
AddCommand("exit", command_line.Exit)
AddCommand("quit", command_line.Exit)
