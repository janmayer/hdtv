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
import peak

dlmgr.LoadLibrary("fit")

class Fitter:
    """
    """
    def __init__(self, peakModel, bgdeg):
        self.SetPeakModel(peakModel)
        self.bgdeg = bgdeg
        self.spec = None
        self.peakFitter = None
        self.bgFitter = None
        # degree of internal background , used when no background is set
        self.intBgDeg = 0 
    
    def __getattr__(self, name):
        return getattr(self.peakModel, name)

    def FitBackground(self, spec, backgrounds):
        self.spec = spec
        # do the background fit
        bgfitter = ROOT.HDTV.Fit.PolyBg(self.bgdeg)
        for bg in backgrounds:
            bgfitter.AddRegion(spec.cal.E2Ch(bg[0]), spec.cal.E2Ch(bg[1]))
        self.bgFitter = bgfitter
        self.bgFitter.Fit(spec.fHist)

    def RestoreBackgrounds(self, spec, backgrounds, values, errors, chisquare):
        self.spec = spec
        bgfitter = ROOT.HDTV.Fit.PolyBg(self.bgdeg)
        for bg in backgrounds:
            bgfitter.AddRegion(spec.cal.E2Ch(bg[0]), spec.cal.E2Ch(bg[1]))
        self.bgFitter = bgfitter
        self.bgFitter.Restore(values, errors, chisquare)

    def FitPeaks(self, spec, region, peaklist):
        self.spec = spec
        self.peakFitter = self.peakModel.GetFitter(region, peaklist, spec.cal)
        # Do the fit
        if self.bgFitter:
            self.peakFitter.Fit(self.spec.fHist, self.bgFitter)
        else:
            self.peakFitter.Fit(self.spec.fHist, self.intBgDeg)
        
    def RestorePeaks(self, spec, region, peaklist, params, chisquare):
        self.spec = spec
        self.peakFitter = self.peakModel.GetFitter(region, peaklist, spec.cal)
        if self.bgFitter:
            self.peakFitter.Restore(self.bgFitter, chisquare)
        else:
            # FIXME: internal background
            return 
        for i in range(0, self.peakFitter.GetNumPeaks()):
            cpeak=self.peakFitter.GetPeak(i)
            for param in params:
                cpeak.Restore(param, value, error)


#    def GetResults(self):
#        peaks = list()
#        if not self.peakFitter:
#            return peaks
#        for i in range(0, self.peakFitter.GetNumPeaks()):
#            cpeak=self.peakFitter.GetPeak(i)
#            peaks.append(self.peakModel.CopyPeak(cpeak, self.spec.cal))
#        # in some rare cases it can happen that peaks change position 
#        # while doing the fit, thus we have to sort here
#        peaks.sort()
#        return peaks
#        

    def SetPeakModel(self, model):
        """
        Sets the peak model to be used for fitting. model can be either a string,
        in which case it is used as a key into the gPeakModels dictionary, or a 
        PeakModel object.
        """
        global gPeakModels
        if type(model) == str:
            model = gPeakModels[model]
        self.peakModel = model()
        self.peakFitter = None
        
    
    def Copy(self):
        new = Fitter(self.peakModel.name, self.bgdeg)
        new.peakModel.fParStatus = self.peakModel.fParStatus.copy()
        return new
    
    
# global dictionary of available peak models
def RegisterPeakModel(name, model):
    gPeakModels[name] = model
    
gPeakModels = dict()

RegisterPeakModel("theuerkauf", peak.PeakModelTheuerkauf)
RegisterPeakModel("ee", peak.PeakModelEE)


