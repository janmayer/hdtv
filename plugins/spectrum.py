import hdtv.cmdline
import hdtv.window
import hdtv.cmdhelper
import hdtv.spectrum
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
		
		self.fMainWindow = hdtv.window.Window()
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
print "Loaded module spectrum (commands for 1-d histograms)"
