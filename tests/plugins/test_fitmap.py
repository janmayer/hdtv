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

import os

import pytest

from tests.helpers.utils import redirect_stdout, hdtvcmd

import hdtv.cmdline
import hdtv.options
import hdtv.session

import __main__
# We don’t want to see the GUI. Can we prevent this?
try:
    __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass


import hdtv.plugins.specInterface
import hdtv.plugins.calInterface
import hdtv.plugins.fitInterface
import hdtv.plugins.peakfinder
import hdtv.plugins.fitmap

s = __main__.s
spectra = __main__.spectra

testspectrum = os.path.join(
    os.path.curdir, "tests", "share", "osiris_bg.spc")

@pytest.fixture(autouse=True)
def prepare():
    spectra.Clear()
    yield
    spectra.Clear()

def test_cmd_fit_position():
    s.tv.specIf.LoadSpectra(testspectrum, None)
    hdtvcmd("fit peakfind -a -t 0.05")
    f, ferr = hdtvcmd(
        "fit position assign 10.0 1173.228(3) 12.0 1332.492(4)",
        "fit position erase 10.0 12.0")
    assert ferr == ""

def test_cmd_fit_position_map():
    s.tv.specIf.LoadSpectra(testspectrum, None)
    hdtvcmd("fit peakfind -a -t 0.002")
    f, ferr = hdtvcmd("fit position map tests/share/osiris_bg.map")
    assert ferr == ""
    assert "Mapped 3 energies to peaks" in f
