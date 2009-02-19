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
	def __init__(self, window, peakModel="Teuerkauf", bgdeg=1, color=None):
		Drawable.__init__(self, color)
		self.spec = spec
		self.fits = []
		self.dispObj=[spec]
		
		self.activeFitter = Fitter(peakModel, bgdeg)
		self.activePeakMarkers = []
		self.activeRegionMarkers = []
		self.activeBgMarkers = []

		
class FitCompound(DrawableCollection)
	def __init__(self, spec)
		Drawable.__init__(self, color)
		
		self.spec = spec
		self.fits = []
		self.dispObj=[spec]
		
	def Draw(self, viewport):
		pass
		
	def Refresh(self, viewport):
		pass
