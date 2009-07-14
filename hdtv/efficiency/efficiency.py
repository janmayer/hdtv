from __future__ import with_statement
from hdtv.util import ErrValue
import math
import array


class _Efficiency(object):
    
    def __init__(self, num_pars=0, pars=list()):
        
         self._numPars = num_pars 
         self.fPars = pars
         self.fCov = list(list()) # Simple matrix replacement
         self._dEff_dP = list()

         for i in range(0, num_pars):
             self._dEff_dP.append(None)
 
    def __call__(self, E):
        value = self.value(E)
        error = self.error(E)
        return ErrValue(value, error)
        
    def value(self, E):
        E = float(E) # Make sure E is treated as float, not as int
        if not self.fPars or len(self.fPars) != self._numPars:
            raise ValueError, "Incorrect number of parameters"
        return self._Eff(E, self.fPars)
    
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
