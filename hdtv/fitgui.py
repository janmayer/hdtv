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
from hdtv.drawable import DrawableCollection

hdtv.dlmgr.LoadLibrary("display")

class FitGui():
	def __init__(self, manager, window, peakModel="Teuerkauf", bgdeg=1):
		
		
		self.peakModel=peakModel
		self.bgDegree = bgdeg
		self.activeFitter = 
		self.activePeakMarkers = []
		self.activeRegionMarkers = []
		self.activeBgMarkers = []

		
class FitCompound(Drawable, UserDict.DictMixin)
	def __init__(self, spec)
		Drawable.__init__(self, spec, color)
		self.spec = spec
		self.fits = dict()
		self.visible = set()
		
	def __setitem__(self, ID, obj):
		pass
		
	def __getitem__(self, ID):
		pass
		
	def __delitem__(self, ID):
		pass
		
	def Add(self, fit)
		pass
		
	def GetFreeID(self)
		pass
		
	def Draw(self, viewport):
		if self.fViewport:
			if self.fViewport == viewport:
				# this fit has already been drawn
				self.Refresh()
				return
			else:
				# Unlike the Display object of the underlying implementation,
				# python objects can only be drawn on a single viewport
				raise RuntimeError, "Object can only be drawn on a single viewport"
		self.fViewport = viewport
		# Lock updates
		self.fViewport.LockUpdate()
		for obj in self.dispObj:
			obj.Draw()
		# Unlock updates
		self.fViewport.UnlockUpdate()
		
		
	def Refresh(self):
		# Lock updates
		self.fViewport.LockUpdate()
		for obj in self.dispObj:
			obj.Refresh()
		# Unlock updates
		self.fViewport.UnlockUpdate()
		
	
	def AddFit(self):
		
		
