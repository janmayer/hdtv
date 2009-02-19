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
	
	All values (fit parameters, fit region, peak list) are in uncalibrated units.
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
		self.__dict__["bgdeg"] = None         # Degree of background polynomial
		self.__dict__["peakmodel"] = None     # Peak model
		
		self.__dict__["showDecomp"] = False   # Show decomposition of fit
		
	def __setattr__(self, key, val):
		"""
		Set fit parameter (overwrites the normal set function!)
		 
		The fitter must be reinitialized before the next fit, if the value of 
		spec, region, peaklist, bglist, leftTail or rightTail changed.
		"""
		# Allow doing a set with no effect without reset
		if key in self.__dict__ and self.__dict__[key] == val:
			return
		
		if key in ["spec", "bglist", "bgdeg"]:
			self.ResetBackground()
		if key in ["peakmodel", "spec", "region", "peaklist"]: 
			self.ResetPeak()

		if key == "bglist":
			if val==None:
				val= []
		
		self.__dict__[key] = val
		
	def E2Ch(self, e):
		if self.spec.fCal:
			return self.spec.fCal.E2Ch(e)
		else:
			return e
			
	def Ch2E(self, ch):
		if self.spec.fCal:
			return self.spec.fCal.Ch2E(ch)
		else:
			return ch
			
	def dEdCh(self, ch):
		if self.spec.fCal:
			return self.spec.fCal.dEdCh(ch)
		else:
			return 1.0

	def InitFitter(self):
		"""
		Initialize a new C++ Fitter Object
		"""
		if not self.peakmodel:
			raise RuntimeError, "No peak model defined"
		
		self.peakmodel.fCal = self.spec.fCal
		self.peaklist.sort()
		self.fitter = self.peakmodel.GetFitter(self.region, self.peaklist)
		
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
		self.__dict__["spec"] = None
	
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
			peaks.append(self.peakmodel.CopyPeak(fit=self, cpeak=self.fitter.GetPeak(i)))
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

	def Draw(self, viewport):
		"""
		Display this fit in the viewport given
		"""
		if self.viewport:
			raise RuntimeError, "Fit is already realized"
			
		if not viewport:
			raise RuntimeError, "Called Draw() with invalid viewport"
		
		# Save the viewport
		self.viewport = viewport
		
		# Draw everything we have to the viewport
		self.Update()
			
	def Remove(self):
		"""
		Delete this fit from its viewport
		"""
		# Remove the viewport from this object
		self.viewport = None
		
		# Delete everything drawn
		self.Update()
		
	def CalibrationChanged(self):
		"""
		Called when the calibration of the associated spectrum changes
		"""
		if self.viewport:
			self.viewport.LockUpdate()
		
		if self.dispBgFunc:
			self.dispBgFunc.SetCal(self.spec.fCal)
		if self.dispFunc:
			self.dispFunc.SetCal(self.spec.fCal)
		for func in self.dispDecompFuncs:
			func.SetCal(self.spec.fCal)
			
		if self.viewport:
			self.viewport.UnlockUpdate()

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
				func = self.fitter.GetPeak(i).GetPeakFunc()
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
					func = self.fitter.GetPeak(i).GetPeakFunc()
					dispFunc = ROOT.HDTV.Display.DisplayFunc(func, color.FIT_DECOMP_FUNC)
					if self.spec.fCal:
						dispFunc.SetCal(self.spec.fCal)
					dispFunc.Draw(self.viewport)
					self.dispDecompFuncs.append(dispFunc)
					
		self.showDecomp = stat
			
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
