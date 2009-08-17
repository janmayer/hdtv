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

import __main__

def msg(text, newline = True):
    """
    Print a message
    
    newline: Append newline
    """
    __main__.ui.msg(text, newline = newline)
    
def warn(text, newline = True):
    """
    Print a warning message
    """
    __main__.ui.warn(text, newline = newline)
    
    
def error(text, newline = True):
    """
    Print a error message
    """
    __main__.ui.error(text, newline = newline)
    
def debug(text, level = 1, newline = True):
    """
    Print debug messages
    """
    __main__.ui.debug(text, level = level, newline = newline)
    
def debug_level(level = 0):
    """
    Set debug level
    """
    __main__.ui.DEBUG_LEVEL = level
    
def newline():
    """
    Insert newline
    """
    __main__.ui.newline()    
