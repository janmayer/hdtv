# -*- coding: utf-8 -*-
import hdtv.cmdline
from hdtv.util import ErrValue
import csv
import os
    
class _Element(object):
    """
    Store info about elements
    """
    
    __slots__ = ("id", "z", "symbol", "name", "m")

    def __init__(self, Z, Symbol, Name = None, M = None):
        
        self.z = Z
        self.symbol = Symbol    # Symbol of element (e.g. H)
        self.name = Name        # Full name of element (e.g. Hydrogen)
        self.m = M              # Atomic weight, This is normalizes over nuclides of element and abundancies
        self.id = self.symbol
        
    def _get_Z(self):
        return self.z
    
    Z = property(_get_Z)
    
    def _get_M(self):
        return self.m
    M = property(_get_M)
    
    def __str__(self):
        text = str()
        text += "Name:          " + str(self.name) + "\n"
        text += "Z:             " + str(self.z) + " \n"
        text += "Symbol:        " + self.symbol + " \n"
        text += "atomic Mass:   " + str(self.m) + " u \n"
        return text

class _Elements(list):
    """
    Read and hold complete elements list
    """
    
    def __init__(self, csvfile = os.path.join(hdtv.datadir, "elements.dat")):

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
        maxZ = max(tmp, key = lambda x: x.z) # Get highest Z
        for i in range(maxZ.z):
            self.append(None)

        for e in tmp:
            self[e.z] = e

    def __call__(self, Z = None, symbol = None, name = None):
        
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
    
    __slots__ = ("id", "element", "a", "m", "sigma", "abundance")

    def __init__(self, element, A, abundance = None, sigma = None, M = None):
        
        self.element = element
        super(_Nuclide, self).__init__(element.z, element.symbol, element.name, M = None) # M is different for nuclides and elements
        self.a = A
        self.m = M
        self.sigma = sigma
        self.abundance = abundance
        self.id = str(self.a) + "-" + str(self.symbol)    
    
    
    def _get_symbol(self):
        return self.element.symbol
    
    def _set_symbol(self, symbol):
        self.element.symbol = symbol
    
    symbol = property(_get_symbol, _set_symbol)#    def _Z(self):
#        return self.element.z
#    
#    def _set_Z(self, Z):
#        self.element.z = Z
    
#    z = property(_Z, _set_Z)
    
    def __str__(self):
        text = str()
        text += "id:            " + self.id + "\n"
        text += "Z:             " + str(self.z) + " \n"
        text += "A:             " + str(self.a) + "\n"
        text += "atomic Mass:   " + str(self.m) + " u\n"
        text += "Abundance:     " + str(self.abundance * 100.0) + " %\n"
        text += "Sigma_0:       " + str(self.sigma) + " b\n"
        return text


class _Nuclides(object):
    
    def __init__(self, csvfile = os.path.join(hdtv.datadir, "nuclides.dat")):
        
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
                    abd = ErrValue(line[2].strip()) / 100.0
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
                self._storage[Z][A] = _Nuclide(element, A, abundance = abd, sigma = sigma, M = M)
#                print self._storage[Z][A]
#                self._storage.update({Z: {A:nuclide}})
        except csv.Error, e:
            print 'file %s, line %d: %s' % (filename, reader.line_num, e)      
        finally:
            datfile.close()

    def __call__(self, Z = None, A = None, symbol = None, name = None):
        
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
        self.id = str(nuclide.id) + "@" + str(energy.value.__int__())
        self.nuclide = nuclide
        self.energy = energy
        self.sigma = sigma
        self.intensity = intensity

    def __str__(self):
        text = str()
        text += "id:        " + str(self.nuclide.id) + "\n"
        text += "Energy:    " + str(self.energy) + " keV\n"
        if not self.sigma is None:
            text += "Sigma:     " + str(self.sigma) + " b\n"
        if not self.intensity is None:
            text += "Intensity: " + str(self.intensity * 100.0) + " %\n"
        return text
    
    def _Z(self):
        return self.nuclide.z
    
    z = property(_Z)
    
    def _A(self):
        return self.nuclide.a
    
    a = property(_A)
    
    def _symbol(self):
        return self.nuclide.symbol
    
    symbol = property(_symbol)
        
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
    """
    Class for storing a gamma library
    
    The real libs should be derived from this
    """
    
    __slots__ = ("nuclide", "energy", "sigma", "intensity", "E_fuzziness")

    def __init__(self, fuzziness = 1.0):
        self.fuzziness = fuzziness  # Fuzzyness for energy identification
    
    def find(self, fuzziness = None, sort_key=None, sort_reverse=False, **args):   
        """
        Find in gamma lib
        
        Does a fuzzy compare for floats. All strings are compared lowercase.
        
        Valid key args are:
        
         * sort_key: key to sort
         * sort_reverse: sort_reverse
         * "key: value" : key value pairs to find
        """
        
        if fuzziness is None:
            fuzziness = self.fuzziness

        # convert keys to lowercase
        fields_lower = dict()
        args_lower = dict()
        for (key, conv) in self.fields.items():
            fields_lower[key.lower()] = conv
            
        for (key, value) in args.items():
            try:
                conv = fields_lower[key.lower()] # if this raises a KeyError it was an invalid argument
            except KeyError:
                print "Invalid key", key
                raise KeyError
            args_lower[key.lower()] = conv(value)

        # Prepare find args
        fargs = dict()

        for (key, conv) in fields_lower.items():
            try:
                fargs[key] = conv(args_lower[key]) # Convert as described in fields dict
            except KeyError:
                pass       

        
        # Do the search
        results = self[:]
        
        if fuzziness is None:
            fuzziness = self.fuzziness
                
        if len(fargs) == 0:
            return []
                
        for (key, value) in fargs.items():
            if not value is None:
                if isinstance(value, int): 
                    results = filter(lambda x: getattr(x, key) == value, results)
                elif isinstance(value, str): # Do lowercase cmp for strings
                    value_l = value.lower()
                    results = filter(lambda x: getattr(x, key).lower() == value_l, results)
                else: # Do fuzzy compare
                    results = filter(lambda x: (abs(getattr(x, key) - value) <= fuzziness), results)    

        # Sort
        try:
            if not sort_key is None:
                results.sort(key = lambda x: getattr(x, sort_key), reverse = sort_reverse)
        except AttributeError:
            print "Could not sort by\'" + sort_key + "\': No such key"    
            raise AttributeError
        
        return results


Elements = _Elements()
Nuclides = _Nuclides()
