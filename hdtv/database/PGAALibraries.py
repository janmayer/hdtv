# -*- coding: utf-8 -*-
# PGAA database from Institute of Isotopes, Hungarian Academey of Science, Budapest

from hdtv.database.common import *
import hdtv.ui

class PGAAGamma(Gamma):
    """
    Store data about PGAA gammas
    
    k0_comp is the comparator element for k0 values which k0 should be normed to 1.0
        given as tuple (Z, A) (default: 1-H)
    """
    k0_norm = None
    __slots__ = ("ID", "nuclide", "energy", "sigma", "intensity", "halflife", "_k0")

    def __init__(self, nuclide, energy, sigma = None, intensity = None, k0 = None, halflife = None, k0_comp = (1, 1)):
        
        super(PGAAGamma, self).__init__(nuclide, energy, sigma, intensity)
        self.halflife = halflife
        self._k0 = k0 # TODO
        if nuclide == Nuclides(k0_comp[0], k0_comp[1])[0] and not PGAAGamma.k0_norm:
            # Normalize reference element to k0=1.0
            PGAAGamma.k0_norm = 1.0 / self.getk0(isNorm = True) 

            
    def getk0(self, isNorm = False):
        
        if self._k0 is None: # k0 was not given: we have to calculate
            if isNorm:   
                k0 = self.sigma / self.nuclide.element.m
            else:
                try:
                    k0 = (self.sigma / self.nuclide.element.m) * PGAAGamma.k0_norm
                except TypeError:
                    k0 = None
            return k0
        else:
            return self._k0

    k0 = property(getk0)
    
    def __str__(self):
        
        text = str()
        text += super(PGAAGamma, self).__str__()
        text += "k0:        " + str(self.k0) + "\n"
        return text


class PGAAlib_IKI2000(GammaLib):
    """
    PGAA library of the Institute of Isotopes, Hungarian Academy of Sciences, Budapest
    """
    def __init__(self, csvfile = os.path.join(hdtv.datadir, "PGAAlib-IKI2000.dat"), has_header = True, k0_comp = (1, 1)):
    
        super(PGAAlib_IKI2000, self).__init__()

        self.fOrderedParamKeys = ["z", "a", "symbol", "energy", "intensity", "sigma", "k0", "halflife"] 
        self.fOrderedHeader = ["Z", "A", "El", "Energy/(keV)", "Intensity", "Sigma/(b)", "k0", "Halflife/(s)"] # Header for table printout
        # Conversion functions for parameter
        self.fParamConv = {"symbol": str, "z": int , "a": int, "energy": float, "sigma": float, "intensity": float, "halflife": float, "k0": float}
        self.name = "PGAAlib_IKI2000"
        self.description = "PGAA database, Inst. of Isotopes, Hungarian Academey of Science" 
        self.csvfile = csvfile
        self._has_header = has_header
        self.k0_comp = k0_comp
        
    def open(self):
        
        if self.opened:
            return True

        datfile = open(self.csvfile, "rb")
        
        reader = csv.reader(datfile)
        
        if self._has_header:
            reader.next()
        
        try:
            for line in reader:
                Z = int(line[0])
                A = int(line[1]) 
                energy = ErrValue(float(line[2]), float(line[3]))
                sigma = ErrValue(float(line[4]), float(line[5]))
                intensity = ErrValue(float(line[6]), None) / 100.0
                try:
                    halflife = ErrValue(float(line[7]), None)
                except ValueError:
                    halflife = ErrValue(None, None)
                gamma = PGAAGamma(Nuclides(Z, A)[0], energy, sigma = sigma, intensity = intensity, halflife = halflife, k0_comp = self.k0_comp)
                self.append(gamma)
        except csv.Error, e:
            hdtv.ui.error('file %s, line %d: %s' % (self.csvfile, reader.line_num, e))
        else:
            self.opened = True
        finally:
            datfile.close()
    
        
class PromptGammas(GammaLib):
    """
    Extensive IAEA Prompt-Gamma library
    """
    def __init__(self, csvfile = os.path.join(hdtv.datadir, "PromptGammas.dat"), has_header = True, k0_comp = (1, 1)):
    
        super(PromptGammas, self).__init__()

        self.fOrderedParamKeys = ["z", "a", "symbol", "energy", "sigma", "k0"]
        self.fOrderedHeader = ["Z", "A", "El", "Energy/(keV)", "Sigma/(b)", "k0"] # Header for table printout
        # Conversion functions for parameter
        self.fParamConv = {"symbol": str, "z": int , "a": int, "energy": float, "sigma": float, "k0": float}
        self.name = "PromptGammas"
        self.description = "Extensive Prompt-Gamma library" 
        self.csvfile = csvfile
        self._has_header = has_header
        self.k0_comp = k0_comp
        
    def open(self):
               
        if self.opened:
            return True
        
        datfile = open(self.csvfile, "rb")
        
        reader = csv.reader(datfile)
        
        if self._has_header:
            reader.next()
        
        try:
            for line in reader:
                A = int(line[0])
                Z = int(line[1])
                energy = ErrValue(line[2])
                sigma = ErrValue(line[3])
                k0 = ErrValue(line[4])
                gamma = PGAAGamma(Nuclides(Z, A), energy, sigma = sigma, k0 = k0, k0_comp = self.k0_comp)
                self.append(gamma)
        except csv.Error, e:
            hdtv.ui.error('file %s, line %d: %s' % (self.csvfile, reader.line_num, e))
        else:
            self.opened = True
        finally:
            datfile.close()
