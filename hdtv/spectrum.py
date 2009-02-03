import ROOT
import os
import hdtv.dlmgr
from hdtv.color import *
from hdtv.drawable import Drawable
from hdtv.specreader import SpecReader, SpecReaderError

hdtv.dlmgr.LoadLibrary("display")

class Spectrum(Drawable):
	"""
	Spectrum object
	
	This class is hdtvs wrapper around a ROOT histogram. It adds a calibration,
	plus some internal management for drawing the histogram	to the hdtv spectrum
	viewer.

	Optionally, the class method FromFile can be used to read a spectrum
	from a file, using the SpecReader class. A calibration can be
	defined by supplying a sequence with max. 4 entries, that form the factors
	of the calibration polynom. Moreover a color can be defined, which then
	will be used when the spectrum is displayed. 
	"""
	def __init__(self, hist, cal=None, color=None):
		Drawable.__init__(self, color)
		self.fCal = cal
		self.fHist = hist
		if hist:
			self.fZombie = False
		else:
			self.fZombie = True


	def __str__(self):
		if self.fHist:
			return self.fHist.GetName()


	def Draw(self, viewport):
		"""
		Draw this spectrum to the viewport
		"""
		# Unlike the DisplaySpec object of the underlying implementation,
		# Spectrum() objects can only be drawn on a single viewport
		if self.fViewport != None:
			raise RuntimeError, "Spectrum can only be drawn on a single viewport"
		self.fViewport = viewport
		# Lock updates
		self.fViewport.LockUpdate()
		# Show spectrum
		if self.fDisplayObj == None and self.fHist != None:
			if self.fColor==None:
				# set to default color
				self.fColor = kSpecDef
			self.fDisplayObj = ROOT.HDTV.Display.DisplaySpec(self.fHist, self.fColor)
			self.fDisplayObj.Draw(self.fViewport)
			# add calibration
			if self.fCal:
				self.fDisplayObj.SetCal(self.fCal)
		# finally update the viewport
		self.fViewport.UnlockUpdate()

	@classmethod
	def FromFile(cls, fname, fmt=None, cal=None, color=None):
		"""
		Read a spectrum from file
		"""
		# check if file exists
		try:
			os.path.exists(fname)
		except OSError:
			print "Error: File %s not found" % fname
			return
		# call to SpecReader to get the hist
		try:
			hist = SpecReader().GetSpectrum(fname, fmt)
		except SpecReaderError, msg:
			print "Error: Failed to load spectrum: %s (file: %s)" % (msg, fname)
			return
		spec = cls(hist)
		# set calibration 
		if cal:
			spec.SetCal(cal)
		# set color
		if color:
			spec.SetColor(color)
		spec.fZombie = False
		return spec
		

	def WriteSpectrum(self, fname, fmt):
		"""
		Write the spectrum to file
		"""
		if self.fZombie:
			return False
		try:
			SpecReader().WriteSpectrum(self.fHist, fname, fmt)
		except SpecReaderError, msg:
			print "Error: Failed to write spectrum: %s (file: %s)" % (msg, fname)
			return False
		return True


	def ReadCal(self, fname):
		"""
		Read Calibration from file
		"""
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

		
	def CalFromPairs(self, pairs):
		"""
		Create a calibration from two pairs of channel and corresponding energy
		"""
	 	if len(pairs) != 2:
	 		print "Pairs length must presently be exactly 2"
	 		return False
	 	cal = hdtv.util.Linear.FromXYPairs(pairs[0], pairs[1])
		self.SetCal([cal.p0, cal.p1])

		
	def SetCal(self, cal):
		"""
		set calibration

		The Parameter cal is a sequence with not more than 4 entries.
		The calibration polynom is of the form:
		f(x) = cal[0] + cal[1]*x + cal[2]*x^2 + cal[3]*x^3
		"""
		# FIXME: limitation is obsolete
		if cal:
			if len(cal) >4:
				print "Error: degree of calibration polynom is to big (>=4)"
			while len(cal) <4: 
				# fill the sequence with trivial entries
				cal.append(0.0)
			# create the calibration object
			self.fCal=ROOT.HDTV.Calibration(cal[0], cal[1], cal[2], cal[3])
		else:
			self.fCal = None
		# update the display if needed
		if self.fDisplayObj != None:
			self.fDisplayObj.SetCal(self.fCal)
		
	def UnsetCal(self):
		"""
		delete calibration
		"""
		self.SetCal(cal=None)
		
	def E2Ch(self, e):
		"""
		calculate channel values to energies
		"""
		if self.fCal:
			return self.fCal.E2Ch(e)
		else:
			return e
			
	def Ch2E(self, ch):
		"""
		calculate energies to channels
		"""
		if self.fCal:
			return self.fCal.Ch2E(ch)
		else:
			return ch

	def ToTop(self):
		"""
		"""
		if self.fDisplayObj:
			self.fDisplayObj.ToTop()


	def Update(self, update=True):
		"""
		DEPRECATED
		"""
		print "Called deprecated function Spectrum.Update()"	

	def Realize(self, viewport, update=True):
		"""
		DEPRECATED
		"""
		print "WARNING: Deprecated function Spectrum.Realize() called."
		self.Draw(viewport)
