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
import hdtv.dlmgr
import hdtv.color 

from hdtv.drawable import Drawable, DrawableCompound
from hdtv.specreader import SpecReader, SpecReaderError

hdtv.dlmgr.LoadLibrary("display")

class _RawSpectrum(Drawable):
    """
    Spectrum object
    
    This class is hdtvs wrapper around a ROOT histogram. It adds a calibration,
    plus some internal management for drawing the histogram    to the hdtv spectrum
    viewer.

    Optionally, the class method FromFile can be used to read a spectrum
    from a file, using the SpecReader class. A calibration can be
    defined by supplying a sequence that form the factors of the calibration
    polynom. Moreover a color can be defined, which then will be used when the
    spectrum is displayed. 
    
    A spectrum object can contain a number of fits.
    """
    def __init__(self, hist, color=hdtv.color.default, cal=None):

        self.norm = 1.0
        self.fHist = hist
        self.fEffCal = None

        Drawable.__init__(self, color, cal)
        
        
    def __str__(self):
        return self.name

    # name property
    def _get_name(self):
        if self.fHist:
            return self.fHist.GetName()
        
    def _set_name(self, name):
        self.fHist.SetName(name)
        
    name = property(_get_name, _set_name)
    
    def GetTypeStr(self):
        """
        Return a string describing the type of this spectrum.
        Should be overridden by subclasses.
        """
        if self.fHist:
            return "spectrum"
        else:
            return "empty spectrum (no associated ROOT TH1 object)"
            
    def GetInfo(self):
        """
        Return a string describing this spectrum
        """
        s = "Spectrum type: %s\n" % self.GetTypeStr()
        if not self.fHist:
            return s
        
        s += "Name: %s\n" % str(self)
        s += "Nbins: %d\n" % self.fHist.GetNbinsX()
        xmin = self.fHist.GetXaxis().GetXmin()
        xmax = self.fHist.GetXaxis().GetXmax()
        
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
        self.fHist.Add(spec.fHist, 1.0)
        self.SetHist(self.fHist)

    def Minus(self, spec):
        """
        Substract other spectrum from this one
        """ 
        self.fHist.Add(spec.fHist, -1.0)
        self.SetHist(self.fHist)
    
    def Multiply(self, factor):
        """
        Multiply spectrum with factor
        """ 
        self.fHist.Scale(factor)
        self.SetHist(self.fHist)
        
        
    def Draw(self, viewport):
        """
        Draw this spectrum to the viewport
        """
        if not self.viewport is None:
            if self.viewport == viewport:
                # this spectrum has already been drawn
                self.Show()
                return
            else:
                # Unlike the DisplaySpec object of the underlying implementation,
                # Spectrum() objects can only be drawn on a single viewport
                raise RuntimeError, "Spectrum can only be drawn on a single viewport"
        self.viewport = viewport
        # Lock updates
        self.viewport.LockUpdate()
        # Show spectrum
        if self.displayObj is None and not self.fHist is None:
            if self.active:
                color = self._activeColor
            else:
                color= self._passiveColor
            self.displayObj = ROOT.HDTV.Display.DisplaySpec(self.fHist, color)
            self.displayObj.SetID(self.ID)
            self.displayObj.SetNorm(self.norm)
            self.displayObj.Draw(self.viewport)
            # add calibration
            if self.cal:
                self.displayObj.SetCal(self.cal)
        # finally unlock the viewport
        self.viewport.UnlockUpdate()
        
        
    def SetID(self, ID):
        self.ID = ID
        if self.displayObj:
            self.displayObj.SetID(ID)
            
            
    def SetNorm(self, norm):
        "Set the normalization factor for displaying this spectrum"
        self.norm = norm
        self.SetHist(self.fHist)
        if self.displayObj:
            self.displayObj.SetNorm(self.norm)
        
    
    def Refresh(self):
        """
        Refresh the spectrum, i.e. reload the data inside it
        """
        # The generic spectrum class does not know about the origin of its
        # bin data and thus cannot reload anything.
        pass
        
    
    def SetHist(self, hist):
        self.fHist = hist
        if self.displayObj:
            self.displayObj.SetHist(self.fHist)
        

    def WriteSpectrum(self, fname, fmt):
        """
        Write the spectrum to file
        """
        fname = os.path.expanduser(fname)
        try:
            SpecReader().WriteSpectrum(self.fHist, fname, fmt)
        except SpecReaderError, msg:
            hdtv.ui.error("Failed to write spectrum: %s (file: %s)" % (msg, fname))
            return False
        return True


    def ToTop(self):
        """
        Move the spectrum to the top of its draw stack
        """
        if self.displayObj:
            self.displayObj.ToTop()
            

    def ToBottom(self):
        """
        Move the spectrum to the top of its draw stack
        """
        if self.displayObj:
            self.displayObj.ToBottom()


