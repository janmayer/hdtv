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

import fnmatch
import re
from array import array
from html import escape

import ROOT

import hdtv.options
import hdtv.rootext.calibration
import hdtv.util


class PositionCalibrationDict(dict):
    """
    Dict subclass that stores position calibrations

    Subclasses dict overwriting get() and providing __missing__() and a user config option to enable calibration lookups based on glob or regex matching of dict keys to lookup key.
    Note that in all modes a literally matching dict key is always preferred to globs/regex.
    Note that other methods like __contains__() are not overwritten on purpose, so use "key in dict" to check for literally existing keys and dict[key] or get() to check for glob/regex matching keys.
    """

    calListSpecNameMatching = hdtv.options.Option(
        default="glob", parse=hdtv.options.parse_choices(["literal", "glob", "regex"])
    )
    hdtv.options.RegisterOption(
        "calibration.position.list.spec_name_matching", calListSpecNameMatching
    )

    def __missing__(self, key):
        matchMode = self.calListSpecNameMatching.Get()
        if matchMode == "glob":
            for dictKey, val in self.items():
                if fnmatch.fnmatch(key, dictKey):
                    return val
        elif matchMode == "regex":
            for dictKey, val in self.items():
                if re.fullmatch(dictKey, key):
                    return val
        raise KeyError(key)

    def get(self, key, default=None):
        """
        Return the value for key if key is in the dictionary, else the value of a glob/regex (if enabled) matching key, else default.
        """
        try:
            return self[key]
        except KeyError:
            return default


def MakeCalibration(cal):
    """
    Create a ROOT.HDTV.Calibration object from a python list
    """
    if not isinstance(cal, ROOT.HDTV.Calibration):
        if cal is None:
            cal = []  # Trivial calibration, degree -1
        calarray = ROOT.TArrayD(len(cal))
        for i, c in enumerate(cal):
            calarray[i] = c
        # create the calibration object
        cal = ROOT.HDTV.Calibration(calarray)
    return cal


def GetCoeffs(cal):
    """
    Get the list of calibration coeffs from the ROOT.HDTV.Calibration object
    """
    return list(cal.GetCoeffs())


def PrintCal(cal):
    """
    Get the calibration as string
    """
    return "   ".join([str(c) for c in GetCoeffs(cal)])


