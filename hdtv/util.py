import math

class ErrValue:
	"""
	A value with an error
	"""
	def __init__(self, value, error):
		self.value = value
		self.error = error
		
	def __repr__(self):
		return "ErrValue(" + repr(self.value) + ", " + repr(self.error) + ")"
	
	def __str__(self):
		return self.fmt()
		
	def fmt(self):
		# Check and store sign
		if self.value < 0:
			sgn = "-"
			value = -self.value
		else:
			sgn = ""
			value = self.value
			
		# Errors are always positive
		error = abs(self.error)
	
		# Check whether to switch to scientific notation
		# Catch the case where value is zero
		try:
			log10_val = math.floor(math.log(value) / math.log(10.))
		except OverflowError:
			log10_val = 0.
		
		if log10_val >= 6 or log10_val <= -2:
			# Use scientific notation
			suffix = "e%d" % int(log10_val)
			exp = 10**log10_val
			value /= exp
			error /= exp
		else:
			# Use normal notation
			suffix = ""
			
		# Find precision (number of digits after decimal point) needed such that the
		# error is given to at least two decimal places
		if error >= 10.:
			prec = 0
		else:
			# Catch the case where error is zero
			try:
				prec = -math.floor(math.log(error) / math.log(10.)) + 1
			except OverflowError:
				prec = 6
				
		# Limit precision to sensible values, and capture NaN
		if prec > 20:
			prec = 20
		elif prec != prec:
			prec = 3
			
		# Make sure error is always rounded up
		return "%s%.*f(%.0f)%s" % (sgn, int(prec), value, error*10**prec + 0.5, suffix)
		
	def fmt_no_error(self, prec=6):
		# Check and store sign
		if self.value < 0:
			sgn = "-"
			value = -self.value
		else:
			sgn = ""
			value = self.value
			
		# Check whether to switch to scientific notation
		# Catch the case where value is zero
		try:
			log10_val = math.floor(math.log(value) / math.log(10.))
		except OverflowError:
			log10_val = 0.
		
		if log10_val >= 6 or log10_val <= -2:
			# Use scientific notation
			suffix = "e%d" % int(log10_val)
			value /= 10**log10_val
		else:
			# Use normal notation
			suffix = ""
			
		# Make sure error is always rounded up
		return "%s%.*f%s" % (sgn, prec, value, suffix)

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
		
def HSV2RGB(hue, satur, value):
		# This is a copy of the ROOT function TColor::HSV2RGB,
		# which we cannot use because it uses references to return
		# several values.
		# TODO: Find a proper way to deal with C++ references from
		# PyROOT, then replace this function by a call to
		# TColor::HSV2RGB.
		
		
		# Static method to compute RGB from HSV.
		# - The hue value runs from 0 to 360.
		# - The saturation is the degree of strength or purity and is from 0 to 1.
		#   Purity is how much white is added to the color, so S=1 makes the purest
		#   color (no white).
		# - Brightness value also ranges from 0 to 1, where 0 is the black.
		# The returned r,g,b triplet is between [0,1].

		if satur==0.:
			# Achromatic (grey)
			r = g = b = value
			return (r, g, b)

		hue /= 60.;   # sector 0 to 5
		i = int(math.floor(hue))
		f = hue-i;   # factorial part of hue
		p = value*(1-satur)
		q = value*(1-satur*f )
		t = value*(1-satur*(1-f))

		if i==0:
			r = value
			g = t
			b = p
		elif i==1:
			r = q
			g = value
			b = p
		elif i==2:
			r = p
			g = value
			b = t
		elif i==3:
			r = p
			g = q
			b = value
		elif i==4:
			r = t
			g = p
			b = value
		else:
			r = value
			g = p
			b = q

		return (r,g,b)
