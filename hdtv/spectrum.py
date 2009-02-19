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
	defined by supplying a sequence that form the factors of the calibration
	polynom. Moreover a color can be defined, which then will be used when the
	spectrum is displayed. 
	
	A spectrum object can contain a number of fits.
	"""
	def __init__(self, hist, cal=None, color=None):
		Drawable.__init__(self, color)
		self.fHist = hist
		self.fFits = list()
		self.fCal = cal
		
	def __setattr__(self, key, value):
		self.__dict__[key] = value

		if key == "fCal":
			if self.fViewport:
				self.fViewport.LockUpdate()
			for fit in self.fFits:
				fit.CalibrationChanged()
			if self.fViewport:
				self.fViewport.UnlockUpdate()

	def __str__(self):
		if self.fHist:
			return self.fHist.GetName()

	def Draw(self, viewport):
		"""
		Draw this spectrum to the viewport
		"""
		if self.fViewport:
			if self.fViewport == viewport:
				# this spectrum has already been drawn
				self.Show()
				return
			else:
				# Unlike the DisplaySpec object of the underlying implementation,
				# Spectrum() objects can only be drawn on a single viewport
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
		
	
	def Refresh(self):
		"""
		Refresh the spectrum, i.e. reload the data inside it
		"""
		# The generic spectrum class does not know about the origin of its
		# bin data and thus cannot reload anything.
		pass
		
	
	def SetHist(self, hist):
		self.fHist = hist
		if self.fDisplayObj:
			self.fDisplayObj.SetHist(self.fHist)
		

	def WriteSpectrum(self, fname, fmt):
		"""
		Write the spectrum to file
		"""
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

		The Parameter cal is a sequence with the coefficients of the
		calibration polynom:
		f(x) = cal[0] + cal[1]*x + cal[2]*x^2 + cal[3]*x^3 + ...
		"""
		if cal:
			calarray = ROOT.TArrayD(len(cal))
			for (i,c) in zip(range(0,len(cal)),cal):
				calarray[i] = c
			# create the calibration object
			self.fCal = ROOT.HDTV.Calibration(calarray)
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
		

	def GetPeakList(self):
		"Returns a list of all fitted peaks in this spectrum"
		peaks = []
		for fit in self.fFits:
			peaks += fit.resultPeaks
		return peaks
		
	
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
		Move the spectrum to the top of its draw stack
		"""
		if self.fDisplayObj:
			self.fDisplayObj.ToTop()
			

	def ToBottom(self):
		"""
		Move the spectrum to the top of its draw stack
		"""
		if self.fDisplayObj:
			self.fDisplayObj.ToBottom()


		
class FileSpectrum(Spectrum):
	"""
	File spectrum object
	
	A spectrum that comes from a file in any of the formats supported by hdtv.
	"""
	def __init__(self, fname, fmt=None, cal=None, color=None):
		"""
		Read a spectrum from file
		"""
		# check if file exists
		try:
			os.path.exists(fname)
		except OSError:
			print "Error: File %s not found" % fname
			raise
		# call to SpecReader to get the hist
		try:
			hist = SpecReader().GetSpectrum(fname, fmt)
		except SpecReaderError, msg:
			print "Error: Failed to load spectrum: %s (file: %s)" % (msg, fname)
			raise
		self.fFilename = fname
		self.fFmt = fmt
		Spectrum.__init__(self, hist)
		# set calibration 
		if cal:
			self.SetCal(cal)
		# set color
		if color:
			self.SetColor(color)
		
	
	def Refresh(self):
		"""
		Reload the spectrum from disk
		"""
		try:
			os.path.exists(self.fFilename)
		except OSError:
			print "Warning: File %s not found, keeping previous data" % self.fFilename
			return
		# call to SpecReader to get the hist
		try:
			hist = SpecReader().GetSpectrum(self.fFilename, self.fFmt)
		except SpecReaderError, msg:
			print "Warning: Failed to load spectrum: %s (file: %s), keeping previous data" \
			      % (msg, self.fFilename)
			return
		self.SetHist(hist)
		
