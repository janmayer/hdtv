# -*- coding: utf-8 -*-

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

import hdtv.peakmodels
from hdtv.util import Pairs


class Fitter(object):
    """
    PeakModel independent part of the Interface to the C++ Fitter
    The parts that depend on a special peak model can be found in peak.py.
    """

    def __init__(self, peakModel, bgdeg):
        self.SetPeakModel(peakModel)
        self.bgdeg = bgdeg
        self.peakFitter = None
        self.bgFitter = None

    @property
    def params(self):
        params = ["background"]
        for param in self.peakModel.OrderedParamKeys():
            if len(self.peakModel.fValidParStatus[param]) > 1:
                params.append(param)
        return params

    def __getattr__(self, name):
        # Look in peakModell for unknown attributes
        return getattr(self.peakModel, name)

    def FitBackground(self, spec, backgrounds=Pairs()):
        """
        Create Background Fitter object and do the background fit
        """
        # create fitter
        bgfitter = ROOT.HDTV.Fit.PolyBg(self.bgdeg)
        for bg in backgrounds:
            bgfitter.AddRegion(bg[0], bg[1])
        self.bgFitter = bgfitter
        # do the background fit
        self.bgFitter.Fit(spec.hist.hist)

    def RestoreBackground(self, backgrounds=Pairs(),
                          coeffs=list(), chisquare=0.0):
        """
        Create Background Fitter object and
        restore the background polynom from coeffs
        """
        # create fitter
        bgfitter = ROOT.HDTV.Fit.PolyBg(self.bgdeg)
        for bg in backgrounds:
            bgfitter.AddRegion(bg[0], bg[1])
        self.bgFitter = bgfitter
        # restore the fitter
        valueArray = ROOT.TArrayD(len(coeffs))
        errorArray = ROOT.TArrayD(len(coeffs))
        for i, coeff in enumerate(coeffs):
            valueArray[i] = coeff.nominal_value
            errorArray[i] = coeff.std_dev
        self.bgFitter.Restore(valueArray, errorArray, chisquare)

    def FitPeaks(self, spec, region=Pairs(), peaklist=list()):
        """
        Create the Peak Fitter object and do the peak fit
        """
        # create the fitter
        self.peakFitter = self.peakModel.GetFitter(region, peaklist, spec.cal)
        # Do the fitpeak
        if self.bgFitter:
            # external background
            self.peakFitter.Fit(spec.hist.hist, self.bgFitter)
        else:
            # internal background
            self.peakFitter.Fit(spec.hist.hist, self.bgdeg)

    def RestorePeaks(self, cal=None, region=Pairs(),
                     peaks=list(), chisquare=0.0, coeffs=list()):
        """
        Create the Peak Fitter object and
        restore all peaks
        """
        # create the fitter
        peaklist = [p.pos.nominal_value for p in peaks]
        self.peakFitter = self.peakModel.GetFitter(region, peaklist, cal)
        # restore first the fitter and afterwards the peaks
        if self.bgFitter:
            # external background
            self.peakFitter.Restore(self.bgFitter, chisquare)
        else:
            # internal background
            values = ROOT.TArrayD(self.bgdeg + 1)
            errors = ROOT.TArrayD(self.bgdeg + 1)
            for i in range(0, self.bgdeg + 1):
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

    def SetParameter(self, parname, status):
        """
        Sets the parameter status for fitting.
        """
        if parname == "background":
            try:
                deg = int(status)
            except ValueError:
                try:  # HACK! 'background degree <degree>' should still be possible
                    deg = int(status.split()[1])
                except (ValueError, IndexError):
                    msg = "Failed to parse status specifier `%s'" % status
                    raise ValueError(msg)
            self.bgdeg = deg
        else:
            # all other parnames are treated in the peakmodel
            self.peakModel.SetParameter(parname, status)

    def __copy__(self):
        """
        Create a copy of this fitter
        This also copies the status of the corresponding peakModel,
        and hence the status of the fit parameters.
        """
        new = Fitter(self.peakModel.name, self.bgdeg)
        new.peakModel.fParStatus = self.peakModel.fParStatus.copy()
        return new
