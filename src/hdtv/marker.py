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
import hdtv.rootext.display
from hdtv.drawable import Drawable
from hdtv.util import LockViewport


class Marker(Drawable):
    """
    Markers in X or in Y direction

    Every marker contains a pair of positions as many markers come always in
    pairs to mark a region (like background markers). Of course it is also
    possible to have markers that consist of a single marker, then the second
    position is None.
    """

    def __init__(self, xytype, p1, color=hdtv.color.zoom, cal=None, connecttop=False):
        self._activeColor = color
        self._cal = cal
        self._dashed = False
        self.fixedInCal = True
        self.xytype = xytype
        self.connecttop = connecttop
        self.p1 = p1
        self.p2 = None
        Drawable.__init__(self, color=color, cal=cal)

    # p1 and p2 properties
    def _set_p(self, pos, p):
        if isinstance(pos, (float, int)):
            pos = hdtv.util.Position(pos, self.fixedInCal, self.cal)
        setattr(self, "_%s" % p, pos)

    def _get_p(self, p):
        return getattr(self, "_%s" % p)

    p1 = property(
        lambda self: self._get_p("p1"), lambda self, pos: self._set_p(pos, "p1")
    )
    p2 = property(
        lambda self: self._get_p("p2"), lambda self, pos: self._set_p(pos, "p2")
    )

    # color property
    def _set_color(self, color):
        # active color is given at creation and should not change
        self._passiveColor = hdtv.color.Highlight(color, active=False)
        if self.displayObj:
            if self.active:
                self.displayObj.SetColor(self._activeColor)
            else:
                self.displayObj.SetColor(self._passiveColor)

    def _get_color(self):
        return self._passiveColor

    color = property(_get_color, _set_color)

    # cal property
    def _set_cal(self, cal):
        self.p1.cal = cal
        if self.p2 is not None:
            self.p2.cal = cal
        Drawable._set_cal(self, cal)
        if self.displayObj:
            # call Refresh to carry the possible change
            # of p1.pos_uncal und p2.pos_uncal to the displayObj
            self.Refresh()

    def _get_cal(self):
        return self._cal

    cal = property(_get_cal, _set_cal)

    # dashed property
    def _set_dashed(self, state):
        self._dashed = state
        if self.displayObj:
            self.displayObj.SetDash(state, state)

    def _get_dashed(self):
        return self._dashed

    dashed = property(_get_dashed, _set_dashed)

    def Draw(self, viewport):
        """
        Draw the marker
        """
        if self.viewport and not self.viewport == viewport:
            # Marker can only be drawn to a single viewport
            raise RuntimeError("Marker cannot be realized on multiple viewports")
        self.viewport = viewport
        # adjust the position values for the creation of the makers
        # on the C++ side all values must be uncalibrated
        p1 = self.p1.pos_uncal
        if self.p2 is None:
            n = 1
            p2 = 0.0
        else:
            n = 2
            p2 = self.p2.pos_uncal
        # X or Y?
        if self.xytype == "X":
            constructor = ROOT.HDTV.Display.XMarker
        elif self.xytype == "Y":
            constructor = ROOT.HDTV.Display.YMarker
        if self.active:
            self.displayObj = constructor(n, p1, p2, self._activeColor)
        else:
            self.displayObj = constructor(n, p1, p2, self._passiveColor)
        # set some properties
        if self.ID is not None:
            self.displayObj.SetID(str(self.ID))
        self.displayObj.SetDash(self.dashed, self.dashed)
        if self.xytype == "X":
            # these properties make only sense on the X axis
            self.displayObj.SetConnectTop(self.connecttop)
            if self.cal:
                self.displayObj.SetCal(self.cal)
        self.displayObj.Draw(self.viewport)

    def Refresh(self):
        if not self.displayObj:
            return
        p1 = self.p1.pos_uncal
        if self.p2 is None:
            # on the C++ side all values must be uncalibrated
            self.displayObj.SetN(1)
            self.displayObj.SetPos(p1)
        else:
            # on the C++ side all values must be uncalibrated
            p2 = self.p2.pos_uncal
            self.displayObj.SetN(2)
            self.displayObj.SetPos(p1, p2)

    def __str__(self):
        if self.p2 is not None:
            return f"{self.xytype} marker at {self.p1} and {self.p2}"
        else:
            return f"{self.xytype} marker at {self.p1}"

    def FixInCal(self):
        self.fixedInCal = True
        self.p1.FixInCal()
        if self.p2 is not None:
            self.p2.FixInCal()

    def FixInUncal(self):
        self.fixedInCal = False
        self.p1.FixInUncal()
        if self.p2 is not None:
            self.p2.FixInUncal()


