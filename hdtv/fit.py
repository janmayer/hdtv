import ROOT
import gspec
import dlmgr
from color import *
from peak import Peak

dlmgr.LoadLibrary("fit")

class Fit:
	"""
	Fit object

	all internal values are uncalibrated values (in channels),
	if spec has a calibration then the values will be automatically converted
	between channels and energies when interacting with the user (Input/Output).
	"""
	def __init__(self, spec=None, region=[], peaklist=[], bglist=[], 
							 lTail=None, rTail=None):
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
		
		self.fBgDeg = 0
		self.fPeakModel = "ee"
		

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
		if self.fPeakModel.lower() == "theuerkauf":
			# Define a fitter and a region
			fitter = ROOT.HDTV.Fit.TheuerkaufFitter(self.region[0],self.region[1])
			
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
		elif self.fPeakModel.lower() == "ee":
			fitter = ROOT.HDTV.Fit.EEFitter(self.region[0], self.region[1])
			
			for _pos in self.peaklist:
				pos = fitter.AllocParam(_pos)
				amp = fitter.AllocParam()
				sigma1 = fitter.AllocParam()
				sigma2 = fitter.AllocParam()
				eta = fitter.AllocParam()
				gamma = fitter.AllocParam()
				peak = ROOT.HDTV.Fit.EEPeak(pos, amp, sigma1, sigma2, eta, gamma)
				fitter.AddPeak(peak)
				
			self.fitter = fitter
		else:
			raise RuntimeError, "Unknown peak model"
		
	def InitBgFitter(self, fittype = ROOT.HDTV.Fit.PolyBg):
		"""
		Initialize a new background fitter
		"""
		bgfitter = ROOT.HDTV.Fit.PolyBg()
		for bg in self.bglist:
			bgfitter.AddRegion(bg[0], bg[1])
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
		#numPeaks = self.fitter.GetNumPeaks()
		
		# information for each peak
		#peaks = []
		#for i in range(0, numPeaks):
		#	peak = fitter.GetPeak(i)
		#	pos = hdtv.util.ErrValue(peak.GetPos(), peak.GetPosError())
		#	fwhm = hdtv.util.ErrValue(peak.GetFWHM(), peak.GetFWHMError())
		#	vol = hdtv.util.ErrValue(peak.GetVol(), peak.GetVolError())
			
		#	if peak.HasLeftTail():
		#		lt = hdtv.util.ErrValue(peak.GetLeftTail(), peak.GetLeftTailError())
		#	else:
		#		lt = None
			
		#	if peak.HasRightTail():
		#		rt = hdtv.util.ErrValue(peak.GetRightTail(), peak.GetRightTailError())
		#	else:
		#		rt = None
			
		#	peaks.append(Peak(mean, fwhm, vol, lt, rt, cal=self.spec.fCal))
		# draw function to viewport
		if update:
			self.Update(True)
		#self.resultPeaks = peaks
		#return peaks

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
		bgfunc = self.bgfitter.Fit(self.spec.fHist)
		# FIXME: why is this needed? Possibly related to some
		# subtle issue with PyROOT memory management
		self.bgfunc = ROOT.TF1(bgfunc)
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

