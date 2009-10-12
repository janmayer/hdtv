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

import weakref # TODO: remove if workspec problem has been solved properly 

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

    # List of hook functions to be called before/after FitPeakFunc()
    # These hook functions should accept a reference to the Fit class
    # that calls them as first argument
    FitPeakPreHooks = list()
    FitPeakPostHooks = list()
    
    def __init__(self, fitter, color=None, cal=None):
        self.regionMarkers = MarkerCollection("X", paired=True, maxnum=1,
                                             color=hdtv.color.region, cal=cal)
        self.peakMarkers = MarkerCollection("X", paired=False, maxnum=None,
                                             color=hdtv.color.peak, cal=cal, hasIDs=True)
        self.bgMarkers = MarkerCollection("X", paired=True, maxnum=None,
                                             color=hdtv.color.bg, cal=cal)
        self.fitter = fitter
        self.peaks = []
        self.chi = None
        self.bgChi = None
        self.bgCoeffs = []
        self.showDecomp = False
        self.dispPeakFunc = None
        self.dispBgFunc = None
        self._title = None
# FIXME:
#        self._workspec = None # Spectrum to work on if there is no parent spectrum -> HACK! TODO: FIX 
        Drawable.__init__(self, color, cal)

# FIXME: do not use parent link!!!
#    @property
#    def spec(self):
#        # TODO: Fix this (see above)
#        if self.parent is None:
#            return self._workspec
#        else:
#            self._workspec = None
#            return self.parent
        
    def __copy__(self):
        return self.Copy()
    
    # title property
    def _get_title(self):
        return self._title
    
    def _set_title(self, title):
        self._title = "#" + str(title)
        self.peakMarkers.Refresh()
        
    title = property(_get_title, _set_title)
    
    # cal property
    def _set_cal(self, cal):
        self._cal = hdtv.cal.MakeCalibration(cal)
        if self.viewport:
            self.viewport.LockUpdate()
        self.peakMarkers.cal=cal
        self.regionMarkers.cal = cal
        self.bgMarkers.cal = cal
        if self.dispPeakFunc:
            self.dispPeakFunc.SetCal(self.cal)
        if self.dispBgFunc:
            self.dispBgFunc.SetCal(self.cal)
        for peak in self.peaks:
            peak.cal = cal
        if self.viewport:
            self.viewport.UnlockUpdate()
    
    def _get_cal(self):
        return self._cal
        
    cal = property(_get_cal,_set_cal)
    
    # color property
    def _set_color(self, color):
        self._activeColor = hdtv.color.Highlight(color, active=True)
        self._passiveColor = hdtv.color.Highlight(color, active=False)
        if self.viewport:
            self.viewport.LockUpdate()
        self.peakMarkers.color = color
        self.regionMarkers.color = color
        self.bgMarkers.color = color
        for peak in self.peaks:
            peak.color = color
        self._RefreshDisplay()
        if self.viewport:
            self.viewport.UnlockUpdate()
            
    def _get_color(self):
        return self._passiveColor
        
    color = property(_get_color, _set_color)

    # active property
    def _set_active(self, state):
        if self.viewport:
            self.viewport.LockUpdate()
        self._active = state
        self.peakMarkers.active = state
        self.regionMarkers.active = state
        self.bgMarkers.active = state
        for peak in self.peaks:
            peak.active = state
        self._RefreshDisplay()
        if self.viewport:
            self.viewport.UnlockUpdate()
            
    def _get_active(self):
        return self._active
        
    active = property(_get_active, _set_active)
            
    @property
    def xdimensions(self):
        """
        Return dimensions of fit in x-direction
        
        returns: tuple (x_start, x_end)
        """
        markers = list()
        # Get maximum of region markers, peak markers and peaks
        for r in self.regionMarkers:
            markers.append(r.p1.GetPosInCal())
            markers.append(r.p2.GetPosInCal())
        for p in self.peakMarkers:
            markers.append(p.p1.GetPosInCal())
        for p in self.peaks:
            markers.append(p.pos_cal)
        for b in self.bgMarkers:
            markers.append(b.p1.GetPosInCal())
            markers.append(b.p2.GetPosInCal())
        # calulate region limits
        if len(markers) == 0: # No markers
            return None
        else:
            x_start = min(markers)
            x_end = max(markers)
            return (x_start, x_end)
        
    def __str__(self):
        return self.formatted_str(verbose=False)
        
    def formatted_str(self, verbose=True):
        i=0
        text = str()
        for peak in self.peaks:
            text += ("\nPeak %d:" %i).ljust(10)
            peakstr = peak.formatted_str(verbose).strip()
            peakstr = peakstr.split("\n")
            peakstr =("\n".ljust(10)).join(peakstr)
            text += peakstr
            i+=1
        return text
    
    def PutPeakMarker(self, pos):
        self.dispPeakFunc = None
        self.peaks = list()
        self.peakMarkers.PutMarker(pos)

    def PutRegionMarker(self, pos):
        self.dispPeakFunc = None
        self.peaks = list()
        self.regionMarkers.PutMarker(pos)
        
        
    def PutBgMarker(self, pos):
        self.dispBgFunc = None
        self.dispPeakFunc = None
        self.peaks = list()
        self.bgMarkers.PutMarker(pos)
        

    def FixMarkerCal(self):
        """
        Fix marker in calibrated space
        """
        for m in [self.bgMarkers, self.regionMarkers, self.peakMarkers]:
            m.FixCal()
    
    
    def FixMarkerUncal(self):
        """
        Fix marker in calibrated space
        """
        for m in [self.bgMarkers, self.regionMarkers, self.peakMarkers]:
            m.FixUncal()
            
            
    def FitBgFunc(self, spec=None):
        """
        Do the background fit and extract the function for display
        Note: You still need to call Draw afterwards.
        """
        if spec is None:
            spec = self.spec 
        # set calibration without changing position of markers,
        # because the marker have been set by the user to calibrated values
