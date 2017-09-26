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

#-------------------------------------------------------------------------
# HDTV dynamic (C++) library manager
#-------------------------------------------------------------------------

import os
import stat
import ROOT
import hdtv


class DLImportError(Exception):
    pass


path = [hdtv.clibpath]


def FindLibrary(name):
    """
    Find a dynamic library in the path. Returns the full filename.
    """
    global path
    for p in path:
        fname = "%s/%s.so" % (p, name)
        try:
            mode = os.stat(fname)[stat.ST_MODE]
            if stat.S_ISREG(mode):
                return fname
        except OSError:
            # Ignore the file if stat failes
            pass
    return None


def LoadLibrary(name):
    fname = FindLibrary(name)
    if not fname:
        raise DLImportError("Failed to find library %s" % name)

    if ROOT.gSystem.Load(fname) < 0:
        raise DLImportError("Failed to load library %s" % fname)
