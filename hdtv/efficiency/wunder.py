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


class WunderEff(_Efficiency):
    """
    'Wunder' efficiency formula.

    eff(E) = (a*E + b/E) * exp(c*E + d/E)
    """

    def __init__(self, pars=None, norm=True):
        self.name = "Wunder"
        self.id = self.name + "_" + hex(id(self))
        #                        ( N  * ( a *E +  b /E) * exp( c *E +  d /E))
        # [0] is fixed
        self.TF1 = TF1(self.id, "([0] * ([1]*x + [2]/x) * exp([3]*x + [4]/x))", 0, 0)

        _Efficiency.__init__(self, num_pars=5, pars=pars, norm=norm)

        # List of derivatives
        self._dEff_dP = [None, None, None, None, None]
        self._dEff_dP[0] = (
            lambda E, fPars: self.norm
            * (fPars[1] * E + fPars[2] / E)
            * math.exp(fPars[3] * E + fPars[4] / E)
        )  # dEff/dN
        self._dEff_dP[0] = (
            lambda E, fPars: self.norm
            * fPars[0]
            * E
            * math.exp(fPars[3] * E + fPars[4] / E)
        )  # dEff/da
        self._dEff_dP[1] = (
            lambda E, fPars: self.norm
            * fPars[0]
            * 1.0
            / E
            * math.exp(fPars[3] * E + fPars[4] / E)
        )  # dEff/db
        self._dEff_dP[2] = (
            lambda E, fPars: self.norm
            * fPars[0]
            * (fPars[1] * E + fPars[2] / E)
            * E
            * math.exp(fPars[3] * E + fPars[4] / E)
        )  # dEff/dc
        self._dEff_dP[3] = (
            lambda E, fPars: self.norm
            * fPars[0]
            * (fPars[1] * E + fPars[1] / E)
            * 1.0
            / E
            * math.exp(fPars[3] * E + fPars[4] / E)
        )  # dEff/dd
