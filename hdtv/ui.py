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

#-------------------------------------------------------------------------------
# Basic user interface functions (Input/Output, etc)
#-------------------------------------------------------------------------------

DEBUG = False
newline_chars = "\r\n"

import sys

def msg(text, newline = True):
    """
    Print a message
    
    newline: Append newline
    """
    sys.stdout.write(text)
    if newline:
        sys.stdout.write(newline_chars)
    
def warn(text, newline = True):
    """
    Print a warning message
    """
    text = "WARN: " + text
    msg(text)
    
def error(text, newline = True):
    """
    Print a error message
    """
    text = "ERR: " + text
    msg(text)
    
def debug(text, newline = True):
    """
    Print debug messages
    """
    if DEBUG:
        text = "DEBUG: " + text
        print text,
        if newline:
            print ""
    
def newline():
    """
    Insert newline
    """
    msg("")
    
class Table(object):
    """
    Print tables
    """
    def __init__(self, data, attrs, header = None, sortBy = None, reverseSort = False):
        
        self.col_sep_char = "|"
        self.empty_field = "-"
        self.header_sep_char = "-"
        self.crossing_char = "+"
        
        self.lines = list()
        
        self.sortBy = sortBy
        
        self._width = 0 # Width of table
        self.col_width = list() # width of columns
        
        # sort 
        if not sortBy is None:
            data = data[:]
            data.sort(key = lambda x: getattr(x, sortBy), reverse = reverseSort)
            
        if header is None: # No header given: set them from attrs
            self.header = list()
            for a in attrs:
                self.header.append(a)
        else:
            self.header = header
                
        # Determine initial width of columns
        for header in self.header:
            self.col_width.append(len(str(header)) + 2)
            
        # Build lines
        for d in data:
            line = list()
            for i in range(0, len(attrs)):
                try:
                    value = str(getattr(d, attrs[i]))
                    line.append(value)
                    self.col_width[i] = max(self.col_width[i], len(value) + 2) # Store maximum col width
                except AttributeError:
                    line.append(self.empty_field)
            self.lines.append(line)
            
            
        # Determine table widths
        for w in self.col_width:
            self._width += w
            self._width += len(self.col_sep_char)

    def __str__(self):
        
        text = str()
        # Build Header
        header_line = str()
        for col in range(0, len(self.header) - 1):
            header_line += str(" " + self.header[col] + " ").center(self.col_width[col]) + self.col_sep_char 

        # Last column has no final col seperator
        header_line += str(self.header[-1].center(self.col_width[-1]))

        text += header_line + newline_chars

        # Seperator between header and data
        header_sep_line = str()
        for w in self.col_width[:-1]:
            for i in range(0, w):
                header_sep_line += self.header_sep_char
            header_sep_line += self.crossing_char
            
        # Last column has no final col seperator
        for i in range(0, self.col_width[-1]):
            header_sep_line += self.header_sep_char
            
        text += header_sep_line + newline_chars
                
        # Build lines
        for line in self.lines:
            line_str = ""
            for col in range(0, len(line) - 1):
                line_str += str(" " + line[col] + " ").rjust(self.col_width[col]) + self.col_sep_char
            
            # Last column has no final col seperator
            line_str += str(" " + line[-1] + " ").rjust(self.col_width[-1])
            
            text += line_str + newline_chars
            
        return text

    
    def out(self):
        """
        Print it out
        """
        msg(self.__str__())

        

    
    
    
