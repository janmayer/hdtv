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

import math
from functools import total_ordering

import ROOT
from uncertainties import ufloat

from hdtv.drawable import Drawable

from .peak import PeakModel


@total_ordering
class TheuerkaufPeak(Drawable):
    """
    Peak object for the Theuerkauf (classic TV) fitter
    """

    def __init__(self, pos, vol, width, tl, tr, sh, sw, color=None, cal=None):
        super().__init__(color, cal)
        # values are uncalibrated!
        self.pos = pos
        self.vol = vol
        # width==fwhm (internally the C++ fitter uses sigma)
        self.width = width
        self.tl = tl
        self.tr = tr
        self.sh = sh
        self.sw = sw
        # dictionary for storing additional user supplied values
        self.extras = {}

    def __getattr__(self, name):
        """
        calculate calibrated values on the fly for pos and width
        """
        if name == "pos_cal":
            if self.cal is None:
                return self.pos
            pos_uncal = self.pos.nominal_value
            pos_err_uncal = self.pos.std_dev
            pos_cal = self.cal.Ch2E(pos_uncal)
            pos_err_cal = abs(self.cal.dEdCh(pos_uncal) * pos_err_uncal)
            return ufloat(pos_cal, pos_err_cal, self.pos.tag)
        elif name == "width_cal":
            if self.cal is None:
                return self.width
            pos_uncal = self.pos.nominal_value
            hwhm_uncal = self.width.nominal_value / 2
            width_err_uncal = self.width.std_dev
            width_cal = self.cal.Ch2E(pos_uncal + hwhm_uncal) - self.cal.Ch2E(
                pos_uncal - hwhm_uncal
            )
            # This is only an approximation, valid as d(width_cal)/d(pos_uncal) \approx 0
            #  (which is true for Ch2E \approx linear)
            width_err_cal = abs(
                (
                    self.cal.dEdCh(pos_uncal + hwhm_uncal) / 2.0
                    + self.cal.dEdCh(pos_uncal - hwhm_uncal) / 2.0
                )
                * width_err_uncal
            )
            return ufloat(width_cal, width_err_cal, self.width.tag)
        elif name in ["vol_cal", "tl_cal", "tr_cal", "sh_cal", "sw_cal"]:
            name = name[0 : name.rfind("_cal")]
            return getattr(self, name)
        else:
            # DON'T FORGET THIS LINE! see
            # http://code.activestate.com/recipes/52238/
            raise AttributeError(name)

    def __str__(self):
        return self.formatted_str(verbose=False)

    def formatted_str(self, verbose=False):
        """
        print the properties of this peak in a nicely formatted way
        """
        text = ""
        if verbose:
            text += "Pos:         {0.pos_cal:S}\n"
            text += "Channel:     {0.pos:S}\n"
            text += "Volume:      {0.vol:S}\n"
            text += "FWHM:        {0.width_cal:S}\n"
            if self.tl is not None:
                text += "Left Tail:   {0.tl:S}\n"
            else:
                text += "Left Tail:   None\n"
            if self.tr is not None:
                text += "Right Tail:  {0.tr:S}\n"
            else:
                text += "Right Tail:  None\n"
            if self.sh is not None:
                text += "Step height: {0.sh:S}\n"
                text += "Step width:  {0.sw:S}\n"
            else:
                text += "Step:        None"
        else:
            text += "Peak@ {0.pos_cal}"
        return text.format(self)

    def __eq__(self, other):
        return (self.pos, self.vol, self.width, self.tl, self.tr, self.sh, self.sw) == (
            other.pos,
            other.vol,
            other.width,
            other.tl,
            other.tr,
            other.sh,
            other.sw,
        )

    def __ne__(self, other):
        return not (
            (self.pos, self.vol, self.width, self.tl, self.tr, self.sh, self.sw)
            == (
                other.pos,
                other.vol,
                other.width,
                other.tl,
                other.tr,
                other.sh,
                other.sw,
            )
        )

    def __lt__(self, other):
        return self.pos.nominal_value < other.pos.nominal_value

    def Draw(self, viewport):
        """
        Draw the function of this peak
        """
        if self.viewport:
            if self.viewport == viewport:
                self.Show()
            else:
                # Unlike the Display object of the underlying implementation,
                # python objects can only be drawn on a single viewport
                raise RuntimeError("Peak cannot be drawn on multiple viewports")
        self.viewport = viewport
        if self.displayObj:
            self.displayObj.Draw(self.viewport)


