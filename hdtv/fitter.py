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
import dlmgr
dlmgr.LoadLibrary("fit")

import hdtv.peakmodels

class Fitter:
    """
    PeakModel independent part of the Interface to the C++ Fitter
    The parts that depend on a special peak model can be found in peak.py.
    """
    def __init__(self, peakModel, bgdeg):
        self.SetPeakModel(peakModel)
        self.bgdeg = bgdeg
        self.spec = None
        self.peakFitter = None
        self.bgFitter = None
        # degree of internal background , used when no background is set
        self.intBgDeg = 0 
    
    @property
    def params(self):
        params = ["background"]
        for param in self.peakModel.OrderedParamKeys():
            if len(self.peakModel.fValidParStatus[param])>1:
                params.append(param)
        return params
    
    def __getattr__(self, name):
        # Look in peakModell for unknown attributes
        return getattr(self.peakModel, name)

    def FitBackground(self, spec, backgrounds):
        """
        Create Background Fitter object and do the background fit
        """
        self.spec = spec
        # create fitter
        bgfitter = ROOT.HDTV.Fit.PolyBg(self.bgdeg)
        for bg in backgrounds:
            # convert to uncalibrated values and add to fitter
            bgfitter.AddRegion(spec.cal.E2Ch(bg[0]), spec.cal.E2Ch(bg[1]))
        self.bgFitter = bgfitter
        # do the background fit
        self.bgFitter.Fit(spec.fHist)

    def RestoreBackground(self, spec, backgrounds, coeffs, chisquare):
        """
        Create Background Fitter object and 
        restore the background polynom from coeffs
        """
        self.spec = spec
        # create fitter
        bgfitter = ROOT.HDTV.Fit.PolyBg(self.bgdeg)
        for bg in backgrounds:
            # convert to uncalibrated values and add to fitter
            bgfitter.AddRegion(spec.cal.E2Ch(bg[0]), spec.cal.E2Ch(bg[1]))
        self.bgFitter = bgfitter
        # restore the fitter
        valueArray = ROOT.TArrayD(len(coeffs))
        errorArray = ROOT.TArrayD(len(coeffs))
        for i in range(0, len(coeffs)): 
            valueArray[i] = coeffs[i].value
            errorArray[i] = coeffs[i].error
        self.bgFitter.Restore(valueArray, errorArray, chisquare)

    def FitPeaks(self, spec, region, peaklist):
        """
        Create the Peak Fitter object and do the peak fit
        """
        self.spec = spec
        # convert to uncalibrated values
        region = [spec.cal.E2Ch(r) for r in region]
        peaklist = [spec.cal.E2Ch(p) for p in peaklist]
        # create the fitter
        self.peakFitter = self.peakModel.GetFitter(region, peaklist, spec.cal)
        # Do the fitpeak
        if self.bgFitter:
            # external background
            self.peakFitter.Fit(self.spec.fHist, self.bgFitter)
        else:
            # internal background
            self.peakFitter.Fit(self.spec.fHist, self.intBgDeg)
        
    def RestorePeaks(self, spec, region, peaks, chisquare):
        """
        Create the Peak Fitter object and 
        restore all peaks
        """
        self.spec = spec
        # convert to uncalibrated values
        region = [spec.cal.E2Ch(r) for r in region]
        # peak.pos is already uncalibrated
        peaklist = [p.pos.value for p in peaks]
        # create the fitter
        self.peakFitter = self.peakModel.GetFitter(region, peaklist, spec.cal)
        # restore first the fitter and afterwards the peaks
        if self.bgFitter:
            # external background
            self.peakFitter.Restore(self.bgFitter, chisquare)
        else:
            # internal background
            self.peakFitter.Restore(self.intBgDeg, chisquare)
        if not len(peaks)==self.peakFitter.GetNumPeaks():
            raise RuntimeError, "Number of peaks does not match"
        for i in range(0,len(peaks)):
            cpeak = self.peakFitter.GetPeak(i)
            peak = peaks[i]
            self.peakModel.RestoreParams(peak, cpeak)

    def SetPeakModel(self, model):
        """
        Sets the peak model to be used for fitting. 
        Model can be either a string, in which case it is used as a key into 
        the gPeakModels dictionary, or a PeakModel object.
        """
        if type(model) == str:
            model = hdtv.peakmodels.PeakModels[model]
        self.peakModel = model()
        self.peakFitter = None
        
    def SetParameter(self, parname, status):
        """
        Sets the parameter status for fitting.
        """
        if parname=="background":
            try:
                deg = int(status)
            except ValueError:
                try: # HACK! 'background degree <degree>' should still be possible
                    deg = int(status.split()[1])
                except ValueError:
                    msg = "Failed to parse status specifier `%s'" % status
                    raise ValueError, msg
            self.bgdeg = deg
        else:
            # all other parnames are treated in the peakmodel
            self.peakModel.SetParameter(parname, status)
        

    def Copy(self):
        """
        Create a copy of this fitter
        This also copies the status of the corresponding peakModel, 
        and hence the status of the fit parameters.
        """
        new = Fitter(self.peakModel.name, self.bgdeg)
        new.peakModel.fParStatus = self.peakModel.fParStatus.copy()
        return new
    
    



