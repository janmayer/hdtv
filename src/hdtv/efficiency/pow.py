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

from ROOT import TF1

from .efficiency import _Efficiency


class PowEff(_Efficiency):
    """
    'Power function' efficiency formula.

    eff(E) = a + b * pow(E,-c)
    """

    def __init__(self, pars=None, norm=True):
        self.name = "Power"
        self.id = self.name + "_" + hex(id(self))
        #                       "( N *( a + b *E ^( -c )))"
        # [0] is fixed
        self.TF1 = TF1(self.id, "([0]*([1]+[2]*x**(-[3])))", 0, 0)

        _Efficiency.__init__(self, num_pars=4, pars=pars, norm=norm)

        # List of derivatives
        self._dEff_dP = [None, None, None, None, None]
        self._dEff_dP[0] = lambda E, fPars: self.norm * fPars[1] + fPars[2] * pow(
            E, -fPars[3]
        )  # dEff/dN
        self._dEff_dP[1] = lambda E, fPars: self.norm * fPars[0]  # dEff/da
        self._dEff_dP[2] = (
            lambda E, fPars: self.norm * fPars[0] * pow(E, -fPars[3])
        )  # dEff/db
        self._dEff_dP[3] = (
            lambda E, fPars: self.norm
            * fPars[0]
            * fPars[2]
            * (-fPars[3])
            * pow(E, (-fPars[3] - 1))
        )  # dEff/dc