#        self.Recalibrate(spec.cal)
        self._set_cal(spec.cal)
#        self.bgMarkers.FixUncal()

        # remove old fit
        self.Reset()
        
        # fit background 
        if len(self.bgMarkers)>0 and not self.bgMarkers.IsPending():
            backgrounds = hdtv.util.Pairs()
            for m in self.bgMarkers:
                backgrounds.add(m.p1.GetPosInUncal(), m.p2.GetPosInUncal()) 
            self.fitter.FitBackground(spec=spec, backgrounds=backgrounds)
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
            
            
    def FitPeakFunc(self, spec=None, silent=False):
        """
        Do the actual peak fit and extract the functions for display
        Note: You still need to call Draw afterwards.
        """
        # Call pre hooks
        for func in Fit.FitPeakPreHooks:
            func(self)
        
        if spec is None:
            spec = self.spec
        # set calibration without changing position of markers,
        # because the marker have been set by the user to calibrated values
        self.cal=spec.cal
#        self.peakMarkers.FixUncal()
#        self.regionMarkers.FixUncal()
#        self.bgMarkers.FixUncal()
        
        # remove old fit
        if self.dispBgFunc:
            self.dispBgFunc = None
        self.bgCoeffs = []
        self.bgChi = None
        if self.dispPeakFunc:
            self.dispPeakFunc = None

        self.peaks = []
        self.chi=None
        # fit background 
        if len(self.bgMarkers)>0 and not self.bgMarkers.IsPending():
            backgrounds = hdtv.util.Pairs()
            for m in self.bgMarkers:
                backgrounds.add(m.p1.GetPosInUncal(), m.p2.GetPosInUncal())
            self.fitter.FitBackground(spec=spec, backgrounds=backgrounds)
        # fit peaks
        if len(self.peakMarkers)>0 and self.regionMarkers.IsFull():
            region = [self.regionMarkers[0].p1.GetPosInUncal(), self.regionMarkers[0].p2.GetPosInUncal()]
            # remove peak marker that are outside of region
            region.sort()
            for m in self.peakMarkers:
                if m.p1.GetPosInUncal()<region[0] or m.p1.GetPosInUncal()>region[1]:
                    self.peakMarkers.remove(m)
            peaks = [m.p1.GetPosInUncal() for m in self.peakMarkers]
            peaks.sort()
            self.fitter.FitPeaks(spec=spec, region=region, peaklist=peaks)
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
                if marker.p1.pos_cal is None: # Marker is fixed in uncalibrated space
                    marker.p1.pos_uncal = peak.pos.value
                else:
                    marker.p1.pos_cal = peak.pos_cal.value
            # print result
            if not silent:
                print "\n"+6*" "+self.formatted_str(verbose=True)
                
        # Call pre hooks
        for func in Fit.FitPeakPostHooks:
            func(self)

    def Restore(self, spec=None, silent=False):
        # set calibration also for the markers,
        # as the marker position is set to uncalibrated values, 
        # when read from xml fit list
        
        if spec is None:
            spec = self.spec
