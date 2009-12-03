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

def Median(values):
    """
    Calculate Median of list
    """
    values.sort()
    n = len(values)
    if not n:
        return None
    
    if n % 2 == 0: 
        return (values[(n - 1) / 2] + values[n / 2]) * 0.5
    else:
        return values[n / 2]
        
def compareID(a,b):
    try:fa = float(a)
    except ValueError: fa=a
    try: fb = float(b)
    except ValueError: fb=b
    return cmp(fa,fb)


class ErrValue:
    """
    A value with an error
    
    values may be given as floats or strings containing value and error in
    the form "12.3456(78)" if no error is given.
     
    Beware: Error propagation is only working for statistically independant 
    values for now!
    """
    def __init__(self, value, error = 0):
                
        if isinstance(value, str):
            tmp = self._fromString(value)
            self.value = tmp[0]
            self.error = tmp[1]
        # Instantiate ErrValue from another ErrValue 
        elif isinstance(value, ErrValue):
            self.value = value.value
            self.error = value.error
        else:
            try:
                self.error = abs(error) # Errors are always positive
            except TypeError:
                self.error = error
            self.value = value    
        try:
            self.rel_error = self.error / self.value * 100.0 # Error in percent
        except (ZeroDivisionError, TypeError):
            self.rel_error = None
    
    
    def __repr__(self):
        return "ErrValue(" + repr(self.value) + ", " + repr(self.error) + ")"
    
    def __str__(self):
        return self.fmt()

    def __eq__(self, other):
        """
        Test for equality; taking errors into account
        """
        # Check given objects
        val1 = self._sanitize(self)
        val2 = self._sanitize(other)
        
        # Do the comparison
        if (abs(val1.value - val2.value) <= (val1.error + val2.error)):
            return True
        else:
            return False
        
    def __cmp__(self, other):
        """
        compare by value
        """
        # Check given objects
        
        otherval = self._sanitize(other)
        
        return cmp(self.value, otherval.value)
    
    def __add__(self, other):
        """Add two values with error propagation"""
        val1 = self._sanitize(self)
        val2 = self._sanitize(other)
        ret = ErrValue(0, 0)
        
        ret.value = val1.value + val2.value
        ret.error = math.sqrt(math.pow(val1.error, 2) + math.pow(val2.error, 2))
        return ret

    def __radd__(self, other):
        return self.__add__(other)
    
    
    def __difference(self, minuend, subtrahend):
        """Subtract two values with error propagation"""
        val1 = self._sanitize(minuend)
        val2 = self._sanitize(subtrahend)
        ret = ErrValue(0, 0)
        
        ret.value = val1.value - val2.value
        ret.error = math.sqrt(math.pow(val1.error, 2) + math.pow(val2.error, 2))

        return ret

    def __sub__(self, other):
        return self.__difference(self, other)
    
    def __rsub__(self, other):
        return self.__difference(other, self)

    def __mul__(self, other):
        """Multiply two values with error propagation"""
        val1 = self._sanitize(self)
        val2 = self._sanitize(other)
        ret = ErrValue(0, 0)
        
        ret.value = val1.value * val2.value
        ret.error = math.sqrt(math.pow((val1.value * val2.error), 2) \
                              + math.pow((val2.value * val1.error), 2))
        return ret

    def __rmul__(self, other):
        return self.__mul__(other)
    
    
    def __quotient(self, dividend, divisor):
        """Divide two values with error propagation"""
        val1 = self._sanitize(dividend)
        val2 = self._sanitize(divisor)
        ret = ErrValue(0, 0)
        
        ret.value = val1.value / val2.value
        ret.error = math.sqrt(math.pow((val1.error / val2.value), 2) \
                              + math.pow((val1.value * val2.error / math.pow(val2.value, 2)), 2))
        return ret
        
    def __div__(self, other):
        return self.__quotient(self, other)
    
    def __rdiv__(self, other):
        return self.__quotient(other, self)
    
    def __float__(self):
        return float(self.value)
    
    def _sanitize(self, val):
        """
        * Convert floats or strings to ErrValue
        * Return .error=0 for .error==None values to be able to do calculations
        """
        ret = ErrValue(0, 0)
               
        try:
            ret.value = val.value
            ret.error = abs(val.error)
        except TypeError:
            ret.value = val.value
            ret.error = 0
        except AttributeError:
            ret.value = val
            ret.error = 0
            
        return ret
        
        
    def __abs__(self):
        return ErrValue(abs(self.value), self.error)
    
    def _fromString(self, strvalue):
        """
        Convert values with error given as strings (e.g. "0.1234(56)") to
        ErrValues
        """
        
        try: # Try to convert string values like "0.1234(56)" into numbers
            
            strvalue = strvalue.strip() # Strip whitespaces
            
            # Extract exponent
            match = re.match(r".*[eE](\-?[0-9]*\.?[0-9]*).*" , strvalue)
            try:
                exp = float(match.group(1))
            except AttributeError:
                exp = 0.0
                
            # Extract error
            match = re.match(r".*\(([0-9]+)\)", strvalue)
            try:
                err = match.group(1)
            except AttributeError:
                err = "0"

                
            # Extract value
            # TODO: Handle decimal seperator properly, depending on locale
            match = re.match(r"^(\-?[0-9]*\.?([0-9]*)).*", strvalue)
            
            value = float(match.group(1)) * math.pow(10, exp)
            
            try:
                decplaces = match.group(2)
            except AttributeError:
                decplaces = ""
            
            # Calculate magnitude of error
            error = float(err) / math.pow(10, len(decplaces)) * math.pow(10, exp)

        except TypeError: # No valid string given
            return (strvalue, None)
        except AttributeError: # String does not contain error
            value = float(strvalue)
            error = 0
        
        return (value, error)
        
    
    def fmt(self):
    
        try:
            # Call fmt_no_error() for values without error
            if self.error == 0 or self.error is None:
                return self.fmt_no_error()

            # Check and store sign
            if self.value < 0:
                sgn = "-"
                value = -self.value
            else:
                sgn = ""
                value = self.value
                
            error = self.error
        
            # Check whether to switch to scientific notation
            # Catch the case where value is zero
            try:
                log10_val = math.floor(math.log(value) / math.log(10.))
            except (ValueError, OverflowError):
                log10_val = 0.

            if log10_val >= 6 or log10_val <= -2:
                # Use scientific notation
                suffix = "e%d" % int(log10_val)
                exp = 10 ** log10_val
                value /= exp
                error /= exp
            else:
                # Use normal notation
                suffix = ""
            
            # Find precision (number of digits after decimal point) needed such that the
            # error is given to at least two decimal places
            if error >= 10.:
                prec = 0
            else:
                # Catch the case where error is zero
                try:
                    prec = -math.floor(math.log(error) / math.log(10.)) + 1
                except (ValueError, OverflowError):
                    prec = 6
                    
            # Limit precision to sensible values, and capture NaN
            #  (Note that NaN is by definition unequal to itself)
            if prec > 20:
                prec = 20
            elif prec != prec:
                prec = 3

            return "%s%.*f(%.0f)%s" % (sgn, int(prec), value, error * 10 ** prec, suffix)
        
        except (ValueError, TypeError):
            return ""
    
    def fmt_full(self):
        """
        Print ErrValue with absolute and relative error
        """
        string = str(self.fmt()) + " [" + "%.*f" % (2, self.rel_error) + "%]"
        return string 
        
    def fmt_no_error(self, prec = 6):
        try:
            # Check and store sign
            if self.value < 0:
                sgn = "-"
                value = -self.value
            else:
                sgn = ""
                value = self.value
            
            # Check whether to switch to scientific notation
            # Catch the case where value is zero
            try:
                log10_val = math.floor(math.log(value) / math.log(10.))
            except (ValueError, OverflowError):
                log10_val = 0.
            
            if log10_val >= 6 or log10_val <= -2:
                # Use scientific notation
                suffix = "e%d" % int(log10_val)
                value /= 10 ** log10_val
            else:
                # Use normal notation
                suffix = ""

            return "%s%.*f%s" % (sgn, prec, value, suffix)
        except (ValueError, TypeError):
            return ""

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
        
