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

import math
import re
import os
import glob
import traceback
import hdtv.errvalue
import hdtv.ui

def Median(values):
    """
    Calculate Median of a list
    """
    values.sort()
    n = len(values)
    if not n:
        return None
    
    if n % 2 == 0: 
        return (values[(n - 1) / 2] + values[n / 2]) * 0.5
    else:
        return values[n / 2]

def gcd(a, b):
    """
    Calculate greatest common denomiator of two integers
    """
    while b != 0:
        (a, b) = (b, a%b)
    return a


def compareID(a,b):
    try:fa = float(a)
    except ValueError: fa=a
    try: fb = float(b)
    except ValueError: fb=b
    return cmp(fa,fb)

class ErrValue(hdtv.errvalue.ErrValue):
    def __init__(self, *args):
        tb = traceback.extract_stack()[-2]
        hdtv.ui.warn("ErrValue class has been moved to file errvalue.py!\n"
                     + "    (called from file \"%s\", line %d, in %s)" % (tb[0], tb[1], tb[2]))
        hdtv.errvalue.ErrValue.__init__(self, *args)

class Linear:
    """
    A linear relationship, i.e. y = p1 * x + p0
    """
    def __init__(self, p0 = 0., p1 = 0.):
        self.p0 = p0
        self.p1 = p1
        
    def Y(self, x):
        """
        Get y corresponding to a certain x
        """
        return self.p1 * x + self.p0
        
    def X(self, y):
        """
        Get x corresponding to a certain y
        May raise a ZeroDivisionError
        """
        return (y - self.p0) / self.p1
        
    @classmethod
    def FromXYPairs(cls, a, b):
        """
        Construct a linear relationship from two (x,y) pairs
        """
        l = cls()
        l.p1 = (b[1] - a[1]) / (b[0] - a[0])
        l.p0 = a[1] - l.p1 * a[0]
        return l
        
    @classmethod
    def FromPointAndSlope(cls, point, p1):
        """
        Construct a linear relationship from a slope and a point ( (x,y) pair )
        """
        l = cls()
        l.p1 = p1
        l.p0 = point[1] - l.p1 * point[0]
        return l


class TxtFile(object):
    """
    Handle txt files, ignoring commented lines
    """
    def __init__(self, filename, mode = "r"):
                
        self.lines = list()  
        self.mode = mode
        filename = filename.rstrip() # TODO: this has to be handled properly (escaped whitespaces, etc...)
        self.filename = os.path.expanduser(filename) 
        self.fd = None
        
    def read(self, verbose = False):
        """
        Read text file to self.lines
        
        Comments are stripped and lines seperated by '\' are automatically
        concatenated
        """
        try:
            self.fd = open(self.filename, self.mode)
            prev_line = ""
            for line in self.fd:
                line = line.rstrip('\r\n ')
                if len(line) > 0 and line[-1] == '\\': # line is continued on next line
                    prev_line += line.rstrip('\\') 
                    continue
                else:
                    if prev_line != "":
                        line = prev_line + " " + line
                    prev_line = ""
                if verbose:
                    hdtv.ui.msg("file> " + str(line))
                
                # Strip comments 
                line = line.split("#")[0] 
                if line.strip() == "":
                    continue
                self.lines.append(line)
                
        except IOError, msg:
            raise IOError, "Error opening file:" + str(msg) 
        except: # Let MainLoop handle other exceptions
            raise
        finally:
            if not self.fd is None:
                self.fd.close()
                
    def write(self):
        """
        Write lines stored in self.lines to text file
        
        Newlines are automatically appended if necessary
        """
        try:
            self.fd = open(self.filename, self.mode)
            for line in self.lines:
                line.rstrip('\r\n ')
                line += os.linesep
                self.fd.write(line)
        except IOError, msg:
            raise IOError, ("Error opening file: %s" % msg)
        except:
            raise
        finally:
            if not self.fd is None:
                self.fd.close()
    
