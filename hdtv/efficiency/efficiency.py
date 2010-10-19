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

from __future__ import with_statement
from hdtv.util import TxtFile, Pairs
from hdtv.errvalue import ErrValue
from ROOT import TF1, TF2, TGraphErrors, TVirtualFitter
import hdtv.ui

import math
import array
import string
import os

class _Efficiency(object):
    
    def __init__(self, num_pars = 0, pars = list(), norm = True):
    
        self._numPars = num_pars 
        self.parameter = pars
        self.fCov = [[None for j in range(self._numPars)] for i in range(self._numPars)] # Simple matrix replacement
        self._dEff_dP = list()
        self.TGraph = TGraphErrors() 
         
        # Normalization factors
        self._doNorm = norm
        self.norm = 1.0
        self.TF1.FixParameter(0, self.norm) # Normalization
        self.TF1.SetRange(0, 10000) # Default range for efficiency function
         
        self._fitInput = Pairs(ErrValue)
         
#         if self.parameter: # Parameters were given
#             map(lambda i: self.TF1.SetParameter(i + 1, self.parameter[i]), range(1, len(pars))) # Set initial parameters
#         else:
#             self.parameter = [None for i in range(1, self._numPars + 1)]
#             
        self.TF1.SetParName(0, "N") # Normalization
         
        for i in range(0, num_pars):
            self._dEff_dP.append(None)
            if num_pars <= len(string.ascii_lowercase):
                self.TF1.SetParName(i + 1, string.ascii_lowercase[i])
 
    def _getParameter(self):
        """
        Get parameter of efficiency function
        """
        pars = list()
        for i in range(self._numPars):
            pars.append(self.TF1.GetParameter(i + 1))
            
        return pars
        
    def _setParameter(self, pars):
        """
        Set parameter for efficiency function
        """
        for i in range(self._numPars):
            try:
                self.TF1.SetParameter(i + 1, pars[i])
            except IndexError:
                self.TF1.SetParameter(i + 1, 0)

    parameter = property(_getParameter, _setParameter)
 
    def __call__(self, E):
        value = self.value(E)
        error = self.error(E)
        return ErrValue(value, error)


    def _set_fitInput(self, fitPairs):
        
        self._fitInput = fitPairs
        
        for i in range(len(self._fitInput)):
            p = self._fitInput[i]
            try:
                values = [p[0].value, p[1].value]
                errors = [p[0].error, p[1].error]
            except AttributeError:
                values = [p[0], p[1]]
                errors = [0., 0.] 
                
            self.TGraph.SetPoint(i, values[0], values[1])
            self.TGraph.SetPointError(i, errors[0], errors[1])
        
        
    def _get_fitInput(self):
        return self._fitInput
        
    fitInput = property(_get_fitInput, _set_fitInput)
    
    def fit(self, fitPairs=None, quiet = True):
        """
        Fit efficiency curve to values given by 'fitPairs' which should be a list
        of energy<->efficiency pairs. (See hdtv.util.Pairs())
        
        'energies' and 'efficiencies' may be a list of hdtv.util.ErrValues()
        """
        # TODO: Unify this with the energy calibration fitter
        if fitPairs is not None:
            self.fitInput = fitPairs

        E = array.array("d")
        delta_E = array.array("d")
        eff = array.array("d")
        delta_eff = array.array("d")
        

#        map(energies.append(self.fitInput[0]), self.fitInput)
#        map(efficiencies.append(self.fitInput[1]), self.fitInput)
        hasXerrors = False
        # Convert energies to array needed by ROOT        
        try:
            map(lambda x: E.append(x[0].value), self.fitInput)
            map(lambda x: delta_E.append(x[0].error), self.fitInput)
            hasXerrors = True
        except AttributeError: # energies does not seem to be ErrValue list
            map(lambda x: E.append(x[0]), self.fitInput)
            map(lambda x: delta_E.append(0.0), self.fitInput)

        # Convert efficiencies to array needed by ROOT
        try:
            map(lambda x: eff.append(x[1].value), self.fitInput)
            map(lambda x: delta_eff.append(x[1].error), self.fitInput)
        except AttributeError: # energies does not seem to be ErrValue list
            map(lambda x: eff.append(x[1]), self.fitInput)
            map(lambda x: delta_eff.append(0.0), self.fitInput)

        # Preliminary normalization
