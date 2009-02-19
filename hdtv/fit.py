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

from hdtv.color import *
from hdtv.drawable import Drawable

hdtv.dlmgr.LoadLibrary("display")

class Fit(Drawable):
	"""
	Fit object
	
	This Fit object is the graphical representation of a fit in HDTV. 
	It contains the marker lists and the functions. The actual interface to
	the C++ fitting routines is the class Fitter.
	"""
	def __init__(self, fitter, region=[], peaks=[], backgrounds=[], color=None):
		Drawable.__init__(self, color)
		self.regionMarkers = region
		self.peakMarkers = peaks
		self.bgMarkers = backgrounds
		self.fitter = fitter
		self.showDecomp = False
		self.displayObjs = []


	def __str__(self):
		 return "Fit peaks in region from %s to %s" %(self.region[0], self.region[1])


	def Draw(self, viewport):
		if self.viewport:
			if self.viewport == viewport:
				# this fit has already been drawn
				self.Refresh()
				return
			else:
				# Unlike the Display object of the underlying implementation,
				# python objects can only be drawn on a single viewport
				raise RuntimeError, "Object can only be drawn on a single viewport"
		self.viewport = viewport
		# Lock updates
		self.viewport.LockUpdate()
			# do the fit and draw the functions 
			# this also updates the peak markers
			self._DrawFitFuncs()
			# draw the remaining markers
			for marker in self.regionMarker+self.bgMarkers:
				marker.Draw(self.viewport)
				self.displayObjs.append(marker)
		self.viewport.UnlockUpdate()
		

	def Refresh(self):
		self.viewport.LockUpdate()
		# remove old fit functions
		if self.dispFunc:
			self.displayObjs.remove(self.dispFunc)
			self.dispFunc.Remove()
			self.dispFunc = None
		if self.dispBgFunc:
			self.displayObjs.remove(self.dispBgFunc):
			self.dispBgFunc.Remove()
			self.dispBgFunc = None
		for func in self.dispDecompFuncs:
			self.displayObjs.remove(func)
			func.Remove()
		self.dispDecompFuncs = []
		# Repeat the fit and draw the functions
		# this also updates the peak markers
		self._DrawFitFuncs()
		# Draw the remaining markers
		for marker in self.regionMarker+self.bgMarker:
			marker.Refresh()
		self.viewport.UnlockUpdate()


	def _DrawFitFuncs(self):
		"""
		Internal function that calls the fit functions of the Fitter and 
		afterwards extracs the functions to display them
		"""
		if not self.viewport:
			raise RuntimeError, "No viewport defined."
		self.viewport.LockUpdate()
		# fit background and draw it
		if len(self.bgMarkers)>0 and self.bgMarkers[-1].p2:
			backgrounds =  map(lambda m: [m.p1, m.p2], self.bgMarkers)
			self.fitter.FitBackground(backgrounds)
			func = self.fitter.bgfitter.GetFunc()
			self.dispBgFunc = ROOT.HDTV.Display.DisplayFunc(func, color.FIT_BG_FUNC)
			if self.spec.cal:
				self.dispBgFunc.SetCal(self.spec.cal)
			self.dispBgFunc.Draw(self.fViewport)
			self.displayObjs.append(self.dispBgFunc)
		# fit peaks and draw it
		if len(self.peaks)>0 and len(self.region)==1 and self.region[-1].p2:
			region = [self.regionMarkers[0].p1, self.regionMarkers[0].p2]
			peaks = map(lambda m: m.p1, self.peakMarkers)
			self.fitter.FitPeaks(region, peaks)
			func = self.fitter.GetSumFunc()
			self.dispFunc = ROOT.HDTV.Display.DisplayFunc(func, color.FIT_SUM_FUNC)
			if self.spec.cal:
				self.dispFunc.SetCal(self.spec.fCal)
			self.dispFunc.Draw(self.viewport)
			self.displayObj.append(self.dispFunc)
			# update peak markers
			for (marker, peak) in zip(self.peakMarkers, self.fitter.resultPeaks):
				marker.p1 = peak.GetPos()
				marker.Refresh()
			# draw function for each peak (decomposition)
			for i in range(0, self.fitter.GetNumPeaks()):
				func = self.fitter.GetPeak(i).GetPeakFunc()
				dispFunc = ROOT.HDTV.Display.DisplayFunc(func, color.FIT_DECOMP_FUNC)
				if self.spec.cal:
					dispFunc.SetCal(self.spec.cal)
				dispFunc.Draw(self.viewport)
				if not self.showDecomp:
					# hide it directly, it showDecomp==False
					dispFunc.Hide()
				self.dispDecompFuncs.append(dispFunc)
			self.displayObj = self.displayObj+self.dispDecompFuncs
		self.viewport.UnlockUpdate()


	def Show(self):
		self.viewport.LockUpdate()
		for obj in self.displayObjs:
			obj.Show()
		self.viewport.UnlockUpdate()
		
	def Hide(self):
		self.viewport.LockUpdate()
		for obj in self.displayObjs:
			obj.Hide()
		self.viewport.UnlockUpdate()
		
	def Remove(self):
		self.viewport.LockUpdate()
		for obj in self.displayObjs:
			obj.Remove()
		self.viewport.UnlockUpdate()

	def SetColor(self, color):
		#FIXME: colors of markers according to some color scheme
		pass
		
	
	def SetDecomp(self, stat=True):
		"""
		Sets whether to display a decomposition of the fit
		"""
		if self.showDecomp == stat:
			# this is already the situation, thus nothing to be done here
			return
		else:
			self.showDecomp =  stat
			if stat:
				for func in self.dispDecompFuncs:
					func.Show()
			else:
				for func in self.dispDecompFuncs:
					func.Hide()
		

