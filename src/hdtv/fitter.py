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

import hdtv.backgroundmodels
import hdtv.peakmodels
from hdtv.util import Pairs


class Fitter:
    """
    PeakModel independent part of the Interface to the C++ Fitter
    The parts that depend on a special peak model can be found in peak.py.
    """

    def __init__(self, peakModel, backgroundModel):
        self.SetPeakModel(peakModel)
        self.SetBackgroundModel(backgroundModel)
        self.peakFitter = None
        self.bgFitter = None

    @property
    def params(self):
        params = ["background"]
        for param, valid_status in self.peakModel.fValidParStatus.items():
            if "calculated" not in valid_status:
                params.append(param)
        for param in self.peakModel.fValidOptStatus.keys():
            params.append(param)
        return params

    def __getattr__(self, name):
        # Look in peakModel for unknown attributes
        return getattr(self.peakModel, name)

    def FitBackground(self, spec, backgrounds=None):
        """
        Create Background Fitter object and do the background fit
        """
        backgrounds = backgrounds or Pairs()
        # create fitter
        self.bgFitter = self.backgroundModel.GetFitter(
            integrate=self.peakModel.GetOption("integrate"),
            likelihood=self.peakModel.GetOption("likelihood"),
            nparams=self.backgroundModel.fParStatus["nparams"],
            nbg=len(backgrounds),
        )
        if self.bgFitter is None:
            msg = "Background model %s needs at least %i background regions to execute a fit. Found %i."
            raise ValueError(msg)
        else:
            for bg in backgrounds:
                self.bgFitter.AddRegion(bg[0], bg[1])
            # do the background fit
            self.bgFitter.Fit(spec.hist.hist)

    def RestoreBackground(self, backgrounds=None, params=None, chisquare=0.0):
        """
        Create Background Fitter object and
        restore the background polynom from coeffs
        """
        backgrounds = backgrounds or Pairs()
        params = params or []
        self.bgFitter = self.backgroundModel.GetFitter(
            integrate=self.peakModel.GetOption("integrate"),
            likelihood=self.peakModel.GetOption("likelihood"),
            nparams=len(params),
            nbg=len(backgrounds),
        )
        # restore the fitter
        valueArray = ROOT.TArrayD(len(params))
        errorArray = ROOT.TArrayD(len(params))
        for i, param in enumerate(params):
            valueArray[i] = param.nominal_value
            errorArray[i] = param.std_dev
        self.bgFitter.Restore(valueArray, errorArray, chisquare)

    def FitPeaks(self, spec, region=None, peaklist=None):
        """
        Create the Peak Fitter object and do the peak fit
        """
        region = region or Pairs()
        peaklist = peaklist or []
        # create the fitter
        self.peakFitter = self.peakModel.GetFitter(region, peaklist, spec.cal)
        # Do the peak fit
        if self.bgFitter:
            # external background
            self.peakFitter.Fit(spec.hist.hist, self.bgFitter)
        else:
            # internal background
            self.peakFitter.Fit(
                spec.hist.hist, self.backgroundModel.fParStatus["nparams"]
            )

    def RestorePeaks(
        self, cal=None, region=None, peaks=None, chisquare=0.0, coeffs=None
    ):
        """
        Create the Peak Fitter object and
        restore all peaks
        """
        # create the fitter
        region = region or Pairs
        peaks = peaks or []
        coeffs = coeffs or []
        peaklist = [p.pos.nominal_value for p in peaks]
        self.peakFitter = self.peakModel.GetFitter(region, peaklist, cal)
        # restore first the fitter and afterwards the peaks
        if self.bgFitter:
            # external background
            self.peakFitter.Restore(self.bgFitter, chisquare)
        else:
            # internal background
            values = ROOT.TArrayD(self.backgroundModel.fParStatus["nparams"])
            errors = ROOT.TArrayD(self.backgroundModel.fParStatus["nparams"])
            for i in range(self.backgroundModel.fParStatus["nparams"]):
                values[i] = coeffs[i].nominal_value
                errors[i] = coeffs[i].std_dev
            self.peakFitter.Restore(values, errors, chisquare)
        if not len(peaks) == self.peakFitter.GetNumPeaks():
            raise RuntimeError("Number of peaks does not match")
        for i, peak in enumerate(peaks):
            self.peakModel.RestoreParams(peak, self.peakFitter.GetPeak(i))

    def SetPeakModel(self, model):
        """
        Sets the peak model to be used for fitting.
        Model can be either a string, in which case it is used as a key into
        the gPeakModels dictionary, or a PeakModel object.
        """
        if isinstance(model, str):
            model = hdtv.peakmodels.PeakModels[model]
        self.peakModel = model()
        self.peakFitter = None

    def SetBackgroundModel(self, model):
        """
        Sets the background model to be used for fitting.
        Model can be either a string, in which case it is used as a key into
        the gPeakModels dictionary, or a BackgroundModel object.
        """
        if isinstance(model, str):
            model = hdtv.backgroundmodels.BackgroundModels[model]
        self.backgroundModel = model()
        self.backgroundFitter = None

    def SetParameter(self, parname, status):
        """
        Sets the parameter status for fitting.
        """
        if parname == "background":
            self.backgroundModel.SetParameter("nparams", status)
        else:
            # all other parnames are treated in the peakmodel
            self.peakModel.SetParameter(parname, status)

    def __copy__(self):
        """
        Create a copy of this fitter
        This also copies the status of the corresponding peakModel,
        and hence the status of the fit parameters and options.
        """
        new = Fitter(self.peakModel.name, self.backgroundModel.name)
        new.peakModel.fParStatus = self.peakModel.fParStatus.copy()
        new.peakModel.fOptStatus = self.peakModel.fOptStatus.copy()
        new.backgroundModel.fParStatus = self.backgroundModel.fParStatus.copy()
        return new

    def __eq__(self, other):
        return (
            isinstance(other, Fitter)
            and self.peakModel.name == other.peakModel.name
            and self.backgroundModel.name == other.backgroundModel.name
            and self.peakModel.fParStatus == other.peakModel.fParStatus
            and self.peakModel.fOptStatus == other.peakModel.fOptStatus
            and self.backgroundModel.fParStatus == other.backgroundModel.fParStatus
        )
