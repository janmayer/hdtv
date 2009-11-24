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
from hdtv.spectrum import Histogram

# Don't add created spectra to the ROOT directory
ROOT.TH1.AddDirectory(ROOT.kFALSE)

class Histo2D(object):
    def __init__(self):
        pass
    
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
    def xproj(self):
        if self._prx == None:
            name = self.rhist.GetName() + "_prx"
            rprx = self.rhist.ProjectionX(name, 0, -1, "e")
            self._prx = Histogram(rprx)
    
        return self._prx
        
    @property
    def yproj(self):
        if self._pry == None:
            name = self.rhist.GetName() + "_pry"
            rpry = self.rhist.ProjectionY(name, 0, -1, "e")
            self._pry = Histogram(rpry)
        
        return self._pry
    
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
        
        name = self.rhist.GetName() + "_pro"
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
        
        return Histogram(rhist)

######
# HACK for testing until low-level object is implemented
import copy
from hdtv.spectrum import FileHistogram

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

