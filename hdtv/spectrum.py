import ROOT
import os
import gspec
import color as c
from fit import Fit
from specreader import SpecReader


class Spectrum:
	"""
	Spectrum object

	A spectrum is read from a file by using SpecReader. A calibration can be
	defined by supplying a sequence with max. 4 entries, that form the factors
	of the calibration polynom. Moreover a color can be defined, which then
	will be used when the spectrum is displayed. 
	"""
	def __init__(self, histfile, cal=None, color=None):
		self.fCal = None
		self.fHist = None
		self.fColor = c.kSpecDef
		self.fFitlist = []
		self.fSid = None
		self.fViewport = None

		# check if file exists
		try:
			os.path.exists(histfile)
		except OSError:
			print "Error: File %s not found" % histfile
			return
		# call to SpecReader to get the hist
		self.fHist = SpecReader().Get(histfile, histfile, "hist")
		if not self.fHist:
			print "Error: Invalid spectrum format (file: %s)" %histfile
			return
		# set calibration 
		if cal:
			self.SetCal(cal)
		# set color
		if color:
			self.SetColor(color)

	def SetColor(self, color):
		"""
		set color
		"""
		if color:
			self.fColor = color
		# update the display if needed
		if self.fViewport:
			self.Update()
		
	def SetCal(self, cal):
		"""
		set calibration

		The Parameter cal is a sequence with not more than 4 entries.
		The calibration polynom is of the form:
		f(x) = cal[0] + cal[1]*x + cal[2]*x^2 + cal[3]*x^3
		"""
		if len(cal) >4:
			print "Error: degree of calibration polynom is to big (>=4)"
		while len(cal) <4: 
			# fill the sequence with trivial entries
			cal.append(0.0)
		# create the calibration object
		self.fCal=ROOT.GSCalibration(cal[0], cal[1], cal[2], cal[3])
		# update the display if needed
		if self.fViewport:
			self.Update()

	def UnsetCal(self):
		"""
		delete calibration
		"""
		# set calibration to None
		self.fCal=None
		# update the display if needed
		if self.fViewport:
			self.Update()
		
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

#	def AddFit(self, fit, update=True):
#		self.fFitlist.append(fit)
#		if self.fViewport:
#			fit.Realize(self.fViewport, update)

#	def DelFit(self, fid, update=True):
#		pass

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
				self.fColor = c.kSpecDef
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
			# finally update the viewport
			if update:
				self.fViewport.Update(True)
			# remove the viewport
			self.fViewport = None

	def Update(self, update=True):
		"""
		Redraw this spectrum
		"""
		viewport = self.fViewport
		self.Delete(False)
		self.Realize(viewport, True)
		
