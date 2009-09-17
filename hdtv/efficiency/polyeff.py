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

from . efficiency import _Efficiency
from ROOT import TF1
import math

class PolyEff(_Efficiency):
    """
    'Polynom' efficiency
    
    """
    def __init__(self, pars = list(), norm = True):
        
        self.name = "Polynom"
        self.id = self.name + "_" + hex(id(self))

        self.TF1 = TF1(self.id, "[0] * ([1] + [2] * x + [3] * x^2 + [4] * x^3 + [5] * x^4)", 0, 0) # [0] is normalization factor
        
        _Efficiency.__init__(self, num_pars = 5, pars = pars, norm = norm)

        # List of derivatives
        self._dEff_dP[0] = lambda E, fPars: self.norm 
        self._dEff_dP[1] = lambda E, fPars: self.norm * E
        self._dEff_dP[2] = lambda E, fPars: self.norm * 2 * fPars[2] * E 
        self._dEff_dP[3] = lambda E, fPars: self.norm * 3 * fPars[3] * math.pow(E, 2)
        self._dEff_dP[4] = lambda E, fPars: self.norm * 4 * fPars[4] * math.pow(E, 3)