class PeakModelTheuerkauf(PeakModel):
    """
    Theuerkauf peak model - "classical" model used by tv
    """

    def __init__(self):
        super().__init__()
        self.fParStatus = {
            "pos": None,
            "vol": None,
            "width": None,
            "tl": None,
            "tr": None,
            "sh": None,
            "sw": None,
        }
        self.fValidParStatus = {
            "pos": [float, "free", "hold"],
            "vol": [float, "free", "hold"],
            "width": [float, "free", "equal"],
            "tl": [float, "free", "equal", "none"],
            "tr": [float, "free", "equal", "none"],
            "sh": [float, "free", "equal", "none"],
            "sw": [float, "free", "equal", "hold"],
        }
        self.fOptStatus = {
            "integrate": False,
            "likelihood": "normal",
            "onlypositivepeaks": False,
        }
        self.fValidOptStatus = {
            "integrate": [False, True],
            "likelihood": ["normal", "poisson"],
            "onlypositivepeaks": [False, True],
        }

        self.ResetParamStatus()
        self.Peak = TheuerkaufPeak
        self.name = "theuerkauf"

    def CopyPeak(self, cpeak, color=None, cal=None):
        """
        create a python peak object from C++ peak object
        """
        # get values from C++ object (uncalibrated)
        pos_uncal = cpeak.GetPos()
        pos_err_uncal = cpeak.GetPosError()
        # width==fwhm (internally the C++ fitter uses sigma)
        width_uncal = cpeak.GetSigma() * 2.0 * math.sqrt(2.0 * math.log(2.0))
        width_err_uncal = cpeak.GetSigmaError() * 2.0 * math.sqrt(2.0 * math.log(2.0))
        # create ufloats from this
        pos = ufloat(pos_uncal, pos_err_uncal, cpeak.PosIsFree())
        vol = ufloat(cpeak.GetVol(), cpeak.GetVolError(), cpeak.VolIsFree())
        width = ufloat(width_uncal, width_err_uncal, cpeak.SigmaIsFree())
        # optional parameters
        if cpeak.HasLeftTail():
            tl = ufloat(
                cpeak.GetLeftTail(), cpeak.GetLeftTailError(), cpeak.LeftTailIsFree()
            )
        else:
            tl = None
        if cpeak.HasRightTail():
            tr = ufloat(
                cpeak.GetRightTail(), cpeak.GetRightTailError(), cpeak.RightTailIsFree()
            )
        else:
            tr = None
        if cpeak.HasStep():
            sh = ufloat(
                cpeak.GetStepHeight(),
                cpeak.GetStepHeightError(),
                cpeak.StepHeightIsFree(),
            )
            sw = ufloat(
                cpeak.GetStepWidth(), cpeak.GetStepWidthError(), cpeak.StepWidthIsFree()
            )
        else:
            sh = sw = None
        # create peak object
        peak = self.Peak(pos, vol, width, tl, tr, sh, sw, color, cal)
        func = cpeak.GetPeakFunc()
        peak.displayObj = ROOT.HDTV.Display.DisplayFunc(func, color)
        peak.displayObj.SetCal(cal)
        return peak

    def RestoreParams(self, peak, cpeak):
        """
        Restore the params of a C++ peak object using a python peak object
        """
        cpeak.RestorePos(peak.pos.nominal_value, peak.pos.std_dev)
        cpeak.RestoreVol(peak.vol.nominal_value, peak.vol.std_dev)
        # internally the C++ fitter uses sigma
        sigma = peak.width.nominal_value / (2.0 * math.sqrt(2.0 * math.log(2.0)))
        sigma_err = peak.width.std_dev / (2.0 * math.sqrt(2.0 * math.log(2.0)))
        cpeak.RestoreSigma(sigma, sigma_err)
        if peak.tl:
            cpeak.RestoreLeftTail(peak.tl.nominal_value, peak.tl.std_dev)
        if peak.tr:
            cpeak.RestoreRightTail(peak.tr.nominal_value, peak.tr.std_dev)
        if peak.sh:
            cpeak.RestoreStepHeight(peak.sh.nominal_value, peak.sh.std_dev)
            cpeak.RestoreStepWidth(peak.sw.nominal_value, peak.sw.std_dev)

    def ResetParamStatus(self):
        """
        Reset parameter status to defaults
        """
        self.fParStatus["pos"] = "free"
        self.fParStatus["vol"] = "free"
        self.fParStatus["width"] = "equal"
        self.fParStatus["tl"] = "none"
        self.fParStatus["tr"] = "none"
        self.fParStatus["sh"] = "none"
        self.fParStatus["sw"] = "hold"
        self.fOptStatus["integrate"] = False
        self.fOptStatus["likelihood"] = "normal"
        self.fOptStatus["onlypositivepeaks"] = False

    def Uncal(self, parname, value, pos_uncal, cal):
        """
        Convert a value from calibrated (spectrum) to uncalibrated (fitter) units
        This is needed, when a value is hold to a specific calibrated value.
        """
        if parname == "pos":
            return cal.E2Ch(value)
        elif parname == "width":
            pos_cal = cal.Ch2E(pos_uncal)
            width_uncal = cal.E2Ch(pos_cal + value / 2.0) - cal.E2Ch(
                pos_cal - value / 2.0
            )
            # Note that the underlying fitter uses ``sigma'' as a parameter
            #  (see HDTV technical documentation in the wiki)
            return width_uncal / (2.0 * math.sqrt(2.0 * math.log(2.0)))
        elif parname in ("vol", "tl", "tr", "sh", "sw"):
            return value
        else:
            raise RuntimeError("Unexpected parameter name")

    def GetFitter(self, region, peaklist, cal):
        """
        Creates a C++ Fitter object, which can then do the real work
        """
        # Define a fitter and a region
        # FIXME: show_inipar seems to create a crash, see ticket #103 for trace
        # debug_show_inipar = hdtv.options.Get("__debug__.fit.show_inipar")
        # self.fFitter = ROOT.HDTV.Fit.TheuerkaufFitter(region[0],region[1],debug_show_inipar)
        integrate = self.GetOption("integrate")
        likelihood = self.GetOption("likelihood")
        onlypositivepeaks = self.GetOption("onlypositivepeaks")
        self.fFitter = ROOT.HDTV.Fit.TheuerkaufFitter(
            region[0], region[1], integrate, likelihood, onlypositivepeaks
        )
        self.ResetGlobalParams()
        # Check if enough values are provided in case of per-peak parameters
        #  (the function raises a RuntimeError if the check fails)
        self.CheckParStatusLen(len(peaklist))

        # Copy peaks to the fitter
        for pid in range(len(peaklist)):
            pos_uncal = peaklist[pid]

            pos = self.GetParam("pos", pid, pos_uncal, cal, pos_uncal)
            vol = self.GetParam("vol", pid, pos_uncal, cal)
            sigma = self.GetParam("width", pid, pos_uncal, cal)
            tl = self.GetParam("tl", pid, pos_uncal, cal)
            tr = self.GetParam("tr", pid, pos_uncal, cal)
            sh = self.GetParam("sh", pid, pos_uncal, cal)
            sw = self.GetParam("sw", pid, pos_uncal, cal)

            cpeak = ROOT.HDTV.Fit.TheuerkaufPeak(pos, vol, sigma, tl, tr, sh, sw)
            self.fFitter.AddPeak(cpeak)

        return self.fFitter
