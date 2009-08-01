# -*- coding: utf-8 -*-
import hdtv.cmdline
from hdtv.util import ErrValue
import csv
import os
    
class _Element(object):
    """
    Store info about elements
    """
    
    __slots__ = ("id", "Z", "symbol", "name", "M")

    def __init__(self, Z, Symbol, Name=None, M=None):
        
        self.Z = Z
        self.symbol = Symbol    # Symbol of element (e.g. H)
        self.name = Name        # Full name of element (e.g. Hydrogen)
        self.M = M              # Atomic weight, This is normalizes over nuclides of element and abundancies
        self.id = self.symbol
        
    def __str__(self):
        text = str()
        text += "Name:          " + str(self.name) + "\n"
        text += "Z:             " + str(self.Z)   + " \n"
        text += "Symbol:        " + self.symbol + " \n"
        text += "atomic Mass:   " + str(self.M) + " u \n"
        return text

class _Elements(list):
    """
    Read and hold complete elements list
    """
    
    def __init__(self, csvfile=os.path.join(hdtv.datadir, "elements.dat")):

        super(_Elements, self).__init__()

        tmp = list()
        
        try:
            datfile = open(csvfile, "rb")
            reader = csv.reader(datfile)
            reader.next() # Skip header
            
            for line in reader:
                Z = int(line[0])
                Symbol = line[1].strip()
                Name = line[2].strip()
                try:
                    Mass = ErrValue(line[3].strip())
                except ValueError:
                    Mass = None
                element = _Element(Z, Symbol, Name, Mass)
                tmp.append(element)
        except csv.Error, e:
            print 'file %s, line %d: %s' % (filename, reader.line_num, e)
        finally:
            datfile.close()
            
        # Now store elements finally
        maxZ = max(tmp, key=lambda x: x.Z) # Get highest Z
        for i in range(maxZ.Z):
            self.append(None)

        for e in tmp:
            self[e.Z] = e

    def __call__(self, Z=None, symbol=None, name=None):
        
        if symbol:
            for z in self:
                try:
                    if z.symbol.lower() == symbol.lower():
                        return z
                except AttributeError:
                    pass      
        if name:
            for z in self:
                try:
                    if z.name.lower() == name.lower():
                        return z
                except AttributeError:
                    pass
                
        if Z:
            return self[Z]
        
        return self
    
    def __setitem__(self, index, value):
        if index == 0:
            return None
        
        if index > 0:
            index = index - 1
        
        return super(_Elements, self).__setitem__(index, value)
        
    def __getitem__(self, index):
        if index == 0:
            return None
        
        if index > 0:
            index = index - 1
        
        return super(_Elements, self).__getitem__(index)
    


class _Nuclide(_Element):
    
    __slots__ = ("id", "element", "A", "M", "sigma", "abundance")

    def __init__(self, element, A, abundance=None, sigma=None, M=None):
        
        super(_Nuclide, self).__init__(element.Z, element.symbol, element.name, M=None) # M is different for nuclides and elements
        self.element = element
        self.A = A
        self.M = M
        self.sigma = sigma
        self.abundance = abundance
        self.id = str(self.A) + "-" + str(self.symbol)    
        
    def __str__(self):
        text = str()
        text += "id:            " + self.id  + "\n"
        text += "Z:             " + str(self.Z)   + " \n"
        text += "A:             " + str(self.A)   + "\n"
        text += "atomic Mass:   " + str(self.M)   + " u\n"
        text += "Abundance:     " + str(self.abundance * 100.0) + " %\n"
        text += "σ_0:           " + str(self.sigma)   + " b\n"
        return text


class _Nuclides(object):
    
    def __init__(self, csvfile=os.path.join(hdtv.datadir, "nuclides.dat")):
        
        self._storage = dict()
        try:
            datfile = open(csvfile, "rb")
            reader = csv.reader(datfile)
            reader.next() # Skip header
            
            for line in reader:
                Z = int(line[0].strip())
                element = Elements(Z)
                A = int(line[1].strip())
                if line[2].strip():
                    abd = ErrValue(line[2].strip())/100.0
                else:
                    abd = ErrValue(None, None)
                if line[3].strip():
                    M = ErrValue(line[3].strip())
                else:
                    M = ErrValue(None, None)
                if line[4].strip():
                    sigma = ErrValue(line[4].strip())
                else:
                    sigma = ErrValue(None, None)
                
                if not Z in self._storage:
                    self._storage[Z] = dict()
                self._storage[Z][A] = _Nuclide(element, A, abundance=abd, sigma=sigma, M=M)
#                print self._storage[Z][A]
#                self._storage.update({Z: {A:nuclide}})
        except csv.Error, e:
            print 'file %s, line %d: %s' % (filename, reader.line_num, e)      
        finally:
            datfile.close()

    def __call__(self, Z=None, A=None, symbol=None, name=None):
        
        if symbol:
            for e in self._storage.itervalues():
                if e.symbol == symbol:
                    ret.append(e)
            return ret     
        if name:
            for e in self._storage.itervalues():
                if e.name == name:
                    ret.append(e)
            return ret
                
        if Z:
            if A:
                return self._storage[Z][A]
            else:
                return self._storage[Z]
            

class Gamma(object):
    """Class for storing information about gammas"""
    
    __slots__ = ("id", "nuclide", "energy", "sigma", "intensity")
     
    def __init__(self, nuclide, energy, sigma, intensity):
        self.id = str(nuclide.id) + "@" + str(energy)
        self.nuclide = nuclide
        self.energy = energy
        self.sigma = sigma
        self.intensity = intensity

    def __str__(self):
        text = str()
        text += "id:        " + str(self.nuclide.id) + "\n"
        text += "Energy:    " + str(self.energy) + " keV\n"
        text += "σ:         " + str(self.sigma) + " b\n"
        text += "Intensity: " + str(self.intensity * 100.0) + " %\n"
        return text
    
    def __cmp__(self, other):
        
        ret = cmp(self.energy, other.energy)
        
        if ret == 0 and other.id != None:
            if self.id == other.id:
                return ret
            else: # Gammas are from different isotope
                return cmp(self.id, other.id)
        else:
            return ret
         
class GammaLib(list):
    """Class for storing a gamma library"""
    
    __slots__ = ("nuclide", "energy", "sigma", "intensity", "E_fuzzyness")

    def __init__(self, E_fuzzyness=1.0):
        self.E_fuzzyness = E_fuzzyness  # Fuzzyness for energy identification

    
    def lookup(self, id=None, Z=None, A=None, element=None, energy=None, fuzzyness=None):
        
        results = self.find(id=id, Z=Z, A=A, element=element, energy=energy, fuzzyness=fuzzyness)
        
        for r in results:
            print r
        
    def find(self, Z=None, A=None, element=None, energy=None, fuzzyness=None):
    
        results = self[:]
        
        if fuzzyness == None:
            fuzzyness = self.E_fuzzyness
            
        if Z != None:
            results = filter(lambda x: x.nuclide.Z == Z, results)
 
        if A != None:
            results = filter(lambda x: x.nuclide.A == A, results)
 
        if element != None:
            results = filter(lambda x: x.nuclide.symbol == element, results)
 
        if energy != None:
              
            tmp = list()
            for r in results:
                diff = r.energy - energy

                if abs(diff) < fuzzyness + diff.error:
                    tmp.append(r)
                   
            results = tmp

        return results


Elements = _Elements()
Nuclides = _Nuclides()
