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


import hdtv.ui
import hdtv.cmdline

def Indent(s, indent=" "):
    """
    Re-format a (possibly multi-line) string such that each line is indented.
    """
    return indent + ("\n" + indent).join(s.splitlines()) + "\n"

def GetCompleteOptions(begin, options):
    l = len(begin)
    return [o + " " for o in options if o[0:l] == begin]
    
def ParseIds(strings, drawable, only_existent=True):
    """
    Parse Spectrum/Fit Ids
    
    Allowed keywords: "ALL","NONE","ACTIVE","VISIBLE", "NEXT", "PREV", "FIRST", "LAST"
    
    Raised ValueError on malformed Ids
    
    if only_existent is True only currently existing ids are returned
    """
    
    special = ["ALL","NONE","ACTIVE","VISIBLE", "NEXT", "PREV", "FIRST", "LAST"]
    # parse the arguments
    try:
        ids = ParseRange(strings, special)
    except ValueError:
        hdtv.ui.error("Invalid IDs.")
        raise hdtv.cmdline.HDTVCommandError

    # processing different cases
    if ids=="NONE":
        ids = list()
#    if ids in [ "ACTIVE" ]:
#        if not hasattr(spec, "activeID") or spec.activeID is None:
#            hdtv.ui.warn("There is no active fit.")
#            return list()
    elif ids == "NEXT":
        ids = [drawable.nextID]
    elif ids == "PREV":
        ids = [drawable.prevID]
    elif ids == "FIRST":
        ids = [drawable.firstID]
    elif ids == "LAST":
        ids = [drawable.lastID]
    elif ids == "ACTIVE" or len(ids) == 0:
        ids = [drawable.activeID]
    elif ids=="ALL":
        ids = drawable.keys()
    elif ids=="VISIBLE":
        ids = list(drawable.visible)
        
    fits = list()
    # filter non-existing ids
    valid_ids = list() 
    if only_existent:
        for ID in ids:
            if ID is None: continue
            if not ID in drawable.keys():
                hdtv.ui.warn("Non-existent id %s" %ID)
            else:
                valid_ids.append(ID)
    else:
        map(valid_ids.append, ids)
    return valid_ids

def ParseRange(strings, special=["ALL", "NONE"]):
    """
    Parse a string or a list of strings specifying (possibly many)
    ranges and return all values from all ranges. Ranges are inclusive.
    Each value is returned at most once, but it is no error if it occurs
    more than once. Within strings, space and comma (,) are accepted as
    separators. If one of the values from the special array is
    passed, it is returned (in uppercase); matching is case-insensitive.
    If the string is malformed, a ValueError exception is raised.
    
    Example: "1 3 2-5, 10,12" gives set([1 2 3 4 5 10 12]).
    """
    # Normalize separators
    if not isinstance(strings, str):
        strings = ",".join(strings)
    strings = ",".join(strings.split())
    
    # Split string
    parts = [p for p in strings.split(",") if p]
    
    # Test for special strings (case-insensitive)
    special = [s.upper() for s in special]
    if len(parts) == 1:
        part=parts[0].upper()
        for s in special:
            if s.startswith(part):
                return s
  
    # Parse ranges
    values = set()
    for part in parts:
        r = part.split("-")
        if len(r) == 1:
            values.add(int(r[0]))
        elif len(r) == 2:
            values |= set(range(int(r[0]), int(r[1])+1))
        else:
            raise ValueError, "Malformed range"
            
    return values
