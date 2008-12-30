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
		
class TheuerkaufPeak:
	"""
	Peak object for the Theuerkauf (classic TV) fitter
	"""
	def __init__(self, pos, vol, fwhm, tl, tr):
		self.pos = pos
		self.vol = vol
		self.fwhm = fwhm
		self.tl = tl
		self.tr = tr
		
	def GetPos(self):
		return self.pos.value
		
	def __str__(self):
		text = ""

		text += "Pos:        " + self.pos.fmt() + "\n"
		text += "Volume:     " + self.vol.fmt() + "\n"
		text += "FWHM:       " + self.fwhm.fmt() + "\n"
		
		if self.tl != None:
			text += "Left Tail:  " + self.tl.fmt() + "\n"
		else:
			text += "Left Tail:  None\n"
			
		if self.tr != None:
			text += "Right Tail: " + self.tr.fmt() + "\n"
		else:
			text += "Right Tail: None\n"
			
		return text

# For each model implemented on the C++ side, we have a corresponding Python
# class to handle fitter setup and data transfer to the Python side

# Base class for all peak models
class PeakModel:
	def __init__(self):
		self.fGlobalParams = dict()
		
	def ResetGlobalParams(self):
		self.fGlobalParams.clear()
		
	def CheckParStatusLen(self, minlen):
		"""
		Checks if each parameter status provided on a peak-by-peak basis
		has at least minlen entires. Raises a RuntimeError with an appropriate
		error message if the check fails.
		"""
		for (parname, status) in self.fParStatus.iteritems():
			if type(status) == list and len(status) < minlen:
				raise RuntimeError, "Not enough values for status of %s" % parname
		
	def ParseParamStatus(self, parname, status):
		"""
		Parse a parameter status specification string
		"""
		# Case-insensitive matching
		status = status.strip().lower()
	
		# Check to see if status corresponds, possibly abbreviated,
		#  to a number of special keywords
		stat = None
		if len(status) < 1:
			raise ValueError
		elif "free"[0:len(status)] == status:
			stat = "free"
		elif "ifree"[0:len(status)] == status:
			stat = "ifree"
		elif "disabled"[0:len(status)] == status:
			stat = "disabled"
		elif "hold"[0:len(status)] == status:
			stat = "hold"
	
		# If status was a keyword, see if this setting is legal for the
		#  parameter in question
		if stat != None:
			if stat in self.fValidParStatus[parname]:
				return stat
			else:
				raise RuntimeError, "Invalid status %s for parameter %s" % (stat, parname)
		# If status was not a keyword, try to parse it as a string
		else:
			return float(status)
		
	def SetParameter(self, parname, status):
		"""
		Set status for a certain parameter
		"""
		parname = parname.strip().lower()
		
		if not parname in self.fValidParStatus.keys():
			raise RuntimeError, "Invalid parameter name"
			
		if "," in status:
			self.fParStatus[parname] = map(lambda s: self.ParseParamStatus(parname, s),
			                               status.split(","))
		else:
			self.fParStatus[parname] = self.ParseParamStatus(parname, status)
		
	def GetParam(self, name, pk, ival=None):
		"""
		Return an appropriate HDTV.Fit.Param object for the specified parameter
		"""
		# See if the parameter status has been specified for each peak
		# individually, or for all peaks at once
		if type(self.fParStatus[name]) == list:
			parStatus = self.fParStatus[name][pk]
		else:
			parStatus = self.fParStatus[name]
			
		# Switch according to parameter status
		if parStatus == "free":
			if not name in self.fGlobalParams:
				if ival == None:
					self.fGlobalParams[name] = self.fFitter.AllocParam()
				else:
					self.fGlobalParams[name] = self.fFitter.AllocParam(ival)
			return self.fGlobalParams[name]
		elif parStatus == "ifree":
			if ival == None:
				return self.fFitter.AllocParam()
			else:
				return self.fFitter.AllocParam(ival)
		elif parStatus == "hold":
			if ival == None:
				return ROOT.HDTV.Fit.Param.Fixed()
			else:
				return ROOT.HDTV.Fit.Param.Fixed(ival)
		elif parStatus == "disabled":
			return False
		elif type(parStatus) == float:
			return ROOT.HDTV.Fit.Param.Fixed(parStatus)
		else:
			raise RuntimeError, "Invalid parameter status"
			
