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
import os
import hdtv.color 
import hdtv.ui

from hdtv.drawable import Drawable, DrawableManager
from hdtv.specreader import SpecReader, SpecReaderError

# Don't add created spectra to the ROOT directory
ROOT.TH1.AddDirectory(ROOT.kFALSE)

class Histogram(Drawable):
    """
    Histogram object
    
    This class is hdtvs wrapper around a ROOT histogram. It adds a calibration,
    plus some internal management for drawing the histogram to the hdtv spectrum
    viewer.
    """
    def __init__(self, hist, color=hdtv.color.default, cal=None):
        Drawable.__init__(self, color, cal)
        self._hist = hist
        self._norm = 1.0
        self._ID = None
        self.effCal = None
        self.typeStr = "spectrum"

    def __str__(self):
        return self.name
        
    def __copy__(self):
        # call C++ copy constructor
        hist = self._hist.__class__(self._hist)
        # create new spectrum object
        return Histogram(hist, color=self.color, cal=self.cal)
        
    # hist property
    def _set_hist(self, hist):
        self._hist = hist
        if self.displayObj:
            self.displayObj.SetHist(self._hist)
    
    def _get_hist(self):
        return self._hist
        
    hist = property(_get_hist, _set_hist)
        
    # name property
    def _get_name(self):
        if self._hist:
            return self._hist.GetName()
        
    def _set_name(self, name):
        self._hist.SetName(name)
        
    name = property(_get_name, _set_name)

    # norm property
    def _set_norm(self, norm):
        self._norm = norm
        if self.displayObj:
            self.displayObj.SetNorm(self.norm)

    def _get_norm(self):
        return self._norm
        
    norm = property(_get_norm, _set_norm)
    
    @property   
    def info(self):
        """
        Return a string describing this spectrum
        """
        s = "Spectrum type: %s\n" % self.typeStr
        if not self._hist:
            return s
        s += "Name: %s\n" % str(self)
        s += "Nbins: %d\n" % self._hist.GetNbinsX()
        xmin = self._hist.GetXaxis().GetXmin()
        xmax = self._hist.GetXaxis().GetXmax()
        if self.cal and not self.cal.IsTrivial():
            s += "Xmin: %.2f (cal)  %.2f (uncal)\n" % (self.cal.Ch2E(xmin), xmin)
            s += "Xmax: %.2f (cal)  %.2f (uncal)\n" % (self.cal.Ch2E(xmax), xmax)
        else:
            s += "Xmin: %.2f\n" % xmin
            s += "Xmax: %.2f\n" % xmax
        
        if not self.cal or self.cal.IsTrivial():
            s += "Calibration: none\n"
        elif type(self.cal) == ROOT.HDTV.Calibration:
            s += "Calibration: Polynomial, degree %d\n" % self.cal.GetDegree()
        else:
            s += "Calibration: unknown\n"
        return s
              
    # TODO: sumw2 function should be called at some point for correct error handling
    def Plus(self, spec):
        """
        Add other spectrum to this one
        """ 
        self._hist.Add(spec._hist, 1.0)
        self.typeStr = "spectrum, modified (sum)"
        
    def Minus(self, spec):
        """
        Substract other spectrum from this one
        """ 
        self._hist.Add(spec._hist, -1.0)
        self.typeStr = "spectrum, modified (difference)"
            
    def Multiply(self, factor):
        """
        Multiply spectrum with factor
        """ 
        self._hist.Scale(factor)
        self.typeStr = "spectrum, modified (multiplied)"
        
       
    def Draw(self, viewport):
        """
        Draw this spectrum to the viewport
        """
        
        if not self.viewport is None and not self.viewport == viewport:
            # Unlike the DisplaySpec object of the underlying implementation,
            # Spectrum() objects can only be drawn on a single viewport
            raise RuntimeError, "Spectrum can only be drawn on a single viewport"
        self.viewport = viewport
        # Lock updates
        self.viewport.LockUpdate()
        # Show spectrum
        if self.displayObj is None and not self._hist is None:
            if self.active:
                color = self._activeColor
            else:
                color= self._passiveColor
            self.displayObj = ROOT.HDTV.Display.DisplaySpec(self._hist, color)
            self.displayObj.SetNorm(self.norm)
            self.displayObj.Draw(self.viewport)
            # add calibration
            if self.cal:
                self.displayObj.SetCal(self.cal)
            # and ID
            if not self.ID is None:
                self.displayObj.SetID(self.ID)
        # finally unlock the viewport
        self.viewport.UnlockUpdate()
        

    def WriteSpectrum(self, fname, fmt):
        """
        Write the spectrum to file
        """
        fname = os.path.expanduser(fname)
        try:
            SpecReader().WriteSpectrum(self._hist, fname, fmt)
        except SpecReaderError, msg:
            hdtv.ui.error("Failed to write spectrum: %s (file: %s)" % (msg, fname))
            return False
        return True
       