class MarkerCollection(list):
    """
    A collection of identical markers
    """

    def __init__(
        self, xytype, paired=False, maxnum=None, color=None, cal=None, connecttop=True
    ):
        list.__init__(self)
        self.viewport = None
        self.xytype = xytype
        self.paired = paired
        self.maxnum = maxnum
        self.connecttop = connecttop
        self.cal = cal
        self.ID = None
        # active color is defined at creation time of MarkerCollection
        self.activeColor = color
        # color = passiveColor can be changed
        self.color = hdtv.color.Highlight(color, active=False)
        self.active = True  # By default markers are active when newly created
        self.fixedInCal = True  # By default markers are fixed in calibrated space

    # delegate everything to the markers
    def __setattr__(self, name, value):
        for marker in self:
            if hasattr(marker, name):
                marker.__setattr__(name, value)
        self.__dict__[name] = value

    def Draw(self, viewport):
        self.viewport = viewport
        for marker in self:
            marker.Draw(self.viewport)

    def Show(self):
        for marker in self:
            marker.Show()

    def Hide(self):
        for marker in self:
            marker.Hide()

    def Refresh(self):
        for marker in self:
            marker.Refresh()

    def FixInCal(self):
        self.fixedInCal = True
        for marker in self:
            marker.FixInCal()

    def FixInUncal(self):
        self.fixedInCal = False
        for marker in self:
            marker.FixInUncal()

    def SetMarker(self, pos):
        """
        Set a marker to calibrated position pos, possibly completing a marker pair
        """
        if self.IsFull():
            pending = self.pop(0)
            pending.p1 = pos
            pending.p2 = None
            pending.Refresh()
            self.append(pending)
        elif self.IsPending():
            pending = self[-1]
            pending.p2 = pos
            pending.Refresh()
        else:
            m = Marker(self.xytype, pos, self.activeColor, self.cal, self.connecttop)
            m.color = self.color
            m.ID = self.ID
            m.active = self.active
            self.append(m)
            if self.viewport:
                m.Draw(self.viewport)

    def IsFull(self):
        """
        Checks if this MarkerCollection already contains the maximum number of
        markers allowed
        """
        if self.maxnum is None:
            return False
        if self.IsPending():
            return False
        return len(self) == self.maxnum

    def IsPending(self):
        """
        Checks if there is a single marker waiting to form a pair.
        Always returns False if this is a MarkerCollection with paired == False.
        """
        if not self.paired:
            return False
        return len(self) > 0 and self[-1].p2 is None

    def Clear(self):
        """
        Remove all markers from this collection
        """
        with LockViewport(self.viewport):
            while self:
                self.pop()

    def RemoveNearest(self, pos):
        """
        Remove the marker that is nearest to pos
        If one of the members of a marker pair is nearest to pos,
        both are removed
        """
        if len(self) == 0:
            hdtv.ui.warning("No marker available, no action taken")
            return
        index = {}
        for m in self:
            p1 = m.p1.pos_cal
            diff = abs(pos - p1)
            index[diff] = m
            if self.paired and m.p2 is not None:
                p2 = m.p2.pos_cal
                diff = abs(pos - p2)
                index[diff] = m
        nearest = index[min(index.keys())]
        self.remove(nearest)
        self.Refresh()
