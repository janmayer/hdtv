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
	def IsVisible(self):
		return self.fSid != None
		
	def ReadCal(self, fname):
		try:
			f = open(fname)
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
			
		return self.SetCal(calpoly)
		
	def CalFromPairs(self, pairs, **args):
	 	if len(pairs) != 2:
	 		print "Pairs length must presently be exactly 2"
	 		return False
	 		
	 	#c = []
	 	#e = []
	 	#for pair in pairs:
	 	#	if len(pair) != 2:
	 	#		raise RuntimeError, "Expected a channel/energy pair"
	 	#	c.append(pair[0])
	 	#	e.append(pair[1])
	 		
	 	cal = hdtv.util.Linear.FromXYPairs(pairs[0], pairs[1])
		self.SetCal([cal.p0, cal.p1])
		
class SpecWindow(hdtv.window.Window):
	def __init__(self):
		hdtv.window.Window.__init__(self)
		
		self.fPeakMarkers = []
		self.fRegionMarkers = []
		self.fBgMarkers = []
		self.fCurrentSpec = None
		
		self.fDefaultCal = ROOT.GSCalibration(0.0, 0.5)
		self.fFitter = hdtv.fit.Fit()
		
		self.fSpectra = dict()
		self.fActiveID = None
		
		# self.SetTitle("No spectrum - hdtv")
		
		# Create fit panel, but do not show it yet
		self.fFitPanel = hdtv.fitpanel.FitPanel()
		self.fFitPanel.fFitHandler = self.Fit
		self.fFitPanel.fClearHandler = self.DeleteFit
		
		# Register hotkeys
		self.fKeys.AddKey(ROOT.kKey_b, self.PutBackgroundMarker)
		self.fKeys.AddKey(ROOT.kKey_r, self.PutRegionMarker)
		self.fKeys.AddKey(ROOT.kKey_p, self.PutPeakMarker)
	  	self.fKeys.AddKey([ROOT.kKey_Minus, ROOT.kKey_F], self.DeleteFit)
	  	self.fKeys.AddKey(ROOT.kKey_B, self.FitBackground)
	  	self.fKeys.AddKey(ROOT.kKey_F, self.Fit)
	  	self.fKeys.AddKey(ROOT.kKey_I, self.Integrate)
		
	def SetCurrentSpec(self, spec):
		self.fCurrentSpec = spec
		self.fFitter.spec = spec
		
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
		self.fFitPanel.Show()
			
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
		if type(args) == str or type(args) == unicode:
			args = [args]
	
		nloaded = 0
		for arg in args:
			# PUT FMT IF AVAILABLE
			sparg = arg.rsplit("'", 1)
			if len(sparg) == 1 or not sparg[1]:
				(pat, fmt) = (sparg[0], None)
			else:
				(pat, fmt) = sparg
			
			path = os.path.expanduser(pat)
			for fname in glob.glob(path):
				if self.LoadSpectrum(fname, fmt) != None:
					nloaded += 1
				
		if nloaded == 0:
			print "Warning: no spectra loaded."
		elif nloaded == 1:
			print "Loaded 1 spectrum"
		else:
			print "Loaded %d spectra" % nloaded
			
		if nloaded > 0:
			self.fViewport.Update(True)

	def LoadSpectrum(self, fname, fmt=None):
		spec = Spectrum.FromFile(fname, fmt)
		return self.AddSpectrum(spec)
		
	def AddSpectrum(self, spec):
		"""
		Adds a spectrum object to the window
		"""
		# No admission for zombies
		if spec.fZombie:
			return None
		
		# Find a free spectrum ID
		sid = 0
		while sid in self.fSpectra.keys():
			sid += 1

		# Set correct color
		spec.SetColor(self.ColorForID(sid,1.,.5))
		
		# Display it
		self.fSpectra[sid] = spec
		self.ActivateSpectrum(sid)
		spec.Realize(self.fViewport, False)
		
		return sid
		
	def AddHistogram(self, hist):
		"""
		Adds a ROOT histogram to the window
		"""
		return self.AddSpectrum(Spectrum(hist))
		
	def ActivateSpectrum(self, sid):
		if not sid in self.fSpectra:
			print "Error: No such ID"
			return
	
		if self.fActiveID != None:
			self.fSpectra[self.fActiveID].SetColor(self.ColorForID(self.fActiveID, 1., .5))
		
		self.fActiveID = sid
		spec = self.fSpectra[sid]
		spec.SetColor(self.ColorForID(sid, 1., 1.))
		self.SetCurrentSpec(spec)
		
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
			print "%d %s %s" % (sid, stat, spec.fHist.GetName())
			
	def DeleteSpectrum(self, sid):
		self.fSpectra[sid].Delete(False)
		del self.fSpectra[sid]
		if self.fActiveID == sid:
			self.fActiveID = None
			self.SetCurrentSpec(None)
			
	def DeleteAllSpectra(self):
		for sid in self.fSpectra.keys():
			self.DeleteSpectrum(sid)
		self.fViewport.Update(True)
		
	def DeleteSpectra(self, ids):
		for sid in ids:
			try:
				self.DeleteSpectrum(sid)
			except KeyError:
				print "Warning: ID %d not found" % sid
					
		self.fMainWindow.fViewport.Update(True)
			
	# Note that we may call Delete() on an already deleted
	# spectrum, or Realize() on an already visible spectrum,
	# with no ill effects.
	def ShowNone(self):
		for spec in self.fSpectra.itervalues():
				spec.Delete(False)
		self.fViewport.Update(True)
	
	def ShowAll(self):
		for spec in self.fSpectra.itervalues():
				spec.Realize(self.fViewport, False)
		self.fViewport.Update(True)
	
	def Show(self, ids):
		for (sid, spec) in self.fSpectra.iteritems():
			if sid in ids and not spec.IsVisible():
				spec.Realize(self.fViewport, False)
			elif not sid in ids and spec.IsVisible():
				spec.Delete(False)
		self.fViewport.Update(True)
		
	# Helper functions to process the active spectrum
	def SetCal(self, calpoly):
		if self.fActiveID == None:
			print "Warning: No active spectrum, no action taken."
			return False
			
		self.fSpectra[self.fActiveID].SetCal(calpoly)
		
	def ReadCal(self, fname):
		if self.fActiveID == None:
			print "Warning: No active spectrum, no action taken."
			return False
			
		self.fSpectra[self.fActiveID].ReadCal(fname)
		
	def CalFromPairs(self, pairs, **args):
		if self.fActiveID == None:
			print "Warning: No active spectrum, no action taken."
			return False
			
		self.fSpectra[self.fActiveID].CalFromPairs(pairs, **args)
		
	def WriteSpectrum(self, fname, fmt):
		if self.fActiveID == None:
			print "Warning: No active spectrum, no action taken."
			return False
			
		self.fSpectra[self.fActiveID].WriteSpectrum(fname, fmt)
		
	def __getitem__(self, x):
		return self.fSpectra[x]
	

