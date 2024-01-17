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
from hdtv.drawable import DrawableManager
from hdtv.spectrum import CutSpectrum
from hdtv.weakref_proxy import weakref


class Matrix(DrawableManager):
    def __init__(self, histo2D, sym, viewport):
        DrawableManager.__init__(self, viewport)
        self.histo2D = histo2D
        self.sym = sym
        self.ID = None
        self._xproj = None
        self._yproj = None
        self._color = hdtv.color.default

    # color property
    def _set_color(self, color):
        # give all cuts and projections the same color
        self._color = color
        for cut in self.dict.values():
            cut.color = color
        if self._xproj is not None:
            self._xproj.color = color
        if self._yproj is not None:
            self._yproj.color = color

    def _get_color(self):
        return self._color

    color = property(_get_color, _set_color)

    # name
    @property
    def name(self):
        return self.histo2D.name

    # projections
    @property
    def xproj(self):
        return self.project(axis="x")

    @property
    def yproj(self):
        return self.project(axis="y")

    def project(self, axis):
        """
        Return Projection along a given axis
        """
        if getattr(self, "_%sproj" % axis) is None:
            # no valid link to that projection, create fresh object
            hist = getattr(self.histo2D, "%sproj" % axis)
            if self.sym:
                a = "0"
            else:
                a = axis
            proj = CutSpectrum(hist, self, axis=a)
            proj.color = self.color
            setattr(self, "_%sproj" % axis, weakref(proj))
            return proj
        else:
            return getattr(self, "_%sproj" % axis)

    def ExecuteCut(self, cut):
        cutHisto = self.histo2D.ExecuteCut(cut.regionMarkers, cut.bgMarkers, cut.axis)
        if cut.axis == "x":
            axis = "y"
        elif cut.axis == "y":
            axis = "x"
        elif self.sym:
            axis = "0"
        else:
            raise RuntimeError
        cutSpec = CutSpectrum(cutHisto, self, axis)
        cutSpec.color = self.color
        return cutSpec

    # overwrite some functions from Drawable
    def Insert(self, obj, ID=None):
        """
        Insert cut to internal dict
        """
        obj.color = self.color
        obj.dashed = True
        if ID is None:
            ID = self.activeID
        ID = DrawableManager.Insert(self, obj, ID)
        self.ActivateObject(ID)
        return ID

    def ActivateObject(self, ID):
        if ID is not None and ID not in self.ids:
            raise KeyError
        # housekeeping for old active cut
        if self.activeID is not None:
            cut = self.GetActiveObject()
            cut.active = False
        # change active ID
        self.activeID = ID
        self._iteratorID = self.activeID
        # housekeeping for new active cut
        if self.activeID is not None:
            cut = self.GetActiveObject()
            cut.active = True

    def Show(self, axis="0"):
        for ID in self.visible:
            if self.dict[ID].axis == axis:
                self.dict[ID].Show()
