#!/usr/bin/python
# -*- coding: utf-8 -*-
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


def ColorForID(ID, satur, value):
	"""
	Returns the color corresponding to a certain spectrum ID. The idea is to maximize the
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
	(r,g,b) = hdtv.util.HSV2RGB(hue*360., satur, value)
	return ROOT.TColor.GetColor(r,g,b)
