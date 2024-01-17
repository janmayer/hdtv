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

import array
import string
from math import sqrt

from ROOT import TF2, TGraphErrors, TVirtualFitter
from uncertainties import ufloat

import hdtv.ui
from hdtv.util import Pairs, TxtFile


class _Efficiency:
    def __init__(self, num_pars=0, pars=None, norm=True):
        pars = pars or []

        self._numPars = num_pars
        self.parameter = pars
        self.fCov = [
            [None for j in range(self._numPars)] for i in range(self._numPars)
        ]  # Simple matrix replacement
        self._dEff_dP = []
        self.TGraph = TGraphErrors()

        # Normalization factors
        self._doNorm = norm
        self.norm = 1.0
        self.TF1.FixParameter(0, self.norm)  # Normalization
        self.TF1.SetRange(0, 10000)  # Default range for efficiency function

        self._fitInput = Pairs(lambda x: ufloat(x, 0))

        #         if self.parameter: # Parameters were given
        #             map(lambda i: self.TF1.SetParameter(i + 1, self.parameter[i]), range(1, len(pars))) # Set initial parameters
        #         else:
        #             self.parameter = [None for i in range(1, self._numPars + 1)]
        #
        self.TF1.SetParName(0, "N")  # Normalization

        for i in range(num_pars):
            self._dEff_dP.append(None)
            if num_pars <= len(string.ascii_lowercase):
                self.TF1.SetParName(i + 1, string.ascii_lowercase[i])

    def _getParameter(self):
        """
        Get parameter of efficiency function
        """
        pars = []
        for i in range(self._numPars):
            pars.append(self.TF1.GetParameter(i))

        return pars

    def _setParameter(self, pars):
        """
        Set parameter for efficiency function
        """
        for i in range(self._numPars):
            try:
                self.TF1.SetParameter(i, pars[i])
            except IndexError:
                self.TF1.SetParameter(i, 0)

    parameter = property(_getParameter, _setParameter)

    def __call__(self, E):
        value = self.value(E)
        try:
            error = self.error(E)
        except TypeError:
            error = None
        return ufloat(value, error)

    def _set_fitInput(self, fitPairs):
        self._fitInput = fitPairs

        for i in range(len(self._fitInput)):
            p = self._fitInput[i]
            try:
                e_nominal_value = p[0].nominal_value
                e_std_dev = p[0].std_dev
            except AttributeError:
                e_nominal_value = float(p[0])
                e_std_dev = 0.0

            try:
                eff_nominal_value = p[1].nominal_value
                eff_std_dev = p[1].std_dev
            except AttributeError:
                eff_nominal_value = float(p[1])
                eff_std_dev = 0.0

            self.TGraph.SetPoint(i, e_nominal_value, eff_nominal_value)
            self.TGraph.SetPointError(i, e_std_dev, eff_std_dev)

    def _get_fitInput(self):
        return self._fitInput

    fitInput = property(_get_fitInput, _set_fitInput)

    def fit(self, fitPairs=None, quiet=True):
        """
        Fit efficiency curve to values given by 'fitPairs' which should be a list
        of energy<->efficiency pairs. (See hdtv.util.Pairs())

        'energies' and 'efficiencies' may be a list of ufloats
        """
        # TODO: Unify this with the energy calibration fitter
        if fitPairs is not None:
            # self.fitInput = fitPairs
            self._fitInput = fitPairs

        E = array.array("d")
        delta_E = array.array("d")
        eff = array.array("d")
        delta_eff = array.array("d")
        EN = array.array("d")
        effN = array.array("d")

        #        map(energies.append(self.fitInput[0]), self.fitInput)
        #        map(efficiencies.append(self.fitInput[1]), self.fitInput)
        hasXerrors = False
        # Convert energies to array needed by ROOT
        try:
            [E.append(x[0].nominal_value) for x in self._fitInput]
            [delta_E.append(x[0].std_dev) for x in self._fitInput]
            [EN.append(0.0) for x in self._fitInput]
            hasXerrors = True
        except AttributeError:  # energies does not seem to be ufloat list
            [E.append(x[0]) for x in self._fitInput]
            [delta_E.append(0.0) for x in self._fitInput]

        # Convert efficiencies to array needed by ROOT
        try:
            [eff.append(x[1].nominal_value) for x in self._fitInput]
            [delta_eff.append(x[1].std_dev) for x in self._fitInput]
            [effN.append(0.0) for x in self._fitInput]
        except AttributeError:  # energies does not seem to be ufloat list
            [eff.append(x[1]) for x in self._fitInput]
            [delta_eff.append(0.0) for x in self._fitInput]

        # if fit has errors we first fit without errors to get good initial values
        # if hasXerrors == True:
        # print "Fit parameter without errors included:"
        # self.TGraphWithoutErrors = TGraphErrors(len(E), E, eff, EN, effN)
        # fitWithoutErrors = self.TGraphWithoutErrors.Fit(self.id, "SF")

        hdtv.ui.msg("Fit parameter with errors included:")

        # Preliminary normalization
        #        if self._doNorm:
        #            self.norm = 1 / max(efficiencies)
        #            for i in range(len(eff)):
        #                eff[i] *= self.norm
        #                delta_eff[i] *= self.norm

        # self.TF1.SetRange(0, max(E) * 1.1)
        # self.TF1.SetParameter(0, 1) # Unset normalization for fitting

        self.TGraph = TGraphErrors(len(E), E, eff, delta_E, delta_eff)

        # Do the fit
        fitopts = "0"  # Do not plot

        if hasXerrors:
            # We must use the iterative fitter (minuit) to take x errors
            # into account.
            fitopts += "F"
            hdtv.ui.info(
                "switching to non-linear fitter (minuit) for x error weighting"
            )
        if quiet:
            fitopts += "Q"

        fitopts += (
            "S"  # Additional fitinfo returned needed for ROOT5.26 workaround below
        )
        fitreturn = self.TGraph.Fit(self.id, fitopts)

        try:
            # Workaround for checking the fitstatus in ROOT 5.26 (TFitResultPtr
            # does not cast properly to int)
            fitstatus = fitreturn.Get().Status()
        except AttributeError:  # This is for ROOT <= 5.24, where fit returns an int
            fitstatus = int(fitreturn)

        if fitstatus != 0:
            # raise RuntimeError, "Fit failed"
            hdtv.ui.msg("Fit failed")

        #         # Final normalization
        #         if self._doNorm:
        #             self.normalize()

        # Get parameter
        for i in range(self._numPars):
            self.parameter[i] = self.TF1.GetParameter(i)

        # Get covariance matrix
        tvf = TVirtualFitter.GetFitter()
        ##        cov = tvf.GetCovarianceMatrix()
        for i in range(self._numPars):
            for j in range(self._numPars):
                self.fCov[i][j] = tvf.GetCovarianceMatrixElement(i, j)
        ##                 self.fCov[i][j] = cov[i * self._numPars + j]

        return self.parameter

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
            value = E.nominal_value
        except AttributeError:
            value = E

        return self.TF1.Eval(value)

    def error(self, E):
        """
        Calculate error using the covariance matrix via:

          delta_Eff = sqrt((dEff_dP[0], dEff_dP[1], ... dEff_dP[num_pars]) x cov x (dEff_dP[0], dEff_dP[1], ... dEff_dP[num_pars]))

        """
        try:
            value = E.nominal_value
        except AttributeError:
            value = E

        if not self.fCov or (len(self.fCov) != self._numPars):
            raise ValueError("Incorrect size of covariance matrix")

        res = 0.0

        # Do matrix multiplication
        for i in range(self._numPars):
            tmp = 0.0
            for j in range(self._numPars):
                tmp += self._dEff_dP[j](value, self.parameter) * self.fCov[i][j]

            res += self._dEff_dP[i](value, self.parameter) * tmp

        return sqrt(res)

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
            raise RuntimeError("Incorrect number of parameters found in file")

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
            val_row = [float(s) for s in line.split()]
            if len(val_row) != self._numPars:
                raise RuntimeError("Incorrect format of parameter error file")
            vals.append(val_row)

        if len(vals) != self._numPars:
            raise RuntimeError("Incorrect format of parameter error file")

        self.fCov = vals

    def load(self, parfile, covfile=None):
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

        for i in range(self._numPars):
            line = ""
            for j in range(self._numPars):
                line += str(self.fCov[i][j]) + " "
            file.lines.append(line.strip())

        file.write()

    def save(self, parfile, covfile=None):
        """
        Save parameter and covariance matrix to files
        """
        # Write paramter
        self.savePar(parfile)

        # Write covariance matrix
        if covfile is not None:
            self.saveCov(covfile)
