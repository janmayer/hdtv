from . efficiency import _Efficiency
from ROOT import TF1
import math

class WunderEff(_Efficiency):
    """
    'Wunder' efficiency formula.
    
    eff(E) = (a*E + b/E) * exp(c*E + d/E) 
    """
    def __init__(self, pars=list()):
        
        self.id = "wundereff_" + hex(id(self))
        self.TF1 = TF1(self.id, "([0]*x + [1]/x) * exp([2]*x + [3]/x)", 0, 0)
        
        _Efficiency.__init__(self, num_pars=4, pars=pars)
        
        # Efficiency function
        self._Eff = lambda E, fPars: (fPars[0]*E + fPars[1]/E) * math.exp(fPars[2]*E + fPars[3]/E)
        
        # List of derivatives
        self._dEff_dP = [None, None, None, None]
        
        self._dEff_dP[0] = lambda E, fPars: E * math.exp(fPars[2]*E + fPars[3]/E)    # dEff/da
        self._dEff_dP[1] = lambda E, fPars: 1/E * math.exp(fPars[2]*E + fPars[3]/E)  # dEff/db
        self._dEff_dP[2] = lambda E, fPars: (fPars[0]*E + fPars[1]/E) * E * math.exp(fPars[2]*E + fPars[3]/E)  # dEff/dc
        self._dEff_dP[3] = lambda E, fPars: (fPars[0]*E + fPars[1]/E) * 1/E * math.exp(fPars[2]*E + fPars[3]/E)  # dEff/dd
        