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


import colorsys
import math
import ROOT


# some default colors
default = ROOT.kRed
zoom = ROOT.kWhite
region = ROOT.kBlue - 4
peak = ROOT.kViolet - 4
bg = ROOT.kGreen - 4
cut = ROOT.kYellow - 4

activeSatur = 1.0
nonactiveSatur = 0.5


def ColorForID(ID, active=False):
    try:
        ID = ID.split(".")
        ID = int(ID[0])
    except BaseException:
        pass
    if active:
        satur = activeSatur
    else:
        satur = nonactiveSatur
    hue = HueForID(ID)
    value = 1.0
    (r, g, b) = colorsys.hsv_to_rgb(hue, satur, value)
    return ROOT.TColor.GetColor(r, g, b)


def HueForID(ID):
    """
    Returns the hue corresponding to a certain spectrum ID. The idea is to
    maximize the hue difference between the spectra shown, without knowing
    beforehand how many spectra there will be and without being able to change
    the color afterwards (that would confuse the user). The saturation and value
    of the color can be set arbitrarily, for example to indicate which spectrum
    is currently active.
    """
    # Special case
    if ID == 0:
        hue = 0.0
    else:
        p = math.floor(math.log(float(ID)) / math.log(2))
        q = ID - 2**p
        hue = 2**(-p - 1) + q * 2**(-p)
    return hue


def Highlight(color, active=True):
    """
    Manipulates the color in HSV room to achieve highlighting
     - The hue value runs from 0 to 360.
     - The saturation is the degree of strength or purity and is from 0 to 1.
       Purity is how much white is added to the color, so S=1 makes the purest
       color (no white).
     - Brightness value also ranges from 0 to 1, where 0 is black.
    """
    if color is None:
        color = default
    # you can not highlight white and black
    if color == 10 or color == 0:
        return color
    color = ROOT.gROOT.GetColor(color)
    if not color:
        # FIXME
        raise RuntimeError
    hue = ROOT.TColor.GetHue(color)
    value = 1.0
    if active:
        satur = activeSatur
    else:
        satur = nonactiveSatur
    (r, g, b) = colorsys.hsv_to_rgb(hue / 360, satur, value)
    return ROOT.TColor.GetColor(r, g, b)


def GetRGB(color):
    color = ROOT.gROOT.GetColor(color)
    if not color:
        # FIXME
        raise RuntimeError
    r = ROOT.TColor.GetRed(color)
    g = ROOT.TColor.GetGreen(color)
    b = ROOT.TColor.GetBlue(color)
    return (r, g, b)
