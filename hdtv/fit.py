import ROOT
import gspec
from color import *
from peak import Peak

class Fit:
	"""
	Fit object

	all internal values are uncalibrated values (in channels),
	if spec has a calibration then the values will be automatically converted
	between channels and energies when interacting with the user (Input/Output).
	"""
	def __init__(self, spec=None, region=[], peaklist=[], bglist=[], 
							 lTail=0, rTail=0):
		self.spec = spec
		self.region = region
		self.peaklist = peaklist
		self.bglist = bglist
		self.leftTail = lTail
		self.rightTail = rTail
		self.fitter = None
		self.bgfitter = None
		self.bgfunc = None
		self.func = None
		self.resultPeaks = []
		self.peakFuncID = None
		self.bgFuncID = None
		self.viewport=None

	def __setattr__(self, key, val):
		"""
		Set fit parameter (overwrites the normal set function!)
		 
		The fitter must be reinitialized before the next fit, if the value of 
		spec, region, peaklist, bglist, leftTail or rightTail changed.
		Moreover some values have to be transferred to uncalibrated ones,
		before saving.
		"""
		if key in ["spec", "bglist"]:
			# reset background fitter
			self.ResetBackground()
		if key in ["spec", "region", "peaklist", "leftTail", "rightTail"]: 
			# reset fitter as it is deprecated now
			self.ResetPeak()
		if key in ["region", "peaklist"]:
			# convert to uncalibrated values
			val = [self.spec.E2Ch(i) for i in val]
			self.__dict__[key] = val 
		elif key == "bglist":
			if val==None:
				val= []
			# convert all pairs to uncalibrated values
			val = [[self.spec.E2Ch(i[0]), self.spec.E2Ch(i[1])] for i in val] 
			self.__dict__[key] = val
		else:
			# use all other values as they are
			self.__dict__[key] = val

	def InitFitter(self):
		"""
		Initialize a new Fitter Object
		"""
		# define a fitter and a region
		fitter = ROOT.GSFitter(self.region[0],self.region[1])
		# add all peaks
		for peak in self.peaklist:
			fitter.AddPeak(peak)
		# add all background regions
		for bg in self.bglist:
			fitter.AddBgRegion(bg[0],bg[1])
		# add LeftTail
		if self.leftTail:
			fitter.SetLeftTails(self.leftTail)
		# add RightTail
		if self.rightTail:
			fitter.SetRightTails(self.rightTail)
		self.fitter = fitter
		
	def InitBgFitter(self):
		"""
		Initialize a new background fitter
		"""
		bgfitter = ROOT.GSFitter(0., 0.)
		for bg in self.bglist:
			bgfitter.AddBgRegion(bg[0], bg[1])
		self.bgfitter = bgfitter
		
	def ResetBackground(self):
		"""
		Reset the background fitter
		"""
		self.__dict__["bgfitter"] = None
		self.__dict__["bgfunc"] = None
		
	def ResetPeak(self):
		"""
		Reset the peak fitter
		"""
		self.__dict__["fitter"] = None
		self.__dict__["func"] = None
		self.__dict__["resultPeaks"] = []
		
	def Reset(self):
		"""
		Resets the fitter to its original state
		"""
		self.ResetBackground()
		self.ResetPeak()
		
	def DoPeakFit(self, bgfunc=None, update=True):
		""" 
		Fit all peaks in the current region
		"""
		# check if there is a spectrum available
		if not self.spec:
			raise RuntimeError, "No spectrum to fit"
		# check if there is already a fitter available
		if not self.fitter:
			self.InitFitter()
		# use internal background function if available
		if not bgfunc:
			bgfunc = self.bgfunc
		func = self.fitter.Fit(self.spec.fHist, bgfunc)
		self.func = ROOT.TF1(func)
		numPeaks = int(self.func.GetParameter(0))
		
		# information for each peak
		peaks = []
		for i in range(0, numPeaks):
			mean= ROOT.GSFitter.GetPeakPos(self.func, i)
			fwhm = ROOT.GSFitter.GetPeakFWHM(self.func, i)
			vol = ROOT.GSFitter.GetPeakVol(self.func, i)
			lt=ROOT.GSFitter.GetPeakLT(self.func, i)
			rt=ROOT.GSFitter.GetPeakRT(self.func, i)
			peaks.append(Peak(mean, fwhm, vol, lt, rt, cal=self.spec.fCal))
		# draw function to viewport
		if update:
			self.Update(True)
		self.resultPeaks = peaks
		return peaks

	def DoBgFit(self, update=True):
		"""
		Fit the background function in the current region
		"""
		# check if there is a spectrum available
		if not self.spec:
			raise RuntimeError, "No spectrum to fit"
		# check if there is already a fitter available
		if not self.bgfitter:
			self.InitBgFitter()
		bgfunc = self.bgfitter.FitBackground(self.spec.fHist)
		# FIXME: why is this needed? Possibly related to some
		# subtle issue with PyROOT memory management
		self.bgfunc =  ROOT.TF1(bgfunc)
		# draw function to viewport
		if update:
			self.Update(True)
		return self.bgfunc

	def DoFit(self):
		"""
		Fit first the background and then the peaks
		"""
		# fit the background
		bgfunc = self.DoBgFit(update=False)
		# fit the peaks
		peaks = self.DoPeakFit(bgfunc, update=True)
		return peaks

	def Realize(self, viewport, update=True):
		"""
		Draw this spectrum to the window
		"""
		# save the viewport
		self.viewport = viewport
		# TODO: set all markers for this fit (remove old ones before)
		if self.bgfunc:
			self.bgFuncID = viewport.AddFunc(self.bgfunc, kFitDef, False)
			if self.spec.fCal:
				viewport.GetDisplayFunc(self.bgFuncID).SetCal(self.spec.fCal)
		if self.func:
			self.peakFuncID = viewport.AddFunc(self.func, kFitDef, False)
			if self.spec.fCal:
				viewport.GetDisplayFunc(self.peakFuncID).SetCal(self.spec.fCal)
		# finally update the viewport
		if update:
			viewport.Update(True)
			
	def Delete(self, update=True):
		"""
		Delete this fit from the window
		"""
		if self.viewport:
			# TODO: markers?

			# background function
			if not self.bgFuncID==None:
				self.viewport.DeleteFunc(self.bgFuncID)
				self.bgFuncID = None
			# peak function
			if not self.peakFuncID==None:
				self.viewport.DeleteFunc(self.peakFuncID)
				self.peakFuncID = None
			# update the viewport
			if update:
				self.viewport.Update(True)
			# finally remove the viewport from this object
			self.viewport = None

	def Update(self, update=True):
		""" 
		Update the screen
		"""
		if self.viewport:
			# Background
			if not self.bgFuncID==None:
				self.viewport.DeleteFunc(self.bgFuncID)
			if self.bgfunc:
				self.bgFuncID = self.viewport.AddFunc(self.bgfunc, kFitDef, False)
				if self.spec.fCal:
					self.viewport.GetDisplayFunc(self.bgFuncID).SetCal(self.spec.fCal)
			# Peak function
			if not self.peakFuncID==None:
				self.viewport.DeleteFunc(self.peakFuncID)
			if self.func:
				self.peakFuncID = self.viewport.AddFunc(self.func, kFitDef, False)
				if self.spec.fCal:
					self.viewport.GetDisplayFunc(self.peakFuncID).SetCal(self.spec.fCal)
			# finally update the viewport
			if update:
				self.viewport.Update(True)
				
	def __str__(self):
		text = ""
		i = 1
		if self.bgfunc:
			text += "Background (seperate fit)\n"
			text += "bg[0]: %.2f   bg[1]: %.3f\n\n" % (self.bgfunc.GetParameter(0), \
			                                           self.bgfunc.GetParameter(1))
		elif self.func:
			text += "Background\n"
			text += "bg[0]: %.2f   bg[1]: %.3f\n\n" % (ROOT.GSFitter.GetBg0(self.func), \
			                                           ROOT.GSFitter.GetBg1(self.func))

		for peak in self.resultPeaks:
			text += "#%d: %s\n\n" % (i, str(peak))
			
		return text