#        self.cal = spec.cal
            
        if len(self.bgMarkers)>0 and self.bgMarkers[-1].p2.GetPosInCal():
            
            backgrounds = hdtv.util.Pairs()
            for m in self.bgMarkers:
                backgrounds.add(m.p1.GetPosInUncal(), m.p2.GetPosInUncal())
            self.fitter.RestoreBackground(backgrounds=backgrounds, coeffs=self.bgCoeffs, chisquare=self.bgChi)
        region = [self.regionMarkers[0].p1.GetPosInUncal(), self.regionMarkers[0].p2.GetPosInUncal()]
        region.sort()
        self.fitter.RestorePeaks(spec=spec, region=region, peaks=self.peaks, chisquare=self.chi)
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
        # draw fit func, if available
        if self.dispPeakFunc:
            self.dispPeakFunc.Draw(self.viewport)
        if self.dispBgFunc:
            self.dispBgFunc.Draw(self.viewport)
        # draw peaks
        for peak in self.peaks:
            peak.color=self.color
            peak.Draw(self.viewport)
        self._RefreshDisplay()
        self.viewport.UnlockUpdate()


    def Refresh(self):
        """
        Refresh
        """
        # repeat the fits
        if self.dispPeakFunc:
            # this includes the background fit
            self.FitPeakFunc()
        elif self.dispBgFunc:
            # maybe there was only a background fit
            self.FitBgFunc()
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
        # draw the markers (do this after the fit, 
        # because the fit updates the position of the peak markers)
        self.peakMarkers.Refresh()
        self.regionMarkers.Refresh()
        self.bgMarkers.Refresh()
        self._RefreshDisplay()
        self.viewport.UnlockUpdate()


    def Reset(self):
        """
        Reset the fit. NOTE: the fitter is *not* resetted 
        """
        self.dispBgFunc = None
        self.bgCoeffs = []
        self.bgChi = None
        self.dispPeakFunc = None
        self.peaks = []
        self.chi=None 
        
        
    def _RefreshDisplay(self):
        """ 
        This function contains the logic what markers/functions to show and 
        in what color depending on the state (active or not) of this fit.
        """
        if self.viewport:
            self.viewport.LockUpdate()
        if self.active or len(self.peaks)==0:
            # show all markers, if fit is active or if fit is unfinished,
            # the second case can happen when switching to another spectrum,
            # after executing only the background fit
            self.regionMarkers.Show()
            self.peakMarkers.Show()
            self.bgMarkers.Show()
        else:
            self.regionMarkers.Hide()
            self.peakMarkers.Show()
            self.bgMarkers.Hide()
        # coloring
        if self.dispPeakFunc:
            if self.active:
                self.dispPeakFunc.SetColor(hdtv.color.region)
            else:
                self.dispPeakFunc.SetColor(self.color)
            self.dispPeakFunc.Show()
        if self.dispBgFunc:
            if self.active:
                self.dispBgFunc.SetColor(hdtv.color.bg)
            else:
                self.dispBgFunc.SetColor(self.color)
            self.dispBgFunc.Show()
        # peak list
        for peak in self.peaks:
            if self.active:
                peak.color = hdtv.color.peak
            else:
                peak.color = self.color
            if self.showDecomp:
                peak.Show()
            else:
                peak.Hide()
        if self.viewport:
            self.viewport.UnlockUpdate()

    def Show(self):
        if not self.viewport:
            return
        self._RefreshDisplay()
        

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

    
    def Copy(self, cal=None, color=None):
        """
        Create new fit with identical markers
        """
        cal = hdtv.cal.MakeCalibration(cal)
        new = Fit(self.fitter.Copy(), cal=cal, color=color)
        for marker in self.bgMarkers:
            newmarker = marker.Copy(cal)
            new.bgMarkers.append(newmarker)
        for marker in self.regionMarkers:
            newmarker = marker.Copy(cal)
            new.regionMarkers.append(newmarker)
        for marker in self.peakMarkers:
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




