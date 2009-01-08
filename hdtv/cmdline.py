#!/bin/false
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# HDTV command line
#-------------------------------------------------------------------------------
import os
import sys
import traceback
import code
import atexit

import readline
import ROOT

class HDTVCommandError(Exception):
	pass
	
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
		Find the nodes child whose title begins with title.	The use_levels
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
		
	def SetDefaultLevel(self, level):
		self.default_level = level
		
	def AddCommand(self, title, command, **opt):
		"""
		Adds a command, specified by title, to the command tree.
		"""
		if "overwrite" in opt:
			overwrite = bool(opt["overwrite"])
			del opt["overwrite"]
		else:
			overwrite = False
			
		if "level" in opt:
			level = opt["level"]
			del opt["level"]
		else:
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
						break
				if not next:
					next = HDTVCommandTreeNode(node, elem, self.default_level)
				node = next
				
		# Check to see if the node we are trying to add already exists; if it
		# does and we are not allowed to overwrite it, raise an error
		if not overwrite:
			if path[-1] in map(lambda n: n.title, node.childs):
				raise RuntimeError, "Refusing to overwrite already existing command"
		
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
			next = node.FindChild(elem, use_levels)
			if next == None:  # more than one node found
				raise HDTVCommandError, "Command is ambiguous"
			elif next == 0:   # no nodes found
				path.insert(0, elem)
				break
			node = next
		
		return (node, path)
		
	def CheckNumParams(self, cmdnode, n):
		"""
		Checks if the command given by cmdnode will take n parameters.
		"""
		if "nargs" in cmdnode.options and n != cmdnode.options["nargs"]:
			return False
		if "minargs" in cmdnode.options and n < cmdnode.options["minargs"]:
			return False
		if "maxargs" in cmdnode.options and n > cmdnode.options["maxargs"]:
			return False
		return True
		
	def ExecCommand(self, cmdline):
		if cmdline.strip() == "":
			return
		
		path = cmdline.split()
		(node, args) = self.FindNode(path)
		
		while node and not node.command:
			node = node.PrimaryChild()

		if not node or not node.command:
			raise HDTVCommandError, "Command not recognized"
		
		if not self.CheckNumParams(node, len(args)):
			raise HDTVCommandError, "Wrong number of arguments to command"
		
		node.command(args)
		
	def RemoveCommand(self, title):
		"""
		Removes the command node specified by the string title.
		"""
		(node, args) = self.FindNode(title.split(), False)
		if len(args) != 0 or not node.command:
			raise RuntimeError, "No valid command node specified"
			
		while not node.HasChildren() and node.parent != None:
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
		path = buf.split()
		
		# If the buffer is empty or ends in a space, the children of the
		# node specificed by path are our completion options. (The empty
		# path corresponds to the root node). If the buffer does not end
		# in a space, the last part is still incomplete, and the children
		# of the node above are potential completion candidates, if their
		# names begin with the last part of the path.
		last_path = ""
		if buf != "" and buf[-1] != " ":
				last_path = path[-1]
				path = path[0:-1]
		
		# Find node specified by path. Since we stripped the incomplete part
		# from path above, it now needs to be unambiguous. If is isn't, we
		# cannot suggest any completions.
		try:
			(node, args) = self.FindNode(path, False)
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
		# ... if not, we suggest files, but only if the command will
		# take files or directories as arguments.
		elif ("fileargs" in node.options and node.options["fileargs"]) or \
		     ("dirargs" in node.options and node.options["dirargs"]):
			if "dirargs" in node.options:
				dirs_only = True
			else:
				dirs_only = False
		     
			# If the last part of path was incomplete (i.e. did not end
			# in a space), but contains a slash '/', the part before that
			# slash should be taken a a directory from where to suggest
			# files.
			filepath = ""
			if last_path:
				filepath = os.path.split(last_path)[0]
			
			# Note that the readline library splits at either space ' ' or
			# slash '/', so text, the last part of the command line, would
			# be an (incomplete) filename, always without a directory.
			options = self.GetFileCompleteOptions(filepath or ".", text, dirs_only)
		else:
			options = []
		
		return options
			
