import hdtv.cmdline
import hdtv.window
import hdtv.cmdhelper
import hdtv.spectrum
import hdtv.fitpanel
import hdtv.marker
import hdtv.peak
import hdtv.util
import hdtv.fit
from hdtv.color import *
import os
import glob
import math
import ROOT

# Don't add created spectra to the ROOT directory
ROOT.TH1.AddDirectory(ROOT.kFALSE)

class Spectrum(hdtv.spectrum.Spectrum):
	def __init__(self, fname, color):
		self.fFilename = fname
		hdtv.spectrum.Spectrum.__init__(self, fname, color=color)
		
	def IsVisible(self):
		return self.fSid != None
		
class SpecWindow(hdtv.window.Window):
	def __init__(self):
		hdtv.window.Window.__init__(self)
		
		self.fPeakMarkers = []
		self.fRegionMarkers = []
		self.fBgMarkers = []
		self.fCurrentSpec = None
		
		self.fDefaultCal = ROOT.GSCalibration(0.0, 0.5)
		self.fFitter = hdtv.fit.Fit()
		
		# self.SetTitle("No spectrum - hdtv")
		
		# Initialize and show the fit panel
		self.fFitPanel = None
		self.EnsureFitPanel()
		
	def SetCurrentSpec(self, spec):
		self.fCurrentSpec = spec
		self.fFitter.spec = spec
		
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
	  	elif key == ROOT.kKey_B:
	  		self.FitBackground()
	  	elif key == ROOT.kKey_F:
	  		self.Fit()
	  	elif key == ROOT.kKey_I:
	  		self.Integrate()
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
  		
		self.fFitter.Reset()
		self.fFitter.Delete(False)
		if self.fFitPanel:
			self.fFitPanel.SetText(" ")
						
		self.fViewport.Update(True)
		
	def Integrate(self):
		if not self.fPendingMarker and len(self.fRegionMarkers) == 1:
			# Integrate histogram in requested region
			spec = self.fFitter.spec
			ch_1 = spec.E2Ch(self.fRegionMarkers[0].p1)
			ch_2 = spec.E2Ch(self.fRegionMarkers[0].p2)
				
			fitter = ROOT.GSFitter(ch_1, ch_2)
			total_int = fitter.Integrate(spec.fHist)
			total_err = math.sqrt(total_int)
			                       
			# Integrate background function in requested region if it
			# is available
			if self.fFitter and self.fFitter.bgfunc:
				bgfunc = self.fFitter.bgfunc
				bg_int = bgfunc.Integral(math.ceil(min(ch_1, ch_2) - 0.5) - 0.5,
				                         math.ceil(max(ch_1, ch_2) - 0.5) + 0.5)
				bg_err = math.sqrt(bg_int)
			else:
				bg_int = None

			# Output results
			if bg_int != None:
				sum_int = total_int - bg_int
				sum_err = math.sqrt(total_int + bg_int)

				text  = "Total:      %10.1f +- %7.1f\n" % (total_int, total_err)
				text += "Background: %10.1f +- %7.1f\n" % (bg_int, bg_err)
				text += "Sub:        %10.1f +- %7.1f\n" % (sum_int, sum_err)
			else:
				text = "Integral: %.1f +- %.1f\n" % (total_int, total_err)
			
			self.EnsureFitPanel()
			self.fFitPanel.SetText(text)
			
	def SyncFitter(self):
		self.fFitter.region = [self.fRegionMarkers[0].p1, self.fRegionMarkers[0].p2]
		self.fFitter.peaklist = map(lambda m: m.p1, self.fPeakMarkers)
		self.fFitter.leftTail = self.fFitPanel.GetLeftTails()
		self.fFitter.rightTail = self.fFitPanel.GetRightTails()
		
	def EnsureFitPanel(self):
		if not self.fFitPanel:
			self.fFitPanel = hdtv.fitpanel.FitPanel()
			self.fFitPanel.fFitHandler = self.Fit
			self.fFitPanel.fClearHandler = self.DeleteFit
		
	def FitBackground(self):
		self.fFitter.Delete()
		
		if not self.fPendingMarker and \
			len(self.fBgMarkers) > 0:
			
			# Make sure a fit panel is displayed
			self.EnsureFitPanel()
			
			self.fFitter.bglist = map(lambda m: [m.p1, m.p2], self.fBgMarkers)
			self.fFitter.DoBgFit()
			self.fFitter.Realize(self.fViewport)
			
			self.fFitPanel.SetText(str(self.fFitter))
		
	def Fit(self):
		self.fFitter.Delete()
	
	  	if not self.fPendingMarker and \
	  		len(self.fRegionMarkers) == 1 and \
	  		len(self.fPeakMarkers) > 0:

			# Make sure a fit panel is displayed
			self.EnsureFitPanel()
				
			# Do the fit
			self.SyncFitter()
			self.fFitter.DoPeakFit()
			self.fFitter.Realize(self.fViewport, False)
						                   
			self.fFitPanel.SetText(str(self.fFitter))
				
			for (marker, peak) in zip(self.fPeakMarkers, self.fFitter.resultPeaks):
				marker.p1 = peak.GetPos()
				marker.UpdatePos(self.fViewport, False)
				
			self.fViewport.Update(True)

