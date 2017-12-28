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

# ----------------------------------------------------------------------
# HDTV command line
# ----------------------------------------------------------------------

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
import readline

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

import hdtv.util
from hdtv.color import tcolors

import ROOT
import __main__


class HDTVCommandError(Exception):
    def __init__(self, value=""):
        self.value = value
    def __str__(self):
        return self.value

class HDTVCommandAbort(Exception):
    def __init__(self, value=""):
        self.value = value
    def __str__(self):
        return self.value


class HDTVOptionParser(argparse.ArgumentParser):
    def error(self, message):
        raise HDTVCommandError(message)

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
        """
        lex = shlex.shlex(s, posix=True)
        lex.whitespace_split = True
        lex.quotes = "\""
        lex.commenters = ""
        return list(lex)

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
        # Strip comments
        cmdline = hdtv.util.remove_comments(cmdline)
        for command in hdtv.util.split_line(cmdline):
            if not command_line.fKeepRunning:
                break
            parser = None
            try:
                if command.strip() == "":
                    continue
                try:
                    path = self.SplitCmdline(command)
                except ValueError:
                    print("Inappropriate use of quotation characters.")
                    continue

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
                if msg.value:
                    hdtv.ui.error(msg.value)
            except (HDTVCommandError, BaseException) as msg:
                try:
                    if msg.value:
                        hdtv.ui.error(msg.value)
                except AttributeError:
                    hdtv.ui.error(str(msg))
                if parser:
                    parser.print_usage()
                hdtv.ui.debug(traceback.format_exc())
        return

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

        if l:
            for f in files:
                if f.find(" ") > -1:
                    files.remove(f)

        options = []
        for f in files:
            if f[0:l] == text:
                if os.path.isdir(directory + "/" + f):
                    options.append(f + "/")
                elif not dirs_only:
                    options.append(f + " ")
        return options

    def GetCompleteOptions(self, text):
        """
        Get all possible completions. text is the last part of the current
        command line, split according to the separators defined by the
        readline library. This is the part for which completions are
        suggested.
        """
        # Get the entire buffer from the readline library (we need the context)
        # and split it at spaces.
        buf = readline.get_line_buffer()
        try:
            buf = hdtv.util.split_line(buf)[-1]
        except BaseException:
            pass

        try:
            path = self.SplitCmdline(buf)
        except ValueError:
            return []
        # If the buffer is empty or ends in a space, the children of the
        # node specificed by path are our completion options. (The empty
        # path corresponds to the root node). If the buffer does not end
        # in a space, the last part is still incomplete, and the children
        # of the node above are potential completion candidates, if their
        # names begin with the last part of the path.
        last_path = ""

        # if buf != "" and not buf[-1].isspace():
        if buf != "" and (not buf[-1].isspace() or path[-1][-1].isspace()):
            last_path = path[-1]
            path = path[0:-1]

        # Find node specified by path. Since we stripped the incomplete part
        # from path above, it now needs to be unambiguous. If is isn't, we
        # cannot suggest any completions.
        try:
            (node, args) = self.FindNode(path)
        except RuntimeError:
            # Command is ambiguous
            return []

        options = []

        # If the node found has children, and no parts of the part had to
        # be interpreted as arguments, we suggest suitable child nodes...
        if not args and node.childs:
            l = len(text)
            for child in node.childs:
                if child.title[0:l] == text:
                    options.append(child.title + " ")
        # ... if not, we use the nodes registered autocomplete handler ...
        elif "completer" in node.options and callable(node.options["completer"]):
            options = node.options["completer"](text, args)
        # ... if that fails as well, we suggest files, but only if the command will
        # take files or directories as arguments.
        elif ("fileargs" in node.options and node.options["fileargs"]) or \
             ("dirargs" in node.options and node.options["dirargs"]):
            if "dirargs" in node.options and node.options["dirargs"]:
                dirs_only = True
            else:
                dirs_only = False

            # If the last part of path was incomplete (i.e. did not end
            # in a space), but contains a slash '/', the part before that
            # slash should be taken a a directory from where to suggest
            # files.
            filepath = ""
            if last_path:
                (filepath, text) = os.path.split(last_path)
                #filepath = os.path.split(last_path)[0]

            # Note that the readline library splits at either space ' ' or
            # slash '/', so text, the last part of the command line, would
            # be an (incomplete) filename, always without a directory.

            options = self.GetFileCompleteOptions(
                filepath or ".", text, dirs_only)
        else:
            options = []

        return options


class PyModeQuitter(object):
    def __init__(self, name, eof):
        self.name = name
        self.eof = eof
    def __repr__(self):
        return 'Use %s() to exit hdtv or %s to exit python and return to hdtv' % (self.name, self.eof)
    def __call__(self, code=None):
        # Shells like IDLE catch the SystemExit, but listen when their
        # stdin wrapper is closed.
        try:
            sys.stdin.close()
        except:
            pass
        raise SystemExit(code)


class CommandLine(object):
    """
    Class implementing the HDTV command line, including switching between
    command and Python mode.
    """

    def __init__(self, command_tree, python_completer=None):
        self.fCommandTree = command_tree
        self.fPythonCompleter = python_completer or (lambda: None)

        self.fReadlineHistory = None
        self.fReadlineExitHandler = False

        self._py_console = code.InteractiveConsole(__main__.__dict__)

        self.fPyMode = False
        self.fPyMore = False

        self.fKeepRunning = True

        if os.sep == '\\':
            eof = 'Ctrl-Z plus Return'
        else:
            eof = 'Ctrl-D (i.e. EOF)'

        builtins.quit = PyModeQuitter('quit', eof)
        builtins.exit = PyModeQuitter('exit', eof)

    def ReadReadlineInit(self, filename):
        if os.path.isfile(filename):
            readline.read_init_file(filename)

    def SetReadlineHistory(self, filename):
        try:
            if not os.path.isfile(filename):
                open(filename, 'a').close()
            self.fReadlineHistory = filename

            readline.clear_history()
            readline.read_history_file(self.fReadlineHistory)

            if not self.fReadlineExitHandler:
                atexit.register(self.WriteReadlineHistory)
                self.fReadlineExitHandler = True
        except OSError:
            hdtv.ui.error("Could not read history file \'" + filename +
                "\', history will be discarded.")

    def WriteReadlineHistory(self):
        try:
            readline.write_history_file(self.fReadlineHistory)
        except (IOError, OSError):
            hdtv.ui.error("Could not write history file \'" + self.fReadlineHistory + "\', history was discarded.")
            sys.exit(1)

    def RegisterInteractive(self, name, ref):
        __main__.__dict__[name] = ref

    def Unescape(self, s):
        "Recognize special command prefixes"
        s = s.lstrip()
        if len(s) == 0:
            return ("HDTV", s)

        if s[0] == ':':
            return ("PYTHON", s[1:])
        elif s[0] == "%":
            return ("SHELL", s[1:])
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
                platform.python_version(), eof))
        self.fPyMode = True

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
            (cmd_type, cmd) = self.Unescape(readline.get_line_buffer())

        if cmd_type == "HDTV":
            return self.fCommandTree.GetCompleteOptions(text)
        elif cmd_type == "PYTHON":
            # Extract the possible complete options from the systems
            #  Python completer
            opts = list()
            state = 0

            while True:
                opt = self.fPythonCompleter(text, state)
                if opt is not None:
                    opts.append(opt)
                else:
                    break
                state += 1

            return opts
        elif cmd_type == "CMDFILE":
            filepath = os.path.split(cmd)[0]
            return self.fCommandTree.GetFileCompleteOptions(
                filepath or ".", text)
        else:
            # No completion support for shell commands
            return []

    def Complete(self, text, state):
        """
        Suggest completions for the current command line, whose last token
        is text. This function is intended to be called from the readline
        library *only*.
        """
        # We get called several times, always with state incremented by
        # one, until we return None. We prepare the complete list to
        # be returned at the initial call and then return it element by
        # element.

        if state == 0:
            self.fCompleteOptions = self.GetCompleteOptions(text)
        if state < len(self.fCompleteOptions):
            return self.fCompleteOptions[state]
        else:
            return None

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
            print(hdtv.util.get_prompt('file', inputable=False) + line)
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
                self.fCommandTree.ExecCommand(cmd)
            elif cmd_type == "PYTHON":
                # The push() function returns a boolean indicating
                #  whether further input from the user is required.
                #  We set the python mode accordingly.
                self.fPyMore = self._py_console.push(cmd)
            elif cmd_type == "CMDFILE":
                self.ExecCmdfile(cmd)
            elif cmd_type == "SHELL":
                self.ExecShell(cmd)
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

        readline.set_completer(self.Complete)
        readline.set_completer_delims(" \t" + os.sep)
        readline.parse_and_bind("tab: complete")
        while(self.fKeepRunning):
            # Read a command from the user
            # Choose correct prompt for current mode
            if self.fPyMore:
                prompt = hdtv.util.get_prompt('... ')
            elif self.fPyMode:
                prompt = hdtv.util.get_prompt('py', sep='>>>')
            else:
                prompt = hdtv.util.get_prompt('hdtv')

            # Read the command
            try:
                line = get_input(prompt)
            except EOFError:
                # Ctrl-D exits in command mode, and switches back to command mode
                #  from Python mode
                if self.fPyMode:
                    self.ExitPython()
                else:
                    self.EOFHandler()
                continue
            except KeyboardInterrupt:
                # The SIGINT signal (which Python turns into a KeyboardInterrupt
                # exception) is used for asynchronous exit, i.e. if another thread
                # (e.g. the GUI thread) wants to exit the application.
                if not self.fKeepRunning:
                    print("")
                    break

                # If we get here, we assume the KeyboardInterrupt is due to the user
                #  hitting Ctrl-C.

                # Ctrl-C can be used to abort the entry of a (multi-line) command.
                #  If no command is being entered, we assume the user wants to exit
                #  and explain how to do that correctly.
                if self.fPyMore:
                    self._py_console.resetbuffer()
                    self.fPyMore = False
                    print("")
                elif readline.get_line_buffer() != "":
                    print("")
                else:
                    print("\nKeyboardInterrupt: Use \'Ctrl-D\' to exit")
                continue

            # Execute the command
            self.DoLine(line)


def RegisterInteractive(name, ref):
    global command_line
    command_line.RegisterInteractive(name, ref)


def SetInteractiveDict(d):
    global command_line
    command_line.fInteractiveLocals = d


def AddCommand(title, command, **opt):
    global command_tree
    command_tree.AddCommand(title, command, **opt)


def ExecCommand(cmdline):
    global command_tree
    command_tree.ExecCommand(cmdline)


def RemoveCommand(title):
    global command_tree
    command_tree.RemoveCommand(title)


def ReadReadlineInit(filename):
    global command_line
    command_line.ReadReadlineInit(filename)


def SetReadlineHistory(filename):
    global command_line
    command_line.SetReadlineHistory(filename)


def AsyncExit():
    global command_line
    command_line.AsyncExit()


def MainLoop():
    global command_line
    command_line.MainLoop()


# Module-global variables initialization
global command_tree, command_line
command_tree = HDTVCommandTree()
command_line = CommandLine(command_tree, readline.get_completer())
RegisterInteractive("gCmd", command_tree)

AddCommand("python", command_line.EnterPython)
AddCommand("shell", command_line.EnterShell, level=2)
AddCommand("exit", command_line.Exit)
AddCommand("quit", command_line.Exit)

try: # Python2
    get_input = raw_input
except NameError: # Python3+
    get_input = input