class Pairs(list):
    """
    List of pair values
    """
    def __init__(self, conv_func = lambda x: x): # default conversion is "identity" -> No conversion
        
        super(Pairs, self).__init__()
        self.conv_func = conv_func # Conversion function, e.g. float
        
    def add(self, x, y):
        """
        Add a pair
        """
        self.append([self.conv_func(x), self.conv_func(y)])
        
    def remove(self, pair):
        """
        TODO
        """
        pass
        
    def fromFile(self, fname, sep = None):
        """
        Read pairs from file
        """    
        file = TxtFile(fname)
        file.read()
        for line in file.lines:
            pair = line.split(sep)
            try:
                self.add(pair[0], pair[1])
            except (ValueError, IndexError):
                print "Invalid Line in", fname, ":", line
                
    def fromLists(self, list1, list2):
        """
        Create pairs from to lists by assigning corresponding indices
        """
        if len(list1) != len(list2):
            hdtv.ui.error("Lists for Pairs.fromLists() are of different length")
            return False
        
        for i in range(0, len(list1)):
            self.add(list1[i], list2[i])
        
        
class Table(object):
    """
    Class to store tables
    """
    def __init__(self, data, keys, header = None, ignoreEmptyCols = True,
                 sortBy = None, reverseSort = False, extra_header = None, extra_footer = None):
        
        self.col_sep_char = "|"
        self.empty_field = "-"
        self.header_sep_char = "-"
        self.crossing_char = "+"
        self.extra_header = extra_header
        self.extra_footer = extra_footer
        
        self.lines = list()
        
        self.sortBy = sortBy
        
        self._width = 0 # Width of table
        self._col_width = list() # width of columns
        
        self._ignore_col = [ignoreEmptyCols for i in range(0, len(keys) + 1)] # One additional "border column"
        
        self.data = list()                   

        for d in data:
            if isinstance(d, dict):
                tmp = d
            else: # convert to dict
                tmp = dict()
                for k in keys:
                    tmp[k] = getattr(d, k)
            self.data.append(tmp)
            
        # sort
        if not sortBy is None:
            if sortBy.upper()=="ID":
                self.data.sort(cmp=compareID, key = lambda x: x[sortBy], reverse = reverseSort)
            else:
                self.data.sort(key = lambda x: x[sortBy], reverse = reverseSort)

        if header is None: # No header given: set them from keys
            self.header = list()
            for k in keys:
                self.header.append(k)
        else:
            self.header = header

        # Determine initial width of columns
        for header in self.header:
            # TODO: len fails on unicode characters (e.g. σ) -> str.decode(encoding)
            self._col_width.append(len(str(header)) + 2)
            
        # Build lines
        for d in self.data:
            line = list()
            for i in range(0, len(keys)):
                try:
                    value = d[keys[i]]

                    try: # Handle ErrValues with value None
                        if value.value is None: 
                            if value.error == 0:
                                value = ""
                    except:
                        pass
                    if value is None:
                        value = ""
                    else:
                        value = str(value)
                        
                    if not value is "" : # We have values in this columns -> don't ignore it
                        self._ignore_col[i] = False
                        
                    line.append(value)
                    # TODO: len fails on unicode characters (e.g. σ) -> str.decode(encoding)
                    self._col_width[i] = max(self._col_width[i], len(value) + 2) # Store maximum col width
                except KeyError:
                    line.append(self.empty_field)
            self.lines.append(line)
                        
        # Determine table widths
        for w in self._col_width:
            self._width += w
            # TODO: for unicode awareness we have to do something like len(col_sep_char.decode('utf-8')
            self._width += len(self.col_sep_char) 

    def __str__(self):
        
        text = str()
        if not self.extra_header is None:
            text += str(self.extra_header) + os.linesep
            
        # Build Header
        header_line = str()
        for col in range(0, len(self.header)):
            if not self._ignore_col[col]:
                header_line += str(" " + self.header[col] + " ").center(self._col_width[col]) 
            if not self._ignore_col[col + 1]:
                header_line += self.col_sep_char 

        text += header_line + os.linesep

        # Seperator between header and data
        header_sep_line = str()
        for i in range(0, len(self._col_width)):
            if not self._ignore_col[i]:
                for j in range(0, self._col_width[i]):
                    header_sep_line += self.header_sep_char
                if not self._ignore_col[i + 1]:
                    header_sep_line += self.crossing_char
                        
        text += header_sep_line + os.linesep
                
        # Build lines
        for line in self.lines:
            line_str = ""
            for col in range(0, len(line)):
                if not self._ignore_col[col]:
                    line_str += str(" " + line[col] + " ").rjust(self._col_width[col]) 
                if not self._ignore_col[col + 1]:
                    line_str += self.col_sep_char

            text += line_str + os.linesep
   
        if not self.extra_footer is None:
            text += str(self.extra_footer) + os.linesep
            
        return text

