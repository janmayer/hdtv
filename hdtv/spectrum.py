# -*- coding: utf-8 -*-

# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2009  The HDTV development team (see file AUTHORS)
#
# This file is part of HDTV.
#
# HDTV is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# HDTV is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with HDTV; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import ROOT
import os
import hdtv.dlmgr
from hdtv.color import *
from hdtv.drawable import Drawable, DrawableCompound
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
		self.ID = -1
		self.norm = 1.0
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
			self.displayObj.SetID(self.ID)
			self.displayObj.SetNorm(self.norm)
			self.displayObj.Draw(self.viewport)

			# add calibration
			if self.cal:
				self.displayObj.SetCal(self.cal)
		# finally update the viewport
		self.viewport.UnlockUpdate()
		
		
	def SetID(self, ID):
		self.ID = ID
		if self.displayObj:
			self.displayObj.SetID(ID)
			
			
	def SetNorm(self, norm):
		"Set the normalization factor for displaying this spectrum"
		self.norm = norm
		if self.displayObj:
			self.displayObj.SetNorm(self.norm)
		
	
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
		

class SpectrumCompound(DrawableCompound):
	""" 
	This CompoundObject is a dictionary of Fits belonging to a spectrum.
	Everything that is not directed at the Fit dict is dispatched to the 
	underlying spectrum. Thus from the outside this can be treated as an 
	spectrum object, so that everything that has been written with a 
	spectrum object in mind will continue to work. 
	"""
	def __init__(self, viewport, spec):
		DrawableCompound.__init__(self,viewport)
		self.spec = spec
		self.color = spec.color
		
	def __getattr__(self, name):
		"""
		Dispatch everything which is unknown to this object to the spectrum
		"""
		return getattr(self.spec, name)

	def __setitem__(self, ID, obj):
		obj.Recalibrate(self.cal)
		DrawableCompound.__setitem__(self, ID, obj)

		
	def Refresh(self):
		"""
		Refresh spectrum and fits
		"""
		self.spec.Refresh()
		DrawableCompound.Refresh(self)
		
		
	def Draw(self, viewport):
		"""
		Draw spectrum and fits
		"""
		self.spec.Draw(viewport)
		DrawableCompound.Draw(self, viewport)
		
		
	def Show(self):
		"""
		Show the spectrum and all fits that are marked as visible
		"""
		self.spec.Show()
		# only show objects that have been visible before
		for i in list(self.visible):
			self.objects[i].Show()
		
			
	def ShowAll(self):
		"""
		Show spectrum and all fits
		"""
		DrawableCompound.ShowAll(self)
		
	def Remove(self):
		"""
		Remove spectrum and fits
		"""
		self.spec.Remove()
		DrawableCompound.Remove(self)
		
		
	def Hide(self):
		"""
		Hide the whole object,
		but remember which fits were visible
		"""
		# hide the spectrum itself
		self.spec.Hide()
		# Hide all fits, but remember what was visible
		visible = self.visible.copy()
		DrawableCompound.Hide(self)
		self.visible = visible
		
	def HideAll(self):
		"""
		Hide only the fits
		"""
		DrawableCompound.HideAll(self)

	def SetCal(self, cal):
		self.spec.SetCal(cal)
		DrawableCompound.SetCal(self, cal)
