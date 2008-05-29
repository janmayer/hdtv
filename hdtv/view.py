import ROOT
import gspec

from spectrum import Spectrum

class View:
	""" 
	View object.
	
	A view is a selection of stuff that can be displayed in a window.
	There can be several views in one window. Every view can contain 
	several spectra.
	If fViewport is set, then this view is currently displayed
	"""
	def __init__(self, title=None):
		self.fTitle = title
		self.fSpectra = []
		self.fViewport = None
		
	def AddSpec(self, fname, cal=None, color=None, update=True):
		"""
		Add a spectrum to this view

		The display will be automatically updated, 
		if this view is currently active. If the user wants to postpone the
		update, because there are more things to change, that can be done
		by setting update=False in the parameter list. The user is then 
		responsible for initilizing the update later.
		"""
		spec = Spectrum(fname, cal, color)
		self.fSpectra.append(spec)
		if self.fViewport:
			# update the display if this view is currently active
			spec.Realize(self.fViewport, update)
		return spec

	def DelSpec(self, sid, update=True):
		"""
		Delete a spectrum from this view.

		The display will be automatically updated, 
		if this view is currently active. If the user wants to postpone the
		update, because there are more things to change, that can be done
		by setting update=False in the parameter list. The user is then 
		responsible for initilizing the update later.
		"""
		if sid>=0 and sid < len(self.fSpectra):
			spec = self.fSpectra.pop(sid)
			if self.fViewport:
				spec.Delete(update)

	def Realize(self, viewport, update=True):
		"""
		Draw this view with all its ingredients to the window
		"""
		# save the viewport
		self.fViewport = viewport
		# show all spectra
		for spec in self.fSpectra:
			spec.Realize(viewport, False)
		# finally update the viewport
		if update:
			viewport.Update(True)
		
	def Delete(self, update=True):
		"""
		Delete this view with all its ingedients from the window
		"""
		if self.fViewport:
			# clear all spectra
			for spec in self.fSpectra:
				spec.Delete(False)
			# finally update the viewport
			if update:
				self.fViewport.Update(True)
			# remove the viewport from this view
			self.fViewport = None

	def Update(self, update=True):
		"""
		Update the screen
		"""
		if self.fViewport:
			for spec in self.fSpectra:
				spec.Update(False)
			# finally update the viewport
			if update:
				self.fViewport.Update(True)
	
