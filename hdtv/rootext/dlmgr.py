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
import shutil
import subprocess
import sys
import tempfile

import ROOT

import hdtv.ui
from hdtv._version import get_versions
from hdtv.rootext import libfmt, modules

__version__ = get_versions()["version"]
del get_versions

cachedir = os.path.join(
    os.getenv("XDG_CACHE_HOME", os.path.join(os.environ["HOME"], ".cache")), "hdtv"
)
usrdir = os.path.join(
    cachedir, "%d-%d-%s" % (sys.hexversion, ROOT.gROOT.GetVersionInt(), __version__)
)
sysdir = os.path.join(
    os.path.dirname(__file__), "root-" + str(ROOT.gROOT.GetVersionInt())
)

# Fix performance degradation in ROOT 6.19.02 and higher, caused by
# https://github.com/root-project/root/commit/75161283352217c156c435ba8bac870cd5a125fb
ROOT.gEnv.IgnoreDuplicates(True)
ROOT.gEnv.SetValue("X11.UseXft", 0)


def FindLibrary(name, libname):
    """
    Find the path to a dynamic library in a subfolder.
    Returns the full filename.
    """
    paths = [os.path.join(usrdir, "lib"), os.path.join(sysdir, "lib")]
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
        loaded = _LoadLibrary(fname) >= 0

    if not loaded:
        fname = BuildLibrary(name, usrdir)
        loaded = _LoadLibrary(fname) >= 0

    if not loaded:
        hdtv.ui.error("Failed to load library %s" % libname)
        sys.exit(1)


def _LoadLibrary(fname):
    ROOT.gSystem.SetDynamicPath(
        os.path.dirname(fname) + os.pathsep + ROOT.gSystem.GetDynamicPath()
    )
    ROOT.gSystem.SetIncludePath(
        os.path.dirname(fname) + os.pathsep + ROOT.gSystem.GetDynamicPath()
    )
    return ROOT.gSystem.Load(fname)


def RebuildLibraries(dir, libraries=None):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    for name in libraries or modules:
        BuildLibrary(name, dir)


def BuildLibrary(name, dir):
    srcdir = os.path.join(os.path.dirname(__file__), name)
    # with tempfile.TemporaryDirectory() as tmpdir: TOOD: Not available in python2
    tmpdir = tempfile.mkdtemp()
    subprocess.check_call(
        [
            "cmake",
            srcdir,
            "-DCMAKE_INSTALL_PREFIX=%s" % dir,
            "-DCMAKE_BUILD_TYPE=Release",
        ],
        cwd=tmpdir,
    )
    subprocess.check_call(["cmake", "--build", ".", "-j"], cwd=tmpdir)
    subprocess.check_call(["cmake", "--build", ".", "--target", "install"], cwd=tmpdir)
    shutil.rmtree(tmpdir)

    hdtv.ui.info(f"Rebuild library {(libfmt % name)} in {dir}")
    return os.path.join(dir, "lib", libfmt % name)
