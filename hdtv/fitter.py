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
import ROOT
import dlmgr
import peak

dlmgr.LoadLibrary("fit")

class Fitter:
	"""
	"""
	def __init__(self, spec, peakModel, bgdeg=1):
		self.spec = spec
		self.SetPeakModel(peakModel)
		self.bgdeg = bgdeg
		self.fitter = None
		self.bgfitter = None
		self.resultPeaks = []
	
	def __getattr__(self, name):
		if self.fitter:
			return getattr(self.fitter, name)


	def FitBackground(self, backgrounds):
		# do the background fit
		bgfitter = ROOT.HDTV.Fit.PolyBg(self.bgdeg)
		for bg in backgrounds:
			bgfitter.AddRegion(bg[0], bg[1])
		self.bgfitter = bgfitter
		self.bgfitter.Fit(self.spec.fHist)


	def FitPeaks(self, region, peaklist):
		self.peakModel.fCal = self.spec.cal
		peaklist.sort()
		self.fitter = self.peakModel.GetFitter(region, peaklist)
		# Do the fit
		if self.bgfitter:
			self.fitter.Fit(self.spec.fHist, self.bgfitter)
		else:
			self.fitter.Fit(self.spec.fHist)
		peaks = []
		for i in range(0, self.fitter.GetNumPeaks()):
			peaks.append(self.peakModel.CopyPeak(self.fitter.GetPeak(i)))
		self.resultPeaks = peaks
		

	def SetPeakModel(self, model):
		"""
		Sets the peak model to be used for fitting. model can be either a string, in
		which case it is used as a key into the gPeakModels dictionary, or a PeakModel
		object.
		"""
		global gPeakModels
		if type(model) == str:
			model = gPeakModels[model]
		self.peakModel = model()
		
	
	def SetParameter(self, parname, status):
		"""
		Sets a parameter of the underlying peak model
		"""
		self.peakModel.SetParameter(parname, status)
	
	
	def GetParameters(self):
		"""
		Return a list of parameter names of the peak model, in the preferred ordering
		"""
		if self.peakModel:
			return self.peakModel.OrderedParamKeys()
		else:
			return []


	def ResetParameters(self):
		"""
		Resets all parameters of the underlying peak model to their default values
		"""
		self.peakModel.ResetParamStatus()

	def OptionsStr(self):
		"""
		Returns a string describing the currently set fit parameters
		"""
		statstr = str()
		statstr += "Background model: polynomial, deg=%d\n" % self.bgdeg
		statstr += "Peak model: %s\n" % self.peakModel.Name()
		statstr += "\n"
		for name in self.peakModel.OrderedParamKeys():
			status = self.peakModel.fParStatus[name]
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
		
			
	def DataStr(self):
		text = str()
		if self.bgfitter:
			deg = self.bgfitter.GetDegree()
			chisquare = self.bgfitter.GetChisquare()
			text += "Background (seperate fit): degree = %d   chi^2 = %.2f\n" % (deg, chisquare)
			for i in range(0,deg+1):
				value = hdtv.util.ErrValue(self.bgfitter.GetCoeff(i),
				                           self.bgfitter.GetCoeffError(i))
				text += "bg[%d]: %s   " % (i, value.fmt())
			text += "\n\n"
		i = 1
		if self.fitter:
			text += "Peak fit: chi^2 = %.2f\n" % self.fitter.GetChisquare()
			for peak in self.resultPeaks:
				text += "Peak %d:\n%s\n" % (i, str(peak))
				i += 1
        # For debugging only		
		# text += "\n"
		# text += "Volume: %.6f +- %.6f\n" % (self.fitter.GetVol(), self.fitter.GetVolError())
		return text





# global dictionary of available peak models
def RegisterPeakModel(name, model):
	gPeakModels[name] = model
	
gPeakModels = dict()

RegisterPeakModel("theuerkauf", peak.PeakModelTheuerkauf)
RegisterPeakModel("ee", peak.PeakModelEE)


