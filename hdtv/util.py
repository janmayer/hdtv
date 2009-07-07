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

import math

def GetCompleteOptions(begin, options):
	l = len(begin)
	return [o + " " for o in options if o[0:l] == begin]
	
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

	def __eq__(self, other):
		"""
		Test for equality; taking errors into account
		"""
		# Check given objects
		val1 = self._sanitize(self)
		val2 = self._sanitize(other)
		
		# Do the comparison
		if (abs(val1.value - val2.value) <= (abs(val1.error) + abs(val2.error))):
			return True
		else:
			return False
		
	def __cmp__(self, other):
		"""
		compare by value
		"""
		# Check given objects
		
		otherval = self._sanitize(other)
		
		return cmp(self.value, otherval.value)
		
	def _sanitize(self, val):
		"""
		* Convert floats to ErrValue with error=0, if necessary
		* Return .error=0 for .error==None values to be able to do calculations
		"""
		ret = ErrValue(0, 0)
		
		try:
			ret.value = val.value
			ret.error = abs(val.error)
		except AttributeError:
			ret.value = val
			ret.error = 0
			
		return ret
		
	def fmt(self):
	
		try:
			# Call fmt_no_error() for values without error
			if self.error == None:
				return self.fmt_no_error()

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
			except (ValueError, OverflowError):
				log10_val = 0.

			if log10_val >= 6 or log10_val <= -2:
				# Use scientific notation
				suffix = "e%d" % int(log10_val)
				exp = 10 ** log10_val
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
				except (ValueError, OverflowError):
					prec = 6
					
			# Limit precision to sensible values, and capture NaN
			#  (Note that NaN is by definition unequal to itself)
			if prec > 20:
				prec = 20
			elif prec != prec:
				prec = 3
				
			return "%s%.*f(%.0f)%s" % (sgn, int(prec), value, error * 10 ** prec, suffix)
		
		except (ValueError, TypeError):
			return ""
		
	def fmt_no_error(self, prec=6):
		try:
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
			except (ValueError, OverflowError):
				log10_val = 0.
			
			if log10_val >= 6 or log10_val <= -2:
				# Use scientific notation
				suffix = "e%d" % int(log10_val)
				value /= 10 ** log10_val
			else:
				# Use normal notation
				suffix = ""
				
			return "%s%.*f%s" % (sgn, prec, value, suffix)
		except (ValueError, TypeError):
			return ""

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



