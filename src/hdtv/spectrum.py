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

from hdtv.drawable import DrawableManager
from hdtv.util import LockViewport


class Spectrum(DrawableManager):
    def __init__(self, histogram):
        # Create histogram attribute avoiding __setattr__ method
        self.__dict__["hist"] = histogram
        DrawableManager.__init__(self)

    # delegate everything to the underlying histogram
    def __setattr__(self, name, value):
        if self.hist is not None:
            self.hist.__setattr__(name, value)
        if hasattr(self, name):  # Update attribute of this class, if existent
            DrawableManager.__setattr__(self, name, value)

    def __getattr__(self, name):
        # The use of self.__dict__ replaces an infinite recusion by a KeyError
        #  if self.hist does not exist
        return getattr(self.__dict__["hist"], name)

    # color property
    def _set_color(self, color):
        for fit in self.dict.values():
            fit.color = color

    def _get_color(self):
        return self.hist.color

    color = property(_get_color, _set_color)

    # cal property
    def _set_cal(self, cal):
        for fit in self.dict.values():
            fit.cal = cal

    def _get_cal(self):
        return self.hist.cal

    cal = property(_get_cal, _set_cal)

    # overwrite some functions of DrawableManager to do some extra work
    def Insert(self, fit, ID=None):
        fit.spec = self
        return DrawableManager.Insert(self, fit, ID)

    def Pop(self, ID):
        fit = DrawableManager.Pop(self, ID)
        if fit is not None:
            fit.spec = None
        return fit

    def Draw(self, viewport):
        self.viewport = viewport
        with LockViewport(self.viewport):
            DrawableManager.Draw(self, viewport)
            if self.hist:
                self.hist.Draw(viewport)

    def Show(self):
        if self.viewport is None:
            return
        with LockViewport(self.viewport):
            DrawableManager.Show(self)
            if self.hist:
                self.hist.Show()

    def Hide(self):
        if self.viewport is None:
            return
        with LockViewport(self.viewport):
            DrawableManager.Hide(self)
            if self.hist:
                self.hist.Hide()

    def Refresh(self):
        if self.viewport is None:
            return
        with LockViewport(self.viewport):
            DrawableManager.Refresh(self)
            if self.hist:
                self.hist.Refresh()


class CutSpectrum(Spectrum):
    def __init__(self, hist, matrix, axis):
        Spectrum.__init__(self, hist)

        # Use self.__dict__ to avoid delegation to the underlying histogram
        self.__dict__["matrix"] = matrix
        self.__dict__["axis"] = axis

    def Show(self):
        """
        Show all visible cut markers for the axis of this spectrum
        """
        Spectrum.Show(self)
        if self.matrix:
            self.matrix.Show(axis=self.axis)

    def Hide(self):
        """
        Hide also the cut markers, but without changing the visibility state of the matrix
        """
        Spectrum.Hide(self)
        if self.matrix:
            self.matrix.Hide()

    def Refresh(self):
        """
        Repeat the cut
        """
        if self.matrix:
            for cut in self.matrix.dict.values():
                if self == cut.spec:
                    cut.Refresh()
                    break