class CalibrationFitter:
    """
    Fit a calibration polynom to a list of channel/energy pairs.
    """

    def __init__(self):
        self.Reset()

    def Reset(self):
        self.pairs = []
        self.calib = None
        self.chi2 = None
        self.__TF1 = None
        self.__TF1_id = None
        self.graph = ROOT.TGraph()

    def AddPair(self, ch, e):
        self.pairs.append([ch, e])

    def FitCal(self, degree, ignore_errors=False):
        """
        Use the reference peaks found in the histogram to fit the actual
        calibration function.
        If degree == 0, the linear coefficient of the polynomial is fixed at 1.

        If self.pairs contains ufloats the channel std_dev is respected
        """
        hdtv.ui.debug("conducting calibration from fitted peaks")
        if degree < 0:
            raise ValueError("Degree cannot be negative")

        if len(self.pairs) < degree + 1:
            raise RuntimeError(
                "You must specify at least as many channel/energy pairs as there are free parameters"
            )

        self.__TF1_id = "calfitter_" + hex(id(self))  # unique function ID

        # Create ROOT function
        if degree == 0:
            self.__TF1 = ROOT.TF1(self.__TF1_id, "pol1", 0, 0)
            self.__TF1.FixParameter(1, 1.0)
            degree = 1
        else:
            self.__TF1 = ROOT.TF1(self.__TF1_id, "pol%d" % degree, 0, 0)

        # Prepare data for fitter
        channels = array("d")
        channels_err = array("d")
        energies = array("d")
        energies_err = array("d")
        all_have_error = True
        any_has_error = False
        any_has_xerror = False

        for ch, e in self.pairs:
            has_xerror = False
            has_error = False

            # Store channels
            try:  # try to read from ufloat
                channel = float(ch.nominal_value)
                channel_err = float(ch.std_dev)
                channels.append(channel)
                channels_err.append(channel_err)
                if ch.std_dev != 0.0:
                    has_xerror = True
            except AttributeError:
                channels.append(float(ch))
                channels_err.append(0.0)

            any_has_xerror = has_xerror or any_has_xerror

            # Store energies
            try:  # try to read from ufloat
                energy = float(e.nominal_value)
                energy_err = float(e.std_dev)
                energies.append(energy)
                energies_err.append(energy_err)
                if e.std_dev != 0.0:
                    has_error = True
            except AttributeError:
                energies.append(float(e))
                energies_err.append(0.0)

            all_have_error = all_have_error and has_error
            any_has_error = any_has_error or has_error

        hdtv.ui.debug("all_have_error: " + str(all_have_error), level=2)
        hdtv.ui.debug("any_has_error: " + str(any_has_error), level=2)
        hdtv.ui.debug("any_has_xerror: " + str(any_has_xerror), level=2)

        hdtv.ui.debug("channels: " + str(channels), level=5)
        hdtv.ui.debug("channels err: " + str(channels_err), level=5)
        hdtv.ui.debug("energies: " + str(energies), level=5)
        hdtv.ui.debug("energies err: " + str(energies_err), level=5)

        self.__TF1.SetRange(0, max(energies) * 1.1)
        self.TGraph = ROOT.TGraphErrors(
            len(energies), channels, energies, channels_err, energies_err
        )

        fitoptions = "0"  # Do not plot
        fitoptions += "Q"  # Quiet
        fitoptions += "S"  # Return TFitResult for new ROOT versions

        if not ignore_errors and not all_have_error:
            ignore_errors = True
            if any_has_error:
                hdtv.ui.warning(
                    "Some values specified without error, ignoring all errors in fit"
                )

        if ignore_errors:
            fitoptions += "W"
        else:
            hdtv.ui.info("doing error-weighted fit")
            if any_has_xerror:
                # We must use the iterative fitter (minuit) to take x errors
                # into account.
                fitoptions += "F"
                hdtv.ui.info(
                    "switching to non-linear fitter (minuit) for x error weighting"
                )

        # Do the fit
        result = self.TGraph.Fit(self.__TF1_id, fitoptions)
        if isinstance(result, int):
            if result != 0:
                raise RuntimeError("Fit failed")
        elif isinstance(result, ROOT.TFitResultPtr):
            if result.Get().Status() != 0:
                raise RuntimeError("Fit failed")
        else:  # Fallback, attempt to cast result to an int
            if int(result) != 0:
                raise RuntimeError("Fit failed")

        # Save the fit result
        self.calib = MakeCalibration(
            [self.__TF1.GetParameter(i) for i in range(degree + 1)]
        )
        self.chi2 = self.__TF1.GetChisquare()

    def ResultStr(self):
        """
        Return string describing the result of the calibration
        """
        if self.calib is None:
            raise RuntimeError("No calibration available (did you call FitCal()?)")

        s = "<b>Calibration</b>: "
        s += " ".join([escape("%.6e") % x for x in self.calib.GetCoeffs()])
        s += "\n<b>Chi²</b>: %.4f" % self.chi2

        return s

    def ResultTable(self):
        """
        Return a table showing the fit results
        """
        if self.calib is None:
            raise RuntimeError("No calibration available (did you call FitCal()?)")

        header = ["Channel", "E_given", "E_fit", "Residual"]
        keys = "channel", "e_given", "e_fit", "residual"
        tabledata = []

        for ch, e_given in self.pairs:
            tableline = {}
            e_fit = self.calib.Ch2E(ch.nominal_value)
            residual = e_given - e_fit

            tableline["channel"] = "%10.2f" % ch.nominal_value
            tableline["e_given"] = "%10.2f" % e_given.nominal_value
            tableline["e_fit"] = "%10.2f" % e_fit
            tableline["residual"] = "%10.2f" % residual.nominal_value
            tabledata.append(tableline)

        return hdtv.util.Table(tabledata, keys, header=header, sortBy="channel")

    def DrawCalFit(self):
        """
        Draw fit used for calibration
        """
        if self.calib is None:
            raise RuntimeError("No calibration available (did you call FitCal()?)")

        canvas = ROOT.TCanvas("CalFit", "Calibration Fit")
        # Prevent canvas from being closed as soon as this function finishes
        ROOT.SetOwnership(canvas, False)

        min_ch = self.pairs[0][0].nominal_value
        max_ch = self.pairs[0][0].nominal_value
        graph = ROOT.TGraphErrors(len(self.pairs))
        ROOT.SetOwnership(graph, False)

        i = 0
        for ch, e in self.pairs:
            min_ch = min(min_ch, ch.nominal_value)
            max_ch = max(max_ch, ch.nominal_value)

            try:
                graph.SetPoint(i, ch.nominal_value, e.nominal_value)
            except Exception:
                graph.SetPoint(i, ch.nominal_value, e)
            graph.SetPointError(i, ch.std_dev, 0)
            i += 1

        coeffs = self.calib.GetCoeffs()
        func = ROOT.TF1("CalFitFunc", "pol%d" % (len(coeffs) - 1), min_ch, max_ch)
        ROOT.SetOwnership(func, False)
        for i, coeff in enumerate(coeffs):
            func.SetParameter(i, coeff)

        graph.SetTitle("Calibration Fit")
        graph.GetXaxis().SetTitle("Channel")
        graph.GetXaxis().CenterTitle()
        graph.GetYaxis().SetTitle("Energy")
        graph.GetYaxis().CenterTitle()

        graph.Draw("A*")
        func.Draw("SAME")
        canvas.Update()

    def DrawCalResidual(self):
        """
        Debug: draw residual of fit used for calibration
        """
        if self.calib is None:
            raise RuntimeError("No calibration available (did you call FitCal()?)")

        canvas = ROOT.TCanvas("CalResidual", "Calibration Residual")
        # Prevent canvas from being closed as soon as this function finishes
        ROOT.SetOwnership(canvas, False)

        min_ch = self.pairs[0][0].nominal_value
        max_ch = self.pairs[0][0].nominal_value
        graph = ROOT.TGraph(len(self.pairs))
        ROOT.SetOwnership(graph, False)

        i = 0
        for ch, e in self.pairs:
            min_ch = min(min_ch, ch.nominal_value)
            max_ch = max(max_ch, ch.nominal_value)
            try:
                # energie may be ufloat
                e = e.nominal_value
            except Exception:
                pass

            graph.SetPoint(i, ch.nominal_value, e - self.calib.Ch2E(ch.nominal_value))
            i += 1

        nullfunc = ROOT.TF1("CalResidualFunc", "pol0", min_ch, max_ch)
        ROOT.SetOwnership(nullfunc, False)

        graph.SetTitle("Residual of calibration fit")
        graph.GetXaxis().SetTitle("Channel")
        graph.GetXaxis().CenterTitle()
        graph.GetYaxis().SetTitle("Energy difference")
        graph.GetYaxis().CenterTitle()

        graph.Draw("A*")
        nullfunc.Draw("SAME")
        canvas.Update()
