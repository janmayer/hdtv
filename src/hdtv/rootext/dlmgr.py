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

"""
HDTV dynamic (C++) library manager
"""

import os
import sys
import sysconfig

import ROOT

import hdtv.ui
from hdtv.rootext import libfmt, modules


# Fix performance degradation in ROOT 6.19.02 and higher, caused by
# https://github.com/root-project/root/commit/75161283352217c156c435ba8bac870cd5a125fb
ROOT.gEnv.IgnoreDuplicates(True)
ROOT.gEnv.SetValue("X11.UseXft", 0)

libray_path : str = os.path.join(sysconfig.get_paths()["platlib"], "hdtv", "lib")
ROOT.gSystem.SetDynamicPath(libray_path + os.pathsep + ROOT.gSystem.GetDynamicPath())
ROOT.gSystem.SetIncludePath(libray_path + os.pathsep + ROOT.gSystem.GetIncludePath())

def LoadLibrary(name):
    """
    Load a dynamic library from wheel
    """
    libname = libfmt % name
    if ROOT.gSystem.Load(libname) < 0:
        hdtv.ui.error("Failed to load library %s" % libname)
        sys.exit(1)