class FileHistogram(Histogram):
    """
    File spectrum object
    
    A spectrum that comes from a file in any of the formats supported by hdtv.
    """
    def __init__(self, fname, fmt=None, color=hdtv.color.default, cal=None):
        """
        Read a spectrum from file
        """
        # check if file exists
        try:
            os.path.exists(fname)
        except OSError:
            hdtv.ui.error("File %s not found" % fname)
            raise
        # call to SpecReader to get the hist
        try:
            hist = SpecReader().GetSpectrum(fname, fmt)
        except SpecReaderError, msg:
            hdtv.ui.error(str(msg))
            raise 
        self.fmt = fmt
        self.filename = fname
        Histogram.__init__(self, hist, color, cal)
        self.typeStr = "spectrum, read from file"
        
    @property
    def info(self):
        # get the info property of the baseclass
        s = Histogram.info.fget(self)
        s += "Filename: %s\n" % self.filename
        if self.fmt:
            s += "File format: %s\n" % self.fmt
        else:
            s += "File format: autodetected\n"
        return s
    
    def Refresh(self):
        """
        Reload the spectrum from disk
        """
        try:
            os.path.exists(self.filename)
        except OSError:
            hdtv.ui.warn("File %s not found, keeping previous data" % self.filename)
            return
        # call to SpecReader to get the hist
        try:
            hist = SpecReader().GetSpectrum(self.filename, self.fmt)
        except SpecReaderError, msg:
            hdtv.ui.warn("Failed to load spectrum: %s (file: %s), keeping previous data" \
                  % (msg, self.filename))
            return
        self.hist = hist       


class Spectrum(DrawableManager):
    def __init__(self, histogram):
        DrawableManager.__init__(self)
        self.hist = histogram
  
    # delegate everything to the underlying histogram
    def __setattr__(self, name, value):
        if hasattr(self, "hist") and self.hist is not None:
            self.hist.__setattr__(name, value)
        DrawableManager.__setattr__(self, name, value)
        
    def __getattr__(self, name):
        if hasattr(self, "hist"):
            return getattr(self.hist, name)
        else:
            raise AttributeError

    # color property
    def _set_color(self, color):
        for fit in self.dict.itervalues():
            fit.color = color
            
    def _get_color(self):
        return self.hist.color
            
    color = property(_get_color, _set_color)
        
    # cal property
    def _set_cal(self, cal):
        for fit in self.dict.itervalues():
            fit.cal = cal
    
    def _get_cal(self):
        return self.hist.cal
        
    cal = property(_get_cal, _set_cal)
    
    # overwrite some functions of DrawableManager to do some extra work
    def Insert(self, fit, ID=None):
        fit.spec = self
        return DrawableManager.Insert(self, fit, ID)
        
    def Pop(self, ID):
        fit = DrawableManager.Pop(self, ID)
        fit.spec = None
        return fit
        
    def Draw(self, viewport):
        self.viewport = viewport
        self.viewport.LockUpdate()
        DrawableManager.Draw(self, viewport)
        if self.hist:
            self.hist.Draw(viewport)
        self.viewport.UnlockUpdate()
        
    def Show(self):
        if self.viewport is None:
            return
        self.viewport.LockUpdate()
        DrawableManager.Show(self)
        if self.hist:
            self.hist.Show()
        self.viewport.UnlockUpdate()
        
    def Hide(self):
        if self.viewport is None:
            return
        self.viewport.LockUpdate()
        DrawableManager.Hide(self)
        if self.hist:
            self.hist.Hide()
        self.viewport.UnlockUpdate()
        
    def Refresh(self):
        if self.viewport is None:
            return
        self.viewport.LockUpdate()
        DrawableManager.Refresh(self)
        if self.hist:
            self.hist.Refresh()
        self.viewport.UnlockUpdate()
        
    

