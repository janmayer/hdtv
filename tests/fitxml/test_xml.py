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
This script contains some test cases for the writing and reading of fits to XML
if this test work fine, one also needs to test, how thing behave after changing
the calibration back and forth (see test_cal.py for that).
"""


import os

import pytest

from hdtv.util import monkey_patch_ui
from tests.helpers.utils import redirect_stdout, setup_io

monkey_patch_ui()

import __main__
import hdtv.session

try:
    __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass
spectra = __main__.spectra

from hdtv.plugins.fitInterface import fit_interface
from hdtv.plugins.fitlist import fitxml
from hdtv.plugins.specInterface import spec_interface

testspectrum = os.path.join(os.path.curdir, "tests", "share", "osiris_bg.spc")


@pytest.fixture(autouse=True)
def prepare():
    fit_interface.ResetFitterParameters()
    hdtv.options.Set("table", "classic")
    hdtv.options.Set("uncertainties", "short")
    spec_interface.LoadSpectra(testspectrum)
    yield
    spectra.Clear()


def list_fit():
    f, ferr = setup_io(2)
    with redirect_stdout(f, ferr):
        fit_interface.ListFits()
        fit_interface.ListIntegrals()
    assert ferr.getvalue().strip() == ""
    return f.getvalue().strip()


def fit_write_and_save(filename):
    spectra.ExecuteFit()
    spectra.StoreFit()
    spectra.ClearFit()

    out_original = list_fit()

    print("Saving fits to file %s" % filename)
    fitxml.WriteXML(spectra.Get("0").ID, filename)
    print("Deleting all fits")
    spectra.Get("0").Clear()
    print("Reading fits from file %s" % filename)
    fitxml.ReadXML(spectra.Get("0").ID, filename)

    assert out_original == list_fit()


def test_fitxml_all_free_no_bg(temp_file_compressed):
    """
    all parameter free, just one peak, no background, theuerkauf model
    """
    fit_interface.SetPeakModel("theuerkauf")
    spectra.SetMarker("region", 1450)
    spectra.SetMarker("region", 1470)
    spectra.SetMarker("peak", 1460)
    fit_write_and_save(temp_file_compressed)


def test_fitxml_all_free_bg(temp_file_compressed):
    """
    all parameter free, just one peak, background
    """
    spectra.SetMarker("region", 500)
    spectra.SetMarker("region", 520)
    spectra.SetMarker("peak", 511)
    spectra.SetMarker("bg", 480)
    spectra.SetMarker("bg", 490)
    spectra.SetMarker("bg", 530)
    spectra.SetMarker("bg", 540)
    fit_write_and_save(temp_file_compressed)


def test_fitxml_all_free_multi_peak(temp_file_compressed):
    """
    all parameter free, more than one peak
    """
    spectra.SetMarker("region", 1395)
    spectra.SetMarker("region", 1415)
    spectra.SetMarker("peak", 1400)
    spectra.SetMarker("peak", 1410)
    spectra.SetMarker("bg", 1350)
    spectra.SetMarker("bg", 1355)
    spectra.SetMarker("bg", 1420)
    spectra.SetMarker("bg", 1425)
    fit_write_and_save(temp_file_compressed)


def test_fitxml_parameter_hold(temp_file_compressed):
    """
    one parameter status!=free, but equal for all peaks
    """
    spectra.SetMarker("region", 960)
    spectra.SetMarker("region", 975)
    spectra.SetMarker("peak", 965)
    spectra.SetMarker("peak", 970)
    spectra.SetMarker("bg", 950)
    spectra.SetMarker("bg", 955)
    spectra.SetMarker("bg", 980)
    spectra.SetMarker("bg", 985)
    fit_interface.SetFitterParameter("pos", "hold")
    fit_write_and_save(temp_file_compressed)


def test_fitxml_parameter_multi(temp_file_compressed):
    """
    different parameter status for each peak
    """
    spectra.SetMarker("region", 1750)
    spectra.SetMarker("region", 1780)
    spectra.SetMarker("peak", 1765)
    spectra.SetMarker("peak", 1770)
    spectra.SetMarker("bg", 1700)
    spectra.SetMarker("bg", 1710)
    spectra.SetMarker("bg", 1800)
    spectra.SetMarker("bg", 1810)
    fit_interface.SetFitterParameter("pos", "hold,free")
    fit_write_and_save(temp_file_compressed)


def test_fitxml_eepeak(temp_file_compressed):
    """
    ee peak (just proof of concept, not a thorough test)
    """
    fit_interface.SetPeakModel("ee")
    spectra.SetMarker("region", 1115)
    spectra.SetMarker("region", 1125)
    spectra.SetMarker("peak", 1120)
    fit_write_and_save(temp_file_compressed)
