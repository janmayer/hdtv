# -*- coding: utf-8 -*-

from . common import *

class PGAAGamma(Gamma):
    """
    Store data about PGAA gammas
    
    k0_comp is the comparator element for k0 values which k0 should be normed to 1.0
        given as tuple (Z, A)
    """
    k0_norm = None
    
    def __init__(self, nuclide, energy, sigma, intensity, halflife, k0_comp):
        
        super(PGAAGamma, self).__init__(nuclide, energy, sigma, intensity)
        self.halflife = halflife
        if nuclide == Nuclides(k0_comp[0], k0_comp[1]) and not PGAAGamma.k0_norm:
            PGAAGamma.k0_norm = 1.0 / self.getk0(isNorm = True) # Normalize reference element to k0=1.0

            
    def getk0(self, isNorm = False):
        
        if isNorm:   
            k0 = self.sigma / self.nuclide.element.M
        else:
            try:
                k0 = (self.sigma / self.nuclide.element.M) * PGAAGamma.k0_norm
            except TypeError:
                k0 = None
        return k0 

    k0 = property(getk0)
    
    def __str__(self):
        
        text = str()
        text += super(PGAAGamma, self).__str__()
        text += "k0:        " + str(self.k0) + "\n"
        return text


class _PGAAlib_IKI2000(GammaLib):
    """
    PGAA library of the Institute of Isotopes, Hungarian Academy of Sciences, Budapest
    """
    def __init__(self, csvfile=os.path.join(hdtv.datadir, "PGAAlib-IKI2000.dat"), has_header=True, k0_comp=(1, 1)):
    
        super(_PGAAlib_IKI2000, self).__init__()
        
        file = open(csvfile, "rb")
        
        reader = csv.reader(file)
        
        if has_header:
            reader.next()
        
        try:
            for line in reader:
                Z = int(line[0])
                A = int(line[1]) 
                energy = ErrValue(float(line[2]), float(line[3]))
                sigma = ErrValue(float(line[4]), float(line[5]))
                intensity = ErrValue(float(line[6]), None)/100.0
                try:
                    halflife = ErrValue(float(line[7]), None)
                except ValueError:
                    halflife = ErrValue(None, None)
                gamma = PGAAGamma(Nuclides(Z, A), energy, sigma, intensity, halflife, k0_comp)
                self.append(gamma)
        except csv.Error, e:
            print ('file %s, line %d: %s' % (filename, reader.line_num, e))
        finally:
            file.close()

    
PGAAlib_IKI2000 = _PGAAlib_IKI2000()
