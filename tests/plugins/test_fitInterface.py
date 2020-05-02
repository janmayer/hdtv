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

import re
import os
import sys

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
import hdtv.plugins.fitInterface
import hdtv.plugins.peakfinder

s = __main__.s
spectra = __main__.spectra

testspectrum = os.path.join(
    os.path.curdir, "tests", "share", "osiris_bg.spc")

@pytest.fixture(autouse=True)
def prepare():
    __main__.f.ResetFitterParameters()
    hdtv.options.Set("table", "classic")
    hdtv.options.Set("uncertainties", "short")
    spectra.Clear()
    yield
    spectra.Clear()
    __main__.f.ResetFitterParameters()

def test_cmd_fit_various():
    hdtvcmd("fit function peak activate theuerkauf")
    __main__.s.LoadSpectra(testspectrum)
    assert len(s.spectra.dict) == 1
    f, ferr = setup_fit()
    assert f == ""
    assert ferr == ""
    f, ferr = hdtvcmd("fit execute 0")
    assert "WorkFit on spectrum: 0" in f
    assert "WARNING: Non-existent id 0" in ferr
    assert ".0 |" in f
    assert ".1 |" in f
    assert "2 peaks in WorkFit" in f
    f, ferr = hdtvcmd("fit store")
    assert f == "Storing workFit with ID 0"
    assert ferr == ""
    f, ferr = hdtvcmd("fit clear", "fit list")
    assert ferr == ""
    assert "Fits in Spectrum 0" in f
    f, ferr = hdtvcmd(
        "fit hide 0",
        "fit show 0",
        "fit show decomposition 0",
        "fit hide decomposition 0")
    assert ferr == ""
    assert f == ""
    f, ferr = hdtvcmd("fit activate 0")
    assert "Activating fit 0" in f
    assert ferr == ""
    f, ferr = hdtvcmd("fit delete 0",
                      "fit function peak activate ee")
    assert ferr == ""
    assert f == ""

def test_cmd_fit_peakfind():
    __main__.s.LoadSpectra(testspectrum)
    assert len(s.spectra.dict) == 1
    f, ferr = hdtvcmd("fit peakfind -a -t 0.002")
    assert "Search Peaks in region" in f
    assert "Found 68 peaks" in f
    assert ferr == ""

def setup_fit():
    return hdtvcmd(
        "fit parameter background set 2",
        "fit marker peak set 580",
        "fit marker peak set 610",
        "fit marker background set 520",
        "fit marker background set 550",
        "fit marker background set 620",
        "fit marker background set 650",
        "fit marker region set 570",
        "fit marker region set 615")


# More tests are still needed for:
#
# fit focus
# fit getlists
# fit read
# fit savelists
# fit tex
# fit write
