import hdtv.cmdline
import hdtv.window
import hdtv.cmdhelper
import hdtv.spectrum
import hdtv.fitpanel
import hdtv.marker
import hdtv.peak
from hdtv.color import *
import os
import glob
import ROOT

# Don't add created spectra to the ROOT directory
ROOT.TH1.AddDirectory(ROOT.kFALSE)

class Spectrum(hdtv.spectrum.Spectrum):
	def __init__(self, fname, color):
		self.fFilename = fname
		hdtv.spectrum.Spectrum.__init__(self, fname, color=color)
		
	def IsVisible(self):
		return self.fSid != None
		
class Fit:
	def __init__(self, func, bgfunc, cal):
		self.bgfunc = bgfunc
		self.func = func
		self.fCal = cal

	def Realize(self, viewport, update=True):
		"""
		Draw this spectrum to the window
		"""
		# save the viewport
		self.viewport = viewport
		# TODO: set all markers for this fit (remove old ones before)
		if self.bgfunc:
			self.bgFuncID = viewport.AddFunc(self.bgfunc, kFitDef, False)
			if self.fCal:
				viewport.GetDisplayFunc(self.bgFuncID).SetCal(self.fCal)
		if self.func:
			self.peakFuncID = viewport.AddFunc(self.func, kFitDef, False)
			if self.fCal:
				viewport.GetDisplayFunc(self.peakFuncID).SetCal(self.fCal)
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
				if self.fCal:
					self.viewport.GetDisplayFunc(self.bgFuncID).SetCal(self.fCal)
			# Peak function
			if not self.peakFuncID==None:
				self.viewport.DeleteFunc(self.peakFuncID)
			if self.func:
				self.peakFuncID = self.viewport.AddFunc(self.func, kFitDef, False)
				if self.fCal:
					self.viewport.GetDisplayFunc(self.peakFuncID).SetCal(self.fCal)
			# finally update the viewport
			if update:
				self.viewport.Update(True)
		
