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

import os

import ROOT
import hdtv.color

from hdtv.drawable import Drawable
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
            self.displayObj.SetNorm(norm)

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
        # update display
        if self.displayObj:
            self.displayObj.SetHist(self._hist)
        self.typeStr = "spectrum, modified (sum)"
        
    def Minus(self, spec):
        """
        Substract other spectrum from this one
        """ 
        self._hist.Add(spec._hist, -1.0)
        # update display
        if self.displayObj:
            self.displayObj.SetHist(self._hist)
        self.typeStr = "spectrum, modified (difference)"
            
    def Multiply(self, factor):
        """
        Multiply spectrum with factor
        """ 
        self._hist.Scale(factor)
        # update display
        if self.displayObj:
            self.displayObj.SetHist(self._hist)
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
                ID = str(self.ID).strip(".")
                self.displayObj.SetID(ID)
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

class CutHistogram(Histogram):
    def __init__(self, hist, axis, gates, color=hdtv.color.default, cal=None):
        Histogram.__init__(self, hist, color, cal)
        self.gates = gates
        self.axis = axis
    
    @property
    def info(self):
        s = Histogram.info.fget(self)
        s += "cut "
        s +="on %s axis gate: " % self.axis
        for i in range(len(self.gates)):
            g = self.gates[i]
            s+= "%d - %d " %(g.p1.pos_cal, g.p2.pos_cal)
            if not i==len(self.gates):
                "and "
        return s


class Histo2D(object):
    def __init__(self):
        pass
    
    @property
    def name(self):
        return "generic 2D histogram"
    
    @property
    def xproj(self):
        return None
        
    @property
    def yproj(self):
        return None
        
    def ExecuteCut(self, regionMarkers, bgMarkers, axis):
        return None


class RHisto2D(Histo2D):
    """
    ROOT TH2-backed matrix for projection
    """
    def __init__(self, rhist):
        self.rhist = rhist
        
        # Lazy generation of projections
        self._prx = None
        self._pry = None
        
    @property
    def name(self):
        return self.rhist.GetName()
        
    @property
    def xproj(self):
        if self._prx == None:
            name = self.rhist.GetName() + "_prx"
            self._prx = self.rhist.ProjectionX(name, 0, -1, "e")
            # do not store the Histogram object here because of garbage collection
            prx = Histogram(self._prx)
            prx.typeStr = "x projection"
        return prx
        
    @property
    def yproj(self):
        if self._pry == None:
            name = self.rhist.GetName() + "_pry"
            self._pry = self.rhist.ProjectionY(name, 0, -1, "e")
            # do not store the Histogram object here because of garbage collection
            pry = Histogram(self._pry)
            pry.typeStr = "y projection"
        return pry

    
    def ExecuteCut(self, regionMarkers, bgMarkers, axis):
        # _axis_ is the axis the markers refer to, so we project on the *other*
        # axis. We call _axis_ the cut axis and the other axis the projection
        # axis. If the matrix is symmetric, this does not matter, so _axis_ is
        # "0" and the implementation can choose.
        
        if len(regionMarkers) < 1:
            raise RuntimeError, "Need at least one gate for cut"
        
        if axis == "0":
            axis = "x"
            
        if not axis in ("x", "y"):
            raise ValueError, "Bad value for axis parameter"
            
        if axis == "x":
            cutAxis = self.rhist.GetXaxis()
            projector = self.rhist.ProjectionY
        else:
            cutAxis = self.rhist.GetYaxis()
            projector = self.rhist.ProjectionX
        
        b1 = cutAxis.FindBin(regionMarkers[0].p1.pos_uncal)
        b2 = cutAxis.FindBin(regionMarkers[0].p2.pos_uncal)
        
        name = self.rhist.GetName() + "_cut"
        rhist = projector(name, min(b1,b2), max(b1,b2), "e")
        # Ensure proper garbage collection for ROOT histogram objects
        ROOT.SetOwnership(rhist, True)
        
        numFgBins = abs(b2 - b1) + 1
        for r in regionMarkers[1:]:
            b1 = cutAxis.FindBin(r.p1.pos_uncal)
            b2 = cutAxis.FindBin(r.p2.pos_uncal)
            numFgBins += (abs(b2 - b1) + 1)
        
            tmp = projector("proj_tmp", min(b1,b2), max(b1,b2), "e")
            ROOT.SetOwnership(tmp, True)
            rhist.Add(tmp, 1.)
        
        bgBins = []
        numBgBins = 0
        for b in bgMarkers:
            b1 = cutAxis.FindBin(b.p1.pos_uncal)
            b2 = cutAxis.FindBin(b.p2.pos_uncal)
            numBgBins += (abs(b2-b1) + 1)
            bgBins.append((min(b1,b2), max(b1,b2)))
            
        if numBgBins > 0:
            bgFactor = -float(numFgBins) / float(numBgBins)

            for b in bgBins:
                tmp = projector("proj_tmp", b[0], b[1], "e")
                ROOT.SetOwnership(tmp, True)
                rhist.Add(tmp, bgFactor)
        
        hist = CutHistogram(rhist, axis, regionMarkers)
        hist.typeStr = "cut"
        return hist

######
# HACK for testing until low-level object is implemented
import copy

class MHisto2D(Histo2D):
    def __init__(self):
        self.projHisto = FileHistogram("test/mat/mat.prx")
        self.projHisto.typeStr = "Projection"
        self.cutHisto = FileHistogram("test/mat/cut.spc")
        self.cutHisto.typeStr = "Cut spectrum"
        
    @property
    def xproj(self):
        return copy.copy(self.projHisto)
        
    @property
    def yproj(self):
        return copy.copy(self.projHisto)
        
    def ExecuteCut(self, regionMarkers, bgMarkers, axis):
        return copy.copy(self.cutHisto)
#####

