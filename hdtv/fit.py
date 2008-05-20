import ROOT
import gspec
import spectrum
import peak

class Fit:
	"""
	Fit object

	all internal values are uncalibrated values (in channels),
	if spec has a calibration then the values will be automatically converted
	between channels and energies when interacting with the user (Input/Output).
	"""
	def __init__(self, spec, region=None, peaklist=None, bglist=None, 
							 lTail=0, rTail=0):
		self.spec = spec
		self.region = region
		self.peaklist = peaklist
		self.bglist = bglist
		self.lTail = lTail
		self.rTail = rTail
		self.fitter = None
		self.peakFunc = None
		self.peakFuncID = None
		self.bgFunc = None
		self.bgFuncID = None
		self.fPeakMarkerIDs = []
		self.fittedPeaks = []

	def __setattr__(self, key, val):
		"""
		set fit parameter (overwrites the normal set function!)

		use calibration to calculate values in channels 
		and reset fitter to None, because it must reinitialized 
		before the next fit.
		"""
		if not key=="fitter":
			# reset fitter as it is deprecated now
			self.__dict__["fitter"] = None
		if key in ["region", "peaklist"]:
			# convert to uncalibrated values
			val = [spec.E2Ch(i) for i in val]
			self.__dict__[key] = val 
		elif key == "bglist":
			# convert all paires to uncalibrated values
			val = [[spec.E2Ch(i[0]), spec.E2Ch(i[1])] for i in bglist] 
			self.__dict__[key] = val
		else:
			# use all other values as they are
			self.__dict__[key] = val
		
	def SetFromMarker(self, marker):
		pass

	def InitFitter(self):
		"""
		This initialized a new Fitter Object
		"""
		# define a fitter and a region
		fitter = ROOT.GSFitter(region[0], region[1])
		# add all peaks
		for peak in self.peaklist:
			fitter.AddPeak(peak)
		# add all background regions
		for bg in self.bglist:
			fitter.AddBgRegion(bg[0], bg[1])
		# add LeftTail
		if leftTail:
			fitter.SetLeftTails(self.leftTail)
		# add RightTail
		if rightTail:
			fitter.SetRightTail(self.rightTail)
		self.fitter=fitter

	def DoPeakFit(self, bgfunc=None):
		""" 
		Fit all peaks in the current region
		"""
		# check if there is already a fitter available
		if not self.fitter:
			self.fitter = InitFitter()
		fitter = self.fitter
		func = fitter.Fit(spec.hist, bgFunc)
		numPeaks = int(func.GetParameter(0))
		# information for each peak
		peaks = []
		for i in range(0, numPeaks):
			mean= ROOT.GSFitter.GetPeakPos(func, i)
			fwhm = ROOT.GSFitter.GetPeakFWHM(func, i)
			vol = ROOT.GSFitter.GetPeakVol(func, i)
			lt=ROOT.GSFitter.GetPeakLT(func, i)
			rt=ROOT.GSFitter.GetPeakRT(func, i)
			peaks.append(Peak(mean, fwhm, vol))
		return peaks

	def DoBgFit(self):
		"""
		Fit the background function in the current region
		"""
		# check if there is already a fitter available
		if not self.fitter:
			self.fitter = InitFitter()
		fitter = self.fitter
		bgFunc = fitter.FitBackground(self.spec)
		return bgfunc

	def DoFit(self):
		"""
		Fit first the background and then the peaks
		"""
		if not self.fitter:
			self.fitter = InitFitter()
		fitter = self.fitter
		# fit the background
		bgfunc = DoBgFit()
		# fit the peaks
		peaks = DoPeakFit(fitter)
		return peaks

	def Realize(self, viewport, update=True):
		# background function
		if self.bgFunc:
			self.bgFuncId = viewport.AddFunc(self.bgFunc, 25, False)
			if self.spec.cal:
				viewport.GetDisplayFunc(self.bgFuncId).SetCal(self.spec.cal)
		# peak function
		if self.peakFunc:
			self.peakFuncId = viewport.AddFunc(self.peakFunc, 10, False)
			if self.spec.cal:
				viewport.GetDisplayFunc(self.peakFuncId).SetCal(self.spec.cal)
		# peak markers
		if self.fittedPeaks:
			self.PeakMarkerIDs = []
			for i in range(0, len(self.fittedPeaks)):
				pos = self.spec.Ch2E(i.pos)
				mid = viewport.AddXMarker(pos, 50, False)
				self.PeakMarkerIDs.append(mid)
		# finally update the viewport
		if update:
			viewport.Update(True)
			
	def Delete(self, viewport, update=True):
		# background function
		if self.bgFuncId:
			viewport.DeleteFunc(self.bgFuncId)
			self.bgFuncId = None
		# peak function
		if self.peakFuncId:
			viewport.DeleteFunc(self.peakFuncId)
			self.peakFuncId = None
		# peak markers
		for mid in self.fPeakMarkerIDs:
			viewport.DeleteXMarker(mid)
		self.fPeakMarkerIDs = []
		# finally update the viewport
		if update:
			viewport.Update(True)
			
	def Update(self, viewport):
		self.Delete(False)
		self.Realize()
		
	def Report(self, output=None):
		"""
		Print the results of the fit to output
		If no output object is given use stdout.
		"""
		pass
