class Peak:
	"""
	Peak object
	"""
	def __init__(self, pos, fwhm, vol, rtail=None, ltail=None):
		# f(x) = norm * exp(-0.5 * ((x - mean) / sigma)**2)
		self.pos = pos
		self.fwhm = fwhm
		self.vol = vol
		self.rtail = rtail
		self.ltail = ltail
		# TODO: Errors
