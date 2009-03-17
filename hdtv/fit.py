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

import hdtv.color
import hdtv.cal
from hdtv.drawable import Drawable
from hdtv.marker import MarkerCollection

hdtv.dlmgr.LoadLibrary("display")

class Fit(Drawable):
	"""
	Fit object
	
	This Fit object is the graphical representation of a fit in HDTV. 
	It contains the marker lists and the functions. The actual interface to
	the C++ fitting routines is the class Fitter.

	All internal values (fit parameters, fit region, peak list) are in 
	uncalibrated units. 
	"""

	def __init__(self, fitter, color=None, cal=None):
		Drawable.__init__(self, color, cal)
		self.regionMarkers = MarkerCollection("X", paired=True, maxnum=1,
												  color=38, cal=self.cal)
		self.peakMarkers = MarkerCollection("X", paired=False, maxnum=None,
												  color=50, cal=self.cal)
		self.bgMarkers = MarkerCollection("X", paired=True, maxnum=None,
												  color=11, cal=self.cal)
		self.fitter = fitter
		self.showDecomp = False
		self.dispPeakFunc = None
		self.dispBgFunc = None
		self.dispDecompFuncs = []
		self.dispFuncs = []
		
	def __str__(self):
		i=1
		text = str()
		for peak in self.fitter.resultPeaks:
			text += "Peak %d:  " %i
			text += ("\n               ".join(str(peak).split('\n')))
			i+=1
		return text
		
	
	def PutPeakMarker(self, pos):
		if self.dispPeakFunc:
			self.dispFuncs.remove(self.dispPeakFunc)
			self.dispPeakFunc.Remove()
			self.dispPeakFunc = None
		for func in self.dispDecompFuncs:
			self.dispFuncs.remove(func)
			func.Remove()
		self.dispDecompFuncs = []
		self.peakMarkers.PutMarker(pos)
		
	
	def PutRegionMarker(self, pos):
		if self.dispPeakFunc:
			self.dispFuncs.remove(self.dispPeakFunc)
			self.dispPeakFunc.Remove()
			self.dispPeakFunc = None
		for func in self.dispDecompFuncs:
			self.dispFuncs.remove(func)
			func.Remove()
		self.dispDecompFuncs = []
		self.peakMarkers.Remove()
		self.regionMarkers.PutMarker(pos)
		
		
	def PutBgMarker(self, pos):
		if self.dispBgFunc:
			self.dispFuncs.remove(self.dispBgFunc)
			self.dispBgFunc.Remove()
			self.dispBgFunc = None
		if self.dispPeakFunc:
			self.dispFuncs.remove(self.dispPeakFunc)
			self.dispPeakFunc.Remove()
			self.dispPeakFunc = None
		for func in self.dispDecompFuncs:
			self.dispFuncs.remove(func)
			func.Remove()
		self.dispDecompFuncs = []
		self.bgMarkers.PutMarker(pos)
		

	def FitBgFunc(self, spec):
		"""
		Do the background fit and extract the function for display
		Note: You still need to call Draw afterwards.
		"""
		# remove old fit
		if self.dispBgFunc:
			self.dispFuncs.remove(self.dispBgFunc)
			self.dispBgFunc.Remove()
			self.dispBgFunc = None
		if self.dispPeakFunc:
			self.dispFuncs.remove(self.dispPeakFunc)
			self.dispPeakFunc.Remove()
			self.dispPeakFunc = None
		for func in self.dispDecompFuncs:
			self.dispFuncs.remove(func)
			func.Remove()
		self.dispDecompFuncs = []
		# fit background 
		if len(self.bgMarkers)>0 and self.bgMarkers[-1].p2:
			backgrounds =  map(lambda m: [m.p1, m.p2], self.bgMarkers)
			self.fitter.FitBackground(spec, backgrounds)
			func = self.fitter.bgFitter.GetFunc()
			self.dispBgFunc = ROOT.HDTV.Display.DisplayFunc(func, hdtv.color.FIT_BG_FUNC)
			if spec.cal:
				self.dispBgFunc.SetCal(spec.cal)
			self.dispFuncs.append(self.dispBgFunc)
			
	
	def FitPeakFunc(self, spec):
		"""
		Do the actual peak fit and extract the functions for display
		Note: You still need to call Draw afterwards.
		"""
		# remove old fit
		if self.dispPeakFunc:
			self.dispFuncs.remove(self.dispPeakFunc)
			self.dispPeakFunc.Remove()
			self.dispPeakFunc = None
		for func in self.dispDecompFuncs:
			self.dispFuncs.remove(func)
			func.Remove()
		self.dispDecompFuncs = []
		# fit peaks
		if len(self.peakMarkers)>0 and len(self.regionMarkers)==1 and self.regionMarkers[-1].p2:
			region = [self.regionMarkers[0].p1, self.regionMarkers[0].p2]
			peaks = map(lambda m: m.p1, self.peakMarkers)
			self.fitter.FitPeaks(spec, region, peaks)
			func = self.fitter.peakFitter.GetSumFunc()
			self.dispPeakFunc = ROOT.HDTV.Display.DisplayFunc(func, hdtv.color.FIT_SUM_FUNC)
			if spec.cal:
				self.dispPeakFunc.SetCal(spec.cal)
			self.dispFuncs.append(self.dispPeakFunc)
			# extract function for each peak (decomposition)
			for i in range(0, self.fitter.peakFitter.GetNumPeaks()):
				func = self.fitter.peakFitter.GetPeak(i).GetPeakFunc()
				dispFunc = ROOT.HDTV.Display.DisplayFunc(func, hdtv.color.FIT_DECOMP_FUNC)
				if spec.cal:
					dispFunc.SetCal(spec.cal)
				self.dispDecompFuncs.append(dispFunc)
				self.dispFuncs.append(dispFunc)
			# update peak markers
			for (marker, peak) in zip(self.peakMarkers, self.fitter.resultPeaks):
				marker.p1 = peak.pos.value
			# print result
			print "\n"+6*" "+str(self)



	def Draw(self, viewport):
		"""
		Draw
		"""
		if self.viewport:
			if not self.viewport == viewport:
				# Unlike the Display object of the underlying implementation,
				# python objects can only be drawn on a single viewport
				raise RuntimeError, "Object can only be drawn on a single viewport"
		self.viewport = viewport
		# Lock updates
		self.viewport.LockUpdate()
		# draw fit funcs, if available
		for func in self.dispFuncs:
			func.Draw(self.viewport)
		if not self.showDecomp:
			# hide decompostion functions
			for func in self.dispDecompFuncs:
				func.Hide()
		# draw the markers (do this after the fit, 
		# because the fit updates the position of the peak markers)
		self.peakMarkers.Draw(self.viewport)
		self.regionMarkers.Draw(self.viewport)
		self.bgMarkers.Draw(self.viewport)
		self.viewport.UnlockUpdate()
		

	def Refresh(self):
		"""
		Refresh
		"""
		# repeat the fits
		if self.dispBgFunc:
			self.FitBgFunc(self.fitter.spec)
		if self.dispPeakFunc:
			self.FitPeakFunc(self.fitter.spec)
		if not self.viewport:
			return
		self.viewport.LockUpdate()
		self.Draw(self.viewport)
		# draw the markers (do this after the fit, 
		# because the fit updates the position of the peak markers)
		self.peakMarkers.Refresh()
		self.regionMarkers.Refresh()
		self.bgMarkers.Refresh()
		self.viewport.UnlockUpdate()


	def Show(self):
		if not self.viewport:
			return
		self.viewport.LockUpdate()
		self.peakMarkers.Show()
		self.regionMarkers.Show()
		self.bgMarkers.Show()
		for obj in self.dispFuncs:
			if not self.showDecomp and obj in self.dispDecompFuncs:
				# do not show decomposition functions if not asked
				continue
			obj.Show()
		self.viewport.UnlockUpdate()
		
		
	def Hide(self):
		if not self.viewport:
			return
		self.viewport.LockUpdate()
		self.peakMarkers.Hide()
		self.regionMarkers.Hide()
		self.bgMarkers.Hide()
		for obj in self.dispFuncs:
			obj.Hide()
		self.viewport.UnlockUpdate()
		
		
	def Remove(self):
		if self.viewport:
			self.viewport.LockUpdate()
			self.peakMarkers.Remove()
			self.regionMarkers.Remove()
			self.bgMarkers.Remove()
			while len(self.dispFuncs)>0:
				self.dispFuncs.pop().Remove()
			self.viewport.UnlockUpdate()
		self.dispPeakFunc = None
		self.dispBgFunc = None
		self.dispDecompFuncs = []
		self.dispFuncs = []
		self.fitter.resultPeaks = []
		
		
	def SetCal(self, cal):
		cal=hdtv.cal.MakeCalibration(cal)
		if self.viewport:
			self.viewport.LockUpdate()
		self.peakMarkers.SetCal(cal)
		self.regionMarkers.SetCal(cal)
		self.bgMarkers.SetCal(cal)
		for obj in self.dispFuncs:
			obj.SetCal(cal)
		if self.viewport:
			self.viewport.UnlockUpdate()


	def SetColor(self, color):
		if self.viewport:
			self.viewport.LockUpdate()
		# FIXME: include markers (they support SetColor() now)
		objs = self.dispFuncs
		for obj in objs:
			obj.SetColor(color)
		if self.viewport:
			self.viewport.UnlockUpdate()
			
	def Recalibrate(self, cal):
		"""
		Changes the internal (uncalibrated) values of the markers in such a way, 
		that the calibrated values are kept fixed, but a new calibration is used.
		"""
		self.cal = hdtv.cal.MakeCalibration(cal)
		self.peakMarkers.Recalibrate(cal)
		self.regionMarkers.Recalibrate(cal)
		self.bgMarkers.Recalibrate(cal)

	def Copy(self, cal=None, color=None):
		cal = hdtv.cal.MakeCalibration(cal)
		new = Fit(self.fitter.Copy())
		for marker in self.bgMarkers.collection:
			newmarker = marker.Copy(cal)
			new.bgMarkers.append(newmarker)
		for marker in self.regionMarkers.collection:
			newmarker = marker.Copy(cal)
			new.regionMarkers.append(newmarker)
		for marker in self.peakMarkers.collection:
			newmarker = marker.Copy(cal)
			new.peakMarkers.append(newmarker)
		new.SetCal(cal)
		new.SetColor(color)
		return new

		
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