class SpecWindow(hdtv.window.Window):
	def __init__(self):
		hdtv.window.Window.__init__(self)
		
		self.fPeakMarkers = []
		self.fRegionMarkers = []
		self.fBgMarkers = []
		self.fFitPanel = hdtv.fitpanel.FitPanel()
		self.fCurrentSpec = None
		self.fCurrentFit = None
		
		self.fDefaultCal = ROOT.GSCalibration(0.0, 0.5)
		
		# self.SetTitle("No spectrum - hdtv")
		
	def KeyHandler(self, key):
		handled = True
	
		if hdtv.window.Window.KeyHandler(self, key):
			pass
		elif key == ROOT.kKey_b:
			self.PutBackgroundMarker()
	  	elif key == ROOT.kKey_r:
			self.PutRegionMarker()
	  	elif key == ROOT.kKey_p:
			self.PutPeakMarker()
	  	elif key == ROOT.kKey_Escape:
	  		self.DeleteFit()
	  	elif key == ROOT.kKey_F:
	  		self.Fit()
	  	elif key == ROOT.kKey_I:
	  		self.IntegrateAll()
	  	else:
	  		handled = False
	  		
	  	return handled
		
	def PutRegionMarker(self):
		self.PutPairedMarker("X", "REGION", self.fRegionMarkers, 1)
			
	def PutBackgroundMarker(self):
		self.PutPairedMarker("X", "BACKGROUND", self.fBgMarkers)
		
	def PutPeakMarker(self):
		pos = self.fViewport.GetCursorX()
  		self.fPeakMarkers.append(hdtv.marker.Marker("PEAK", pos))
  		self.fPeakMarkers[-1].Realize(self.fViewport)
  		
  	def DeleteFit(self):
		for marker in self.fPeakMarkers:
  			marker.Delete(self.fViewport, False)
		for marker in self.fBgMarkers:
  			marker.Delete(self.fViewport, False)
  		for marker in self.fRegionMarkers:
  			marker.Delete(self.fViewport, False)
	  			
  		self.fPendingMarker = None
  		self.fPeakMarkers = []
  		self.fBgMarkers = []
  		self.fRegionMarkers = []
  		
  		if self.fCurrentFit:
			self.fCurrentFit.Delete(False)
			self.fCurrentFit = None
						
		self.fViewport.Update(True)
		
	def Integrate(self, spec, bgFunc=None, corr=1.0):
		if not self.fPendingMarker and len(self.fRegionMarkers) == 1:
			ch_1 = self.E2Ch(self.fRegionMarkers[0].e1)
			ch_2 = self.E2Ch(self.fRegionMarkers[0].e2)
				
			fitter = ROOT.GSFitter(ch_1, ch_2)
			                       
			for marker in self.fBgMarkers:
				fitter.AddBgRegion(self.E2Ch(marker.e1), self.E2Ch(marker.e2))
				
			if not bgFunc and len(self.fBgMarkers) > 0:
				bgFunc = fitter.FitBackground(spec.hist)
			                       
			total_int = fitter.Integrate(spec.hist)
			if bgFunc:
				bg_int = bgFunc.Integral(math.ceil(min(ch_1, ch_2) - 0.5) - 0.5,
				                         math.ceil(max(ch_1, ch_2) - 0.5) + 0.5)
			else:
				bg_int = 0.0
			                          
			#self.fFitPanel.SetText("%.2f %.2f %.2f" % (total_int, bg_int, total_int - bg_int))
			
			integral = total_int - bg_int
			integral_error = math.sqrt(total_int + bg_int)
			
			return (integral * corr, integral_error * corr)
			
	def IntegrateAll(self):
		self.Integrate(self.fViews[0].fSpectra[0])
		
	def Fit(self):
		if self.fCurrentFit:
			self.fCurrentFit.Delete(self.fViewport)
	
	  	if self.fCurrentSpec and \
	  		not self.fPendingMarker and \
	  		len(self.fRegionMarkers) == 1 and \
	  		len(self.fPeakMarkers) > 0:
			# Make sure a fit panel is displayed
			if not self.fFitPanel:
				self.fFitPanel = FitPanel()
				
			reportStr = ""
			i = 0
			
			spec = self.fCurrentSpec
			fitter = ROOT.GSFitter(spec.E2Ch(self.fRegionMarkers[0].p1),
			                       spec.E2Ch(self.fRegionMarkers[0].p2))
				                       
			for marker in self.fBgMarkers:
				fitter.AddBgRegion(spec.E2Ch(marker.p1), spec.E2Ch(marker.p2))
			
			for marker in self.fPeakMarkers:
				fitter.AddPeak(spec.E2Ch(marker.p1))
				
			bgFunc = None
			if len(self.fBgMarkers) > 0:
				bgFunc = fitter.FitBackground(spec.fHist)
				
			# Fit left tails
			fitter.SetLeftTails(self.fFitPanel.GetLeftTails())
			fitter.SetRightTails(self.fFitPanel.GetRightTails())
			
			func = fitter.Fit(spec.fHist, bgFunc)
							
			# FIXME: why is this needed? Possibly related to some
			# subtle issue with PyROOT memory management
			# Todo: At least a clean explaination, possibly a better
			#   solution...
			self.fCurrentFit = Fit(ROOT.TF1(func), ROOT.TF1(bgFunc), spec.fCal)
			self.fCurrentFit.Realize(self.fViewport)
			                   
			self.fFitPanel.SetText(reportStr)	
				
			for marker in self.fPeakMarkers:
				marker.Delete(self.fViewport)

