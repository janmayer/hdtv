import ROOT
import dlmgr
import peak
import color
import sys
import hdtv.util

dlmgr.LoadLibrary("fit")

class Fit:
	"""
	Fit object
	
	A Fit object is the graphical representation of a fit in HDTV. It contains the
	actual fitter as well as the DisplayFunctions and markers for displaying its
	results.
	
	All values (fit parameters, fit region, peak list) are in calibrated units.
	If spec has a calibration, they will automatically be converted into uncalibrated
	units before passing them to the C++ fitter.
	"""
	
	def __init__(self, spec=None, region=[], peaklist=[], bglist=[]):
		self.__dict__["spec"] = spec          # Associated Spectrum() object
		self.__dict__["region"] = region      # Tuple containing region considered in peak fit
		self.__dict__["peaklist"] = peaklist  # List of peak positions
		self.__dict__["bglist"] = bglist      # List of regions considered in background fit
		self.__dict__["fitter"] = None        # C++ peak fitter
		self.__dict__["bgfitter"] = None      # C++ background fitter
		self.__dict__["resultPeaks"] = []     # Positions of peaks
		self.__dict__["dispFunc"] = None      # DisplayFunc for sum
		self.__dict__["dispBgFunc"] = None    # DisplayFunc for background
		self.__dict__["dispDecompFuncs"] = list()  # List of DisplayFunc s for peak decomposition
		self.__dict__["viewport"] = None      # View on which fit is being displayed
		self.__dict__["bgdeg"] = 0            # Degree of background polynomial
		
		self.__dict__["showDecomp"] = False   # Show decomposition of fit
		
		self.fPeakModel = None
		
	def SetParameter(self, parname, status):
		"""
		Sets a parameter of the underlying peak model
		"""
		self.fPeakModel.SetParameter(parname, status)
		self.ResetPeak()
		
	def ResetParameters(self):
		"""
		Resets all parameters of the underlying peak model to their default values
		"""
		self.fPeakModel.ResetParamStatus()
		self.ResetPeak()
		
	def SetPeakModel(self, model):
		"""
		Sets the peak model to be used for fitting. model can be either a string, in
		which case it is used as a key into the gPeakModels dictionary, or a PeakModel
		object.
		"""
		global gPeakModels
		
		if type(model) == str:
			model = gPeakModels[model]
			
		self.fPeakModel = model()
		self.ResetPeak()
		
	def GetParameters(self):
		"Return a list of parameter names of the peak model, in the preferred ordering"
		if self.fPeakModel:
			return self.fPeakModel.OrderedParamKeys()
		else:
			return []

	def __setattr__(self, key, val):
		"""
		Set fit parameter (overwrites the normal set function!)
		 
		The fitter must be reinitialized before the next fit, if the value of 
		spec, region, peaklist, bglist, leftTail or rightTail changed.
		"""
		if key in ["spec", "bglist", "bgdeg"]:
			self.ResetBackground()
		if key in ["spec", "region", "peaklist"]: 
			self.ResetPeak()

		if key == "bglist":
			if val==None:
				val= []
		
		self.__dict__[key] = val

	def ResetParamStatus(self):
		print "WARNING: Used deprecated function ResetParamStatus"
		self.ResetParameters()

	def InitFitter(self):
		"""
		Initialize a new C++ Fitter Object
		"""
		if not self.fPeakModel:
			raise RuntimeError, "No peak model defined"
		
		self.fPeakModel.fCal = self.spec.fCal
		self.peaklist.sort()
		self.fitter = self.fPeakModel.GetFitter(self.region, self.peaklist)
		
	def InitBgFitter(self, fittype = ROOT.HDTV.Fit.PolyBg):
		"""
		Initialize a new background fitter
		"""
		bgfitter = ROOT.HDTV.Fit.PolyBg(self.bgdeg)
		for bg in self.bglist:
			bgfitter.AddRegion(self.spec.E2Ch(bg[0]), self.spec.E2Ch(bg[1]))
		self.bgfitter = bgfitter
		
	def ResetBackground(self):
		"""
		Reset the background fitter
		"""
		if self.dispBgFunc:
			self.dispBgFunc.Remove()
			self.dispBgFunc = None
		
		self.__dict__["bgfitter"] = None
		
	def ResetPeak(self):
		"""
		Reset the peak fitter
		"""
		# Delete all functions dependent on the fitter
		if self.fitter and self.dispBgFunc:
			self.dispBgFunc.Remove()
			self.dispBgFunc = None
			
		if self.dispFunc:
			self.dispFunc.Remove()
			self.dispFunc = None
			
		for dispFunc in self.dispDecompFuncs:
			dispFunc.Remove()
		self.dispDecompFuncs = list()
			
		self.__dict__["fitter"] = None
		self.__dict__["resultPeaks"] = []
		
	def Reset(self):
		"""
		Resets the fitter to its original state
		"""
		self.ResetBackground()
		self.ResetPeak()
	
	def DoPeakFit(self, update=True):
		""" 
		Fit all peaks in the current region
		"""
		# Check if there is a spectrum available
		if not self.spec:
			raise RuntimeError, "No spectrum to fit"
		
		# Check if there is already a fitter available
		if not self.fitter:
			self.InitFitter()
		
		# Do the fit
		if self.bgfitter:
			self.fitter.Fit(self.spec.fHist, self.bgfitter)
		else:
			self.fitter.Fit(self.spec.fHist)
		
		numPeaks = self.fitter.GetNumPeaks()
		
		# Copy information for each peak
		peaks = []
		for i in range(0, numPeaks):
			peaks.append(self.fPeakModel.CopyPeak(self.fitter.GetPeak(i)))
		self.resultPeaks = peaks
			
		# Draw function to viewport
		if(update):
			self.Update()

	def DoBgFit(self, update=True):
		"""
		Fit the background function in the current region
		"""
		# Check if there is a spectrum available
		if not self.spec:
			raise RuntimeError, "No spectrum to fit"
		
		# Check if there is already a fitter available
		if not self.bgfitter:
			self.InitBgFitter()
			
		# Reset possible peak fit
		self.ResetPeak()
		
		# Do the fit
		self.bgfitter.Fit(self.spec.fHist)

		# Draw function to viewport
		if(update):
			self.Update()

	def DoFit(self):
		"""
		Fit first the background and then the peaks
		"""
		# Fit the background
		self.DoBgFit(update=False)
		# Fit the peaks
		self.DoPeakFit(update=True)

	def Realize(self, viewport):
		"""
		Display this fit in the viewport given
		"""
		if self.viewport:
			raise RuntimeError, "Fit is already realized"
			
		if not viewport:
			raise RuntimeError, "Called Realize() with invalid viewport"
		
		# Save the viewport
		self.viewport = viewport
		
		# Draw everything we have to the viewport
		self.Update()
			
	def Delete(self):
		"""
		Delete this fit from its viewport
		"""
		# Remove the viewport from this object
		self.viewport = None
		
		# Delete everything drawn
		self.Update()

	def Update(self):
		""" 
		Update the screen
		"""
		# Lock updates
		if self.viewport:
			self.viewport.LockUpdate()
			
		# Delete old display functions
		if self.dispBgFunc:
			self.dispBgFunc.Remove()
			self.dispBgFunc = None
			
		if self.dispFunc:
			self.dispFunc.Remove()
			self.dispFunc = None
			
		for dispFunc in self.dispDecompFuncs:
			dispFunc.Remove()
		self.dispDecompFuncs = list()
			
		# Nothing more to do if there is no viewport
		if not self.viewport:
			return
		
		# Create new display functions
		if self.bgfitter and not self.fitter:
			func = self.bgfitter.GetFunc()
			self.dispBgFunc = ROOT.HDTV.Display.DisplayFunc(func, color.FIT_BG_FUNC)
			if self.spec.fCal:
				self.dispBgFunc.SetCal(self.spec.fCal)
			self.dispBgFunc.Draw(self.viewport)
		
		if self.fitter:
			func = self.fitter.GetBgFunc()
			self.dispBgFunc = ROOT.HDTV.Display.DisplayFunc(func, color.FIT_BG_FUNC)
			if self.spec.fCal:
				self.dispBgFunc.SetCal(self.spec.fCal)
			self.dispBgFunc.Draw(self.viewport)
		
			func = self.fitter.GetSumFunc()
			self.dispFunc = ROOT.HDTV.Display.DisplayFunc(func, color.FIT_SUM_FUNC)
			if self.spec.fCal:
				self.dispFunc.SetCal(self.spec.fCal)
			self.dispFunc.Draw(self.viewport)
			
		if self.showDecomp and self.fitter:
			for i in range(0, self.fitter.GetNumPeaks()):
				func = self.fitter.GetPeak(i).GetFunc()
				dispFunc = ROOT.HDTV.Display.DisplayFunc(func, color.FIT_DECOMP_FUNC)
				if self.spec.fCal:
					dispFunc.SetCal(self.spec.fCal)
				dispFunc.Draw(self.viewport)
				self.dispDecompFuncs.append(dispFunc)
		
		# finally update the viewport
		self.viewport.UnlockUpdate()
		
	def SetDecomp(self, stat):
		"""
		Sets whether to display a decomposition of the fit
		"""
		# Transition True -> False
		if self.showDecomp and not stat:
			for dispFunc in self.dispDecompFuncs:
				dispFunc.Remove()
			self.dispDecompFuncs = list()
		
		# Transition False -> True
		if not self.showDecomp and stat:
			if self.viewport and self.fitter:
				for i in range(0, self.fitter.GetNumPeaks()):
					func = self.fitter.GetPeak(i).GetFunc()
					dispFunc = ROOT.HDTV.Display.DisplayFunc(func, color.FIT_DECOMP_FUNC)
					if self.spec.fCal:
						dispFunc.SetCal(self.spec.fCal)
					dispFunc.Draw(self.viewport)
					self.dispDecompFuncs.append(dispFunc)
					
		self.showDecomp = stat
			
	def OptionsStr(self):
		"Returns a string describing the currently set fit parameters"
		statstr = str()
	
		statstr += "Background model: polynomial, deg=%d\n" % self.bgdeg
		statstr += "Peak model: %s\n" % self.fPeakModel.Name()
		statstr += "\n"
	
		for name in self.fPeakModel.OrderedParamKeys():
			status = self.fPeakModel.fParStatus[name]

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

def RegisterPeakModel(name, model):
	gPeakModels[name] = model
	
gPeakModels = dict()

RegisterPeakModel("theuerkauf", peak.PeakModelTheuerkauf)
RegisterPeakModel("ee", peak.PeakModelEE)
