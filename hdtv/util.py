class Linear:
	"""
	A linear relationship, i.e. y = p1 * x + p0
	"""
	def __init__(self, p0=0., p1=0.):
		self.p0 = p0
		self.p1 = p1
		
	def Y(self, x):
		"""
		Get y corresponding to a certain x
		"""
		return self.p1 * x + self.p0
		
	def X(self, y):
		"""
		Get x corresponding to a certain y
		May raise a ZeroDivisionError
		"""
		return (y - self.p0) / self.p1
		
	@classmethod
	def FromXYPairs(cls, a, b):
		"""
		Construct a linear relationship from two (x,y) pairs
		"""
		l = cls()
		l.p1 = (b[1] - a[1]) / (b[0] - a[0])
		l.p0 = a[1] - l.p1 * a[0]
		return l
		
	@classmethod
	def FromPointAndSlope(cls, point, p1):
		"""
		Construct a linear relationship from a slope and a point ( (x,y) pair )
		"""
		l = cls()
		l.p1 = p1
		l.p0 = point[1] - l.p1 * point[0]
		return l
