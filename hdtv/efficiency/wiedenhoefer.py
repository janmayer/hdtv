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

class WiedenhoeferEff(_Efficiency):
    """
    'Wiedenhoefer' efficiency formula.
    
    eff(E) = a * (E - c+ d * exp(-e * E))^-b 
    """
    
    def __init__(self, pars=list(), norm=True):
        self.fPars = None

        self.id = "wiedenhoefereff_" + hex(id(self))
        self.TF1 = TF1(self.id, "[0]*([1]*pow(x - [3] + [4] * exp(-[5] *x), -[2]))", 0, 0) # [0] is normalization factor
        
        _Efficiency.__init__(self, num_pars=5, pars=pars, norm=norm)

        # Efficiency function
        self._Eff = lambda E, fPars: self.norm * fPars[0] * math.pow((E - fPars[2] + fPars[3] * math.exp(-fPars[4] * E)), -fPars[1])
        # Alternative representation:
        #  self._Eff = lambda E, fPars: fPars[0] * math.exp(-fPars[1] * math.log(E - fPars[2] + fPars[3] * math.exp(-fPars[4]*E)))
        
        # List of derivatives
        self._dEff_dP = [None, None, None, None, None]
        self._dEff_dP[0] = lambda E, fPars: self.norm * self.value(E) / fPars[0]    # dEff/da 
        self._dEff_dP[1] = lambda E, fPars: self.norm * (- self.value(E)) * math.log(E - fPars[2] + fPars[3] * math.exp(-fPars[4]*E)) # dEff/db
        self._dEff_dP[2] = lambda E, fPars: self.norm * self.value(E) * fPars[1] / (E - fPars[2] + fPars[3] * math.exp(-fPars[4]*E))  # dEff/dc
        self._dEff_dP[3] = lambda E, fPars: self.norm * (- self.value(E)) * fPars[1] / (E - fPars[2] + fPars[3] * math.exp(-fPars[4]*E)) * math.exp(-fPars[4]*E) # dEff/dd 
        self._dEff_dP[4] = lambda E, fPars: self.norm * self.value(E) * fPars[1] / (E - fPars[2] + fPars[3] * math.exp(-fPars[4]*E)) * fPars[3] * math.exp(-fPars[4]*E) * fPars[4] # dEff/de
        	
    # Compatibility functions for old code
    def eff(self, E):
        return self.value(E)
    
    def effErr(self, E):
        return self.error(E)