class Spectrum(_RawSpectrum):
    """ 
    This CompoundObject is a dictionary of Fits belonging to a spectrum.
    """
    def __init__(self, hist, color=hdtv.color.default, cal=None):
        self.fits = DrawableCompound()
        _RawSpectrum.__init__(self, hist, color=color, cal=cal)


    def AddFit(self, fit, ID=None):
        """
        Add a fit to this spectrum with ID
        """
        # as marker positions are uncalibrated, 
        # we need do a recalibration here
        newID = self.fits.Add(fit, ID)
        # TODO: This should be handled via "parent"
        fit.cal = self.cal
        fit.color = self.color
        fit.parent = self
        fit.FixMarkerCal()
        return newID
        
    # cal property
    def _set_cal(self, cal):
        _RawSpectrum._set_cal(self, cal)
        for fit in self.fits.itervalues():
            fit.cal = cal
        
    def _get_cal(self):
        return _RawSpectrum._get_cal(self)
        
    cal = property(_get_cal, _set_cal)
    
    
    # color property
    def _set_color(self,color):
        _RawSpectrum._set_color(self, color)
        for fit in self.fits.itervalues():
            fit.color = color

    def _get_color(self):
        return _RawSpectrum._get_color(self)

    color = property(_get_color, _set_color)
    
        
    def Refresh(self):
        """
        Refresh spectrum and fits
        """
        _RawSpectrum.Refresh(self)
        self.fits.Refresh()
        
        
    def Draw(self, viewport):
        """
        Draw spectrum and fits
        """
        _RawSpectrum.Draw(self, viewport)
        self.fits.Draw(self.viewport)
        
    
    # Show commands
    def Show(self):
        """
        Show the spectrum and all fits that are marked as visible
        """
        _RawSpectrum.Show(self)
        # only show objects that have been visible before
        for ID in self.fits.visible:
            self.fits[ID].Show()
    
    # Hide commands
    def Hide(self):
        """
        Hide the whole object,
        but remember which fits were visible
        """
        # hide the spectrum itself
        _RawSpectrum.Hide(self)
        # Hide all fits, but remember what was visible
        visible = self.fits.visible.copy()
        self.fits.Hide()
        self.fits.visible = visible

    def GetActiveObject(self):
        """
        Return the active fit
        
        This is called from e.g. Drawable.active()
        """
        return self.fits.GetActiveObject()

        
class FileSpectrum(Spectrum):
    """
    File spectrum object
    
    A spectrum that comes from a file in any of the formats supported by hdtv.
    """
    def __init__(self, fname, fmt=None, color=None, cal=None):
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
            hdtv.error("Failed to load spectrum: %s (file: %s)" % (msg, fname))
            raise 
        self.fFilename = fname
        self.fFmt = fmt
        Spectrum.__init__(self, hist, color, cal)

        
    def GetTypeStr(self):
        """
        Return a string describing the type of this spectrum.
        """
        return "spectrum, read from file"
        
    def GetInfo(self):
        s = Spectrum.GetInfo(self)
        s += "Filename: %s\n" % self.fFilename
        if self.fFmt:
            s += "File format: %s\n" % self.fFmt
        else:
            s += "File format: autodetected\n"
        return s
    
    def Refresh(self):
        """
        Reload the spectrum from disk
        """
        try:
            os.path.exists(self.fFilename)
        except OSError:
            hdtv.ui.warn("File %s not found, keeping previous data" % self.fFilename)
            return
        # call to SpecReader to get the hist
        try:
            hist = SpecReader().GetSpectrum(self.fFilename, self.fFmt)
        except SpecReaderError, msg:
            hdtv.ui.warn("Failed to load spectrum: %s (file: %s), keeping previous data" \
                  % (msg, self.fFilename))
            return
        self.SetHist(hist)
        
