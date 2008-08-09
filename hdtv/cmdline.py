#!/usr/bin/python
import readline
import os
import glob

def hdtv_nimp():
	print "Command not implemented"

class HDTVCommandTree:
	"""
	The HDTVCommandTree structure contains all commands understood by HDTV.
	"""
	def __init__(self):
		self.childs = []
		self.parent = None
		self.params = []
		
	def FullTitle(self):
		return ""
		
	def AddCommand(self, title, command, params=None, overwrite=False):
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
		node.params = params
		
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
						raise RuntimeError, "Command is ambiguous"
			if not next:
				path.append(elem)
				break
			node = next
		
		return (node, path)
		
	def ExecCommand(self, path):
		(node, params) = self.FindNode(path.split())
		print "Cmd=%s Params=%s" % (node.FullTitle(), params)
		
	def GetFileCompleteOptions(self, directory, text):
		"""
		Returns a list of all filenames in directory <directory> beginning
		with <text>.
		"""
		global dbg_fifo
		
		try:
			files = os.listdir(directory)
		except OSError:
			files = []
		
		dbg_fifo.write("%s %s\n" % (directory, text))
		dbg_fifo.write(repr(files) + "\n")
		dbg_fifo.flush()
		
		l = len(text)
		options = []
		for f in files:
			if f[0:l] == text:
				if os.path.isdir(directory + "/" + f):
					options.append(f + "/")
				else:
					options.append(f + " ")
		
		return options
		
	def GetCompleteOptions(self, text):
		"""
		Get all possible completions. text is the last part of the current
		command line, split according to the separators defined by the
		readline library.
		"""
		buf = readline.get_line_buffer()
		path = buf.split()
		last_path = ""
		try:
			if buf[-1] != " ":
				last_path = path[-1]
				path = path[0:-1]
			(node, params) = self.FindNode(path)
		except RuntimeError:
			# Command is ambiguous
			return []
			
		options = []
		if not params and node.childs:
			l = len(text)
			for child in node.childs:
				if child.title[0:l] == text:
					options.append(child.title + " ")
		elif node.params and len(node.params) > len(params):
			if node.params[len(params)] == "FILE":
				filepath = ""
				if last_path:
					filepath = os.path.split(last_path)[0]
				options = self.GetFileCompleteOptions(filepath or ".", text)
		else:
			options = []
		
		return options
		
	def Complete(self, text, state):
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

cmds = HDTVCommandTree()
cmds.AddCommand("spectrum", hdtv_nimp, ["FILE"])
cmds.AddCommand("spectrum get", hdtv_nimp, ["FILE"])
cmds.AddCommand("spectrum list", hdtv_nimp)
cmds.AddCommand("spectrum delete", hdtv_nimp)
cmds.AddCommand("spectrum activate", hdtv_nimp)
cmds.AddCommand("spectrum show", hdtv_nimp)

cmds.AddCommand("matrix get", hdtv_nimp)
cmds.AddCommand("matrix list", hdtv_nimp)
cmds.AddCommand("matrix show", hdtv_nimp)
cmds.AddCommand("matrix delete", hdtv_nimp)

cmds.AddCommand("cd", hdtv_nimp)
cmds.AddCommand("exit", hdtv_nimp)
cmds.AddCommand("quit", hdtv_nimp)

readline.set_completer(cmds.Complete)
readline.set_completer_delims(r" /")
readline.parse_and_bind("tab: complete")

try:
	while(True):
		s = raw_input("hdtv> ")
		try:
			cmds.ExecCommand(s)
		except RuntimeError, error:
			print "Error: %s" % error
except EOFError:
	print ""