class CommandLine:
	"""
	Class implementing the HDTV command line, including switching between
	command and Python mode.
	"""
	def __init__(self, command_tree, python_completer=None):
		self.fCommandTree = command_tree
		self.fPythonCompleter = python_completer or (lambda: None)
		self.fInteractiveLocals = dict()
		
		self.fReadlineHistory = None
		self.fReadlineExitHandler = False
		
	def SetReadlineHistory(self, filename):
		self.fReadlineHistory = filename
		
		readline.clear_history()
		if os.path.isfile(self.fReadlineHistory):
			readline.read_history_file(self.fReadlineHistory)
			
		if not self.fReadlineExitHandler:
			atexit.register(self.WriteReadlineHistory)
			self.fReadlineExitHandler = True
			
	def WriteReadlineHistory(self):
		readline.write_history_file(self.fReadlineHistory)
		
	def RegisterInteractive(self, name, ref):
		self.fInteractiveLocals[name] = ref
		
	def PythonUnescape(self, s):
		s = s.lstrip()
		if len(s) == 0 or s[0] != ':':
			return None
		else:
			return s[1:]
			
	def EnterPython(self, args=None):
		self.fPyMode = True
	
	def ExitPython(self):
		print ""
		self.fPyMode = False
		
	def Exit(self, args=None):
		self.fKeepRunning = False
		
	def EOFHandler(self):
		print ""
		self.Exit()
		
	def GetCompleteOptions(self, text):
		if self.fPyMode or self.fPyMore or \
		 self.PythonUnescape(readline.get_line_buffer()) != None:
			opts = list()
			state = 0
			
			while True:
				opt = self.fPythonCompleter(text, state)
				if opt != None:
					opts.append(opt)
				else:
					break
				state += 1
					
			return opts
		else:
			return self.fCommandTree.GetCompleteOptions(text)
			
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
			
	def MainLoop(self):
		self.fKeepRunning = True
		
		py_console = code.InteractiveConsole(self.fInteractiveLocals)
		self.fPyMode = False
		self.fPyMore = False
			
		readline.set_completer(self.Complete)
		readline.set_completer_delims(readline.get_completer_delims() + os.sep)
		readline.parse_and_bind("tab: complete")
		
		while(self.fKeepRunning):
			# Read a command from the user
			# Choose correct prompt for current mode
			if self.fPyMore:
				prompt = "... > "
			elif self.fPyMode:
				prompt = "py  > "
			else:
				prompt = "hdtv> "
				
			# Read the command
			try:
				s = raw_input(prompt)
			except EOFError:
				# Ctrl-D exits in command mode, and switches back to command mode
				#  from Python mode
				if self.fPyMode:
					self.ExitPython()
				else:
					self.EOFHandler()
				continue
			except KeyboardInterrupt:
				# Ctrl-C can be used to abort the entry of a (multi-line) command.
				#  If no command is being entered, we assume the user wants to exit
				#  and explain how to do that correctly.
				if self.fPyMore:
					py_console.resetbuffer()
					self.fPyMore = False
					print ""
				elif readline.get_line_buffer() != "":
					print ""
				else:
					print "\nKeyboardInterrupt: Use \'Ctrl-D\' to exit"
				continue
			
			# Execute the command
			try:
				# In Python mode, all commands need to be Python commands, but
				#  in command mode, we may still get escaped Python commands
				if self.fPyMode or self.fPyMore:
					pycmd = s
				else:
					pycmd = self.PythonUnescape(s)
		
				# Execute as either Python or HDTV
				if pycmd != None:
					# The push() function returns a boolean indicating
					#  whether further input from the user is required.
					#  We set the python mode accordingly.
					self.fPyMore = py_console.push(pycmd)
				else:							
					self.fCommandTree.ExecCommand(s)
			except KeyboardInterrupt:
				print "Aborted"
				if pycmd:
					py_console.resetbuffer()
					self.fPyMore = False
			except HDTVCommandError, msg:
				print "Error: %s" % msg
			except SystemExit:
				self.Exit()
			except Exception:
				print "Unhandled exception:"
				traceback.print_exc()

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
	
def SetReadlineHistory(filename):
	global command_line
	command_line.SetReadlineHistory(filename)
	
def MainLoop():
	global command_line
	command_line.MainLoop()

# Module-global variables initialization
global command_tree, command_line
command_tree = HDTVCommandTree()
command_line = CommandLine(command_tree, readline.get_completer())
RegisterInteractive("gCmd", command_tree)

AddCommand("python", command_line.EnterPython, nargs=0)
AddCommand("exit", command_line.Exit, nargs=0)
AddCommand("quit", command_line.Exit, nargs=0)
