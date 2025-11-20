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

import math

from ROOT import TF1

from .efficiency import _Efficiency


class ExpEff(_Efficiency):
    """
    'Exponential' efficiency formula.

    eff(E) = a * exp(-b*E) + c * exp(-d*E)
    """

    def __init__(self, pars=None, norm=True):
        self.name = "Exponential"
        self.id = self.name + "_" + hex(id(self))
        #                       "( N *( a *exp(- b *E)+ c *exp(- d *E)))"
        # [0] is fixed
        self.TF1 = TF1(self.id, "([0]*([1]*exp(-[2]*x)+[3]*exp(-[4]*x)))", 0, 0)

        _Efficiency.__init__(self, num_pars=5, pars=pars, norm=norm)

        # List of derivatives
        self._dEff_dP = [None, None, None, None, None]
        self._dEff_dP[0] = lambda E, fPars: self.norm * (
            fPars[1] * math.exp((-1.0) * fPars[2] * E)
            + fPars[3] * math.exp((-1.0) * fPars[4] * E)
        )  # dEff/dN
        self._dEff_dP[1] = (
            lambda E, fPars: self.norm * fPars[0] * math.exp((-1.0) * fPars[2] * E)
        )  # dEff/da
        self._dEff_dP[2] = (
            lambda E, fPars: self.norm
            * (-1.0)
            * fPars[0]
            * fPars[1]
            * E
            * math.exp((-1.0) * fPars[2] * E)
        )  # dEff/db
        self._dEff_dP[3] = (
            lambda E, fPars: self.norm * fPars[0] * math.exp((-1.0) * fPars[4] * E)
        )  # dEff/dc
        self._dEff_dP[4] = (
            lambda E, fPars: self.norm
            * (-1.0)
            * fPars[0]
            * fPars[3]
            * E
            * math.exp((-1.0) * fPars[4] * E)
        )  # dEff/dd
