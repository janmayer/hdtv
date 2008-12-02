import ROOT
import dlmgr
import os
from color import *
from specreader import SpecReader, SpecReaderError
from fit import Fit

dlmgr.LoadLibrary("display")

class Spectrum:
	"""
	Spectrum object
	
	This class is hdtvs wrapper around a ROOT histogram. It adds a calibration,
	plus some internal management for drawing the histogram	to the hdtv spectrum
	viewer.

	Optionally, the class method ReadSpectrum can be used to read a spectrum
	from a file, using the SpecReader class. A calibration can be
	defined by supplying a sequence with max. 4 entries, that form the factors
	of the calibration polynom. Moreover a color can be defined, which then
	will be used when the spectrum is displayed. 
	"""
	def __init__(self, hist, cal=None, color=None):
		self.fCal = cal
		self.fHist = hist
		self.fFitlist = []
		self.fSid = None
		self.fViewport = None
		self.fColor = color
		if hist:
			self.fZombie = False
		else:
			self.fZombie = True

	@classmethod
	def FromFile(cls, fname, fmt=None, cal=None, color=None):
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
		if self.fZombie:
			return False
	
		try:
			SpecReader().WriteSpectrum(self.fHist, fname, fmt)
		except SpecReaderError, msg:
			print "Error: Failed to write spectrum: %s (file: %s)" % (msg, fname)
			return False
			
		return True

	def SetColor(self, color):
		"""
		set color
		"""
		if color:
			self.fColor = color
		# update the display if needed
		self.Update(True)
		
	def SetCal(self, cal):
		"""
		set calibration

		The Parameter cal is a sequence with not more than 4 entries.
		The calibration polynom is of the form:
		f(x) = cal[0] + cal[1]*x + cal[2]*x^2 + cal[3]*x^3
		"""
		if cal:
			if len(cal) >4:
				print "Error: degree of calibration polynom is to big (>=4)"
			while len(cal) <4: 
				# fill the sequence with trivial entries
				cal.append(0.0)
			# create the calibration object
			self.fCal=ROOT.GSCalibration(cal[0], cal[1], cal[2], cal[3])
		else:
			self.fCal = None
		# update the display if needed
		self.Update(True)

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

	def AddFit(self, region=None, peaklist=None, 
			   bglist=None, ltail=0, rtail=0, update=True):
		"""
		Add a new fit to the list of fits belonging to this spectrum
		"""
		fit = Fit(self, region, peaklist, bglist, ltail, rtail) 
		self.fFitlist.append(fit)
		if self.fViewport:
			# update the display if this view is currently active
			fit.Realize(self.fViewport, update)
		return fit

	def DelFit(self, fid, update=True):
		""" 
		Delete Fit from Fitlist
		"""
		if fid>=0 and fid < len(self.fFitlist):
			fit = self.fFitlist.pop(fid)
			if self.fViewport:
				fit.Delete(update)

	def Realize(self, viewport, update=True):
		"""
		Draw this spectrum to the window
		"""
		# save the viewport
		self.fViewport = viewport
		# show spectrum
		if self.fSid == None and self.fHist != None:
			if self.fColor==None:
				# set to default color
				self.fColor = kSpecDef
			self.fSid = viewport.AddSpec(self.fHist,self.fColor, False)
			# add calibration
			if self.fCal:
				viewport.GetDisplaySpec(self.fSid).SetCal(self.fCal)
		# show fits
		for fit in self.fFitlist:
			fit.Realize(viewport, False)
		# finally update the viewport
		if update:
			viewport.Update(True)

	def Delete(self, update=True):
		"""
		Delete this spectrum from the window.
		"""
		if self.fViewport:
			# delete this spectrum from viewport
			if self.fSid!=None:
				self.fViewport.DeleteSpec(self.fSid, False)
				self.fSid = None
			# delete all fits
			for fit in self.fFitlist:
				fit.Delete(False)
			# update the viewport
			if update:
				self.fViewport.Update(True)
			# finally remove the viewport from this object
			self.fViewport = None

	def Update(self, update=True):
		"""
		Update screen
		"""
		if self.fViewport:
			# delete old spectrum
			if self.fSid!=None:
				self.fViewport.DeleteSpec(self.fSid, False)
			# if not color is set, use the default
			if self.fColor==None:
				self.fColor = kSpecDef
			# create new spectrum
			self.fSid = self.fViewport.AddSpec(self.fHist,self.fColor, False)
			# add calibration
			if self.fCal:
				self.fViewport.GetDisplaySpec(self.fSid).SetCal(self.fCal)
			# update all fits
			for fit in self.fFitlist:
				fit.Update(False)
			# finally update the viewport
			if update:
				self.fViewport.Update(True)

