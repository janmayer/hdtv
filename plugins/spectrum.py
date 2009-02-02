import hdtv.cmdline
import hdtv.window
import hdtv.cmdhelper
import hdtv.spectrum
import hdtv.fitgui
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
			
class SpecWindow(hdtv.window.Window, hdtv.fitgui.FitGUI):
	def __init__(self):
		hdtv.window.Window.__init__(self)
		hdtv.fitgui.FitGUI.__init__(self, self, show_panel=True)
		
		self.fCurrentSpec = None
		
		self.fSpectra = dict()
		self.fActiveID = None
		
		self.SetTitle("No spectrum")
		
	def SetCurrentSpec(self, spec):
		self.fCurrentSpec = spec
		self.fFitter.spec = spec
		
		if self.fCurrentSpec:
			self.SetTitle(self.fCurrentSpec.fHist.GetTitle())
		else:
			self.SetTitle("No spectrum")
		
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
		
		(r,g,b) = hdtv.util.HSV2RGB(hue*360., satur, value)
		return ROOT.TColor.GetColor(r,g,b)

	def LoadSpectra(self, args):
		"""
		Load multiple spectra
		"""
		# Avoid multiple updates
		self.fViewport.LockUpdate()
	
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
			
		# Update viewport if required
		self.fViewport.UnlockUpdate()

	def LoadSpectrum(self, fname, fmt=None):
		spec = Spectrum.FromFile(fname, fmt)
		if spec == None:
			return None
		else:
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
		spec.Draw(self.fViewport)
		
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
		spec.ToTop()
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
		self.fSpectra[sid].Delete()
		del self.fSpectra[sid]
		if self.fActiveID == sid:
			self.fActiveID = None
			self.SetCurrentSpec(None)
			
	def DeleteAllSpectra(self):
		self.fViewport.LockUpdate()
		for sid in self.fSpectra.keys():
			self.DeleteSpectrum(sid)
		self.fViewport.UnlockUpdate()
		
	def DeleteSpectra(self, ids):
		self.fViewport.LockUpdate()
		for sid in ids:
			try:
				self.DeleteSpectrum(sid)
			except KeyError:
				print "Warning: ID %d not found" % sid
					
		self.fViewport.UnlockUpdate()
			
	# Note that we may call Hide() on an already hidden
	# spectrum, or Show() on an already visible spectrum,
	# with no ill effects.
	def ShowNone(self):
		self.fViewport.LockUpdate()
		for spec in self.fSpectra.itervalues():
			spec.Hide()
		self.fViewport.UnlockUpdate()
	
	def ShowAll(self):
		self.fViewport.LockUpdate()
		for spec in self.fSpectra.itervalues():
			spec.Show()
		self.fViewport.UnlockUpdate()
	
	def Show(self, ids):
		self.fViewport.LockUpdate()
		for (sid, spec) in self.fSpectra.iteritems():
			if sid in ids and not spec.IsVisible():
				spec.Show()
			elif not sid in ids and spec.IsVisible():
				spec.Hide()
		self.fViewport.UnlockUpdate()
		
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
	

class PluginSpectrum:
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
		
		hdtv.cmdline.AddCommand("fit param background degree", self.FitParamBgDeg, nargs=1)
		hdtv.cmdline.AddCommand("fit param status", self.FitParamStatus, nargs=0)
		hdtv.cmdline.AddCommand("fit param reset", self.FitParamReset, nargs=0)
		
		for name in hdtv.fit.gPeakModels.iterkeys():
			hdtv.cmdline.AddCommand("fit function peak activate %s" % name,
			                        self.MakePeakModelCmd(name), nargs=0)
		
		self.fMainWindow = SpecWindow()
		self.fView = self.fMainWindow.AddView("hdtv")
		self.fMainWindow.ShowView(0)
		self.FitSetPeakModel("theuerkauf")
		
		hdtv.cmdline.RegisterInteractive("gSpectra", self.fMainWindow)
		
	def MakePeakModelCmd(self, name):
		return lambda args: self.FitSetPeakModel(name)
	
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
		
	def FitParamBgDeg(self, args):
		try:
			bgdeg = int(args[0])
		except ValueError:
			print "Usage: fit parameter background degree <deg>"
			return False
			
		self.fMainWindow.fFitter.bgdeg = bgdeg

		# Update options
		self.fMainWindow.FitUpdateOptions()
		self.fMainWindow.FitUpdateData()
		
	def FitParamStatus(self, args):
		self.fMainWindow.fFitter.PrintParamStatus()
		
	def FitParamPeak(self, parname, args):
		try:
			self.fMainWindow.fFitter.SetParameter(parname, " ".join(args))
		except ValueError:
			print "Usage: fit parameter <parname> [free|ifree|hold|disable|<number>]"
			return False
		except RuntimeError, e:
			print e
			return False
			
		# Update options
		self.fMainWindow.FitUpdateOptions()
		self.fMainWindow.FitUpdateData()
		
	def FitParamReset(self, args):
		self.fMainWindow.ResetFitParameters()
			
	def MakeParamCmd(self, param):
		return lambda args: self.FitParamPeak(param, args)
			
	def FitSetPeakModel(self, name):
		# Unregister old parameters
		for param in self.fMainWindow.fFitter.GetParameters():
			hdtv.cmdline.RemoveCommand("fit param %s" % param)
		
		# Set new peak model
		self.fMainWindow.fFitter.SetPeakModel(name.lower())
		
		# Register new parameters
		for param in self.fMainWindow.fFitter.GetParameters():
			hdtv.cmdline.AddCommand("fit param %s" % param, 
			                        self.MakeParamCmd(param),
			                        minargs=1)
			                        
		# Update options
		self.fMainWindow.FitUpdateOptions()
		self.fMainWindow.FitUpdateData()

plugin = PluginSpectrum()
print "Loaded plugin spectrum (commands for 1-d histograms)"
