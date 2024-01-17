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

import copy

import ROOT
from uncertainties import ufloat

import hdtv.cal
import hdtv.color
import hdtv.integral
import hdtv.ui
from hdtv.drawable import Drawable
from hdtv.marker import MarkerCollection
from hdtv.util import ID, LockViewport, Pairs, Table
from hdtv.weakref_proxy import weakref


class Fit(Drawable):
    """
    Fit object

    This Fit object is the graphical representation of a fit in HDTV.
    It contains the marker lists and the functions. The actual interface to
    the C++ fitting routines is the class Fitter.

    All internal values (fit parameters, fit region, peak list) are in
    uncalibrated units.
    """

    # List of hook functions to be called before/after FitPeakFunc()
    # These hook functions should accept a reference to the Fit class
    # that calls them as first argument
    FitPeakPreHooks = []
    FitPeakPostHooks = []
    showDecomp = False  # Default value for decomposition status

    def __init__(self, fitter, color=None, cal=None):
        self.regionMarkers = MarkerCollection(
            "X", paired=True, maxnum=1, color=hdtv.color.region, cal=cal
        )
        self.peakMarkers = MarkerCollection(
            "X", paired=False, maxnum=None, color=hdtv.color.peak, cal=cal
        )
        self.bgMarkers = MarkerCollection(
            "X", paired=True, maxnum=None, color=hdtv.color.bg, cal=cal
        )
        self.fitter = fitter
        self.peaks = []
        self.chi = None
        self.bgChi = None
        self.bgParams = []
        self._showDecomp = Fit.showDecomp
        self.dispPeakFunc = None
        self.dispBgFunc = None
        Drawable.__init__(self, color, cal)
        self._spec = None
        self.active = False
        self.integral = None

    # ID property
    def _get_ID(self):
        return self._ID

    def _set_ID(self, ID):
        self._ID = ID
        if ID is not None:
            self.peakMarkers.ID = ID
        else:
            self.peakMarkers.ID = ID

    ID = property(_get_ID, _set_ID)

    # cal property
    def _set_cal(self, cal):
        self._cal = hdtv.cal.MakeCalibration(cal)
        with LockViewport(self.viewport):
            self.peakMarkers.cal = self._cal
            self.regionMarkers.cal = self._cal
            self.bgMarkers.cal = self._cal
            if self.dispPeakFunc:
                self.dispPeakFunc.SetCal(self._cal)
            if self.dispBgFunc:
                self.dispBgFunc.SetCal(self._cal)
            for peak in self.peaks:
                peak.cal = self._cal

    def _get_cal(self):
        return self._cal

    cal = property(_get_cal, _set_cal)

    # color property
    def _set_color(self, color):
        # we only need the passive color for fits
        self._passiveColor = hdtv.color.Highlight(color, active=False)
        with LockViewport(self.viewport):
            self.peakMarkers.color = color
            self.regionMarkers.color = color
            self.bgMarkers.color = color
            for peak in self.peaks:
                peak.color = color
            self.Show()

    def _get_color(self):
        return self._passiveColor

    color = property(_get_color, _set_color)

    # active property
    def _set_active(self, state):
        with LockViewport(self.viewport):
            self._active = state
            self.peakMarkers.active = state
            self.regionMarkers.active = state
            self.bgMarkers.active = state
            for peak in self.peaks:
                peak.active = state
            self.Show()

    def _get_active(self):
        return self._active

    active = property(_get_active, _set_active)

    # spec property
    def _set_spec(self, spec):
        if hasattr(self, "spec") and self._spec == spec:
            return
        # use weakref to prevent problems with cyclic reference
        self._spec = weakref(spec)
        self.Erase()
        if spec is None:
            self.FixMarkerInCal()
            self.cal = None
            self.color = None
        else:
            self.color = spec.color
            self.cal = spec.cal
            self.FixMarkerInUncal()

    def _get_spec(self):
        return self._spec

    spec = property(_get_spec, _set_spec)

    # ids property to get the ids of the peaks
    @property
    def ids(self):
        ids = []
        for i in range(len(self.peaks)):
            ids.append(ID(self.ID.major, i))
        return ids

    def __str__(self):
        """
        show fit results in a nice table
        """
        (objects, params) = self.ExtractParams()
        header = (
            "WorkFit on spectrum: " + str(self.spec.ID) + " (" + self.spec.name + ")"
        )
        footer = "\n" + str(len(objects)) + " peaks in WorkFit"
        table = Table(
            objects, list(params), sortBy="id", extra_header=header, extra_footer=footer
        )
        return str(table)

    def print_integral(self):
        """
        show integral of fit regions in a nice table
        """
        (objects, params) = self.ExtractIntegralParams("all")
        header = (
            "Integrals of WorkFit regions on spectrum: "
            + str(self.spec.ID)
            + " ("
            + self.spec.name
            + ")"
        )
        table = Table(objects, list(params), sortBy="id", extra_header=header)
        return str(table)

    def formatted_str(self, verbose=True):
        """
        show fit results in a more tv like way

        TODO: Since we do not use this any longer, we may as well remove it.
        """
        i = 0
        text = ""
        for peak in self.peaks:
            text += ("\nPeak %d:" % i).ljust(10)
            peakstr = peak.formatted_str(verbose).strip()
            peakstr = peakstr.split("\n")
            peakstr = ("\n".ljust(10)).join(peakstr)
            text += peakstr
            i += 1
        text += "\n\n chi² of fit: %d" % self.chi
        return text

    def ExtractParams(self):
        """
        Helper function for use for printing fit results in a nice table

        Return values:
            peaklist: a list of dicts for each peak in the fit
            params  : a ordered list of valid parameter names
        """
        peaklist = []
        params = ["id", "stat", "chi"]
        # Get peaks
        for peak in self.peaks:
            thispeak = {}
            thispeak["chi"] = "%d" % self.chi
            if self.ID is None:
                thispeak["id"] = hdtv.util.ID(None, self.peaks.index(peak))
            else:
                thispeak["id"] = hdtv.util.ID(self.ID.major, self.peaks.index(peak))
            thispeak["stat"] = ""
            if self.active:
                thispeak["stat"] += "A"
            if self.ID in self.spec.visible or self.ID is None:  # ID of workFit is None
                thispeak["stat"] += "V"
            # get parameter of this fit
            for p in self.fitter.peakModel.fValidParStatus.keys():
                if p == "pos":
                    # Store channel additionally to position
                    thispeak["channel"] = peak.pos
                    if "channel" not in params:
                        params.append("channel")
                # Use calibrated values of params if available
                p_cal = p + "_cal"
                if hasattr(peak, p_cal):
                    thispeak[p] = getattr(peak, p_cal)
                if p not in params:
                    params.append(p)
            # add extra params
            for p in list(peak.extras.keys()):
                thispeak[p] = peak.extras[p]
                if p not in params:
                    params.append(p)
            # Calculate normalized volume if efficiency calibration is present
            # FIXME: does this belong here?
            # if self.spec.effCal is not None:
            #    volume = thispeak["vol"]
            #    energy = thispeak["pos"]
            #    norm_volume = volume / self.spec.effCal(energy)
            #    par = "vol/eff"
            #    par_index = params.index("vol") + 1
            #    params.insert(par_index, par)
            #    thispeak[par] = norm_volume
            peaklist.append(thispeak)
        return (peaklist, params)

    def ExtractIntegralParams(self, integral_type="auto"):
        """
        Helper function for use for printing fit results in a nice table

        Return values:
            integrallist : a list of dicts for each peak in the fit
            params       : a ordered list of valid parameter names
        """
        integrallist = []
        params = ["id", "stat", "type"]

        # if not self.integral:
        #    region = [self.regionMarkers[0].p1.pos_uncal,
        #              self.regionMarkers[0].p2.pos_uncal]
        #    self.integral = hdtv.integral.Integrate(
        #        self.spec, self.fitter.bgFitter, region)
        integrals = self.integral

        if integral_type == "all":
            integral_types = ["tot", "bg", "sub"]
        elif integral_type == "auto":
            if integrals["sub"]:
                integral_types = ["sub"]
            else:
                integral_types = ["tot"]
        else:
            integral_types = [integral_type]

        for int_type, integral in integrals.items():
            if not integral or int_type not in integral_types:
                continue
            int_res = dict(integral["uncal"])

            int_res["type"] = int_type

            if self.ID is None:
                int_res["id"] = hdtv.util.ID(None, None)
            else:
                int_res["id"] = hdtv.util.ID(self.ID.major, None)
            int_res["stat"] = ""

            if self.active:
                int_res["stat"] += "A"
            if self.ID in self.spec.visible or self.ID is None:  # ID of workFit is None
                int_res["stat"] += "V"

            for p in integral["uncal"].keys():
                if p not in params:
                    params.append(p)

            if self.spec.cal:
                # rename pos to channel in uncal
                int_res["channel"] = int_res.pop("pos")
                integral.pop("cal", None)
                # Make sure that calibration is up to date
                integral["cal"] = hdtv.integral.calibrate_integral(
                    integral, self.spec.cal
                )["cal"]
                for key, value in integral["cal"].items():
                    if key == "vol":
                        continue
                    p = key if (key == "pos") else key + "_cal"
                    int_res[p] = value
                    if p not in params:
                        params.append(p)

            integrallist.append(int_res)
        return (integrallist, params)

    def ChangeMarker(self, mtype, pos, action):
        """
        Set a new marker or remove a marker.

        action : "put" or "remove"
        mtype  : "bg", "region", "peak"
        """
        self.spec = None
        markers = getattr(self, "%sMarkers" % mtype)
        if action == "set":
            markers.SetMarker(pos)
        if action == "remove":
            markers.RemoveNearest(pos)

    def FixMarkerInCal(self):
        """
        Fix marker in calibrated space
        """
        for m in [self.bgMarkers, self.regionMarkers, self.peakMarkers]:
            m.FixInCal()

    def FixMarkerInUncal(self):
        """
        Fix marker in uncalibrated space
        """
        for m in [self.bgMarkers, self.regionMarkers, self.peakMarkers]:
            m.FixInUncal()

    def _get_background_pairs(self):
        if self.bgMarkers.IsPending():
            hdtv.ui.warning("Not all background regions are closed.")
        backgrounds = Pairs()
        for m in self.bgMarkers:
            try:
                backgrounds.add(m.p1.pos_uncal, m.p2.pos_uncal)
            except AttributeError:
                pos = m.p1.pos_cal if m.p1.pos_cal else m.p2.pos_cal
                hdtv.ui.warning(
                    f"Background region at {pos:.2f} without second marker was ignored"
                )
        return backgrounds

    def FitBgFunc(self, spec=None):
        """
        Do the background fit and extract the function for display
        Note: You still need to call Draw afterwards.
        """
        if spec is not None:
            self.spec = spec
        self.Erase()
        hdtv.ui.debug("Fitting background")
        # fit background
        if len(self.bgMarkers) > 0:
            backgrounds = self._get_background_pairs()

            try:
                self.fitter.FitBackground(spec=self.spec, backgrounds=backgrounds)
                func = self.fitter.bgFitter.GetFunc()
                self.dispBgFunc = ROOT.HDTV.Display.DisplayFunc(func, hdtv.color.bg)
                self.dispBgFunc.SetCal(self.cal)
                self.bgChi = self.fitter.bgFitter.GetChisquare()
                self.bgParams = []
                nparams = self.fitter.bgFitter.GetNparams()
                for i in range(nparams):
                    self.bgParams.append(
                        ufloat(
                            self.fitter.bgFitter.GetCoeff(i),
                            self.fitter.bgFitter.GetCoeffError(i),
                        )
                    )
            except ValueError:
                raise hdtv.cmdline.HDTVCommandAbort("Background fit failed.")

    def FitPeakFunc(self, spec=None):
        """
        Do the actual peak fit and extract the functions for display
        Note: You still need to call Draw afterwards.
        """
        # Call pre hooks
        for func in Fit.FitPeakPreHooks:
            func(self)

        if spec is not None:
            self.spec = spec
        self.Erase()
        # fit background
        if len(self.bgMarkers) > 0:
            backgrounds = self._get_background_pairs()
            try:
                self.fitter.FitBackground(spec=self.spec, backgrounds=backgrounds)
            except ValueError:
                raise hdtv.cmdline.HDTVCommandAbort("Background fit failed.")
        # fit peaks
        if len(self.peakMarkers) > 0 and self.regionMarkers.IsFull():
            region = sorted(
                [self.regionMarkers[0].p1.pos_uncal, self.regionMarkers[0].p2.pos_uncal]
            )
            # remove peak marker that are outside of region
            for m in self.peakMarkers[:]:
                # we need to loop over a copy here,
                # otherwise we get out of sync after deleting items
                if m.p1.pos_uncal < region[0] or m.p1.pos_uncal > region[1]:
                    self.peakMarkers.remove(m)
            peaks = sorted(m.p1.pos_uncal for m in self.peakMarkers)
            self.fitter.FitPeaks(spec=self.spec, region=region, peaklist=peaks)
            # get background function
            self.bgParams = []
            nparams = self.fitter.backgroundModel.fParStatus["nparams"]
            if not self.fitter.bgFitter:
                for i in range(nparams):
                    self.bgParams.append(
                        ufloat(
                            self.fitter.peakFitter.GetIntBgCoeff(i),
                            self.fitter.peakFitter.GetIntBgCoeffError(i),
                        )
                    )
            else:
                # external background
                self.bgChi = self.fitter.bgFitter.GetChisquare()
                for i in range(nparams):
                    self.bgParams.append(
                        ufloat(
                            self.fitter.bgFitter.GetCoeff(i),
                            self.fitter.bgFitter.GetCoeffError(i),
                        )
                    )
            func = self.fitter.peakFitter.GetBgFunc()
            self.dispBgFunc = ROOT.HDTV.Display.DisplayFunc(func, hdtv.color.bg)
            self.dispBgFunc.SetCal(self.cal)
            # get peak function
            func = self.fitter.peakFitter.GetSumFunc()
            self.dispPeakFunc = ROOT.HDTV.Display.DisplayFunc(func, hdtv.color.region)
            self.dispPeakFunc.SetCal(self.cal)
            self.chi = self.fitter.peakFitter.GetChisquare()
            # create peak list
            for i in range(self.fitter.peakFitter.GetNumPeaks()):
                cpeak = self.fitter.peakFitter.GetPeak(i)
                peak = self.fitter.peakModel.CopyPeak(cpeak, hdtv.color.peak, self.cal)
                self.peaks.append(peak)
            # in some rare cases it can happen that peaks change position
            # while doing the fit, thus we have to sort here
            self.peaks.sort()
            # update peak markers
            for marker, peak in zip(self.peakMarkers, self.peaks):
                # Marker is fixed in uncalibrated space
                marker.p1.pos_uncal = peak.pos.nominal_value

        # Call post hooks
        for func in Fit.FitPeakPostHooks:
            func(self)

    def Restore(self, spec):
        # do not call Erase() while setting spec!
        self._spec = weakref(spec)
        self.cal = spec.cal
        self.color = spec.color
        self.FixMarkerInUncal()
        if len(self.bgMarkers) > 0 and not self.bgMarkers.IsPending():
            backgrounds = Pairs()
            for m in self.bgMarkers:
                backgrounds.add(m.p1.pos_uncal, m.p2.pos_uncal)
            self.fitter.RestoreBackground(
                backgrounds=backgrounds, params=self.bgParams, chisquare=self.bgChi
            )
        region = sorted(
            [self.regionMarkers[0].p1.pos_uncal, self.regionMarkers[0].p2.pos_uncal]
        )
        if self.peaks:
            self.fitter.RestorePeaks(
                cal=self.cal,
                region=region,
                peaks=self.peaks,
                chisquare=self.chi,
                coeffs=self.bgParams,
            )
            # get background function
            func = self.fitter.peakFitter.GetBgFunc()
            self.dispBgFunc = ROOT.HDTV.Display.DisplayFunc(func, self.color)
            self.dispBgFunc.SetCal(self.cal)
            # get peak function
            func = self.fitter.peakFitter.GetSumFunc()
            self.dispPeakFunc = ROOT.HDTV.Display.DisplayFunc(func, self.color)
            self.dispPeakFunc.SetCal(self.cal)

            # restore display functions of single peaks
            for i in range(self.fitter.peakFitter.GetNumPeaks()):
                cpeak = self.fitter.peakFitter.GetPeak(i)
                func = cpeak.GetPeakFunc()
                self.peaks[i].displayObj = ROOT.HDTV.Display.DisplayFunc(
                    func, self.color
                )
                self.peaks[i].displayObj.SetCal(self.cal)

            # create non-existant integral
            if not self.integral:
                self.integral = hdtv.integral.Integrate(
                    self.spec, self.fitter.bgFitter, region
                )

    def Draw(self, viewport):
        """
        Draw
        """
        if self.viewport and not self.viewport == viewport:
            # Unlike the Display object of the underlying implementation,
            # python objects can only be drawn on a single viewport
            raise RuntimeError("Object can only be drawn on a single viewport")
        self.viewport = viewport
        with LockViewport(self.viewport):
            # draw the markers (do this after the fit,
            # because the fit updates the position of the peak markers)
            self.peakMarkers.Draw(self.viewport)
            self.regionMarkers.Draw(self.viewport)
            self.bgMarkers.Draw(self.viewport)
            # draw fit func, if available
            if self.dispPeakFunc:
                self.dispPeakFunc.Draw(self.viewport)
            if self.dispBgFunc:
                self.dispBgFunc.Draw(self.viewport)
            # draw peaks
            for peak in self.peaks:
                peak.color = self.color
                peak.Draw(self.viewport)
            self.Show()

    def Refresh(self):
        """
        Refresh
        """
        if self.spec is None:
            return
        # repeat the fits
        if self.dispPeakFunc:
            # this includes the background fit
            self.FitPeakFunc(self.spec)
        elif self.dispBgFunc:
            # maybe there was only a background fit
            self.FitBgFunc(self.spec)
        if not self.viewport:
            return
        with LockViewport(self.viewport):
            # draw fit func, if available
            if self.dispPeakFunc:
                self.dispPeakFunc.Draw(self.viewport)
            if self.dispBgFunc:
                self.dispBgFunc.Draw(self.viewport)
            # draw peaks
            for peak in self.peaks:
                peak.Draw(self.viewport)
            # draw the markers (do this after the fit,
            # because the fit updates the position of the peak markers)
            self.peakMarkers.Refresh()
            self.regionMarkers.Refresh()
            self.bgMarkers.Refresh()
            self.Show()

    def Erase(self, bg_only=False):
        """
        Erase previous fit. NOTE: the fitter is *not* resetted
        """
        # remove bg fit
        self.dispBgFunc = None
        self.fitter.bgFitter = None
        self.bgParams = []
        self.bgChi = None
        if not bg_only:
            # remove peak fit
            self.dispPeakFunc = None
            self.peaks = []
            self.chi = None

    def ShowAsWorkFit(self):
        if not self.viewport:
            return
        with LockViewport(self.viewport):
            # all markers in active state and solid
            for mc in [self.regionMarkers, self.peakMarkers, self.bgMarkers]:
                mc.active = True
                mc.dashed = False
                mc.Show()
            # coloring
            if self.dispPeakFunc:
                self.dispPeakFunc.SetColor(hdtv.color.region)
                self.dispPeakFunc.Show()
            if self.dispBgFunc:
                self.dispBgFunc.SetColor(hdtv.color.bg)
                self.dispBgFunc.Show()
            # peak list
            for peak in self.peaks:
                peak.color = hdtv.color.peak
                if self._showDecomp:
                    peak.Show()
                else:
                    peak.Hide()

    def ShowAsPending(self):
        if not self.viewport:
            return
        with LockViewport(self.viewport):
            # all markers in passive state and dashed
            for mc in [self.regionMarkers, self.peakMarkers, self.bgMarkers]:
                mc.active = False
                mc.dashed = True
                mc.Show()
            # coloring
            if self.dispPeakFunc:
                self.dispPeakFunc.SetColor(self.color)
                self.dispPeakFunc.Show()
            if self.dispBgFunc:
                self.dispBgFunc.SetColor(self.color)
                self.dispBgFunc.Show()
            # peak list
            for peak in self.peaks:
                peak.color = self.color
                if self._showDecomp:
                    peak.Show()
                else:
                    peak.Hide()

    def ShowAsPassive(self):
        if not self.viewport:
            return
        with LockViewport(self.viewport):
            # marker in passive State and not dashed
            for mc in [self.regionMarkers, self.peakMarkers, self.bgMarkers]:
                mc.active = False
                mc.dashed = False
            # only show peakMarkers
            self.regionMarkers.Hide()
            self.peakMarkers.Show()
            self.bgMarkers.Hide()
            # coloring
            if self.dispPeakFunc:
                self.dispPeakFunc.SetColor(self.color)
                self.dispPeakFunc.Show()
            if self.dispBgFunc:
                self.dispBgFunc.SetColor(self.color)
                self.dispBgFunc.Show()
            # peak list
            for peak in self.peaks:
                peak.color = self.color
                if self._showDecomp:
                    peak.Show()
                else:
                    peak.Hide()

    def Show(self):
        if not self.viewport:
            return
        if self.active:
            if self.ID is None:
                self.ShowAsWorkFit()
            else:
                self.ShowAsPending()
        else:
            self.ShowAsPassive()

    def Hide(self):
        if not self.viewport:
            return
        with LockViewport(self.viewport):
            self.peakMarkers.Hide()
            self.regionMarkers.Hide()
            self.bgMarkers.Hide()
            if self.dispPeakFunc:
                self.dispPeakFunc.Hide()
            if self.dispBgFunc:
                self.dispBgFunc.Hide()
            for peak in self.peaks:
                peak.Hide()

    def __copy__(self):
        """
        Create new fit with identical markers
        """
        new = Fit(copy.copy(self.fitter), cal=self.cal, color=self.color)
        new.FixMarkerInCal()
        for marker in self.bgMarkers:
            new.bgMarkers.SetMarker(marker.p1.pos_cal)
            if marker.p2:
                new.bgMarkers.SetMarker(marker.p2.pos_cal)
        for marker in self.regionMarkers:
            new.regionMarkers.SetMarker(marker.p1.pos_cal)
            if marker.p2:
                new.regionMarkers.SetMarker(marker.p2.pos_cal)
        for marker in self.peakMarkers:
            new.peakMarkers.SetMarker(marker.p1.pos_cal)
            if marker.p2:
                new.peakMarkers.SetMarker(marker.p2.pos_cal)
        return new

    def __eq__(self, other):
        return self.xdimensions == other.xdimensions

    def __ne__(self, other):
        return self.xdimensions != other.xdimensions

    def __gt__(self, other):
        return self.xdimensions > other.xdimensions

    def __lt__(self, other):
        return self.xdimensions < other.xdimensions

    def __ge__(self, other):
        return self.xdimensions >= other.xdimensions

    def __le__(self, other):
        return self.xdimensions <= other.xdimensions

    @property
    def xdimensions(self):
        """
        Return dimensions of fit in x-direction

        returns: tuple (x_start, x_end)
        """
        markers = []
        # Get maximum of region markers, peak markers and peaks
        for r in self.regionMarkers:
            markers.append(r.p1.pos_cal)
            markers.append(r.p2.pos_cal)
        for p in self.peakMarkers:
            markers.append(p.p1.pos_cal)
        for p in self.peaks:
            markers.append(p.pos_cal)
        for b in self.bgMarkers:
            markers.append(b.p1.pos_cal)
            markers.append(b.p2.pos_cal)
        # calulate region limits
        if not markers:  # No markers
            return None
        else:
            x_start = min(markers)
            x_end = max(markers)
            return (x_start, x_end)

    def SetDecomp(self, stat=True):
        """
        Sets whether to display a decomposition of the fit
        """
        self._showDecomp = stat
        if stat:
            for peak in self.peaks:
                peak.Show()
        else:
            for peak in self.peaks:
                peak.Hide()