#        if self._doNorm:
#            self.norm = 1 / max(efficiencies)
#            for i in range(len(eff)):
#                eff[i] *= self.norm
#                delta_eff[i] *= self.norm
        
        self.TF1.SetRange(0, max(E) * 1.1)
        self.TF1.SetParameter(0, 1) # Unset normalization for fitting

        self.TGraph = TGraphErrors(len(E), E, eff, delta_E, delta_eff)
        
        # Do the fit
        fitopts = "0" # Do not plot
        
        if hasXerrors:
            # We must use the iterative fitter (minuit) to take x errors
            # into account.
            fitopts += "F"
            hdtv.ui.info("switching to non-linear fitter (minuit) for x error weighting")
            
        if quiet:
            fitopts += "Q"
        
        if self.TGraph.Fit(self.id, fitopts) != 0:
            raise RuntimeError, "Fit failed"

        # Final normalization
        if self._doNorm:
            self.normalize()

        # Get parameter
        for i in range(self._numPars):
            self.parameter[i] = self.TF1.GetParameter(i + 1)

        # Get covariance matrix
        tvf = TVirtualFitter.GetFitter()
##        cov = tvf.GetCovarianceMatrix()
        for i in range(0, self._numPars):
            for j in range(0, self._numPars):
                self.fCov[i][j] = tvf.GetCovarianceMatrixElement(i, j)
##                 self.fCov[i][j] = cov[i * self._numPars + j]

    def normalize(self):
        # Normalize the efficiency funtion
        try:
            self.norm = 1.0 / self.TF1.GetMaximum(0.0, 0.0)
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
        
        return self.TF1.Eval(value, 0.0, 0.0, 0.0)
    
    def error(self, E):
        """
        Calculate error using the covariance matrix via:
        
          delta_Eff = sqrt((dEff_dP[0], dEff_dP[1], ... dEff_dP[num_pars]) x cov x (dEff_dP[0], dEff_dP[1], ... dEff_dP[num_pars]))
             
        """
        
        try:
            value = E.value
        except AttributeError:
            value = E
        
        if not self.fCov or len(self.fCov) != self._numPars:
            raise ValueError, "Incorrect size of covariance matrix"
        
        res = 0.0
        
        # Do matrix multiplication
        for i in range(0, self._numPars):
            tmp = 0.0   
            for j in range(0, self._numPars):
                tmp += (self._dEff_dP[j](value, self.parameter) * self.fCov[i][j])
            
            res += (self._dEff_dP[i](value, self.parameter) * tmp)
        
        return math.sqrt(res)
    
    def loadPar(self, parfile):
        """
        Read parameter from file
        """
        vals = []
    
        file = TxtFile(parfile)
        file.read()
        
        for line in file.lines:
            vals.append(float(line))
                
        if len(vals) != self._numPars:
            raise RuntimeError, "Incorrect number of parameters found in file"

        self.parameter = vals
        if self._doNorm:
            self.normalize()


    def loadCov(self, covfile):
        """
        Load covariance matrix from file
        """
        
        vals = []

        file = TxtFile(covfile)
        file.read()
        
        for line in file.lines:
            val_row = map(lambda s: float(s), line.split())
            if len(val_row) != self._numPars:
                raise RuntimeError, "Incorrect format of parameter error file"
            vals.append(val_row)

        if len(vals) != self._numPars:
            raise RuntimeError, "Incorrect format of parameter error file"
        
        self.fCov = vals


    def load(self, parfile, covfile = None):
        """
        Read parameter and covariance matrix from file
        """
        self.loadPar(parfile)
                    
        if covfile:
            self.loadCov(covfile)


    def savePar(self, parfile):
        """
        Save parameter to file
        """
        file = TxtFile(parfile, "w")
        
        for p in self.parameter:
            file.lines.append(str(p))
        
        file.write()
        
    def saveCov(self, covfile):
        """
        Save covariance matrix to file
        """
        file = TxtFile(covfile, "w")
        
        for i in range(0, self._numPars):
            line = ""
            for j in range(0, self._numPars):
                line += str(self.fCov[i][j]) + " "
            file.lines.append(line)

        file.write()
    
    
    def save(self, parfile, covfile = None):
        """
        Save parameter and covariance matrix to files
        """
        # Write paramter
        self.savePar(parfile)
        
        # Write covariance matrix
        if covfile is not None:
            self.saveCov(covfile)
        

