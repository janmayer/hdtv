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

import copy
import os
import re

import pytest

from hdtv.util import monkey_patch_ui
from tests.helpers.utils import hdtvcmd

monkey_patch_ui()

import __main__
import hdtv.cmdline
import hdtv.options
import hdtv.session

try:
    __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass

import hdtv.plugins.peakfinder
from hdtv.plugins.fitInterface import fit_interface
from hdtv.plugins.specInterface import spec_interface

spectra = __main__.spectra

testspectrum = os.path.join(os.path.curdir, "tests", "share", "osiris_bg.spc")


@pytest.fixture(autouse=True)
def prepare():
    fit_interface.ResetFitterParameters()
    hdtv.options.Set("table", "classic")
    hdtv.options.Set("uncertainties", "short")
    spectra.Clear()
    yield
    spectra.Clear()
    fit_interface.ResetFitterParameters()


def test_cmd_fit_various():
    hdtvcmd("fit function peak activate theuerkauf")
    spec_interface.LoadSpectra(testspectrum)
    assert len(spec_interface.spectra.dict) == 1
    f, ferr = setup_fit()
    assert f == ""
    assert ferr == ""
    f, ferr = hdtvcmd("fit execute")
    assert "WorkFit on spectrum: 0" in f
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
        "fit hide decomposition 0",
    )
    assert ferr == ""
    assert f == ""
    f, ferr = hdtvcmd("fit activate 0")
    assert "Activating fit 0" in f
    assert ferr == ""
    f, ferr = hdtvcmd("fit delete 0", "fit function peak activate ee")
    assert ferr == ""
    assert f == ""


def test_cmd_fit_peakfind():
    spec_interface.LoadSpectra(testspectrum)
    assert len(spec_interface.spectra.dict) == 1
    f, ferr = hdtvcmd("fit peakfind -a -t 0.002")
    assert "Search Peaks in region" in f
    assert "Found 68 peaks" in f
    # This was not needed before commits around ~b41833c9c66f9ba5dbdcfc6fc4468b242360641f
    # However, some small change has happened that prevents a correct fit of a single
    # double peak at ~1540 keV. When I fit it manually, using a similar fit region
    # and internal background only, it works.
    assert "WARNING: Adding invalid fit" in ferr


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@pytest.mark.parametrize("peak", ["theuerkauf", "ee"])
@pytest.mark.parametrize("bg", ["polynomial", "exponential", "interpolation"])
@pytest.mark.parametrize("integrate", ["True", "False"])
@pytest.mark.parametrize("likelihood", ["normal", "poisson"])
def test_cmd_fit_parameter(peak, bg, integrate, likelihood):
    spec_interface.LoadSpectra(testspectrum)
    f, ferr = setup_fit()
    hdtvcmd("fit marker background set 415", "fit marker background set 450")
    f, ferr = hdtvcmd(
        f"fit function peak activate {peak}",
        f"fit function background activate {bg}",
        f"fit parameter integrate {integrate}",
        f"fit parameter likelihood {likelihood}",
    )
    assert f == ""
    assert ferr == ""
    f, ferr = hdtvcmd("fit execute")
    assert "WorkFit on spectrum: 0" in f
    assert ".0 |" in f
    assert ".1 |" in f
    assert "2 peaks in WorkFit" in f

    f, ferr = hdtvcmd("fit parameter status")
    assert re.search(f"Peak model.*{peak}", f, re.M)
    assert re.search(f"Background model.*{bg}", f, re.M)
    assert f"likelihood: {likelihood}" in f
    assert f"integrate: {integrate}" in f
    assert ferr == ""

    f, ferr = hdtvcmd("fit store")
    assert f == "Storing workFit with ID 0"
    assert ferr == ""

    f, ferr = hdtvcmd("fit clear", "fit list")
    assert ferr == ""
    assert "Fits in Spectrum 0" in f

    f, ferr = hdtvcmd("fit parameter reset")
    assert ferr == ""


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_cmd_fit_copy():
    spec_interface.LoadSpectra(testspectrum)
    f, ferr = setup_fit()
    hdtvcmd("fit marker background set 415", "fit marker background set 450")
    f, ferr = hdtvcmd(
        "fit function peak activate theuerkauf",
        "fit function background activate polynomial",
        "fit parameter integrate True",
        "fit parameter likelihood poisson",
        "fit execute",
    )
    workFit = spec_interface.spectra.workFit
    newFit = copy.copy(workFit)
    assert workFit == newFit
    assert workFit.fitter == newFit.fitter


def test_interpolation_incomplete():
    spec_interface.LoadSpectra(testspectrum)
    assert len(spec_interface.spectra.dict) == 1
    f, ferr = setup_interpolation_incomplete()
    assert f == ""
    assert "Background fit failed" in ferr


def setup_interpolation_incomplete():
    return hdtvcmd(
        "fit function background activate interpolation",
        "fit marker background set 520",
        "fit marker background set 550",
        "fit marker background set 620",
        "fit marker background set 650",
        "fit execute",
    )


def setup_fit():
    return hdtvcmd(
        "fit function background activate polynomial",
        "fit parameter background 2",
        "fit marker peak set 580",
        "fit marker peak set 610",
        "fit marker background set 520",
        "fit marker background set 550",
        "fit marker background set 620",
        "fit marker background set 650",
        "fit marker region set 570",
        "fit marker region set 615",
    )


# More tests are still needed for:
#
# fit focus
# fit getlists
# fit read
# fit savelists
# fit tex
# fit write
