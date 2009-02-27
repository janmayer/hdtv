import util
import math
import ROOT

class FitValue(util.ErrValue):
	def __init__(self, value, error, free):
		util.ErrValue.__init__(self, value, error)
		self.free = free
		
	def fmt(self):
		if self.free:
			return util.ErrValue.fmt(self)
		else:
			return util.ErrValue.fmt_no_error(self) + " (HOLD)"

class EEPeak:
	"""
	Peak object for the ee fitter
	"""
	def __init__(self, fit, pos, amp, sigma1, sigma2, eta, gamma, vol):
		self.fit = fit
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
	
	All values with the exception of pos_cal and fwhm_cal are uncalibrated.
	"""
	def __init__(self, spec, pos, vol, fwhm, tl, tr, sh, sw):
		# all values uncalibrated
		self.spec = spec
		self.pos = pos
		self.vol = vol
		self.fwhm = fwhm
		self.tl = tl
		self.tr = tr
		self.sh = sh
		self.sw = sw
		
	def __getattr__(self, key):
		"""
		Calculate calibrated values for pos and fwhm on the fly with the 
		current calibration.
		"""
		if key == "pos_cal":
			pos_cal_value = self.spec.cal.Ch2E(self.pos.value)
			pos_cal_error = abs(self.spec.cal.dEdCh(self.pos.value) * self.pos.error)
			return FitValue(pos_cal_value, pos_cal_error, self.pos.free)
		elif key == "fwhm_cal":
			hwhm_value = self.fwhm.value / 2.
			fwhm_cal_value = self.spec.cal.Ch2E(self.pos.value + hwhm_value) \
			                   - self.spec.cal.Ch2E(self.pos.value - hwhm_value)
			# This is only an approximation, valid as d(fwhm_cal)/d(pos_uncal) \approx 0
			#  (which is true for Ch2E \approx linear)
			fwhm_cal_error = abs( (self.spec.cal.dEdCh(self.pos.value + hwhm_value) / 2. \
			                        + self.spec.cal.dEdCh(self.pos.value - hwhm_value) / 2. ) \
			                      * self.fwhm.error)
			return FitValue(fwhm_cal_value, fwhm_cal_error, self.fwhm.free)
	
	def __str__(self):
		text = ""

		text += "Pos:         " + self.pos_cal.fmt() + "\n"
		text += "Volume:      " + self.vol.fmt() + "\n"
		text += "FWHM:        " + self.fwhm_cal.fmt() + "\n"
		
		if self.tl != None:
			text += "Left Tail:   " + self.tl.fmt() + "\n"
		else:
			text += "Left Tail:   None\n"
			
		if self.tr != None:
			text += "Right Tail:  " + self.tr.fmt() + "\n"
		else:
			text += "Right Tail:  None\n"
			
		if self.sh != None:
			text += "Step height: " + self.sh.fmt() + "\n"
			text += "Step width:  " + self.sw.fmt() + "\n"
		else:
			text += "Step: None\n"
			
		return text

# For each model implemented on the C++ side, we have a corresponding Python
# class to handle fitter setup and data transfer to the Python side

# Base class for all peak models
class PeakModel:
	"""
	A peak model is a function used to fit peaks. The user can choose how to fit
	its parameters (and whether to include them at all, i.e. for tails). After
	everything has been configured, the peak model produces a C++ fitter object.
	"""
	def __init__(self):
		self.fGlobalParams = dict()

		
	def ResetGlobalParams(self):
		self.fGlobalParams.clear()
		
	def OptionsStr(self):
		"""
		Returns a string describing the currently set parameters of the model
		"""
		statstr = ""
		
		for name in self.OrderedParamKeys():
			status = self.fParStatus[name]

			# Short format for multiple values...
			if type(status) == list:
				statstr += "%s: " % name
				sep = ""
				for stat in status:
					statstr += sep
					if stat in ("free", "equal", "hold", "none"):
						statstr += stat
					else:
						statstr += "%.3f" % stat
					sep = ", "
				statstr += "\n"

			# ... long format for a single value
			else:
				if status == "free":
					statstr += "%s: (individually) free\n" % name
				elif status == "equal":
					statstr += "%s: free and equal\n" % name
				elif status == "hold":
					statstr += "%s: held at default value\n" % name
				elif status == "none":
					statstr += "%s: none (disabled)\n" % name
				else:
					statstr += "%s: fixed at %.3f\n" % (name, status)
					
		return statstr
		
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
		elif "equal"[0:len(status)] == status:
			stat = "equal"
		elif "none"[0:len(status)] == status:
			stat = "none"
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
		
	def GetParam(self, name, peak_id, pos, ival=None):
		"""
		Return an appropriate HDTV.Fit.Param object for the specified parameter
		"""
		# See if the parameter status has been specified for each peak
		# individually, or for all peaks at once
		if type(self.fParStatus[name]) == list:
			parStatus = self.fParStatus[name][peak_id]
		else:
			parStatus = self.fParStatus[name]
			
		# Switch according to parameter status
		if parStatus == "equal":
			if not name in self.fGlobalParams:
				if ival == None:
					self.fGlobalParams[name] = self.fFitter.AllocParam()
				else:
					self.fGlobalParams[name] = self.fFitter.AllocParam(ival)
			return self.fGlobalParams[name]
		elif parStatus == "free":
			if ival == None:
				return self.fFitter.AllocParam()
			else:
				return self.fFitter.AllocParam(ival)
		elif parStatus == "hold":
			if ival == None:
				return ROOT.HDTV.Fit.Param.Fixed()
			else:
				return ROOT.HDTV.Fit.Param.Fixed(ival)
		elif parStatus == "none":
			return ROOT.HDTV.Fit.Param.None()
		elif type(parStatus) == float:
			return ROOT.HDTV.Fit.Param.Fixed(parStatus)
		else:
			raise RuntimeError, "Invalid parameter status"
			
# TVs classic peak model
class PeakModelTheuerkauf(PeakModel):
	def __init__(self):
		PeakModel.__init__(self)
		self.fOrderedParamKeys = ["pos", "vol", "width", "tl", "tr", "sh", "sw"]
		self.fParStatus = { "pos": None, "vol": None, "sigma": None,
		                    "tl": None, "tr": None, "sh": None, "sw": None }
		self.fValidParStatus = { "pos":   [ float, "free", "hold" ],
		                         "vol":   [ float, "free", "hold" ],
		                         "width": [ float, "free", "equal" ],
		                         "tl":    [ float, "free", "equal", "none" ],
		                         "tr":    [ float, "free", "equal", "none" ],
		                         "sh":    [ float, "free", "equal", "none" ],
		                         "sw":    [ float, "free", "equal", "hold" ] }
		                         
		self.ResetParamStatus()
		
	def Name(self):
		return "theuerkauf"
		
	def OrderedParamKeys(self):
		"""
		Return the names of all peak parameters in the preferred ordering
		"""
		return self.fOrderedParamKeys
		
	def CopyPeak(self, spec, cpeak):
		fwhm_value = cpeak.GetSigma() * 2. * math.sqrt(2. * math.log(2.))
		fwhm_error = cpeak.GetSigmaError() * 2. * math.sqrt(2. * math.log(2.))
		
		pos= FitValue(cpeak.GetPos(), cpeak.GetPosError(), cpeak.PosIsFree())
		vol = FitValue(cpeak.GetVol(), cpeak.GetVolError(), cpeak.VolIsFree())
		fwhm = FitValue(fwhm_value, fwhm_error, cpeak.SigmaIsFree())
		
		if cpeak.HasLeftTail():
			tl = FitValue(cpeak.GetLeftTail(), cpeak.GetLeftTailError(), 
			              cpeak.LeftTailIsFree())
		else:
			tl = None
			
		if cpeak.HasRightTail():
			tr = FitValue(cpeak.GetRightTail(), cpeak.GetRightTailError(),
			              cpeak.RightTailIsFree())
		else:
			tr = None
			
		if cpeak.HasStep():
			sh = FitValue(cpeak.GetStepHeight(), cpeak.GetStepHeightError(),
			                   cpeak.StepHeightIsFree())
			sw = FitValue(cpeak.GetStepWidth(), cpeak.GetStepWidthError(),
			                   cpeak.StepWidthIsFree())
		else:
			sh = sw = None
			
		return TheuerkaufPeak(spec, pos, vol, fwhm, tl, tr, sh, sw)
		
	def ResetParamStatus(self):
		"""
		Reset parameter status to defaults
		"""
		self.fParStatus["pos"] = "free"
		self.fParStatus["vol"] = "free"
		self.fParStatus["width"] = "equal"
		self.fParStatus["tl"] = "none"
		self.fParStatus["tr"] = "none"
		self.fParStatus["sh"] = "none"
		self.fParStatus["sw"] = "hold"

	def GetFitter(self, region, peaklist):
		# Define a fitter and a region
		self.fFitter = ROOT.HDTV.Fit.TheuerkaufFitter(region[0],region[1])
		self.ResetGlobalParams()
		
		# Check if enough values are provided in case of per-peak parameters
		#  (the function raises a RuntimeError if the check fails)
		self.CheckParStatusLen(len(peaklist))
		
		# Copy peaks to the fitter
		for pid in range(0, len(peaklist)):
			pos = peaklist[pid]
			
			pos = self.GetParam("pos", pid, pos, pos)
			vol = self.GetParam("vol", pid, pos)
			sigma = self.GetParam("width", pid, pos)
			tl = self.GetParam("tl", pid, pos)
			tr = self.GetParam("tr", pid, pos)
			sh = self.GetParam("sh", pid, pos)
			sw = self.GetParam("sw", pid, pos)
			
			peak = ROOT.HDTV.Fit.TheuerkaufPeak(pos, vol, sigma, tl, tr, sh, sw)
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
		self.fValidParStatus = { "pos":    [ float, "free", "hold" ],
		                         "amp":    [ float, "free", "hold" ],
		                         "sigma1": [ float, "free", "equal" ],
		                         "sigma2": [ float, "free", "equal" ],
		                         "eta":    [ float, "free", "equal" ],
		                         "gamma":  [ float, "free", "equal" ] }
		self.ResetParamStatus()
		
	def Name(self):
		return "ee"
		
	def CopyPeak(self, cpeak):
		"""
		Copies peak data from a C++ peak class to a Python class
		"""
		pos_uncal = cpeak.GetPos()
		pos_err_uncal = cpeak.GetPosError()
		hwhm1_uncal = cpeak.GetSigma1()
		hwhm1_err_uncal = cpeak.GetSigma1Error()
		hwhm2_uncal = cpeak.GetSigma2()
		hwhm2_err_uncal = cpeak.GetSigma2Error()
		
		pos_cal = self.Ch2E(pos_uncal)
		pos_err_cal = abs(self.dEdCh(pos_uncal) * pos_err_uncal)
		
		hwhm1_cal = self.Ch2E(pos_uncal) - self.Ch2E(pos_uncal - hwhm1_uncal)
		hwhm2_cal = self.Ch2E(pos_uncal + hwhm2_uncal) - self.Ch2E(pos_uncal)
		# This is only an approximation, valid as d(fwhm_cal)/d(pos_uncal) \approx 0
		#  (which is true for Ch2E \approx linear)
		hwhm1_err_cal = abs( self.dEdCh(pos_uncal - hwhm1_uncal) * hwhm1_err_uncal)
		hwhm2_err_cal = abs( self.dEdCh(pos_uncal + hwhm2_uncal) * hwhm2_err_uncal)
		
		pos = util.ErrValue(pos_cal, pos_err_cal)
		amp = util.ErrValue(cpeak.GetAmp(), cpeak.GetAmpError())
		sigma1 = util.ErrValue(hwhm1_cal, hwhm1_err_cal)
		sigma2 = util.ErrValue(hwhm2_cal, hwhm2_err_cal)
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
		self.fParStatus["pos"] = "free"
		self.fParStatus["amp"] = "free"
		self.fParStatus["sigma1"] = "equal"
		self.fParStatus["sigma2"] = "equal"
		self.fParStatus["eta"] = "equal"
		self.fParStatus["gamma"] = "equal"
		
	def SpecToFitter(self, parname, value, pos_uncal):
		"""
		Convert a value from calibrated (spectrum) to uncalibrated (fitter) units
		"""
		if parname == "pos":
			return self.E2Ch(value)
		elif parname == "sigma1":
			pos_cal = self.Ch2E(pos_uncal)
			left_hwhm_uncal = pos_uncal - self.E2Ch(pos_cal - value)
			return left_hwhm_uncal
		elif parname == "sigma2":
			pos_cal = self.Ch2E(pos_uncal)
			right_hwhm_uncal = self.E2Ch(pos_cal + value) - pos_uncal
			return right_hwhm_uncal
		elif parname in ("amp", "eta", "gamma"):
			return value
		else:
			raise RuntimeError, "Unexpected parameter name"
		
	def GetFitter(self, region, peaklist_uncal):
		self.fFitter = ROOT.HDTV.Fit.EEFitter(region[0], region[1])
		self.ResetGlobalParams()
		
		# Check if enough values are provided in case of per-peak parameters
		#  (the function raises a RuntimeError if the check fails)
		self.CheckParStatusLen(len(peaklist_uncal))
			
		for pid in range(0, len(peaklist_uncal)):
			pos_uncal = peaklist_uncal[pid]
		
			pos = self.GetParam("pos", pid, pos_uncal, pos_uncal)
			amp = self.GetParam("amp", pid, pos_uncal)
			sigma1 = self.GetParam("sigma1", pid, pos_uncal)
			sigma2 = self.GetParam("sigma2", pid, pos_uncal)
			eta = self.GetParam("eta", pid, pos_uncal)
			gamma = self.GetParam("gamma", pid, pos_uncal)
			peak = ROOT.HDTV.Fit.EEPeak(pos, amp, sigma1, sigma2, eta, gamma)
			self.fFitter.AddPeak(peak)
			
		return self.fFitter

## Obsolete
#class Peak:
#	"""
#	Peak object
#	"""
#	def __init__(self, pos, fwhm, vol, ltail=None, rtail=None, cal=None):
#		# f(x) = norm * exp(-0.5 * ((x - mean) / sigma)**2)
#		self.pos = pos
#		self.fwhm = fwhm
#		self.vol = vol

#		# Tails
#		if ltail and ltail < 1000:
#			self.ltail = ltail
#		else:
#			self.ltail = None
#		if rtail and rtail < 1000:
#			self.rtail = rtail
#		else:
#			self.rtail = None
#		self.cal = cal
#		# TODO: Errors
#		
#	def GetPos(self):
#		if self.cal:
#			return self.cal.Ch2E(self.pos)
#		else:
#			return self.pos

#	def __str__(self):
#		pos = self.pos
#		fwhm = self.fwhm
#		if self.cal:
#			cal = self.cal
#			pos = cal.Ch2E(self.pos)
#			fwhm = cal.Ch2E(self.pos+self.fwhm/2.)-cal.Ch2E(self.pos-self.fwhm/2.)

#		text = "pos: %10.3f   fwhm: %7.3f   vol: %8.1f   " %(pos, fwhm, self.vol)
#		
#		if self.ltail or self.rtail:
#			text += "\n"
#		
#		# Tails
#		if self.ltail:
#			text+="lefttail: %7.3f   " %self.ltail
#		
#		if self.rtail:
#			text+="righttail: %7.3f   "%self.rtail
#		
#		return text
