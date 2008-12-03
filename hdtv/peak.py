import util

class EEPeak:
	"""
	Peak object for the ee fitter
	"""
	def __init__(self, pos, amp, sigma1, sigma2, eta, gamma, vol):
		self.pos = pos
		self.amp = amp
		self.sigma1 = sigma1
		self.sigma2 = sigma2
		self.eta = eta
		self.gamma = gamma
		self.vol = vol
		
	def GetPos(self):
		return self.pos.value
		
	def __str__(self):
		text = ""
		
		text += "Pos:    " + self.pos.fmt() + "\n"
		text += "Amp:    " + self.amp.fmt() + "\n"
		text += "Sigma1: " + self.sigma1.fmt() + "\n"
		text += "Sigma2: " + self.sigma2.fmt() + "\n"
		text += "Eta:    " + self.eta.fmt() + "\n"
		text += "Gamma:  " + self.gamma.fmt() + "\n"
		# text += "Volume: " + self.vol.fmt() + "\n"
		
		return text

# For each model implemented on the C++ side, we have a corresponding Python
# class to handle fitter setup and data transfer to the Python side
class PeakModelEE:
	"""
	ee scattering peak model
	"""
	# Implementation requested by Oleksiy Burda <burda@ikp.tu-darmstadt.de>
	def __init__(self):
		pass
		
	def CopyPeak(self, cpeak):
		"""
		Copies peak data from a C++ peak class to a Python class
		"""
		pos = util.ErrValue(cpeak.GetPos(), cpeak.GetPosError())
		amp = util.ErrValue(cpeak.GetAmp(), cpeak.GetAmpError())
		sigma1 = util.ErrValue(cpeak.GetSigma1(), cpeak.GetSigma1Error())
		sigma2 = util.ErrValue(cpeak.GetSigma2(), cpeak.GetSigma2Error())
		eta = util.ErrValue(cpeak.GetEta(), cpeak.GetEtaError())
		gamma = util.ErrValue(cpeak.GetGamma(), cpeak.GetGammaError())
		vol = util.ErrValue(cpeak.GetVol(), cpeak.GetVolError())

		return EEPeak(pos, amp, sigma1, sigma2, eta, gamma, vol)

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
			fwhm = cal.Ch2E(self.pos+self.fwhm/2.)-cal.Ch2E(self.pos-self.fwhm/2.)

		text = "pos: %10.3f   fwhm: %7.3f   vol: %8.1f   " %(pos, fwhm, self.vol)
		
		if self.ltail or self.rtail:
			text += "\n"
		
		# Tails
		if self.ltail:
			text+="lefttail: %7.3f   " %self.ltail
		
		if self.rtail:
			text+="righttail: %7.3f   "%self.rtail
		
		return text