# TVs classic peak model
class PeakModelTheuerkauf(PeakModel):
	def __init__(self):
		PeakModel.__init__(self)
		self.fOrderedParamKeys = ["pos", "vol", "sigma", "tl", "tr"]
		self.fParStatus = { "pos": None, "vol": None, "sigma": None,
		                    "tl": None, "tr": None }
		self.fValidParStatus = { "pos":   [ float, "ifree", "hold" ],
		                         "vol":   [ float, "ifree", "hold" ],
		                         "sigma": [ float, "ifree", "free" ],
		                         "tl":    [ float, "ifree", "free", "disabled" ],
		                         "tr":    [ float, "ifree", "free", "disabled" ] }
		                         
		self.ResetParamStatus()
		
	def Name(self):
		return "theuerkauf"
		
	def OrderedParamKeys(self):
		"""
		Return the names of all peak parameters in the preferred ordering
		"""
		return self.fOrderedParamKeys
		
	def CopyPeak(self, cpeak):
		pos = util.ErrValue(cpeak.GetPos(), cpeak.GetPosError())
		vol = util.ErrValue(cpeak.GetVol(), cpeak.GetVolError())
		fwhm = util.ErrValue(cpeak.GetFWHM(), cpeak.GetFWHMError())
		
		if cpeak.HasLeftTail():
			tl = util.ErrValue(cpeak.GetLeftTail(), cpeak.GetLeftTailError())
		else:
			tl = None
			
		if cpeak.HasRightTail():
			tr = util.ErrValue(cpeak.GetRightTail(), cpeak.GetRightTailError())
		else:
			tr = None
			
		return TheuerkaufPeak(pos, vol, fwhm, tl, tr)
		
	def ResetParamStatus(self):
		"""
		Reset parameter status to defaults
		"""
		self.fParStatus["pos"] = "ifree"
		self.fParStatus["vol"] = "ifree"
		self.fParStatus["sigma"] = "free"
		self.fParStatus["tl"] = "disabled"
		self.fParStatus["tr"] = "disabled"
		
	def GetFitter(self, region, peaklist):
		# Define a fitter and a region
		self.fFitter = ROOT.HDTV.Fit.TheuerkaufFitter(region[0], region[1])
		self.ResetGlobalParams()
		
		# Check if enough values are provided in case of per-peak parameters
		#  (the function raises a RuntimeError if the check fails)
		self.CheckParStatusLen(len(peaklist))
		
		# Copy peaks to the fitter
		for pid in range(0, len(peaklist)):
			pos = self.GetParam("pos", pid, peaklist[pid])
			vol = self.GetParam("vol", pid)
			sigma = self.GetParam("sigma", pid)
			tl = self.GetParam("tl", pid)
			tr = self.GetParam("tr", pid)
			peak = ROOT.HDTV.Fit.TheuerkaufPeak(pos, vol, sigma, tl, tr)
			self.fFitter.AddPeak(peak)
			
		return self.fFitter

# Peak model for electron-electron scattering
# Implementation requested by Oleksiy Burda <burda@ikp.tu-darmstadt.de>
class PeakModelEE(PeakModel):
	"""
	ee scattering peak model
	"""
	def __init__(self):
		PeakModel.__init__(self)
		self.fOrderedParamKeys = ["pos", "amp", "sigma1", "sigma2", "eta", "gamma"]
		self.fParStatus = { "pos": None, "amp": None, "sigma1": None, "sigma2": None,
		                    "eta": None, "gamma": None }
		self.fValidParStatus = { "pos":    [ float, "ifree", "hold" ],
		                         "amp":    [ float, "ifree", "hold" ],
		                         "sigma1": [ float, "free", "ifree" ],
		                         "sigma2": [ float, "free", "ifree" ],
		                         "eta":    [ float, "free", "ifree" ],
		                         "gamma":  [ float, "free", "ifree" ] }
		self.ResetParamStatus()
		
	def Name(self):
		return "ee"
		
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
		
		# Check if enough values are provided in case of per-peak parameters
		#  (the function raises a RuntimeError if the check fails)
		self.CheckParStatusLen(len(peaklist))
			
		for pid in range(0, len(peaklist)):
			pos = self.GetParam("pos", pid, peaklist[pid])
			amp = self.GetParam("amp", pid)
			sigma1 = self.GetParam("sigma1", pid)
			sigma2 = self.GetParam("sigma2", pid)
			eta = self.GetParam("eta", pid)
			gamma = self.GetParam("gamma", pid)
			peak = ROOT.HDTV.Fit.EEPeak(pos, amp, sigma1, sigma2, eta, gamma)
			self.fFitter.AddPeak(peak)
			
		return self.fFitter

# Obsolete
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
