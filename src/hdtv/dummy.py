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

"""
This is a dummy/noop module that can replace ROOT.HDTV.Display
without actually doing anything. In particular, no GUI windows
are opened.
"""


def _noop(*args, **kwargs):
    pass


def _get_float(self, *args, **kwargs):
    self.i += 0.1
    return self.i


def _get_bool(self, *args, **kwargs):
    return True


class Viewer:
    Connect = _noop

    def __init__(self, *args, **kwargs):
        self.fView = View1D()
        self.fKeySym = 0
        self.fKeyStr = ""

    def GetViewport(self):
        return self.fView


class View1D:
    GetCursorX = _get_float
    GetCursorY = _get_float
    GetDarkMode = _get_bool
    GetXOffset = _get_float
    GetXVisibleRegion = _get_float
    GetYMinVisibleRegion = _get_float
    GetYOffset = _get_float
    GetYVisibleRegion = _get_float
    LockUpdate = _noop
    SetDarkMode = _noop
    SetStatusText = _noop
    SetXCenter = _noop
    SetXVisibleRegion = _noop
    SetYMinVisibleRegion = _noop
    SetYVisibleRegion = _noop
    ShiftXOffset = _noop
    ShiftYOffset = _noop
    ShowAll = _noop
    ToggleLogScale = _noop
    ToggleUseNorm = _noop
    ToggleYAutoScale = _noop
    UnlockUpdate = _noop
    Update = _noop
    XZoomAroundCursor = _noop
    YAutoScaleOnce = _noop
    YZoomAroundCursor = _noop

    def __init__(self, *args, **kwargs):
        self.i = 0.1


class DisplayObj:
    Draw = _noop
    Hide = _noop
    Show = _noop
    __call__ = _noop

    def __init__(self, *args, **kwargs):
        self.ID = None


class DisplayBlock(DisplayObj):
    SetCal = _noop
    SetColor = _noop
    SetNorm = _noop


class Marker(DisplayObj):
    SetColor = _noop
    SetDash = _noop
    SetID = _noop
    SetN = _noop
    SetPos = _noop


class XMarker(Marker):
    SetCal = _noop
    SetConnectTop = _noop


class YMarker(Marker):
    pass


class DisplayFunc(DisplayBlock):
    pass


class DisplaySpec(DisplayBlock):
    SetHist = _noop
    SetID = _noop


class MTViewer(Viewer):
    pass
