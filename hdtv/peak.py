import util
import ROOT

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
		text += "Volume: " + self.vol.fmt() + "\n"
		
		return text

# For each model implemented on the C++ side, we have a corresponding Python
# class to handle fitter setup and data transfer to the Python side

# Base class for all peak models
class PeakModel:
	def __init__(self):
		self.fGlobalParams = dict()
		
	def ResetGlobalParams(self):
		self.fGlobalParams = dict()
		
	def GetParam(self, name, ival=None):
		if self.fParStatus[name] == "free":
			if not name in self.fGlobalParams:
				if ival == None:
					self.fGlobalParams[name] = self.fFitter.AllocParam()
				else:
					self.fGlobalParams[name] = self.fFitter.AllocParam(ival)
			return self.fGlobalParams[name]
		elif self.fParStatus[name] == "ifree":
			if ival == None:
				return self.fFitter.AllocParam()
			else:
				return self.fFitter.AllocParam(ival)
		elif self.fParStatus[name] == "fixed":
			return ROOT.HDTV.Fit.Param.Fixed(ival)
		else:
			return ROOT.HDTV.Fit.Param.Fixed(float(self.fParStatus[name]))
			
# TVs classic peak model
class PeakModelTheuerkauf(PeakModel):
	def __init__(self):
		pass
		
	def attic(self):
		# Define a fitter and a region
		fitter = ROOT.HDTV.Fit.TheuerkaufFitter(self.region[0], self.region[1])
			
		# Add all peaks
		# Like the original TV program, we use a common width and a common tail
		# for all peaks
		sigma = fitter.AllocParam()
			
		if self.leftTail.lower() == 'fit':
			lt = fitter.AllocParam()
		elif self.leftTail == None:
			lt = False
		else:
			lt = ROOT.HDTV.Fit.Param.Fixed(self.leftTail)
		
		if self.rightTail.lower() == 'fit':
			rt = fitter.AllocParam()
		elif self.rightTail == None:
			rt = False
		else:
			rt = ROOT.HDTV.Fit.Param.Fixed(self.rightTail)
				
		# Copy peaks to the fitter
		for _pos in self.peaklist:
			pos = fitter.AllocParam(_pos)
			vol = fitter.AllocParam()
			peak = ROOT.HDTV.Fit.TheuerkaufPeak(pos, vol, sigma, lt, rt)
			fitter.AddPeak(peak)

		self.fitter = fitter

# Peak model for electron-electron scattering
# Implementation requested by Oleksiy Burda <burda@ikp.tu-darmstadt.de>
class PeakModelEE(PeakModel):
	"""
	ee scattering peak model
	"""
	def __init__(self):
		self.fOrderedParamKeys = ["pos", "amp", "sigma1", "sigma2", "eta", "gamma"]
		self.fParStatus = { "pos": None, "amp": None, "sigma1": None, "sigma2": None,
		                    "eta": None, "gamma": None }
		self.ResetParamStatus()
		
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
		
	def SetParameter(self, parname, status):
		"""
		Set status for a certain parameter
		"""
		parname = parname.lower()
		status = status.lower()
		
		if status in ("free", "ifree"):
			if status == "free" and parname in ("pos", "amp"):
				raise RuntimeError, "pos and amp must be ifree, not free" 
			self.fParStatus[parname] = status
		else:
			self.fParStatus[parname] = float(status)
		
	def OrderedParamKeys(self):
		"""
		Return the names of all peak parameters in the preferred ordering
		"""
		return self.fOrderedParamKeys
		
	def ResetParamStatus(self):
		"""
		Reset parameter status to defaults
		"""
		self.fParStatus["pos"] = "ifree"
		self.fParStatus["amp"] = "ifree"
		self.fParStatus["sigma1"] = "free"
		self.fParStatus["sigma2"] = "free"
		self.fParStatus["eta"] = "free"
		self.fParStatus["gamma"] = "free"
		
	def GetFitter(self, region, peaklist):
		self.fFitter = ROOT.HDTV.Fit.EEFitter(region[0], region[1])
		self.ResetGlobalParams()
			
		for _pos in peaklist:
			pos = self.GetParam("pos", _pos)
			amp = self.GetParam("amp")
			sigma1 = self.GetParam("sigma1")
			sigma2 = self.GetParam("sigma2")
			eta = self.GetParam("eta")
			gamma = self.GetParam("gamma")
			peak = ROOT.HDTV.Fit.EEPeak(pos, amp, sigma1, sigma2, eta, gamma)
			self.fFitter.AddPeak(peak)
			
		return self.fFitter

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
