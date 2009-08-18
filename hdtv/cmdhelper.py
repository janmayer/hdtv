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


def GetCompleteOptions(begin, options):
    l = len(begin)
    return [o + " " for o in options if o[0:l] == begin]
    
def ParseSpecIDs(strings, spectra):
    """
    Parse IDs of spectra, raises a ValueError if parsing fails
    """
    ids = ParseRange(strings, ["ALL", "NONE", "ACTIVE"])
    if ids=="NONE":
        return []
    elif ids=="ACTIVE" or len(ids) == 0:
        if spectra.activeID==None:
            print "Error: no active spectrum"
            return []
        else:
            ids = [spectra.activeID]
    elif ids=="ALL":
        ids = spectra.keys()
    return ids

def ParseFitIds(strings, spec):
    """
    Parse fit IDs, allowed keywords are ALL, NONE, ACTIVE, VISIBLE
    """
    special = ["ALL","NONE","ACTIVE","VISIBLE"]
    # parse the arguments
    try:
        ids = ParseRange(strings, special)
    except ValueError, msg:
        print msg
        return list()
    # processing different cases
    if ids=="NONE":
        return list()
    if ids=="ACTIVE" or len(ids) == 0:
        if not hasattr(spec, "activeID") or spec.activeID is None:
            print "Warning: There is no active fit."
            return list()
        else:
            return [spec.activeID]
    # FIXME: this can be remove, when we use SpectrumCompound as default spectrum class
    if not hasattr(spec, "activeID"):
        return list()
    if ids=="ALL":
        return spec.keys()
    if ids=="VISIBLE":
        return list(spec.visible)
    fits = list()
    # else filter non-existing ids
    valid_ids = list() 
    for ID in ids:
        if not ID in spec.keys():
            print "Warning: no fit with id %s" %ID
        else:
            valid_ids.append(ID)
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
