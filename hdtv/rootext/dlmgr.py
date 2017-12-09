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

# ------------------------------------------------------------------------
# HDTV dynamic (C++) library manager
# ------------------------------------------------------------------------

import os
import sys
import shutil
import subprocess
import ROOT
import hdtv.ui
import hdtv.version
from hdtv.rootext import modules, libfmt

configpath = os.environ.get('HDTV_USER_PATH', os.path.join(os.environ.get('HOME', '~'), '.hdtv'))
usrlibdir = os.path.join(configpath, 'lib',
                         "%d-%d-%s" % (sys.hexversion, ROOT.gROOT.GetVersionInt(), hdtv.version.VERSION))
syslibdir = os.path.join(os.path.dirname(__file__), str(ROOT.gROOT.GetVersionInt()))


def FindLibrary(name, libname):
    """
    Find the path to a dynamic library in a subfolder. Returns the full filename.
    """
    paths = [os.path.join(usrlibdir, name), os.path.join(syslibdir, name)]
    for path in paths:
        fname = os.path.join(path, libname)
        if os.path.isfile(fname):
            return fname
    return None


def LoadLibrary(name):
    """
    Load a dynamic library. Try to find and load it, or rebuild it on fail
    """
    loaded = False
    libname = libfmt % name
    fname = FindLibrary(name, libname)
    if fname:
        ROOT.gSystem.SetDynamicPath(os.path.dirname(fname) + os.pathsep + ROOT.gSystem.GetDynamicPath())
        ROOT.gSystem.SetIncludePath(os.path.dirname(fname) + os.pathsep + ROOT.gSystem.GetDynamicPath())
        loaded = (ROOT.gSystem.Load(fname) >= 0)

    if not loaded:
        fname = BuildLibrary(name, usrlibdir)
        ROOT.gSystem.SetDynamicPath(os.path.dirname(fname) + os.pathsep + ROOT.gSystem.GetDynamicPath())
        ROOT.gSystem.SetIncludePath(os.path.dirname(fname) + os.pathsep + ROOT.gSystem.GetDynamicPath())
        loaded = (ROOT.gSystem.Load(fname) >= 0)

    if not loaded:
        hdtv.ui.error("Failed to load library %s" % libname)
        sys.exit(1)


def RebuildLibraries(libdir):
    if os.path.exists(libdir):
        shutil.rmtree(libdir)
    for name in modules:
        BuildLibrary(name, libdir)


def BuildLibrary(name, libdir):
    dir = os.path.join(libdir, name)
    hdtv.ui.info("Rebuild library %s in %s" % ((libfmt % name), dir))
    # Create base directory
    if not os.path.exists(libdir):
        os.makedirs(libdir)
    # Copy everything
    if os.path.exists(dir):
        shutil.rmtree(dir)
    shutil.copytree(os.path.join(os.path.dirname(__file__), name), dir)
    # Make library
    subprocess.check_call(['make', 'clean', '-j', '--silent'], cwd=dir)
    subprocess.check_call(['make', '-j', '--silent'], cwd=dir)
    return os.path.join(dir, libfmt % name)
