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
import hdtv.cal
import hdtv.color
from hdtv.drawable import Drawable


class Marker(Drawable):
	""" 
	Markers in X or in Y direction
	
	Currently there are the following kinds of markers available:
	X: BACKGROUND", "CUT_BG", "REGION", "CUT", "PEAK", "XZOOM
	Y: YZOOM
	"""
	def __init__(self, xytype, p1, color=None, cal=None):
		Drawable.__init__(self, color, cal)
		self.xytype = xytype
		self.p1 = self.cal.E2Ch(p1)
		self.p2 = None
		
	def __str__(self):
		if self.p2:
			return '%s marker at %s and %s' %(self.xytype, self.p1, self.p2)
		else:
			return '%s marker at %s' %(self.xytype, self.p1)
		
	def Draw(self, viewport):
		""" 
		Draw the marker
		"""
		if self.viewport:
			if self.viewport == viewport:
				# this marker has already been drawn
				# but maybe the position 
				self.Refresh()
				return
			else:
				# Marker can only be drawn to a single viewport
				raise RuntimeError, "Marker cannot be realized on multiple viewports"
		self.viewport = viewport
		if self.p2 == None:
			n = 1
			p2 = 0.0
		else:
			n = 2
			p2 = self.p2
		# X or Y?
		if self.xytype == "X":
			constructor = ROOT.HDTV.Display.XMarker
		elif self.xytype == "Y":
			constructor = ROOT.HDTV.Display.YMarker
		if not self.color:
			self.color = hdtv.color.zoom
		self.displayObj = constructor(n, self.p1, p2, self.color)
		if self.xytype=="X":
			self.displayObj.SetCal(self.cal)
		self.displayObj.Draw(self.viewport)
		

	def Refresh(self):
		""" 
		Update the position of the marker
		"""
		if not self.viewport:
			return
		if self.displayObj:
			if self.p2:
				self.displayObj.SetN(2)
				self.displayObj.SetPos(self.p1, self.p2)
			else:
				self.displayObj.SetN(1)
				self.displayObj.SetPos(self.p1)

	def Copy(self, cal=None):
		"""
		Create a copy of this marker
		
		The actual position of the marker on the display (calibrated value)
		is kept. The calibration of the new marker can be set with the parameter
		cal.
		"""
		new = Marker(self.xytype, self.p1, self.color, cal=None)
		new.p2= self.p2
		new.cal=self.cal
		new.Recalibrate(cal)
		return new

	def Recalibrate(self, cal=None):
		"""
		Changes the internal (uncalibrated) values of the position in such a way, 
		that the calibrated values are kept fixed, but a new calibration is used.
		"""
		cal = hdtv.cal.MakeCalibration(cal)
		# translate marker positions to the new calibration
		self.p1 = cal.E2Ch(self.cal.Ch2E(self.p1))
		if self.p2:
			self.p2 = cal.E2Ch(self.cal.Ch2E(self.p2))
		# save new calibration
		self.SetCal(cal)


class MarkerCollection(Drawable):
	def __init__(self, xytype, paired=False, maxnum=None, color=None, cal=None):
		Drawable.__init__(self, color, cal)
		self.xytype = xytype
		self.paired = paired
		self.maxnum = maxnum
		self.collection = list()
		

	def Draw(self, viewport):
		self.viewport = viewport
		for marker in self.collection:
			marker.Draw(self.viewport)
			

	def Show(self):
		for marker in self.collection:
			marker.Show()
			

	def Hide(self):
		for marker in self.collection:
			marker.Hide()
			

	def Remove(self):
		for marker in self.collection:
			marker.Remove()
		self.collection = list()
			

	def SetColor(self, color=None, active=False):
		if not color:
			# use old color
			color = self.color
		self.color=hdtv.color.Highlight(color, active)
		for marker in self.collection:
			marker.SetColor(self.color)
			

	def SetCal(self, cal):
		self.cal= hdtv.cal.MakeCalibration(cal)
		for marker in self.collection:
			marker.SetCal(cal)


	def Recalibrate(self, cal):
		"""
		Changes the internal (uncalibrated) values of the positions in such a way, 
		that the calibrated values are kept fixed, but a new calibration is used.
		"""
		self.cal = hdtv.cal.MakeCalibration(cal)
		for marker in self.collection:
			marker.Recalibrate(cal)


	def __getattr__(self, name):
		# FIXME: include automatic remove when a marker is deleted
		return getattr(self.collection, name)


	def PutMarker(self, pos):
		"""
		Put a marker to position pos, where pos is assumed to be calibrated
		"""
		if not self.paired:
			m = Marker(self.xytype, pos, self.color, self.cal)
			if self.viewport:
				m.Draw(self.viewport)
			self.collection.append(m)
		else:
			if len(self.collection)>0 and self.collection[-1].p2==None:
				pending = self.collection[-1]
				pending.p2 = self.cal.E2Ch(pos)
				pending.Refresh()
			elif self.maxnum and len(self.collection)== self.maxnum:
				pending = self.collection.pop(0)
				pending.p1 = self.cal.E2Ch(pos)
				pending.p2 = None
				pending.Refresh()
				self.collection.append(pending)
			else:
				pending = Marker(self.xytype, pos, self.color, self.cal)
				if self.viewport:
					pending.Draw(self.viewport)
				self.collection.append(pending)
		
		
	def RemoveNearest(self, pos):
		"""
		Remove the marker that is nearest to pos, where pos is a calibrated value
		"""
		if len(self.collection)==0:
			print "Warning: no marker available, no action taken"
			return
		pos = self.cal.E2Ch(pos)
		index = dict()
		for m in self.collection:
			diff = abs(pos-m.p1)
			index[diff] = m
			if self.paired and not m.p2==None:
				diff = abs(pos-m.p2)
				index[diff] = m
		nearest = index[min(index.keys())]
		if not self.paired or nearest.p2==None:
			nearest.Remove()
			self.collection.remove(nearest)
		else:
			if abs(pos-nearest.p1) < abs(pos-nearest.p2):
				nearest.p1 = nearest.p2		
			nearest.p2 = None
			self.collection.remove(nearest)
			self.collection.append(nearest)
			nearest.Refresh()
	
			

