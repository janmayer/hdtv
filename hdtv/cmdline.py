#!/usr/bin/python
import readline
import os
import sys
import traceback

class HDTVCommandError(Exception):
	pass

class HDTVCommandTree:
	"""
	The HDTVCommandTree structure contains all commands understood by HDTV.
	"""
	def __init__(self):
		self.childs = []
		self.parent = None
		self.command = None
		self.options = None
		
	def AddCommand(self, title, command, **opt):
		"""
		Adds a command, specified by title, to the command tree.
		"""
		if "overwrite" in opt and opt["overwrite"]:
			overwrite = True
		else:
			overwrite = False
		
		node = self
		for elem in title.split():
			next = None
			newNode = False
			for child in node.childs:
				if child.title == elem:
					next = child
					break
			if not next:
				next = HDTVCommandTreeNode(node, elem)
				newNode = True
			node = next
		
		if not newNode and not overwrite:
			raise RuntimeError, "Refusing to overwrite already existing command"
		
		node.command = command
		node.options = opt
		
	def FindNode(self, path):
		"""
		Finds the command node given by path, which should be a list
		of path elements. All path elements may be abbreviated if
		unambiguous. Returns a tuple consisting of the node found and
		of the remaining elements in the path.
		"""
		# Go down as far as possible in path
		node = self
		while path:
			elem = path.pop(0)
			l = len(elem)
			next = None
			for child in node.childs:
				if child.title[0:l] == elem:
					if not next:
						next = child
					else:
						raise HDTVCommandError, "Command is ambiguous"
			if not next:
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
		
		if not node.command:
			raise HDTVCommandError, "Command not recognized"
		
		if not self.CheckNumParams(node, len(args)):
			raise HDTVCommandError, "Wrong number of arguments to command"
		
		node.command(args)
		
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
	
class HDTVCommandTreeNode:
	def __init__(self, parent, title):
		self.parent = parent
		self.title = title
		self.command = None
		self.params = None
		self.childs = []
		self.parent.childs.append(self)
		
	def FullTitle(self):
		titles = []
		node = self
		while node.parent:
			titles.append(node.title)
			node = node.parent

		titles.reverse()
		return " ".join(titles)
		
def AddCommand(title, command, **opt):
	global command_tree
	command_tree.AddCommand(title, command, **opt)
		
def EOFHandler():
	print ""
	Exit()
	
def KeyboardInterruptHandler():
	print "\nInterrupt: Use \'exit\' to exit."
		
def Exit(args=None):
	global keep_running
	keep_running = False

def MainLoop():
	global keep_running, command_tree
	keep_running = True
		
	readline.set_completer(command_tree.Complete)
	readline.set_completer_delims(r" /")
	readline.parse_and_bind("tab: complete")
	
	while(keep_running):
		try:
			s = raw_input("hdtv> ")
		except EOFError:
			EOFHandler()
			continue
		except KeyboardInterrupt:
			KeyboardInterruptHandler()
			continue
		
		try:
			command_tree.ExecCommand(s)
		except KeyboardInterrupt:
			print "Aborted"
		except HDTVCommandError, msg:
			print "Error: %s" % msg
		except Exception:
			print "Unhandled exception:"
			traceback.print_exc()

# Module-global variables initialization
global keep_running, command_tree
keep_running = True
command_tree = HDTVCommandTree()

AddCommand("exit", Exit, nargs=0)
AddCommand("quit", Exit, nargs=0)
