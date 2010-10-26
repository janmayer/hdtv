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
from ROOT import TF1, TF2
from hdtv.errvalue import ErrValue, log, exp
from hdtv.util import Pairs
import math

class PolyEff(_Efficiency):
    """
    'Polynom' efficiency
    
    """
    def __init__(self, pars = list(), degree = 4, norm = False):

        self.name = "Polynom"
        self.id = self.name + "_" + hex(id(self))

        # Building root function string
        TFString = "[0]"

        for i in range(1, degree + 1):
            TFString += " + [%d]*x^%d" % (i, i)

#        TFString += ")"
        print "DEBUG TFstring:", TFString
#        self.TF1 = TF1(self.id, "[0] * ([1] + [2] * x + [3] * x^2 + [4] * x^3 + [5] * x^4)", 0, 0) # [0] is normalization factor
        self.TF1 = TF1(self.id, TFString, 0, 0)
        _Efficiency.__init__(self, num_pars = degree + 1 , pars = pars, norm = norm)

        # List of derivatives
        self._dEff_dP[0] = lambda E, fPars: 1. #lambda E, fPars: self.norm 

        # Builing derivatives dEff/dParameter[x]
        for i in range(1, degree + 1 ):
            self._dEff_dP[i] = lambda E, fPars: i * E * fPars[i] * math.pow(E, i - 1)
#        self._dEff_dP[1] = lambda E, fPars: self.norm * E
#        self._dEff_dP[2] = lambda E, fPars: self.norm * 2 * fPars[2] * E 
#        self._dEff_dP[3] = lambda E, fPars: self.norm * 3 * fPars[3] * math.pow(E, 2)
#        self._dEff_dP[4] = lambda E, fPars: self.norm * 4 * fPars[4] * math.pow(E, 3)


#    def __call__(self, E):
#        value = exp(self.value(log(E)))
#        try:
#            error = abs(value * self.error(log(E)))  # We have the error of log(eff). This is Gauss conversion to error of eff
#        except TypeError:
#            error = None
#        
#        return ErrValue(value, error)


    def _set_fitInput(self, fitPairs):

        print "DEBUG polyeff fitinput"
        ln_fitPairs = Pairs(conv_func = log)

        for p in fitPairs:
            print "adding pair p: ", p[0], str(p[1]), ":", log(p[0]), ":", log(p[1])
            ln_fitPairs.add(p[0], p[1])

        _Efficiency._set_fitInput(self, ln_fitPairs)


    def _get_fitInput(self):

        fitPairs = Pairs()

        for p in self._fitInput:
            fitPairs.add(exp(p[0]), exp(p[1]))

        return fitPairs

    fitInput = property(_get_fitInput, _set_fitInput)

    def normalize(self):
        # Normalize the efficiency funtion

        try:
            self.norm = 1.0 / exp(self.TF1.GetMaximum(min([p[0] for p in self._fitInput]), max([p[0] for p in self._fitInput])))
        except ZeroDivisionError:
            self.norm = 1.0

        print "DEBUG normalize polyeff with: ", self.norm, "TFMAX:", exp(self.TF1.GetMaximum(min([p[0] for p in self._fitInput]), max([p[0] for p in self._fitInput])))
#        self.TF1.SetParameter(0, self.norm)
#        normfunc = TF2("norm_" + hex(id(self)), "[0]*y")
#        normfunc.SetParameter(0, self.norm)
#        self.TGraph.Apply(normfunc)

    def value(self, E):
        try:
            value = E.value
        except AttributeError:
            value = E
        return self.norm * self.TF1.Eval(log(value), 0.0, 0.0, 0.0)
#        return self.norm * exp(self.TF1.Eval(log(value), 0.0, 0.0, 0.0))

    def error(self, E):

        try:
            value = E.value
        except AttributeError:
            value = E

        ln_err = _Efficiency.error(self, log(value))
        return ln_err
        tmp1 = self.TF1.Eval(log(value), 0.0, 0.0, 0.0) + ln_err
        tmp2 = self.TF1.Eval(log(value), 0.0, 0.0, 0.0) - ln_err
#        print "DEBUG logeff %s -- %s ->exp-> (%s -- %s)" % (tmp1, tmp2, exp(tmp1), exp(tmp2))
#        print "DEBUG ln_err:", ln_err, "selfvalue(E): ", self.value(E)
        error = abs(self.value(E) * ln_err)  # We have the error of log(eff). This is Gauss conversion to error of eff
#        print "DEBUG error, ", error
        return self.norm * error#(tmp1 - tmp2)/2. # TODO???
