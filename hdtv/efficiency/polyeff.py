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

from math import pow

from ROOT import TF1, TF2
from uncertainties.umath import exp, log

from hdtv.util import Pairs

from .efficiency import _Efficiency


class PolyEff(_Efficiency):
    """
    'Polynom' efficiency

    Internally working on double logarithmic E and eff scale

    """

    def __init__(self, pars=None, degree=4, norm=False):
        self.name = "Polynom"
        self.id = self.name + "_" + hex(id(self))
        self._degree = degree

        # Building root function string
        TFString = "[0] * ([1]"

        for i in range(2, degree + 2):
            TFString += " + [%d]*x^%d" % (i, i - 1)

        TFString += ")"

        self.TF1 = TF1(self.id, TFString, 0, 0)
        _Efficiency.__init__(self, num_pars=degree + 1, pars=pars, norm=norm)

        # Builing derivatives dEff/dParameter[x]

        # See
        # http://stackoverflow.com/questions/2295290/what-do-lambda-function-closures-capture-in-python#2295372
        # http://code.activestate.com/recipes/502271/
        # for this strange constructor
        def dEff_dP(i):
            return lambda logE, fPars: self.norm * pow(logE, i)

        for i in range(degree + 1):
            self._dEff_dP[i] = dEff_dP(i)

    def _set_fitInput(self, fitPairs):
        ln_fitPairs = Pairs(conv_func=log)

        for p in fitPairs:
            ln_fitPairs.add(p[0], p[1])

        _Efficiency._set_fitInput(self, ln_fitPairs)

    def _get_fitInput(self):
        fitPairs = Pairs(conv_func=exp)

        for p in self._fitInput:
            fitPairs.add(p[0], p[1])

        return fitPairs

    fitInput = property(_get_fitInput, _set_fitInput)

    def normalize(self):
        # Normalize the efficiency function

        try:
            self.norm = 1.0 / exp(
                self.TF1.GetMaximum(
                    min(p[0] for p in self._fitInput),
                    max(p[0] for p in self._fitInput),
                )
            )
        except ZeroDivisionError:
            self.norm = 1.0

        self.TF1.SetParameter(0, self.norm)
        normfunc = TF2("norm_" + hex(id(self)), "[0]*y")
        normfunc.SetParameter(0, self.norm)
        self.TGraph.Apply(normfunc)

    def value(self, E):
        try:
            value = E.value
        except AttributeError:
            value = E

        return self.norm * exp(self.TF1.Eval(log(value), 0.0, 0.0, 0.0))

    def error(self, E):
        # TODO: this need checking
        try:
            value = E.value
        except AttributeError:
            value = E

        ln_err = _Efficiency.error(self, log(value))
        ln_eff = self.TF1.Eval(log(value), 0.0, 0.0, 0.0)
        tmp1 = self.norm * exp(ln_eff + ln_err)
        tmp2 = self.norm * exp(ln_eff - ln_err)

        error = abs(tmp1 - tmp2) / 2.0

        return self.norm * error
