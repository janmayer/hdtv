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
	def __init__(self, spec, pos, amp, sigma1, sigma2, eta, gamma, vol):
		self.spec = spec
		self.pos = pos
		self.amp = amp
		self.sigma1 = sigma1
		self.sigma2 = sigma2
		self.eta = eta
		self.gamma = gamma
		self.vol = vol
		

	def __getattr__(self, key):
		"""
		Calculate calibrated values for pos and fwhm on the fly with the 
		current calibration.
		"""
		if key == "pos_cal":
			pos_cal_value = self.spec.cal.Ch2E(self.pos.value)
			pos_cal_error = abs(self.spec.cal.dEdCh(self.pos.value) * self.pos.error)
			return util.ErrValue(pos_cal_value, pos_cal_error)
		elif key == "sigma1_cal":
			sigma1_cal_value = self.spec.cal.Ch2E(self.pos.value) \
			                 - self.spec.cal.Ch2E(self.pos.value - self.sigma1.value)
			# This is only an approximation, valid as d(fwhm_cal)/d(pos_uncal) \approx 0
			#  (which is true for Ch2E \approx linear)
			sigma1_cal_error = abs(self.spec.cal.dEdCh(self.pos.value - self.sigma1.value) * self.sigma1.error)
			return util.ErrValue(sigma1_cal_value, sigma1_cal_error)
		elif key=="sigma2_cal":
			sigma2_cal_value = self.spec.cal.Ch2E(self.pos.value) \
			                 - self.spec.cal.Ch2E(self.pos.value - self.sigma2.value)
			# This is only an approximation, valid as d(fwhm_cal)/d(pos_uncal) \approx 0
			#  (which is true for Ch2E \approx linear)
			sigma2_cal_error = abs(self.spec.cal.dEdCh(self.pos.value - self.sigma2.value) * self.sigma2.error)
			return util.ErrValue(sigma2_cal_value, sigma2_cal_error)

		
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
		text = str()
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
			text += "Step:        None\n"
			
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
		
	def GetParam(self, name, peak_id, ival=None):
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
			return ROOT.HDTV.Fit.Param.Fixed(self.SpecToFitter(name, parStatus))
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
		
	def Uncal(self, parname, value, pos_uncal, cal):
		"""
		Convert a value from calibrated (spectrum) to uncalibrated (fitter) units
		"""
		if parname == "pos":
			return cal.E2Ch(value)
		elif parname == "width":
			pos_cal = cal.Ch2E(pos_uncal)
			fwhm_uncal = cal.E2Ch(pos_cal + value/2.) - cal.E2Ch(pos_cal - value/2.)
			# Note that the underlying fitter uses ``sigma'' as a parameter
			#  (see HDTV technical documentation in the wiki)
			return fwhm_uncal / (2. * math.sqrt(2. * math.log(2.)))
		elif parname in ("vol", "tl", "tr", "sh", "sw"):
			return value
		else:
			raise RuntimeError, "Unexpected parameter name"

	def GetFitter(self, region, peaklist, cal):
		# Define a fitter and a region
		self.fFitter = ROOT.HDTV.Fit.TheuerkaufFitter(region[0],region[1])
		self.ResetGlobalParams()
		
		# Check if enough values are provided in case of per-peak parameters
		#  (the function raises a RuntimeError if the check fails)
		self.CheckParStatusLen(len(peaklist))
		
		# Copy peaks to the fitter
		for pid in range(0, len(peaklist)):
			pos = peaklist[pid]
			
			self.SpecToFitter = lambda parname, value: self.Uncal(parname, value, pos_uncal=pos, cal=cal)
			
			pos = self.GetParam("pos", pid, pos)
			vol = self.GetParam("vol", pid)
			sigma = self.GetParam("width", pid)
			tl = self.GetParam("tl", pid)
			tr = self.GetParam("tr", pid)
			sh = self.GetParam("sh", pid)
			sw = self.GetParam("sw", pid)
			
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
		
	def CopyPeak(self, spec, cpeak):
		"""
		Copies peak data from a C++ peak class to a Python class
		"""
		pos= util.ErrValue(cpeak.GetPos(), cpeak.GetPosError())
		amp = util.ErrValue(cpeak.GetAmp(), cpeak.GetAmpError())
		sigma1 = util.ErrValue(cpeak.GetSigma1(), cpeak.GetSigma1Error())
		sigma2 = util.ErrValue(cpeak.GetSigma2(), cpeak.GetSigma2Error())
		eta = util.ErrValue(cpeak.GetEta(), cpeak.GetEtaError())
		gamma = util.ErrValue(cpeak.GetGamma(), cpeak.GetGammaError())
		vol = util.ErrValue(cpeak.GetVol(), cpeak.GetVolError())
		

		return EEPeak(spec, pos, amp, sigma1, sigma2, eta, gamma, vol)
		
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
		
	
	def Uncal(parname, value, pos_uncal, cal):
		"""
		Convert a value from calibrated to uncalibrated units
		"""
		if parname == "pos":
			return cal.E2Ch(value)
		elif parname == "sigma1":
			pos_cal = cal.Ch2E(pos_uncal)
			left_hwhm_uncal = pos_uncal - cal.E2Ch(pos_cal - value)
			return left_hwhm_uncal
		elif parname == "sigma2":
			pos_cal = cal.Ch2E(pos_uncal)
			right_hwhm_uncal = cal.E2Ch(pos_cal + value) - pos_uncal
			return right_hwhm_uncal
		elif parname in ("amp", "eta", "gamma"):
			return value
		else:
			raise RuntimeError, "Unexpected parameter name"
		
		
	def GetFitter(self, region, peaklist, cal):
		self.fFitter = ROOT.HDTV.Fit.EEFitter(region[0], region[1])
		self.ResetGlobalParams()
		
		# Check if enough values are provided in case of per-peak parameters
		#  (the function raises a RuntimeError if the check fails)
		self.CheckParStatusLen(len(peaklist))
			
		for pid in range(0, len(peaklist)):
			pos = peaklist[pid]
			
			self.SpecToFitter = lambda parname, value: self.Uncal(parname, value, pos_uncal=pos, cal=cal)
		
			pos = self.GetParam("pos", pid, pos_uncal)
			amp = self.GetParam("amp", pid)
			sigma1 = self.GetParam("sigma1", pid)
			sigma2 = self.GetParam("sigma2", pid)
			eta = self.GetParam("eta", pid)
			gamma = self.GetParam("gamma", pid)
			peak = ROOT.HDTV.Fit.EEPeak(pos, amp, sigma1, sigma2, eta, gamma)
			self.fFitter.AddPeak(peak)
			
		return self.fFitter


