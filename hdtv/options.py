class Option:
	"""
	A configuration variable
	"""
	def __init__(self, default=None,
	             parse=lambda(x): x,
	             toStr=lambda(x): str(x),
	             changeCallback=None):
		self.defaultValue = default
		self.value = self.defaultValue
		self.Parse = parse
		self.ToStr = toStr
		self.ChangeCallback = changeCallback
		
	def Set(self, value):
		"""
		Set the variable to the specified value
		"""
		self.value = value
		if self.ChangeCallback:
			self.ChangeCallback(self)
			
	def ParseAndSet(self, rawValue):
		"""
		Parses rawValue and sets the variable to the result
		"""
		self.Set(self.Parse(rawValue))
			
	def Get(self):
		"""
		Return the value of the variable
		"""
		return self.value
		
	def Reset(self):
		"""
		Reset the variable to its default value
		"""
		self.Set(self.defaultValue)
		
	def __str__(self):
		"""
		Returns the value as a string
		"""
		return self.ToStr(self.value)



		
def RegisterOption(varname, variable):
	"""
	Adds a configuration variable
	"""
	global variables
	if varname in variables.keys():
		raise RuntimeError, "Refusing to overwrite existing configuration variable"
	variables[varname] = variable
	
def Set(varname, rawValue):
	"""
	Sets the variable specified by varname. Raises a KeyError if it does not exist.
	"""
	global variables
	variables[varname].ParseAndSet(rawValue)
	
def Get(varname):
	"""
	Gets the value of the variable varname. Raises a KeyError if it does not exist.
	"""
	global variables
	return variables[varname].Get()
	
def Show(varname):
	"""
	Shows the value of the variable varname
	"""
	global variables
	return "%s: %s" % (varname, str(variables[varname]))

def Str():
	"""
	Returns all options as a string
	"""
	global variables
	string = ""
	for (k,v) in variables.iteritems():
		string += "%s: %s\n" % (k, str(v))
	return string
	
variables = dict()