class SpectrumModule:
	def __init__(self):
		hdtv.cmdline.command_tree.SetDefaultLevel(1)
		hdtv.cmdline.AddCommand("spectrum get", self.SpectrumGet, level=0, minargs=1, fileargs=True)
		hdtv.cmdline.AddCommand("spectrum list", self.SpectrumList, nargs=0)
		hdtv.cmdline.AddCommand("spectrum delete", self.SpectrumDelete, minargs=1)
		hdtv.cmdline.AddCommand("spectrum activate", self.SpectrumActivate, nargs=1)
		hdtv.cmdline.AddCommand("spectrum show", self.SpectrumShow, minargs=1)
		hdtv.cmdline.AddCommand("spectrum write", self.SpectrumWrite, minargs=1, maxargs=2)
			
		hdtv.cmdline.AddCommand("cd", self.Cd, level=2, maxargs=1, dirargs=True)
		
		hdtv.cmdline.AddCommand("calibration position read", self.CalPosRead, nargs=1, fileargs=True)
		hdtv.cmdline.AddCommand("calibration position enter", self.CalPosEnter, nargs=4)
		hdtv.cmdline.AddCommand("calibration position set", self.CalPosSet, maxargs=4)
		
		self.fMainWindow = SpecWindow()
		self.fView = self.fMainWindow.AddView("hdtv")
		self.fMainWindow.ShowView(0)
		
		hdtv.cmdline.RegisterInteractive("gSpectra", self.fMainWindow)
		
	def SpectrumGet(self, args):
		self.fMainWindow.LoadSpectra(args)
		
	def SpectrumList(self, args):
		self.fMainWindow.ListSpectra()
		
	def SpectrumDelete(self, args):
		ids = hdtv.cmdhelper.ParseRange(args)
		if ids == "NONE":
			return
		elif ids == "ALL":
			self.fMainWindow.DeleteAllSpectra()
		else:
			self.fMainWindow.DeleteSpectra(ids)
		
	def SpectrumActivate(self, args):
		try:
			sid = int(args[0])
		except ValueError:
			print "Usage: spectrum activate <id>"
			return

		self.fMainWindow.ActivateSpectrum(sid)
		
	def SpectrumShow(self, args):
		ids = hdtv.cmdhelper.ParseRange(args)
		
		if ids == "NONE":
			self.fMainWindow.ShowNone()
		elif ids == "ALL":
			self.fMainWindow.ShowAll()
		else:
			self.fMainWindow.Show(ids)
			
	def SpectrumWrite(self, args):
		try:
			(fname, fmt) = args[0].rsplit('\'', 1)
	
			if len(args) == 1:
				self.fMainWindow.WriteSpectrum(fname, fmt)
			else:
				sid = int(args[1])
				try:				
					self.fMainWindow[sid].WriteSpectrum(fname, fmt)
				except KeyError:
					print "Error: ID %d not found" % sid
		
		except ValueError:
			print "Usage: spectrum write <filename>'<format> [index]"
		
		return	
			
	def Cd(self, args):
		if len(args) == 0:
			print os.getcwdu()
		else:
			try:
				os.chdir(os.path.expanduser(args[0]))
			except OSError, msg:
				print msg

	def CalPosRead(self, args):
		self.fMainWindow.ReadCal(args[0])
		
	def CalPosEnter(self, args):
		# E = E(ch)
		try:
			p0 = [float(args[0]), float(args[1])]
			p1 = [float(args[2]), float(args[3])]
		except ValueError:
			print "Usage: calibration position enter <ch0> <E0> <ch1> <E1>"
			return False
		self.fMainWindow.CalFromPairs([p0, p1])
	
	def CalPosSet(self, args):
		try:
			for arg in args:
				calpoly = map(lambda s: float(s), args)
		except ValueError:
			print "Usage: calibration position set <p0> <p1> <p2> <p3>"
			return False
			
		self.fMainWindow.SetCal(calpoly)

module = SpectrumModule()
print "Loaded plugin spectrum (commands for 1-d histograms)"
