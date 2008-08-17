class Peak:
	"""
	Peak object
	"""
	def __init__(self, pos, fwhm, vol, ltail=None, rtail=None, cal=None):
		# f(x) = norm * exp(-0.5 * ((x - mean) / sigma)**2)
		self.pos = pos
		self.fwhm = fwhm
		self.vol = vol

		# Tails
		if ltail and ltail < 1000:
			self.ltail = ltail
		else:
			self.ltail = None
		if rtail and rtail < 1000:
			self.rtail = rtail
		else:
			self.rtail = None
		self.cal = cal
		# TODO: Errors
		
	def GetPos(self):
		if self.cal:
			return self.cal.Ch2E(self.pos)
		else:
			return self.pos

	def __str__(self):
		pos = self.pos
		fwhm = self.fwhm
		if self.cal:
			cal = self.cal
			pos = cal.Ch2E(self.pos)
			fwhm = cal.Ch2E(self.pos+self.fwhm)-cal.Ch2E(self.pos-self.fwhm)

		text = "pos: %10.3f   fwhm: %7.3f   vol: %8.1f   " %(pos, fwhm, self.vol)
		
		if self.ltail or self.rtail:
			text += "\n"
		
		# Tails
		if self.ltail:
			text+="lefttail: %7.3f   " %self.ltail
		
		if self.rtail:
			text+="righttail: %7.3f   "%self.rtail
		
		return text
