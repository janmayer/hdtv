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

	def __init__(self, fitter, region=[], peaks=[], backgrounds=[], 
	             color=None, cal=None):
		Drawable.__init__(self, color, cal)
		for marker in region+peaks+backgrounds:
			marker.p1 = self.cal.E2Ch(marker.cal.Ch2E(marker.p1))
			if marker.p2:
				marker.p2 = self.cal.E2Ch(marker.cal.Ch2E(marker.p2))
			marker.SetCal(self.cal)
		self.regionMarkers = region
		self.peakMarkers = peaks
		self.bgMarkers = backgrounds
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
			if i==1:
				text += "Peak %d:  " %i
			else:
				text += 6*" "+"Peak %d:  " %i
			text+= "Pos:" + str(peak.pos_cal.fmt()).rjust(15)
			text+= "  Volume:" + str(peak.vol.fmt()).rjust(15)
			text+= "  FWHM:" + str(peak.fwhm_cal.fmt()).rjust(15)
			text+= "\n"
			i+=1
		return text


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
		if self.dispBgFunc and not self.dispBgFunc in self.dispFuncs:
			self.dispBgFunc.Draw(self.viewport)
			self.dispFuncs.append(self.dispBgFunc)
		if self.dispPeakFunc and not self.dispPeakFunc in self.dispFuncs:
			self.dispPeakFunc.Draw(self.viewport)
			self.dispFuncs.append(self.dispPeakFunc)
		for func in self.dispDecompFuncs:
			if not func in self.dispFuncs:
				func.Draw(self.viewport)
				if not self.showDecomp:
					# hide it directly, it showDecomp==False
					func.Hide()
				self.dispFuncs.append(func)
		# refresh the markers (do this after the fit, 
		# because the fit updates the position of the peak markers)
		for marker in self.peakMarkers+self.regionMarkers+self.bgMarkers:
			marker.Refresh()
		self.viewport.UnlockUpdate()
		

	def Refresh(self):
		"""
		Refresh
		"""
		# repeat the fits
		self.viewport.LockUpdate()
		if self.dispBgFunc:
			self.FitBgFunc()
		if self.dispPeakFunc:
			self.FitPeakFunc()
		self.Draw(self.viewport)
		# draw the markers (do this after the fit, 
		# because the fit updates the position of the peak markers)
		for marker in self.peakMarkers+self.regionMarkers+self.bgMarkers:
			marker.Refresh()
		self.viewport.UnlockUpdate()


	def FitBgFunc(self):
		"""
		Do the background fit and extrat the function for display
		Note: You still need to call Draw afterwards.
		"""
		# remove old fit
		if self.dispBgFunc:
			self.dispFuncs.remove(self.dispBgFunc)
			self.dispBgFunc.Remove()
			self.dispBgFunc = None
		# fit background 
		if len(self.bgMarkers)>0 and self.bgMarkers[-1].p2:
			backgrounds =  map(lambda m: [m.p1, m.p2], self.bgMarkers)
			self.fitter.FitBackground(backgrounds)
			func = self.fitter.bgfitter.GetFunc()
			self.dispBgFunc = ROOT.HDTV.Display.DisplayFunc(func, hdtv.color.FIT_BG_FUNC)
			if self.fitter.spec.cal:
				self.dispBgFunc.SetCal(self.fitter.spec.cal)
			
	
	def FitPeakFunc(self):
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
			self.fitter.FitPeaks(region, peaks)
			func = self.fitter.GetSumFunc()
			self.dispPeakFunc = ROOT.HDTV.Display.DisplayFunc(func, hdtv.color.FIT_SUM_FUNC)
			if self.fitter.spec.cal:
				self.dispPeakFunc.SetCal(self.fitter.spec.cal)
			# extract function for each peak (decomposition)
			for i in range(0, self.fitter.GetNumPeaks()):
				func = self.fitter.GetPeak(i).GetPeakFunc()
				dispFunc = ROOT.HDTV.Display.DisplayFunc(func, hdtv.color.FIT_DECOMP_FUNC)
				if self.fitter.spec.cal:
					dispFunc.SetCal(self.fitter.spec.cal)
				self.dispDecompFuncs.append(dispFunc)
			# update peak markers
			for (marker, peak) in zip(self.peakMarkers, self.fitter.resultPeaks):
				marker.p1 = peak.pos.value
			# print result
			print "\n"+6*" "+str(self)
		
	def Show(self):
		self.viewport.LockUpdate()
		objs = self.dispFuncs+self.peakMarkers+self.regionMarkers+self.bgMarkers
		for obj in objs:
			obj.Show()
		self.viewport.UnlockUpdate()
		
		
	def Hide(self):
		self.viewport.LockUpdate()
		objs = self.dispFuncs+self.peakMarkers+self.regionMarkers+self.bgMarkers
		for obj in objs:
			obj.Hide()
		self.viewport.UnlockUpdate()
		
		
	def Remove(self):
		self.viewport.LockUpdate()
		objs = self.dispFuncs+self.peakMarkers+self.regionMarkers+self.bgMarkers
		for obj in objs:
			obj.Remove()
		self.viewport.UnlockUpdate()
		
		
	def SetCal(self, cal):
		cal=hdtv.cal.MakeCalibration(cal)
		if self.viewport:
			self.viewport.LockUpdate()
		for marker in self.peakMarkers+self.regionMarkers+self.bgMarkers:
			marker.SetCal(cal)
		for obj in self.dispFuncs:
			obj.SetCal(cal)
		if self.viewport:
			self.viewport.UnlockUpdate()


	def SetColor(self, color):
		if self.viewport:
			self.viewport.LockUpdate()
		# FIXME: include markers (they do not support SetColor at the moment!)
		objs = self.dispFuncs
		for obj in objs:
			obj.SetColor(color)
		if self.viewport:
			self.viewport.UnlockUpdate()
			
		
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
		

