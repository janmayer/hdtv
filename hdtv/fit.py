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
import hdtv.color
import hdtv.cal
import hdtv.util
from hdtv.drawable import Drawable
from hdtv.marker import MarkerCollection

hdtv.dlmgr.LoadLibrary("display")

class Fit(Drawable):
    """
    Fit object
    
    This Fit object is the graphical representation of a fit in HDTV. 
    It contains the marker lists and the functions. The actual interface to
    the C++ fitting routines is the class Fitter.

    All internal values (fit parameters, fit region, peak list) are in 
    uncalibrated units. 
    """

    def __init__(self, fitter, color=None, cal=None):
        Drawable.__init__(self, color, cal)
        self.regionMarkers = MarkerCollection("X", paired=True, maxnum=1,
                                             color=hdtv.color.region, cal=self.cal)
        self.peakMarkers = MarkerCollection("X", paired=False, maxnum=None,
                                             color=hdtv.color.peak, cal=self.cal)
        self.bgMarkers = MarkerCollection("X", paired=True, maxnum=None,
                                             color=hdtv.color.bg, cal=self.cal)
        self.fitter = fitter
        self.peaks = []
        self.chi = None
        self.bgChi = None
        self.bgCoeffs = []
        self.showDecomp = False
        self.dispPeakFunc = None
        self.dispBgFunc = None
        
    def __str__(self):
        return self.formated_str(verbose=False)
        
    def formated_str(self, verbose=True):
        i=0
        text = str()
        for peak in self.peaks:
            text += ("\nPeak %d:" %i).ljust(10)
            peakstr = peak.formated_str(verbose).strip()
            peakstr = peakstr.split("\n")
            peakstr =("\n".ljust(10)).join(peakstr)
            text += peakstr
            i+=1
        return text
    
    def PutPeakMarker(self, pos):
        if self.dispPeakFunc:
            self.dispPeakFunc.Remove()
            self.dispPeakFunc = None
        for peak in self.peaks:
            peak.Remove()
        self.peakMarkers.PutMarker(pos)
        
    
    def PutRegionMarker(self, pos):
        if self.dispPeakFunc:
            self.dispPeakFunc.Remove()
            self.dispPeakFunc = None
        for peak in self.peaks:
            peak.Remove()
        self.regionMarkers.PutMarker(pos)
        
        
    def PutBgMarker(self, pos):
        if self.dispBgFunc:
            self.dispBgFunc.Remove()
            self.dispBgFunc = None
        if self.dispPeakFunc:
            self.dispPeakFunc.Remove()
            self.dispPeakFunc = None
        for peak in self.peaks:
            peak.Remove()
        self.bgMarkers.PutMarker(pos)
        

    def FitBgFunc(self, spec):
        """
        Do the background fit and extract the function for display
        Note: You still need to call Draw afterwards.
        """
        # remove old fit
        if self.dispBgFunc:
            self.dispBgFunc.Remove()
            self.dispBgFunc = None
        self.bgCoeffs = []
        self.bgChi = None
        if self.dispPeakFunc:
            self.dispPeakFunc.Remove()
            self.dispPeakFunc = None
        for peak in self.peaks:
            peak.Remove()
        self.peaks = []
        self.chi=None
        # fit background 
        if len(self.bgMarkers)>0 and self.bgMarkers[-1].p2:
            backgrounds = [[m.p1, m.p2] for m in self.bgMarkers] 
            self.fitter.FitBackground(spec, backgrounds)
            func = self.fitter.bgFitter.GetFunc()
            self.dispBgFunc = ROOT.HDTV.Display.DisplayFunc(func, hdtv.color.bg)
            self.dispBgFunc.SetCal(spec.cal)
            self.bgChi = self.fitter.bgFitter.GetChisquare()
            self.bgCoeffs = []
            deg = self.fitter.bgFitter.GetDegree()
            for i in range(0, deg+1):
                value = self.fitter.bgFitter.GetCoeff(i)
                error = self.fitter.bgFitter.GetCoeffError(i)
                self.bgCoeffs.append(hdtv.util.ErrValue(value, error))
            
            
    def FitPeakFunc(self, spec, silent=False):
        """
        Do the actual peak fit and extract the functions for display
        Note: You still need to call Draw afterwards.
        """
        # remove old fit
        if self.dispBgFunc:
            self.dispBgFunc.Remove()
            self.dispBgFunc = None
        self.bgCoeffs = []
        self.bgChi = None
        if self.dispPeakFunc:
            self.dispPeakFunc.Remove()
            self.dispPeakFunc = None
        for peak in self.peaks:
            peak.Remove()
        self.peaks = []
        self.chi=None
        # fit background 
        if len(self.bgMarkers)>0 and self.bgMarkers[-1].p2:
            backgrounds =  map(lambda m: [m.p1, m.p2], self.bgMarkers)
            self.fitter.FitBackground(spec, backgrounds)
        # fit peaks
        if len(self.peakMarkers)>0 and len(self.regionMarkers)==1 and self.regionMarkers[-1].p2:
            region = [self.regionMarkers[0].p1, self.regionMarkers[0].p2]
            # remove peak marker that are outside of region
            region.sort()
            for m in self.peakMarkers:
                if m.p1<region[0] or m.p1>region[1]:
                    m.Remove()
                    self.peakMarkers.remove(m)
            peaks = [m.p1 for m in self.peakMarkers]
            peaks.sort()
            self.fitter.FitPeaks(spec, region, peaks)
            # get background function
            func = self.fitter.peakFitter.GetBgFunc()
            self.dispBgFunc = ROOT.HDTV.Display.DisplayFunc(func, hdtv.color.bg)
            self.dispBgFunc.SetCal(spec.cal)
            if self.fitter.bgFitter:
                self.bgChi = self.fitter.bgFitter.GetChisquare()
                self.bgCoeffs = []
                deg = self.fitter.bgFitter.GetDegree()
                for i in range(0, deg+1):
                    value = self.fitter.bgFitter.GetCoeff(i)
                    error = self.fitter.bgFitter.GetCoeffError(i)
                    self.bgCoeffs.append(hdtv.util.ErrValue(value, error))
            # get peak function
            func = self.fitter.peakFitter.GetSumFunc()
            self.dispPeakFunc = ROOT.HDTV.Display.DisplayFunc(func, hdtv.color.region)
            self.dispPeakFunc.SetCal(spec.cal)
            self.chi = self.fitter.peakFitter.GetChisquare()
            # create peak list
            for i in range(0, self.fitter.peakFitter.GetNumPeaks()):
                cpeak = self.fitter.peakFitter.GetPeak(i)
                peak = self.fitter.peakModel.CopyPeak(cpeak, hdtv.color.peak, spec.cal)
                self.peaks.append(peak)
            # in some rare cases it can happen that peaks change position 
            # while doing the fit, thus we have to sort here
            self.peaks.sort()
            # update peak markers
            for (marker, peak) in zip(self.peakMarkers, self.peaks):
                marker.p1 = peak.pos_cal.value
            # print result
            if not silent:
                print "\n"+6*" "+self.formated_str(verbose=True)

    def Restore(self, spec, silent=False):
        self.SetCal(spec.cal)
        if len(self.bgMarkers)>0 and self.bgMarkers[-1].p2:
            backgrounds = [[m.p1, m.p2] for m in self.bgMarkers]
            self.fitter.RestoreBackground(spec, backgrounds, self.bgCoeffs, self.bgChi)
        region = [self.regionMarkers[0].p1, self.regionMarkers[0].p2]
        region.sort()
        self.fitter.RestorePeaks(spec, region, self.peaks, self.chi)
        # get background function
        func = self.fitter.peakFitter.GetBgFunc()
        self.dispBgFunc = ROOT.HDTV.Display.DisplayFunc(func, hdtv.color.bg)
        self.dispBgFunc.SetCal(spec.cal)
        # get peak function
        func = self.fitter.peakFitter.GetSumFunc()
        self.dispPeakFunc = ROOT.HDTV.Display.DisplayFunc(func, hdtv.color.region)
        self.dispPeakFunc.SetCal(spec.cal)
        # print result
        if not silent:
            print "\n"+6*" "+str(self)


    def Draw(self, viewport):
        """
        Draw
        """
        if self.viewport:
            if not self.viewport == viewport:
                # Unlike the Display object of the underlying implementation,
                # python objects can only be drawn on a single viewport
                raise RuntimeError, "Object can only be drawn on a single viewport"
        self.viewport = viewport
        # Lock updates
        self.viewport.LockUpdate()
        # draw the markers (do this after the fit, 
        # because the fit updates the position of the peak markers)
        self.peakMarkers.Draw(self.viewport)
        self.regionMarkers.Draw(self.viewport)
        self.bgMarkers.Draw(self.viewport)
        try:
            if self.fitter.spec.GetActiveObject() != self: # Show markers only on active fit
                self.regionMarkers.Hide()
                self.bgMarkers.Hide()      
        except AttributeError: # Fitter not yet initialized
            self.regionMarkers.Show()
            self.bgMarkers.Show()
        # draw fit func, if available
        if self.dispPeakFunc:
            self.dispPeakFunc.Draw(self.viewport)
        if self.dispBgFunc:
            self.dispBgFunc.Draw(self.viewport)
        # draw peaks
        for peak in self.peaks:
            peak.Draw(self.viewport)
            if not self.showDecomp:
                peak.Hide()
        self.viewport.UnlockUpdate()


    def Refresh(self):
        """
        Refresh
        """
        # repeat the fits)
        if self.dispPeakFunc:
            # this includes the background fit
            self.FitPeakFunc(self.fitter.spec)
        elif self.dispBgFunc:
            # maybe there was only a background fit
            self.FitBgFunc(self.fitter.spec)
        if not self.viewport:
            return
        self.viewport.LockUpdate()
        # draw fit func, if available
        if self.dispPeakFunc:
            self.dispPeakFunc.Draw(self.viewport)
        if self.dispBgFunc:
            self.dispBgFunc.Draw(self.viewport)
        # draw peaks
        for peak in self.peaks:
            peak.Draw(self.viewport)
            if not self.showDecomp:
                peak.Hide()
        # draw the markers (do this after the fit, 
        # because the fit updates the position of the peak markers)
        self.peakMarkers.Refresh()
        self.regionMarkers.Refresh()
        self.bgMarkers.Refresh()
        self.viewport.UnlockUpdate()


    def Show(self):
        if not self.viewport:
            return
        self.viewport.LockUpdate()
        self.peakMarkers.Show()
        try:
            if self.fitter.spec.GetActiveObject() == self: # Is this fit the active fit?
                self.regionMarkers.Show()
                self.bgMarkers.Show()
        except AttributeError: # Fitter not yet initialized
            self.regionMarkers.Show()
            self.bgMarkers.Show()
        if self.dispPeakFunc:
            self.dispPeakFunc.Show()
        if self.dispBgFunc:
            self.dispBgFunc.Show()
        if self.showDecomp:
            for peak in self.peaks:
                peak.Show()
        self.viewport.UnlockUpdate()
    
    @property
    def xdimensions(self):
        """
        Return dimensions of fit in x-direction
        
        returns: tuple (x_start, x_end)
        """
        
        markers = list()
        
        # Get maximum of region markers, peak markers and peaks
        for r in self.regionMarkers.collection:
            markers.append(r.p1)
            markers.append(r.p2)
        for p in self.peakMarkers.collection:
            markers.append(p.p1)
        for p in self.peaks:
            markers.append(p.pos_cal)
        for b in self.bgMarkers.collection:
            markers.append(b.p1)
            markers.append(b.p2)
    
        x_start = min(markers)
        x_end = max(markers)

        return (x_start, x_end)
    
        
    def Hide(self):
        if not self.viewport:
            return
        self.viewport.LockUpdate()
        self.peakMarkers.Hide()
        self.regionMarkers.Hide()
        self.bgMarkers.Hide()
        if self.dispPeakFunc:
            self.dispPeakFunc.Hide()
        if self.dispBgFunc:
            self.dispBgFunc.Hide()
        for peak in self.peaks:
            peak.Hide()
        self.viewport.UnlockUpdate()
        
        
    def Remove(self):
        if self.viewport:
            self.viewport.LockUpdate()
            self.peakMarkers.Remove()
            self.regionMarkers.Remove()
            self.bgMarkers.Remove()
            if self.dispPeakFunc:
                self.dispPeakFunc.Remove()
            if self.dispBgFunc:
                self.dispBgFunc.Remove()
            for peak in self.peaks:
                peak.Remove()
            self.viewport.UnlockUpdate()
        self.dispPeakFunc = None
        self.dispBgFunc = None
        self.bgCoeffs = []
        self.bgChi = None
        self.peaks = []
        self.chi = None
        
        
    def SetCal(self, cal):
        self.cal = hdtv.cal.MakeCalibration(cal)
        if self.viewport:
            self.viewport.LockUpdate()
        self.peakMarkers.SetCal(self.cal)
        self.regionMarkers.SetCal(self.cal)
        self.bgMarkers.SetCal(self.cal)
        if self.dispPeakFunc:
            self.dispPeakFunc.SetCal(self.cal)
        if self.dispBgFunc:
            self.dispBgFunc.SetCal(self.cal)
        for peak in self.peaks:
            peak.SetCal(self.cal)
        if self.viewport:
            self.viewport.UnlockUpdate()

    def SetTitle(self, ID):
        """
        Set title of fit and display it near peak markers
        """
        if self.viewport:
            self.viewport.LockUpdate()
        
        for p in self.peakMarkers:
            p.SetTitle("#" + ID)
        
        if self.viewport:
            self.viewport.UnlockUpdate()
        
            
    def SetColor(self, color=None, active=False):
        if self.viewport:
            self.viewport.LockUpdate()
        if not color:
            color = self.color
        self.color = hdtv.color.Highlight(color, active)
        if active:
            self.regionMarkers.SetColor(hdtv.color.region)
            self.peakMarkers.SetColor(hdtv.color.peak)
            self.bgMarkers.SetColor(hdtv.color.bg)
            if self.dispPeakFunc:
                self.dispPeakFunc.SetColor(hdtv.color.region)
            if self.dispBgFunc:
                self.dispBgFunc.SetColor(hdtv.color.bg)
            for peak in self.peaks:
                peak.SetColor(hdtv.color.peak)
        else:
            self.regionMarkers.Hide()
            self.peakMarkers.SetColor(self.color)
            self.bgMarkers.Hide()
            if self.dispPeakFunc:
                self.dispPeakFunc.SetColor(self.color)
            if self.dispBgFunc:
                self.dispBgFunc.SetColor(self.color)
            for peak in self.peaks:
                peak.SetColor(self.color)
        if self.viewport:
            self.viewport.UnlockUpdate()
            
    def Recalibrate(self, cal):
        """
        Changes the internal (uncalibrated) values of the markers in such a way, 
        that the calibrated values are kept fixed, but a new calibration is used.
        """
        self.cal = hdtv.cal.MakeCalibration(cal)
        self.peakMarkers.Recalibrate(cal)
        self.regionMarkers.Recalibrate(cal)
        self.bgMarkers.Recalibrate(cal)

    def Copy(self, cal=None, color=None):
        cal = hdtv.cal.MakeCalibration(cal)
        new = Fit(self.fitter.Copy(), cal=cal, color=color)
        for marker in self.bgMarkers.collection:
            newmarker = marker.Copy(cal)
            new.bgMarkers.append(newmarker)
        for marker in self.regionMarkers.collection:
            newmarker = marker.Copy(cal)
            new.regionMarkers.append(newmarker)
        for marker in self.peakMarkers.collection:
            newmarker = marker.Copy(cal)
            new.peakMarkers.append(newmarker)
        return new

        
    def SetDecomp(self, stat=True):
        """
        Sets whether to display a decomposition of the fit
        """
        if self.showDecomp == stat:
            # this is already the situation, thus nothing to be done here
            return
        else:
            self.showDecomp =  stat
            if stat:
                for peak in self.peaks:
                    peak.Show()
            else:
                for peak in self.peaks:
                    peak.Hide()





