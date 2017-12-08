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
import stat
import sys
import shutil
import subprocess
import ROOT
import hdtv.ui
import hdtv.version

configpath = os.environ["HDTV_USER_PATH"] or os.environ["HOME"]
usrlibdir = configpath + os.sep + "lib" + os.sep + \
            "%d-%d-%s" % (sys.hexversion, ROOT.gROOT.GetVersionInt(), hdtv.version.VERSION)

def FindLibrary(name):
    """
    Find a dynamic library in the path. Returns the full filename.
    """
    paths = [usrlibdir + os.sep + name, os.path.realpath(__file__) + os.sep + name]
    for p in paths:
        fname = p + os.sep + name + '.so'
        pcmname = p + os.sep + 'rootdict-' + name + '_rdict.pcm'
        try:
            mode_so = os.stat(fname)[stat.ST_MODE]
            mode_pcm = os.stat(pcmname)[stat.ST_MODE]
            if stat.S_ISREG(mode_so) and stat.S_ISREG(mode_pcm):
                return fname
        except OSError:
            # Ignore the file if stat failes
            pass
    return None

def LoadLibrary(name):
    fname = FindLibrary(name)
    if not fname:
        fname = BuildLibraryForUsr(name)

    if ROOT.gSystem.Load(fname) < 0:
        hdtv.ui.info("Could not load library %s" % fname)
        fname = BuildLibraryForUsr(name)
        if ROOT.gSystem.Load(fname) < 0:
            hdtv.ui.error("Failed to load library %s" % name)
            sys.exit(1)

def BuildLibraryForUsr(name):
    hdtv.ui.info("Trying to rebuild library %s in %s" % (name, usrlibdir))
    # Create base directory
    if not os.path.exists(usrlibdir):
        os.makedirs(usrlibdir)
    # Copy everything
    if os.path.exists(os.path.join(usrlibdir, name)):
        shutil.rmtree(os.path.join(usrlibdir, name))
    shutil.copytree(os.path.join(os.path.dirname(__file__), name), os.path.join(usrlibdir, name))
    # Make library
    subprocess.check_call(['make', 'clean', '-j', '--silent'], cwd=os.path.join(usrlibdir, name))
    subprocess.check_call(['make', '-j', '--silent'], cwd=os.path.join(usrlibdir, name))
    return os.path.join(usrlibdir, name) + os.sep + name + '.so'