class SpectrumModule:
	def __init__(self):
		hdtv.cmdline.AddCommand("spectrum", self.LoadSpectra, minargs=1, fileargs=True)
		hdtv.cmdline.AddCommand("spectrum get", self.LoadSpectra, minargs=1, fileargs=True)
		hdtv.cmdline.AddCommand("spectrum list", self.ListSpectra, nargs=0)
		hdtv.cmdline.AddCommand("spectrum delete", self.DeleteSpectra, minargs=1)
		hdtv.cmdline.AddCommand("spectrum activate", self.ActivateSpectrum, nargs=1)
		hdtv.cmdline.AddCommand("spectrum show", self.ShowSpectra, minargs=1)
			
		hdtv.cmdline.AddCommand("cd", self.Cd, maxargs=1, dirargs=True)
		
		hdtv.cmdline.AddCommand("calibration position read", self.ReadCal, nargs=1, fileargs=True)
		hdtv.cmdline.AddCommand("calibration position enter", self.EnterCal, nargs=4)
		hdtv.cmdline.AddCommand("calibration position set", self.SetCal, maxargs=4)
		
		self.fMainWindow = SpecWindow()
		self.fView = self.fMainWindow.AddView("hdtv")
		self.fMainWindow.ShowView(0)
		
		self.fSpectra = dict()
		self.fActiveID = None
		
	def ReadCal(self, args):
		try:
			f = open(args[0])
		except IOError, msg:
			print msg
			return False
			
		try:
			calpoly = []
			for line in f:
				l = line.strip()
				if l != "":
					calpoly.append(float(l))

		except ValueError:
			f.close()
			print "Malformed calibration parameter file."
			return False
		
		f.close()

		if len(calpoly) < 1 or len(calpoly) > 4:
			print "Too many or too few parameters in calibration file"
			return False
			
		return self._SetCal(calpoly)
		
	def _SetCal(self, calpoly):
		if self.fActiveID == None:
			print "Warning: No active spectrum, no action taken."
			return False
			
		self.fSpectra[self.fActiveID].SetCal(calpoly)
		
	def EnterCal(self, args):
		pass
		
	def SetCal(self, args):
		calpoly = []
		try:
			for arg in args:
				calpoly.append(float(arg))
		except ValueError:
			print "Usage: calibration position set <p0> <p1> <p2> <p3>"
			return False
			
		self._SetCal(calpoly)

	def LoadSpectra(self, args):
		nloaded = 0
		for arg in args:
			for fname in glob.glob(arg):
				if self.LoadSpectrum(fname):
					nloaded += 1
				
		if nloaded == 0:
			print "Warning: no spectra loaded."
		elif nloaded == 1:
			print "Loaded 1 spectrum"
		else:
			print "Loaded %d spectra" % nloaded
			
		if nloaded > 0:
			self.fMainWindow.fViewport.Update(True)

	def LoadSpectrum(self, fname):
		sid = 0
		while sid in self.fSpectra.keys():
			sid += 1
		
		spec = Spectrum(fname, sid+2)
		if spec.fZombie:
			return False
		
		self.fSpectra[sid] = spec
		self.fActiveID = sid
		self.fMainWindow.fCurrentSpec = self.fSpectra[sid]
		spec.Realize(self.fMainWindow.fViewport, False)

		return True
		
	def ListSpectra(self, args=None):
		for (sid, spec) in self.fSpectra.iteritems():
			if sid == self.fActiveID:
				stat = "A"
			else:
				stat = " "
			if spec.IsVisible():
				stat += "V"
			else:
				stat += " "
			print "%d %s %s" % (sid, stat, spec.fFilename)
			
	def DeleteSpectrum(self, sid):
		self.fSpectra[sid].Delete(False)
		del self.fSpectra[sid]
		
	def DeleteSpectra(self, args):
		ids = hdtv.cmdhelper.ParseRange(args)
		if ids == "NONE":
			return
		elif ids == "ALL":
			for spec in self.fSpectra.itervalues():
				self.DeleteSpectrum(spec)
		else:
			for sid in ids:
				try:
					self.DeleteSpectrum(sid)
				except KeyError:
					print "Warning: ID %d not found" % sid
					
		self.fMainWindow.fViewport.Update(True)
		
	def ActivateSpectrum(self, args):
		try:
			sid = int(args[0])
		except ValueError:
			print "Usage: spectrum activate <id>"
			return
			
		if sid in self.fSpectra:
			self.fActiveID = sid
			self.fMainWindow.fCurrentSpec = self.fSpectra[sid]
		else:
			print "Error: No such ID"
		
	def ShowSpectra(self, args):
		ids = hdtv.cmdhelper.ParseRange(args)
		
		# Note that we may call Delete() on an already deleted
		# spectrum, or Realize() on an already visible spectrum,
		# with no ill effects.
		if ids == "NONE":
			for spec in self.fSpectra.itervalues():
				spec.Delete(False)
		elif ids == "ALL":
			for spec in self.fSpectra.itervalues():
				spec.Realize(self.fMainWindow.fViewport, False)
		else:
			for (sid, spec) in self.fSpectra.iteritems():
				if sid in ids and not spec.IsVisible():
					spec.Realize(self.fMainWindow.fViewport, False)
				elif not sid in ids and spec.IsVisible():
					spec.Delete(False)
					
		self.fMainWindow.fViewport.Update(True)
						
	def Cd(self, args):
		if len(args) == 0:
			print os.getcwdu()
		else:
			try:
				os.chdir(os.path.expanduser(args[0]))
			except OSError, msg:
				print msg

module = SpectrumModule()
print "Loaded plugin spectrum (commands for 1-d histograms)"