class Position(object):
    """
    Class for storing postions that may be fixed in calibrated or uncalibrated space
    
    if self.pos_cal is set the position is fixed in calibrated space. 
    if self.pos_uncal is set the position is fixed in uncalibrated space.
    """
    def __init__(self, pos, fixedInCal, cal = None):
        self.cal = cal
        self._fixedInCal = fixedInCal
        if fixedInCal:
            self._pos_cal = pos
            self._pos_uncal = None
        else:
            self._pos_cal = None
            self._pos_uncal = pos

    # pos_cal 
    def _set_pos_cal(self, pos):
        if not self.fixedInCal:
            raise TypeError, "Position is fixed in uncalibrated space"
        self._pos_cal = pos
        self._pos_uncal = None
        
    def _get_pos_cal(self):
        if self.fixedInCal:
            return self._pos_cal
        else:
            return self._Ch2E(self._pos_uncal)
        
    pos_cal = property(_get_pos_cal, _set_pos_cal)
    
    # pos_uncal
    def _set_pos_uncal(self, pos):
        if self._fixedInCal:
            raise TypeError, "Position is fixed in calibrated space"
        self._pos_uncal = pos
        self._pos_cal = None
    
    def _get_pos_uncal(self):
        if self.fixedInCal:
            return self._E2Ch(self._pos_cal)
        else:
            return self._pos_uncal
    
    pos_uncal = property(_get_pos_uncal, _set_pos_uncal)
    
    # fixedInCal property
    def _set_fixedInCal(self, fixedInCal):
        if fixedInCal:
            self.FixInCal()
        else:
            self.FixInUncal()
            
    def _get_fixedInCal(self):
        return self._fixedInCal
        
    fixedInCal = property(_get_fixedInCal, _set_fixedInCal)
        
           
    # other functions
    def __str__(self):
        text = str()
        if self.fixedInCal:
            text += "Cal: %s" % self._pos_cal
        else:
            text += "Uncal: %s" % self._pos_uncal
        return text
    
    def _Ch2E(self, Ch):
        if self.cal is None:
            E = Ch
        else:
            E = self.cal.Ch2E(Ch)
        return E
    
    def _E2Ch(self, E):
        if self.cal is None:
            Ch = E
        else:
            Ch = self.cal.E2Ch(E)
        return Ch
        
    def FixInCal(self):
        """
        Fix position in calibrated space
        """
        if not self._fixedInCal:
            self._fixedInCal = True
            self.pos_cal = self._Ch2E(self._pos_uncal)
         
    def FixInUncal(self):
        """
        Fix position in uncalibrated space
        """
        if self._fixedInCal:
            self._fixedInCal = False
            self.pos_uncal = self._E2Ch(self._pos_cal)
        
def GetCompleteOptions(text, keys):
    options = []
    l = len(text)
    for k in keys:
        if k[0:l] == text:
            options.append(k)
    return options