class SpectrumModule:
	def __init__(self):
		hdtv.cmdline.AddCommand("spectrum", self.LoadSpectra, minargs=1, fileargs=True)
		hdtv.cmdline.AddCommand("spectrum get", self.LoadSpectra, minargs=1, fileargs=True)
		hdtv.cmdline.AddCommand("spectrum list", self.ListSpectra, nargs=0)
		hdtv.cmdline.AddCommand("spectrum delete", self.DeleteSpectra, minargs=1)
		hdtv.cmdline.AddCommand("spectrum activate", self.ActivateSpectrum, nargs=1)
		hdtv.cmdline.AddCommand("spectrum show", self.ShowSpectra, minargs=1)
			
		hdtv.cmdline.AddCommand("dir", self.Cd, maxargs=1, dirargs=True)
		
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
		# E = E(ch)
		try:
			p0 = [float(args[0]), float(args[1])]
			p1 = [float(args[2]), float(args[3])]
		except ValueError:
			print "Usage: calibration position enter <ch0> <E0> <ch1> <E1>"
			return False
			
		cal = hdtv.util.Linear.FromXYPairs(p0, p1)
		self._SetCal([cal.p0, cal.p1])
		
	def SetCal(self, args):
		try:
			for arg in args:
				calpoly = map(lambda s: float(s), args)
		except ValueError:
			print "Usage: calibration position set <p0> <p1> <p2> <p3>"
			return False
			
		self._SetCal(calpoly)
		
	def HSV2RGB(self, hue, satur, value):
		# This is a copy of the ROOT function TColor::HSV2RGB,
		# which we cannot use because it uses references to return
		# several values.
		# TODO: Find a proper way to deal with C++ references from
		# PyROOT, then replace this function by a call to
		# TColor::HSV2RGB.
		
		
		# Static method to compute RGB from HSV.
		# - The hue value runs from 0 to 360.
		# - The saturation is the degree of strength or purity and is from 0 to 1.
		#   Purity is how much white is added to the color, so S=1 makes the purest
		#   color (no white).
		# - Brightness value also ranges from 0 to 1, where 0 is the black.
		# The returned r,g,b triplet is between [0,1].

		if satur==0.:
			# Achromatic (grey)
			r = g = b = value
			return (r, g, b)

		hue /= 60.;   # sector 0 to 5
		i = int(math.floor(hue))
		f = hue-i;   # factorial part of hue
		p = value*(1-satur)
		q = value*(1-satur*f )
		t = value*(1-satur*(1-f))

		if i==0:
			r = value
			g = t
			b = p
		elif i==1:
			r = q
			g = value
			b = p
		elif i==2:
			r = p
			g = value
			b = t
		elif i==3:
			r = p
			g = q
			b = value
		elif i==4:
			r = t
			g = p
			b = value
		else:
			r = value
			g = p
			b = q

		return (r,g,b)
		
	def ColorForID(self, sid, satur, value):
		"""
		Returns the color corresponding to a certain spectrum ID. The idea is to maximize the
		hue difference between the spectra shown, without knowing beforehand how many spectra
		there will be and without being able to change the color afterwards (that would confuse
		the user). The saturation and value of the color can be set arbitrarily, for example
		to indicate which spectrum is currently active.
		"""
		# Special case
		if sid==0:
			hue = 0.0
		else:
			p = math.floor(math.log(sid) / math.log(2))
			q = sid - 2**p
			hue = 2**(-p-1) + q*2**(-p)
		
		(r,g,b) = self.HSV2RGB(hue*360., satur, value)
		return ROOT.TColor.GetColor(r,g,b)

	def LoadSpectra(self, args):
		nloaded = 0
		for arg in args:
			path = os.path.expanduser(arg)
			for fname in glob.glob(path):
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
		
		spec = Spectrum(fname, self.ColorForID(sid,1.,.5))
		if spec.fZombie:
			return False
		
		self.fSpectra[sid] = spec
		self._ActivateSpectrum(sid)
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
			for sid in self.fSpectra.keys():
				self.DeleteSpectrum(sid)
		else:
			for sid in ids:
				try:
					self.DeleteSpectrum(sid)
				except KeyError:
					print "Warning: ID %d not found" % sid
					
		self.fMainWindow.fViewport.Update(True)
		
	def _ActivateSpectrum(self, sid):
		if self.fActiveID != None:
			self.fSpectra[self.fActiveID].SetColor(self.ColorForID(self.fActiveID, 1., .5))
		
		self.fActiveID = sid
		spec = self.fSpectra[sid]
		spec.SetColor(self.ColorForID(sid, 1., 1.))
		self.fMainWindow.SetCurrentSpec(spec)

	def ActivateSpectrum(self, args):
		try:
			sid = int(args[0])
		except ValueError:
			print "Usage: spectrum activate <id>"
			return
			
		if sid in self.fSpectra:
			self._ActivateSpectrum(sid)
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
