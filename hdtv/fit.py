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

import copy

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
                                             color=hdtv.color.peak, cal=cal)
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
        Drawable.__init__(self, color, cal)
        self.spec = None
        self.active = True
        self.ShowAsActive = lambda self: self.ShowAsWorkFit

    # ID property
    def _get_ID(self):
        return self.peakMakers.ID
    
    def _set_ID(self, ID):
        self.peakMarkers.ID = ID

    ID = property(_get_ID, _set_ID)
    
    # cal property
    def _set_cal(self, cal):
        self._cal = hdtv.cal.MakeCalibration(cal)
        if self.viewport:
            self.viewport.LockUpdate()
        self.peakMarkers.cal = self._cal
        self.regionMarkers.cal = self._cal
        self.bgMarkers.cal = self._cal
        if self.dispPeakFunc:
            self.dispPeakFunc.SetCal(self._cal)
        if self.dispBgFunc:
            self.dispBgFunc.SetCal(self._cal)
        for peak in self.peaks:
            peak.cal = self._cal
        if self.viewport:
            self.viewport.UnlockUpdate()
    
    def _get_cal(self):
        return self._cal
        
    cal = property(_get_cal,_set_cal)
    
    # color property
    def _set_color(self, color):
        # we only need one the passive color for fits
        self._passiveColor = hdtv.color.Highlight(color, active=False)
        if self.viewport:
            self.viewport.LockUpdate()
        self.peakMarkers.color = color
        self.regionMarkers.color = color
        self.bgMarkers.color = color
        for peak in self.peaks:
            peak.color = color
        self.Show()
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
        self.Show()
        if self.viewport:
            self.viewport.UnlockUpdate()
            
    def _get_active(self):
        return self._active
        
    active = property(_get_active, _set_active)
    
    # spec property
    def _set_spec(self, spec):
        self._spec = spec
        self.Erase()
        if spec is None:
            self.FixMarkerInCal()
            self.cal = None
        else:
            self.cal = spec.cal
            self.FixMarkerInUncal()
            
    def _get_spec(self):
        return self._spec
        
    spec = property(_get_spec, _set_spec)

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
    
    def ChangeMarker(self, mtype, pos, action):
        """
        Set a new marker or remove a marker.
        
        action : "put" or "remove"
        mtype  : "bg", "region", "peak"
        """
        self.spec = None
        markers = getattr(self, "%sMarkers" %mtype)
        if action is "set":
            markers.SetMarker(pos)
        if action is "remove":
            markers.RemoveNearest(pos)
    
    def FixMarkerInCal(self):
        """
        Fix marker in calibrated space
        """
        for m in [self.bgMarkers, self.regionMarkers, self.peakMarkers]:
            m.FixInCal()
    
    def FixMarkerInUncal(self):
        """
        Fix marker in calibrated space
        """
        for m in [self.bgMarkers, self.regionMarkers, self.peakMarkers]:
            m.FixInUncal()
            
            
    def FitBgFunc(self, spec):
        """
        Do the background fit and extract the function for display
        Note: You still need to call Draw afterwards.
        """
        self.spec = spec
        # fit background 
        if len(self.bgMarkers)>0 and not self.bgMarkers.IsPending():
            backgrounds = hdtv.util.Pairs()
            for m in self.bgMarkers:
                backgrounds.add(m.p1.pos_uncal, m.p2.pos_uncal) 
            self.fitter.FitBackground(spec=self.spec, backgrounds=backgrounds)
            func = self.fitter.bgFitter.GetFunc()
            self.dispBgFunc = ROOT.HDTV.Display.DisplayFunc(func, hdtv.color.bg)
            self.dispBgFunc.SetCal(self.cal)
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
        # Call pre hooks
        for func in Fit.FitPeakPreHooks:
            func(self)

        self.spec = spec
        # fit background 
        if len(self.bgMarkers)>0 and not self.bgMarkers.IsPending():
            backgrounds = hdtv.util.Pairs()
            for m in self.bgMarkers:
                backgrounds.add(m.p1.pos_uncal, m.p2.pos_uncal)
            self.fitter.FitBackground(spec=self.spec, backgrounds=backgrounds)
        # fit peaks
        if len(self.peakMarkers)>0 and self.regionMarkers.IsFull():
            region = [self.regionMarkers[0].p1.pos_uncal, self.regionMarkers[0].p2.pos_uncal]
            # remove peak marker that are outside of region
            region.sort()
            for m in self.peakMarkers:
                if m.p1.pos_uncal<region[0] or m.p1.pos_uncal>region[1]:
                    self.peakMarkers.remove(m)
            peaks = [m.p1.pos_uncal for m in self.peakMarkers]
            peaks.sort()
            self.fitter.FitPeaks(spec=self.spec, region=region, peaklist=peaks)
            # get background function
            func = self.fitter.peakFitter.GetBgFunc()
            self.dispBgFunc = ROOT.HDTV.Display.DisplayFunc(func, hdtv.color.bg)
            self.dispBgFunc.SetCal(self.cal)
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
            self.dispPeakFunc.SetCal(self.cal)
            self.chi = self.fitter.peakFitter.GetChisquare()
            # create peak list
            for i in range(0, self.fitter.peakFitter.GetNumPeaks()):
                cpeak = self.fitter.peakFitter.GetPeak(i)
                peak = self.fitter.peakModel.CopyPeak(cpeak, hdtv.color.peak, self.cal)
                self.peaks.append(peak)
            # in some rare cases it can happen that peaks change position 
            # while doing the fit, thus we have to sort here
            self.peaks.sort()
            # update peak markers
            for (marker, peak) in zip(self.peakMarkers, self.peaks):
                # Marker is fixed in uncalibrated space
                marker.p1.pos_uncal = peak.pos.value
            # print result
            if not silent:
                print "\n"+6*" "+self.formatted_str(verbose=True)
                
        # Call post hooks
        for func in Fit.FitPeakPostHooks:
            func(self)

    def Restore(self, spec=None, silent=False):
        self.spec = spec
        if len(self.bgMarkers)>0 and self.bgMarkers[-1].p2.pos_cal:
            
            backgrounds = hdtv.util.Pairs()
            for m in self.bgMarkers:
                backgrounds.add(m.p1.pos_uncal, m.p2.pos_uncal)
            self.fitter.RestoreBackground(backgrounds=backgrounds, coeffs=self.bgCoeffs, chisquare=self.bgChi)
        region = [self.regionMarkers[0].p1.pos_uncal, self.regionMarkers[0].p2.pos_uncal]
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
        if self.viewport and not self.viewport == viewport:
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
        self.Show()
        self.viewport.UnlockUpdate()

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
        self.Show()
        self.viewport.UnlockUpdate()

    def Erase(self, bg_only=False):
        """
        Erase previous fit. NOTE: the fitter is *not* resetted 
        """
        # remove bg fit
        self.dispBgFunc = None
        self.fitter.bgFitter = None
        self.bgCoeffs = []
        self.bgChi = None
        if not bg_only:
            # remove peak fit
            self.dispPeakFunc = None
            self.peaks = []
            self.chi=None 
    
    def ShowAsWorkFit(self):
        if not self.viewport:
            return
        self.viewport.LockUpdate()
        self.regionMarkers.Show()
        self.peakMarkers.Show()
        self.bgMarkers.Show()
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
            if self.showDecomp:
                peak.Show()
            else:
                peak.Hide()
        self.viewport.UnlockUpdate()
        
    
    def ShowAsPending(self):
        # TODO: how should a fit look in this state?
        if not self.viewport:
            return
        self.viewport.LockUpdate()
        self.ShowAsPassive()
        # but show all markers in passive state
        self.regionMarkers.active = False
        self.regionMarkers.Show()
        self.peakMarkers.active = False
        self.peakMarkers.Show()
        self.bgMarkers.active = False
        self.bgMarkers.Show()
        self.viewport.UnlockUpdate()

        
    def ShowAsPassive(self):
        if not self.viewport:
            return
        self.viewport.LockUpdate()
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
            if self.showDecomp:
                peak.Show()
            else:
                peak.Hide()
        self.viewport.UnlockUpdate()
    
        
    def Show(self):
        if not self.viewport:
            return
        if self.active:
            self.ShowAsWorkFit()
        else:
            self.ShowAsPassive()
            

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

    @property
    def xdimensions(self):
        """
        Return dimensions of fit in x-direction
        
        returns: tuple (x_start, x_end)
        """
        markers = list()
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
        if len(markers) == 0: # No markers
            return None
        else:
            x_start = min(markers)
            x_end = max(markers)
            return (x_start, x_end)

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




