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


import math
import ROOT
import hdtv.util

"""
Default colors for HDTV
"""

kSpecDef = 2
kFitDef = 25

# Default colors for fit functions
FIT_SUM_FUNC = ROOT.kOrange - 3
FIT_BG_FUNC = ROOT.kGreen
FIT_DECOMP_FUNC = ROOT.kMagenta + 1

def ColorForID(ID, status):
	if status == "ACTIVE":
		satur = 0.5
	else:
		satur = 1.0
		
	hue = HueForID(ID)
	value = 1.0
	
	(r,g,b) = HSV2RGB(hue*360., satur, value)
	return ROOT.TColor.GetColor(r,g,b)

def HueForID(ID):
	"""
	Returns the hue corresponding to a certain spectrum ID. The idea is to maximize the
	hue difference between the spectra shown, without knowing beforehand how many spectra
	there will be and without being able to change the color afterwards (that would confuse
	the user). The saturation and value of the color can be set arbitrarily, for example
	to indicate which spectrum is currently active.
	"""
	# Special case
	if ID==0:
		hue = 0.0
	else:
		p = math.floor(math.log(ID) / math.log(2))
		q = ID - 2**p
		hue = 2**(-p-1) + q*2**(-p)
		
	return hue
	
def HSV2RGB(hue, satur, value):
	"""
	 Static method to compute RGB from HSV.
	 - The hue value runs from 0 to 360.
	 - The saturation is the degree of strength or purity and is from 0 to 1.
	   Purity is how much white is added to the color, so S=1 makes the purest
	   color (no white).
	 - Brightness value also ranges from 0 to 1, where 0 is the black.
	 The returned r,g,b triplet is between [0,1].
	"""

	# This is a copy of the ROOT function TColor::HSV2RGB,
	# which we cannot use because it uses references to return
	# several values.
	# TODO: Find a proper way to deal with C++ references from
	# PyROOT, then replace this function by a call to
	# TColor::HSV2RGB.
	if satur==0.:
		# Achromatic (grey)
		r = g = b = value
		return (r, g, b)

	hue /= 60.;   # sector 0 to 5
	i = int(math.floor(hue))
	f = hue-i;   # factorial part of hue
	p = value*(1-satur)
	q = value*(1-satur*f )
	t = value*(1-satur*(1-f))

	if i==0:
		r = value
		g = t
		b = p
	elif i==1:
		r = q
		g = value
		b = p
	elif i==2:
		r = p
		g = value
		b = t
	elif i==3:
		r = p
		g = q
		b = value
	elif i==4:
		r = t
		g = p
		b = value
	else:
		r = value
		g = p
		b = q

	return (r,g,b)
	
	
