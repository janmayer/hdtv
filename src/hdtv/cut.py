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

import hdtv.color
from hdtv.drawable import Drawable
from hdtv.util import LockViewport
from hdtv.weakref_proxy import weakref


class Cut(Drawable):
    def __init__(self, color=None, cal=None):
        self.regionMarkers = hdtv.marker.MarkerCollection(
            "X", paired=True, maxnum=1, color=hdtv.color.cut
        )
        self.bgMarkers = hdtv.marker.MarkerCollection(
            "X", paired=True, color=hdtv.color.cut, connecttop=False
        )
        Drawable.__init__(self, color, cal)
        self.spec = None
        self.axis = None  # <- keep this last (needed for __setattr__)

    # delegate everything to the markers
    def __setattr__(self, name, value):
        if name == "cal":
            value = hdtv.cal.MakeCalibration(value)
        if hasattr(self, "axis"):
            self.regionMarkers.__setattr__(name, value)
            self.bgMarkers.__setattr__(name, value)
        Drawable.__setattr__(self, name, value)

    # color property
    def _set_color(self, color):
        # we only need the passive color for fits
        self._passiveColor = hdtv.color.Highlight(color, active=False)
        with LockViewport(self.viewport):
            self.regionMarkers.color = color
            self.bgMarkers.color = color
            if hasattr(self, "spec") and self.spec is not None:
                self.spec.color = color

    def _get_color(self):
        return self._passiveColor

    color = property(_get_color, _set_color)

    def SetMarker(self, mtype, pos):
        if mtype == "":
            if self.regionMarkers.IsFull():
                mtype = "bg"
            else:
                mtype = "region"
        markers = getattr(self, "%sMarkers" % mtype)
        markers.SetMarker(pos)

    def RemoveMarker(self, mtype, pos):
        markers = getattr(self, "%sMarkers" % mtype)
        markers.RemoveNearest(pos)

    def ExecuteCut(self, matrix, axis):
        if self.regionMarkers.IsPending() or len(self.regionMarkers) == 0:
            return None
        self.matrix = matrix
        self.axis = axis
        spec = self.matrix.ExecuteCut(self)
        self.spec = weakref(spec)
        return spec

    def __copy__(self):
        """
        copies marker of this cut
        """
        new = Cut()
        for marker in self.regionMarkers:
            new.regionMarkers.SetMarker(marker.p1.pos_cal)
            if marker.p2:
                new.regionMarkers.SetMarker(marker.p2.pos_cal)
        for marker in self.bgMarkers:
            new.bgMarkers.SetMarker(marker.p1.pos_cal)
            if marker.p2:
                new.bgMarkers.SetMarker(marker.p2.pos_cal)
        return new

    def Draw(self, viewport):
        if not viewport:
            return
        self.viewport = viewport
        self.regionMarkers.Draw(viewport)
        self.bgMarkers.Draw(viewport)

    def Hide(self):
        if not self.viewport:
            return
        with LockViewport(self.viewport):
            self.regionMarkers.Hide()
            self.bgMarkers.Hide()

    def Show(self):
        if not self.viewport:
            return
        with LockViewport(self.viewport):
            self.regionMarkers.Show()
            self.bgMarkers.Show()

    def Refresh(self):
        # FIXME
        if self.matrix:
            self.matrix.ExecuteCut(self, self.axis)
