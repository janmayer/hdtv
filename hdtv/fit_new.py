import ROOT

from hdtv.color import *
from hdtv.drawable import Drawable
from hdtv.fitter import Fitter

hdtv.dlmgr.LoadLibrary("display")

class Fit(Drawable):
	"""
	Fit object
	
	This Fit object is the graphical representation of a fit in HDTV. 
	It contains the marker lists and the functions. The actual interface to
	the C++ fitting routines is the class Fitter.
	"""
	def __init__(self, spec, region=[], peaklist=[], bglist=[], color=None):
		Drawable.__init__(self, color)
		self.fRegionMarkers = region
		self.fPeakMarkers = peaklist
		self.fBgMarkers = bglist
		self.fspec = spec
		# creation of Fitter, should do the fit
		self.fFitter = Fitter(spec, region, peaklist, bglist)

	def __str__(self):
		 return "Fit peaks in region from %s to %s" %(self.region[0], self.region[1])

	def Draw(self, viewport):
		if self.fViewport:
			if self.fViewport == viewport:
				# this fit has already been drawn
				self.Show()
				return
			else:
				# Unlike the Display object of the underlying implementation,
				# python objects can only be drawn on a single viewport
				raise RuntimeError, "Spectrum can only be drawn on a single viewport"
		self.fViewport = viewport
		# Lock updates
		self.fViewport.LockUpdate()
			for marker in self.fRegionMarker:
				marker.Draw(viewport)
			for marker in self.fPeakMarkers:
				marker.Draw(viewport)
			for marker in self.fBgMarkers:
				marker.Draw(viewport)
		# FIXME: Get functions from fitter
		
		self.fViewport.UnlockUpdate()
		
	def Refresh(self):
		self.fViewport.LockUpdate()
		# FIXME: Redo the fit
		for marker in self.fRegionMarker:
			marker.Refresh()
		for marker in self.fPeakMarkers:
			marker.Refresh()
		for marker in self.fBgMarkers:
			marker.Refresh()
		# FIXME: functions
		self.fViewport.UnlockUpdate()

	def Show(self):
		pass

	def Hide(self):
		pass

	def Remove(self):
		pass


