from __future__ import with_statement
from hdtv.util import ErrValue
from ROOT import TF1, TGraphErrors, TVirtualFitter
import math
import array
import string

class _Efficiency(object):
    
    def __init__(self, num_pars=0, pars=list(), norm=True):
        
         self._numPars = num_pars 
         self.fPars = pars
         self.fCov = [[None for j in range(self._numPars)] for i in range(self._numPars)] # Simple matrix replacement

         self._dEff_dP = list()
         self.TGraph = None 
         
         # Normalization factors
         self._doNorm = norm
         self.norm = 1.0
         self.TF1.FixParameter(0, self.norm) # Normalization

         if self.fPars: # Parameters were given
             map(lambda i: self.TF1.SetParameter(i+1, self.fPars[i]), range(1, len(pars))) # Set initial parameters
         else:
             self.fPars = [None for i in range(1, self._numPars + 1)]
             
         self.TF1.SetParName(0, "N") # Normalization
         
         for i in range(0, num_pars):
             self._dEff_dP.append(None)
             if num_pars <= len(string.ascii_lowercase):
                self.TF1.SetParName(i + 1, string.ascii_lowercase[i])
 
    def __call__(self, E):
        value = self.value(E)
        error = self.error(E)
        return ErrValue(value, error)

    def fit(self, energies, efficiencies, energy_errors=None, efficiency_errors=None, quiet=True):
        """
        Fit efficiency curve to values given by 'energies' and 'efficiencies'
        
        'energies' and 'efficiencies' may be a list of hdtv.util.ErrValues()
        """
        E = array.array("d")
        delta_E = array.array("d")
        eff = array.array("d")
        delta_eff = array.array("d")
        
        # Convert energies to array needed by ROOT
        try:
            map(lambda x: E.append(x.value), energies)
            map(lambda x: delta_E.append(x.error), energies)
        except AttributeError: # energies does not seem to be ErrValue list
            map(E.append, energies)
            if energy_errors:
                map(lambda x: delta_E.append(x), energy_errors)
            else:
                map(lambda x: delta_E.append(0.0), energies)
        # Convert efficiencies to array needed by ROOT
        try:
            map(lambda x: eff.append(x.value), efficiencies)
            map(lambda x: delta_eff.append(x.error), efficiencies)
        except AttributeError: # efficiencies does not seem to be ErrValue list
            map(eff.append, efficiencies)
            if energy_errors:
                map(lambda x: delta_eff.append(x), efficiency_errors)
            else:
                map(lambda x: delta_eff.append(0.0), efficiencies)
        
        # Preliminary normalization
#        if self._doNorm:
#            self.norm = 1 / max(efficiencies)
#            for i in range(len(eff)):
#                eff[i] *= self.norm
#                delta_eff[i] *= self.norm
        
        self.TF1.SetRange(0, max(energies) * 1.1)
        self.TGraph = TGraphErrors(len(energies), E, eff, delta_E, delta_eff)
        
        
        # Do the fit
        fitopts = "N"
        if quiet:
            fitopts += "Q"

        self.TGraph.Fit(self.id, fitopts)

        # Final normalization
        if self._doNorm:
            self.norm = 1 / self.TF1.GetMaximum(0.0, 0.0)
            for i in range(len(eff)):
                eff[i] *= self.norm
                delta_eff[i] *= self.norm
                self.TGraph = TGraphErrors(len(energies), E, eff, delta_E, delta_eff)
            
            self.normalize()

        # Get parameter
        for i in range(self._numPars):
            self.fPars[i] = self.TF1.GetParameter(i + 1)

        # Get covariance matrix
        tvf = TVirtualFitter.GetFitter()
##        cov = tvf.GetCovarianceMatrix()
        for i in range(0, self._numPars):
            for j in range(0, self._numPars):
                self.fCov[i][j] = tvf.GetCovarianceMatrixElement(i, j)
##                 self.fCov[i][j] = cov[i * self._numPars + j]

    def normalize(self):
        if self._doNorm:
            self.norm = 1.0 / self.TF1.GetMaximum(0.0, 0.0)
            self.TF1.SetParameter(0, self.norm)

    def value(self, E):
#        E = float(E) # Make sure E is treated as float, not as int
#        if not self.fPars or len(self.fPars) != self._numPars:
#            raise ValueError, "Incorrect number of parameters"
#        return self._Eff(E, self.fPars)
        return self.TF1.Eval(E, 0.0, 0.0, 0.0)
    
    def error(self, E):
        """
        Calculate error using the covariance matrix via:
        
          delta_Eff = sqrt((dEff_dP[0], dEff_dP[1], ... dEff_dP[num_pars]) x cov x (dEff_dP[0], dEff_dP[1], ... dEff_dP[num_pars]))
             
        """
        
        if not self.fCov or len(self.fCov) != self._numPars:
            raise ValueError, "Incorrect size of covariance matrix"
        
        res = 0.0
        E = float(E) # Make sure E is treated as float, not as int
        
        # Do matrix multiplication
        for i in range(0, self._numPars):
            tmp = 0.0   
            for j in range(0, self._numPars):
                tmp += (self._dEff_dP[j](E, self.fPars) * self.fCov[i][j])
            
            res += (self._dEff_dP[i](E, self.fPars) * tmp)
        
        return math.sqrt(res)
    
    def fromfile(self, parfile, covfile=None):
        """
        Read parameter and covariance matrix from file
        """
        vals = []
    
        with open(parfile) as f:
            for line in f:
                line = line.strip()
                if line != '':
                    vals.append(float(line))
                    
        if len(vals) != self._numPars:
            raise RuntimeError, "Incorrect number of parameters found in file"
        
        self.fPars = vals
        for i in range(self._numPars):
            self.TF1.SetParameter(i + 1, self.fPars[i])
            
        if covfile:
            vals = []

            with open(covfile) as f:
                for line in f:
                    line = line.strip()
                    if line != '':
                        val_row = map(lambda s: float(s), line.split())
                        if len(val_row) != self._numPars:
                            raise RuntimeError, "Incorrect format of parameter error file"
                        vals.append(val_row)

            if len(vals) != self._numPars:
                raise RuntimeError, "Incorrect format of parameter error file"
                
            self.fCov = vals
