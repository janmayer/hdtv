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
main session of hdtv
"""

import copy

import hdtv.cal
from hdtv.cut import Cut
from hdtv.drawable import DrawableManager
from hdtv.fit import Fit
from hdtv.fitter import Fitter
from hdtv.integral import Integrate
from hdtv.window import Window


class Session(DrawableManager):
    """
    Main session of hdtv

    First of all this provides a list of spectra, which is why this is called
    spectra in most contexts. But this also keeps track of the basic fit interface
    and of a list of calibrations.
    """

    def __init__(self):
        self.window = Window()
        super().__init__(viewport=self.window.viewport)
        # TODO: make peakModel and bgdeg configurable
        self.workFit = Fit(Fitter(peakModel="theuerkauf", backgroundModel="polynomial"))
        self.workFit.active = True
        self.workFit.Draw(self.viewport)
        self.workCut = Cut()
        self.workCut.active = True
        self.workCut.Draw(self.viewport)
        self.caldict = hdtv.cal.PositionCalibrationDict()
        # main session is always active
        self._active = True

    def ApplyCalibration(self, specIDs, cal, storeInCaldict: bool = True):
        """
        Apply calibration cal to spectra with ids
        """
        if isinstance(specIDs, (str, int, float)):
            specIDs = hdtv.util.ID.ParseIds(str(specIDs), self)
        for ID in specIDs:
            try:
                spec = self.dict[ID]
            except KeyError:
                hdtv.ui.warning("There is no spectrum with id: %s" % ID)
            else:
                if cal is None:
                    hdtv.ui.msg("Unsetting calibration of spectrum with id %s" % ID)
                    try:
                        self.caldict.pop(spec.name)
                    except KeyError:
                        pass
                    spec.cal = None
                else:
                    hdtv.ui.msg("Calibrated spectrum with id %s" % ID)
                    cal = hdtv.cal.MakeCalibration(cal)
                    if storeInCaldict:
                        self.caldict[spec.name] = cal
                    spec.cal = cal
                if self.workFit.spec == spec:
                    self.workFit.cal = cal

    # Marker handling
    def SetMarker(self, mtype, pos=None):
        """
        Set Marker of type "mtype" (bg, peak, region, cut) to position pos,
        if pos is not given, the current position of the cursor is used.
        """
        if pos is None:
            pos = self.viewport.GetCursorX()
        if mtype in ["bg", "peak", "region"]:
            self.workFit.ChangeMarker(mtype, pos, action="set")
        elif mtype in ["cut", "cutregion", "cutbg"]:
            mtype = mtype[3:]
            self.workCut.SetMarker(mtype, pos)

    def RemoveMarker(self, mtype, pos=None):
        """
        Remove the marker of type "mtype" (bg, peak, region), that is
        closest to position "pos", if position is not given, the current position
        of the cursor is used.
        """
        if pos is None:
            pos = self.viewport.GetCursorX()
        if mtype in ["bg", "peak", "region"]:
            self.workFit.ChangeMarker(mtype, pos, action="remove")
        elif mtype in ["cutregion", "cutbg"]:
            mtype = mtype[3:]
            self.workCut.RemoveMarker(mtype, pos)

    def ExecuteIntegral(self):
        spec = self.GetActiveObject()
        if spec is None:
            hdtv.ui.error("There is no active spectrum.")
            return

        fit = self.workFit
        fit.spec = spec
        if not fit.regionMarkers.IsFull():
            hdtv.ui.error("Region not set.")
            return

        if len(fit.bgMarkers) > 0:
            if fit.fitter.backgroundModel.fParStatus["nparams"] == -1:
                hdtv.ui.error("Background degree of -1 contradicts background fit.")
                return
            # pure background fit
            fit.FitBgFunc(spec)

        region = [fit.regionMarkers[0].p1.pos_uncal, fit.regionMarkers[0].p2.pos_uncal]
        bg = fit.fitter.bgFitter

        fit.integral = Integrate(spec, bg, region)
        fit.Draw(self.viewport)
        hdtv.ui.msg(html=fit.print_integral())

    # Functions to handle workFit
    def ExecuteFit(self, peaks=True):
        """
        Execute the fit

        If peaks=False, just a background fit is executed, else a peak fit is executed.
        """
        hdtv.ui.debug("Executing the fit")
        spec = self.GetActiveObject()
        if spec is None:
            hdtv.ui.error("There is no active spectrum.")
            return

        fit = self.workFit
        try:
            if not peaks and len(fit.bgMarkers) > 0:
                fit.FitBgFunc(spec)
            if peaks:
                # full fit
                fit.FitPeakFunc(spec)
            # show fit result
            hdtv.ui.msg(html=str(fit), end="")
            fit.Draw(self.viewport)
        except OverflowError as msg:
            hdtv.ui.error("Fit failed: %s" % msg)
        if fit.regionMarkers.IsFull():
            region = [
                fit.regionMarkers[0].p1.pos_uncal,
                fit.regionMarkers[0].p2.pos_uncal,
            ]
            fit.integral = Integrate(spec, fit.fitter.bgFitter, region)

    def ClearFit(self, bg_only=False):
        """
        Clear the markers and erase a previously executed fit.

        If bg_only is True, only the background fit is cleared and a peak fit
        is repeated now with internal background.
        """
        if bg_only:
            self.workFit.bgMarkers.Clear()
            self.workFit.Erase(bg_only)
            self.workFit.Refresh()
        else:
            self.workFit.bgMarkers.Clear()
            self.workFit.peakMarkers.Clear()
            self.workFit.regionMarkers.Clear()
            # Keeping positions on hold for a new fit is not really sensible
            if "pos" in self.workFit.fitter.params:
                self.workFit.fitter.SetParameter("pos", "free")
                hdtv.ui.msg("'pos' fit parameter reset to 'free'")
            self.workFit.spec = None

    def ActivateFit(self, ID, sid=None):
        """
        Copy markers of a already stored fit to workFit.

        Note: that a call to Store will overwrite the active fit with workFit
        """
        # for interactive use of this function
        if isinstance(ID, (str, int, float)):
            ID = hdtv.util.ID.ParseIds(ID, self)[0]
        if sid is None:
            sid = self.activeID
        if sid is None:
            hdtv.ui.warning("There is no active spectrum")
            return
        spec = self.dict[sid]
        spec.ActivateObject(ID)
        if ID is not None:
            # make a copy for workFit
            self.workFit = copy.copy(spec.GetActiveObject())
            self.workFit.active = True
            self.workFit.Draw(self.viewport)

    def StoreFit(self, ID=None):
        """
        Stores current workFit with ID.

        If no ID is given, the next free ID is used.
        The markers are kept in workFit, for possible re-use.
        """
        spec = self.workFit.spec
        # for interactive use of this function
        if isinstance(ID, (str, int, float)):
            ids = hdtv.util.ID.ParseIds(
                ID, self.dict[self.activeID], only_existent=False
            )
            if len(ids) > 1:
                raise hdtv.cmdline.HDTVCommandError("More than one ID given")
            ID = ids[0]
        if spec is None:
            hdtv.ui.warning("No fit available to store")
            return
        if ID is None:
            ID = spec.activeID
        ID = spec.Insert(self.workFit, ID)
        spec.dict[ID].active = False
        spec.ActivateObject(None)
        hdtv.ui.msg("Storing workFit with ID %s" % ID)
        self.workFit = copy.copy(self.workFit)
        self.workFit.active = True
        self.workFit.Draw(self.viewport)

    # Functions to handle workCut
    def ExecuteCut(self):
        spec = self.GetActiveObject()
        if spec is None:
            hdtv.ui.error("There is no active spectrum")
            return
        if not hasattr(spec, "matrix") or spec.matrix is None:
            hdtv.ui.error("Active spectrum does not belong to a matrix")
            return
        cutSpec = self.workCut.ExecuteCut(spec.matrix, spec.axis)
        if cutSpec is not None:
            ID = spec.matrix.ID
            self.Insert(cutSpec, ID=hdtv.util.ID(ID.major, 1010))

    def ClearCut(self):
        self.workCut.regionMarkers.Clear()
        self.workCut.bgMarkers.Clear()
        self.workCut.axis = None
        if self.workCut.spec is not None:
            self.Pop(self.Index(self.workCut.spec))

    def ActivateCut(self, ID):
        # for interactive use of this function
        if isinstance(ID, (str, int, float)):
            ID = hdtv.util.ID.ParseIds(ID, self)[0]
        spec = self.GetActiveObject()
        if spec is None:
            hdtv.ui.error("There is no active spectrum")
            return
        if not hasattr(spec, "matrix") or spec.matrix is None:
            hdtv.ui.error("Active spectrum does not belong to a matrix")
            return
        spec.matrix.ActivateObject(ID)
        if ID is not None:
            self.workCut = copy.copy(spec.matrix.GetActiveObject())
            self.workCut.active = True
            self.workCut.Draw(self.viewport)

    def StoreCut(self, ID=None):
        # for interactive use of this function
        if isinstance(ID, (str, int, float)):
            ID = hdtv.util.ID.ParseIds(ID, self)[0]
        spec = self.GetActiveObject()
        if spec is None:
            hdtv.ui.error("There is no active spectrum")
            return
        if not hasattr(spec, "matrix") or spec.matrix is None:
            hdtv.ui.error("Active spectrum does not belong to a matrix")
            return
        mat = spec.matrix
        ID = mat.Insert(self.workCut, ID)
        mat.dict[ID].active = False
        mat.ActivateObject(None)
        if self.workCut.spec is not None:
            spec = self.Pop(self.Index(self.workCut.spec))
            # give it a new color
            spec.color = hdtv.color.ColorForID(ID.major)
            self.Insert(spec, ID=hdtv.util.ID(mat.ID.major, ID.major))
        hdtv.ui.msg("Storing workCut with ID %s" % ID)
        self.workCut = copy.copy(self.workCut)
        self.workCut.active = True
        self.workCut.Draw(self.viewport)

    # Overwrite some functions of DrawableManager to do some extra work
    def ActivateObject(self, obj):
        """
        Activate Object and reset workFit when activating another spectrum
        """
        # for interactive use of this function
        if isinstance(obj, (str, int, float)):
            obj = hdtv.util.ID.ParseIds(obj, self)[0]
        if obj is not self.activeID:
            # reset workFit
            self.workFit.spec = None
            # deactivate a possible active fit
            spec = self.GetActiveObject()
            if spec is not None:
                spec.ActivateObject(None)
        super().ActivateObject(obj)

    def Pop(self, ID):
        """
        Pop spectrum with ID and activate prevID if ID was activeID
        """
        # for interactive use of this function
        if isinstance(ID, (str, int, float)):
            ID = hdtv.util.ID.ParseIds(ID, self)[0]
        if self.activeID is ID:
            self.ActivateObject(self.prevID)
        return super().Pop(ID)

    def ShowObjects(self, ids, clear=True):
        """
        Show spectra and make sure one of the visible objects is active
        """
        ids = super().ShowObjects(ids, clear)
        if self.activeID not in self.visible:
            if len(self.visible) > 0:
                self.ActivateObject(max(self.visible))
            else:
                self.ActivateObject(None)
        return ids

    def HideObjects(self, ids):
        """
        Hide spectra and make sure one of the visible objects is active
        """
        ids = super().HideObjects(ids)
        if self.activeID not in self.visible:
            if len(self.visible) > 0:
                self.ActivateObject(max(self.visible))
            else:
                self.ActivateObject(None)
        return ids

    def Clear(self):
        """
        Clear everything
        """
        self.workFit = Fit(Fitter(peakModel="theuerkauf", backgroundModel="polynomial"))
        self.workFit.active = True
        self.workFit.Draw(self.viewport)
        self.caldict = hdtv.cal.PositionCalibrationDict()
        return super().Clear()
