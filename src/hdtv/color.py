# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2019  The HDTV development team (see file AUTHORS)
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

from hdtv.hsluv import hsluv_to_rgb, rgb_to_hsluv

# some default colors
zoom = ROOT.kWhite
region = ROOT.kBlue - 4
peak = ROOT.kViolet - 4
bg = ROOT.kGreen - 4
cut = ROOT.kYellow - 4

active_luminance = 76
nonactive_luminance = 58
golden_angle = 180 * (3 - math.sqrt(5))


def ColorForID(ID, active=False):
    try:
        ID = ID.split(".")
        ID = int(ID[0])
    except BaseException:
        pass
    hue = (ID * golden_angle) % 360
    saturation = 100
    luminance = active_luminance if active else nonactive_luminance
    r, g, b = hsluv_to_rgb([hue, saturation, luminance])
    return ROOT.TColor.GetColor(r, g, b)


default = ColorForID(0)


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
    color_r = ROOT.TColor.GetRed(color)
    color_g = ROOT.TColor.GetGreen(color)
    color_b = ROOT.TColor.GetBlue(color)
    hue, saturation, luminance = rgb_to_hsluv([color_r, color_g, color_b])
    saturation = 100
    luminance = active_luminance if active else nonactive_luminance
    r, g, b = hsluv_to_rgb([hue, saturation, luminance])
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
