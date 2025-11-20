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

"""
Peak Model for electron-electron scattering
Implementation requested by Oleksiy Burda <burda@ikp.tu-darmstadt.de>
"""

import ROOT
from uncertainties import ufloat

from hdtv.drawable import Drawable

from .peak import PeakModel


class EEPeak(Drawable):
    """
    Peak object for the ee fitter
    """

    def __init__(self, pos, amp, sigma1, sigma2, eta, gamma, vol, color=None, cal=None):
        super().__init__(color, cal)
        self.pos = pos
        self.amp = amp
        self.sigma1 = sigma1
        self.sigma2 = sigma2
        self.eta = eta
        self.gamma = gamma
        # vol is not a fit parameter, but rather the result of the fit
        self.vol = vol
        # dictionary for storing additional user supplied values
        self.extras = {}

    def __getattr__(self, name):
        """
        calculate calibrated values on the fly for pos, sigma1 and sigma2
        """
        if name == "pos_cal":
            if self.cal is None:
                return self.pos
            pos_uncal = self.pos.nominal_value
            pos_err_uncal = self.pos.std_dev
            pos_cal = self.cal.Ch2E(pos_uncal)
            pos_err_cal = abs(self.cal.dEdCh(pos_uncal) * pos_err_uncal)
            return ufloat(pos_cal, pos_err_cal)
        elif name == "sigma1_cal":
            if self.cal is None:
                return self.sigma1
            pos_uncal = self.pos.nominal_value
            sigma1_uncal = self.sigma1.nominal_value
            sigma1_err_uncal = self.sigma1.std_dev
            sigma1_cal = self.cal.Ch2E(pos_uncal) - self.cal.Ch2E(
                pos_uncal - sigma1_uncal
            )
            # This is only an approximation, valid as d(fwhm_cal)/d(pos_uncal) \approx 0
            #  (which is true for Ch2E \approx linear)
            sigma1_err_cal = abs(
                self.cal.dEdCh(pos_uncal - sigma1_uncal) * sigma1_err_uncal
            )
            return ufloat(sigma1_cal, sigma1_err_cal)
        elif name == "sigma2_cal":
            if self.cal is None:
                return self.sigma2
            pos_uncal = self.pos.nominal_value
            sigma2_uncal = self.sigma2.nominal_value
            sigma2_err_uncal = self.sigma2.std_dev
            sigma2_cal = self.cal.Ch2E(pos_uncal) - self.cal.Ch2E(
                pos_uncal - sigma2_uncal
            )
            # This is only an approximation, valid as d(fwhm_cal)/d(pos_uncal) \approx 0
            #  (which is true for Ch2E \approx linear)
            sigma2_err_cal = abs(
                self.cal.dEdCh(pos_uncal - sigma2_uncal) * sigma2_err_uncal
            )
            return ufloat(sigma2_cal, sigma2_err_cal)
        elif name in ["amp_cal", "eta_cal", "gamma_cal", "vol_cal"]:
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
        formatted printing of all attributes
        """
        text = ""
        if verbose:
            text += (
                f"Pos:         {self.pos_cal:S}\n"
                f"Channel:     {self.pos:S}\n"
                f"Amp:         {self.amp:S}\n"
                f"Sigma1:      {self.sigma1:S}\n"
                f"Sigma2:      {self.sigma2:S}\n"
                f"Eta:         {self.eta:S}\n"
                f"Gamma:       {self.gamma:S}\n"
                f"Volume:      {self.vol:S}"
            )
        else:
            text += f"Peak@ {self.pos_cal:S}"
        return text

    def __eq__(self, other):
        return self.pos.nominal_value == other.pos.nominal_value

    def __ne__(self, other):
        return self.pos.nominal_value != other.pos.nominal_value

    def __gt__(self, other):
        return self.pos.nominal_value > other.pos.nominal_value

    def __lt__(self, other):
        return self.pos.nominal_value < other.pos.nominal_value

    def __ge__(self, other):
        return self.pos.nominal_value >= other.pos.nominal_value

    def __le__(self, other):
        return self.pos.nominal_value <= other.pos.nominal_value

    def Draw(self, viewport):
        """
        Draw the function of this peak
        """
        if self.viewport:
            if self.viewport == viewport:
                # this has already been drawn
                self.Show()
                return
            else:
                # Unlike the Display object of the underlying implementation,
                # python objects can only be drawn on a single viewport
                raise RuntimeError("Peak cannot be drawn on multiple viewports")
        self.viewport = viewport
        if self.displayObj:
            self.displayObj.Draw(self.viewport)


class PeakModelEE(PeakModel):
    """
    Peak model for electron-electron scattering
    """

    def __init__(self):
        super().__init__()
        self.fParStatus = {
            "pos": None,
            "amp": None,
            "sigma1": None,
            "sigma2": None,
            "eta": None,
            "gamma": None,
            "vol": None,
        }
        # Note that volume is not a true fit parameter, but calculated from
        # the other parameters after the fit
        self.fValidParStatus = {
            "pos": [float, "free", "hold"],
            "amp": [float, "free", "hold"],
            "sigma1": [float, "free", "equal"],
            "sigma2": [float, "free", "equal"],
            "eta": [float, "free", "equal"],
            "gamma": [float, "free", "equal"],
            "vol": ["calculated"],
        }
        self.fOptStatus = {
            "integrate": False,
            "likelihood": "normal",
        }
        self.fValidOptStatus = {
            "integrate": [False, True],
            "likelihood": ["normal", "poisson"],
        }

        self.ResetParamStatus()
        self.name = "ee"
        self.Peak = EEPeak

    def CopyPeak(self, cpeak, color=None, cal=None):
        """
        Copies peak data from a C++ peak class to a Python class
        """
        pos = ufloat(cpeak.GetPos(), cpeak.GetPosError())
        amp = ufloat(cpeak.GetAmp(), cpeak.GetAmpError())
        sigma1 = ufloat(cpeak.GetSigma1(), cpeak.GetSigma1Error())
        sigma2 = ufloat(cpeak.GetSigma2(), cpeak.GetSigma2Error())
        eta = ufloat(cpeak.GetEta(), cpeak.GetEtaError())
        # Triage a bug where error of eta is exceptionally small
        if eta.std_dev / eta.nominal_value < 1e-10:
            eta.std_dev = 0
        gamma = ufloat(cpeak.GetGamma(), cpeak.GetGammaError())
        vol = ufloat(cpeak.GetVol(), cpeak.GetVolError())
        # create the peak object
        peak = self.Peak(pos, amp, sigma1, sigma2, eta, gamma, vol)
        func = cpeak.GetPeakFunc()
        peak.displayObj = ROOT.HDTV.Display.DisplayFunc(func, color)
        peak.displayObj.SetCal(cal)
        return peak

    def RestoreParams(self, peak, cpeak):
        """
        Restore the params of a C++ peak object using a python peak object
        """
        cpeak.RestorePos(peak.pos.nominal_value, peak.pos.std_dev)
        cpeak.RestoreAmp(peak.amp.nominal_value, peak.amp.std_dev)
        cpeak.RestoreSigma1(peak.sigma1.nominal_value, peak.sigma1.std_dev)
        cpeak.RestoreSigma2(peak.sigma2.nominal_value, peak.sigma2.std_dev)
        cpeak.RestoreEta(peak.eta.nominal_value, peak.eta.std_dev)
        cpeak.RestoreGamma(peak.gamma.nominal_value, peak.gamma.std_dev)
        cpeak.RestoreVol(peak.vol.nominal_value, peak.vol.std_dev)

    def ResetParamStatus(self):
        """
        Reset parameter status to defaults
        """
        self.fParStatus["pos"] = "free"
        self.fParStatus["amp"] = "free"
        self.fParStatus["sigma1"] = "equal"
        self.fParStatus["sigma2"] = "equal"
        self.fParStatus["eta"] = "equal"
        self.fParStatus["gamma"] = "equal"
        self.fParStatus["vol"] = "calculated"
        self.fOptStatus["integrate"] = False
        self.fOptStatus["likelihood"] = "normal"

    def Uncal(self, parname, value, pos_uncal, cal):
        """
        Convert a value from calibrated to uncalibrated units
        This is needed, when a value is hold to a specific calibrated value.
        """
        if parname == "pos":
            return cal.E2Ch(value)
        elif parname == "sigma1":
            pos_cal = cal.Ch2E(pos_uncal)
            left_hwhm_uncal = pos_uncal - cal.E2Ch(pos_cal - value)
            return left_hwhm_uncal
        elif parname == "sigma2":
            pos_cal = cal.Ch2E(pos_uncal)
            right_hwhm_uncal = cal.E2Ch(pos_cal + value) - pos_uncal
            return right_hwhm_uncal
        elif parname in ("amp", "eta", "gamma"):
            return value
        else:
            raise RuntimeError("Unexpected parameter name")

    def GetFitter(self, region, peaklist, cal):
        """
        Creates a C++ Fitter object, which can then do the real work
        """

        integrate = self.GetOption("integrate")
        likelihood = self.GetOption("likelihood")
        self.fFitter = ROOT.HDTV.Fit.EEFitter(
            region[0], region[1], integrate, likelihood
        )

        self.ResetGlobalParams()

        # Check if enough values are provided in case of per-peak parameters
        #  (the function raises a RuntimeError if the check fails)
        self.CheckParStatusLen(len(peaklist))

        for pid in range(len(peaklist)):
            pos_uncal = peaklist[pid]

            pos = self.GetParam("pos", pid, pos_uncal, cal, pos_uncal)
            amp = self.GetParam("amp", pid, pos_uncal, cal)
            sigma1 = self.GetParam("sigma1", pid, pos_uncal, cal)
            sigma2 = self.GetParam("sigma2", pid, pos_uncal, cal)
            eta = self.GetParam("eta", pid, pos_uncal, cal)
            gamma = self.GetParam("gamma", pid, pos_uncal, cal)

            peak = ROOT.HDTV.Fit.EEPeak(pos, amp, sigma1, sigma2, eta, gamma)
            self.fFitter.AddPeak(peak)

        return self.fFitter
