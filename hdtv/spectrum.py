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
	def __init__(self, hist, color=None, cal=None):
		Drawable.__init__(self, color, cal)
		self.fHist = hist
		
	def __str__(self):
		if self.fHist:
			return self.fHist.GetName()

	def Draw(self, viewport):
		"""
		Draw this spectrum to the viewport
		"""
		if self.viewport:
			if self.viewport == viewport:
				# this spectrum has already been drawn
				self.Show()
				return
			else:
				# Unlike the DisplaySpec object of the underlying implementation,
				# Spectrum() objects can only be drawn on a single viewport
				raise RuntimeError, "Spectrum can only be drawn on a single viewport"
		self.viewport = viewport
		# Lock updates
		self.viewport.LockUpdate()
		# Show spectrum
		if self.displayObj == None and self.fHist != None:
			if self.color==None:
				# set to default color
				self.color = kSpecDef
			self.displayObj = ROOT.HDTV.Display.DisplaySpec(self.fHist, self.color)
			self.displayObj.Draw(self.viewport)
			# add calibration
			if self.cal:
				self.displayObj.SetCal(self.cal)
		# finally update the viewport
		self.viewport.UnlockUpdate()
		
	
	def Refresh(self):
		"""
		Refresh the spectrum, i.e. reload the data inside it
		"""
		# The generic spectrum class does not know about the origin of its
		# bin data and thus cannot reload anything.
		pass
		
	
	def SetHist(self, hist):
		self.fHist = hist
		if self.displayObj:
			self.displayObj.SetHist(self.fHist)
		

	def WriteSpectrum(self, fname, fmt):
		"""
		Write the spectrum to file
		"""
		fname = os.path.expanduser(fname)
		try:
			SpecReader().WriteSpectrum(self.fHist, fname, fmt)
		except SpecReaderError, msg:
			print "Error: Failed to write spectrum: %s (file: %s)" % (msg, fname)
			return False
		return True

		
# FIXME: does not belong here!
#	def GetPeakList(self):
#		"Returns a list of all fitted peaks in this spectrum"
#		peaks = []
#		for fit in self.fFits:
#			peaks += fit.resultPeaks
#		return peaks
		
# FIXME: does not belong here!
#	def E2Ch(self, e):
#		"""
#		calculate channel values to energies
#		"""
#		if self.cal:
#			return self.cal.E2Ch(e)
#		else:
#			return e
#			

#	def Ch2E(self, ch):
#		"""
#		calculate energies to channels
#		"""
#		if self.cal:
#			return self.cal.Ch2E(ch)
#		else:
#			return ch


	def ToTop(self):
		"""
		Move the spectrum to the top of its draw stack
		"""
		if self.displayObj:
			self.displayObj.ToTop()
			

	def ToBottom(self):
		"""
		Move the spectrum to the top of its draw stack
		"""
		if self.displayObj:
			self.displayObj.ToBottom()


		
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
		
