from . efficiency import _Efficiency
from ROOT import TF1
import math

class WiedenhoeferEff(_Efficiency):
    """
    'Wunder' efficiency formula.
    
    eff(E) = a * (E - c+ d * exp(-e * E))^-b 
    """
    
    def __init__(self, pars=list()):
        self.fPars = None

        self.id = "wiedenhoefereff_" + hex(id(self))
        self.TF1 = TF1(self.id, "[0]*pow(x - [2] + [3] * exp(-[4] *x), -[1])", 0, 0)
        
        _Efficiency.__init__(self, num_pars=5, pars=pars)

        # Efficiency function
        self._Eff = lambda E, fPars: fPars[0] * math.pow((E - fPars[2] + fPars[3] * math.exp(-fPars[4] * E)), -fPars[1])
        # Alternative representation:
        #  self._Eff = lambda E, fPars: fPars[0] * math.exp(-fPars[1] * math.log(E - fPars[2] + fPars[3] * math.exp(-fPars[4]*E)))
        
        # List of derivatives
        self._dEff_dP = [None, None, None, None, None]
        self._dEff_dP[0] = lambda E, fPars: self.value(E) / fPars[0]    # dEff/da 
        self._dEff_dP[1] = lambda E, fPars: - self.value(E) * math.log(E - fPars[2] + fPars[3] * math.exp(-fPars[4]*E)) # dEff/db
        self._dEff_dP[2] = lambda E, fPars: self.value(E) * fPars[1] / (E - fPars[2] + fPars[3] * math.exp(-fPars[4]*E))  # dEff/dc
        self._dEff_dP[3] = lambda E, fPars: - self.value(E) * fPars[1] / (E - fPars[2] + fPars[3] * math.exp(-fPars[4]*E)) * math.exp(-fPars[4]*E) # dEff/dd 
        self._dEff_dP[4] = lambda E, fPars: self.value(E) * fPars[1] / (E - fPars[2] + fPars[3] * math.exp(-fPars[4]*E)) * fPars[3] * math.exp(-fPars[4]*E) * fPars[4] # dEff/de
        	
    # Compatibility functions for old code
    def eff(self, E):
        return self.value(E)
    
    def effErr(self, E):
        return self.error(E)