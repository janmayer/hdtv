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

import filecmp
import os
import sys

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


import hdtv.plugins.calInterface
import hdtv.plugins.fitmap
import hdtv.plugins.peakfinder
from hdtv.plugins.fitInterface import fit_interface
from hdtv.plugins.specInterface import spec_interface

spectra = __main__.spectra

testspectrumfile = "osiris_bg.spc"
testspectrum = os.path.join(os.path.curdir, "tests", "share", testspectrumfile)


@pytest.fixture(autouse=True)
def prepare():
    fit_interface.ResetFitterParameters()
    hdtv.options.Set("table", "classic")
    hdtv.options.Set("uncertainties", "short")
    for _ in range(3):
        spec_interface.LoadSpectra(testspectrum)
    spectra.ActivateObject("0")
    yield
    spectra.Clear()


def test_cmd_cal_pos_set():
    f, ferr = hdtvcmd("calibration position set 1 2")
    assert ferr == ""
    assert "Calibrated spectrum with id 0" in f


def test_cmd_cal_pos_set_3():
    f, ferr = hdtvcmd("calibration position set 1 2 0.0001")
    assert ferr == ""
    assert "Calibrated spectrum with id 0" in f


def test_cmd_cal_pos_unset():
    hdtvcmd("calibration position set 1 2")
    f, ferr = hdtvcmd("calibration position unset")
    assert ferr == ""
    assert "Unsetting calibration of spectrum with id 0" in f


def test_cmd_cal_pos_copy():
    hdtvcmd("calibration position set 1 2 -s 0")
    f, ferr = hdtvcmd("calibration position copy 0 1")
    assert ferr == ""
    assert "Calibrated spectrum with id 1" in f


def test_cmd_cal_pos_enter():
    f, ferr = hdtvcmd("calibration position enter 1543 1173.228(3) 1747 1332.492(4)")
    assert ferr == ""
    assert "Calibrated spectrum with id 0" in f
    assert "Chi" in f


def test_cmd_cal_pos_enter_underdefined():
    f, ferr = hdtvcmd(
        "calibration position enter -d 2 1543 1173.228(3) 1747 1332.492(4)"
    )
    assert "You must specify at least" in ferr


def test_cmd_cal_pos_enter_deg2():
    f, ferr = hdtvcmd(
        "calibration position enter -d 2 1543 1173.228(3) 1747 1332.492(4) 3428 2614.5"
    )
    assert ferr == ""
    assert "Calibrated spectrum with id 0" in f


def test_cmd_cal_pos_enter_table():
    f, ferr = hdtvcmd("calibration position enter -t 1543 1173.228(3) 1747 1332.492(4)")
    assert ferr == ""
    assert "Residual" in f


def test_cmd_cal_pos_assign():
    hdtvcmd("fit peakfind -a -t 0.005")
    f, ferr = hdtvcmd("cal position assign 3.0 1173.228(3) 5.0 1332.492(4)")
    assert ferr == ""
    assert "Calibrated spectrum with id 0" in f


def test_cmd_cal_pos_list():
    hdtvcmd("cal pos set 1 2")
    f, ferr = hdtvcmd("cal position list")
    assert ferr == ""
    assert testspectrumfile + ": 1.0   2.0" in f


@pytest.mark.parametrize("callistfile", ["tests/share/callist.cal"])
def test_cmd_cal_pos_list_read(callistfile):
    f, ferr = hdtvcmd(f"cal position list read {callistfile}")
    assert ferr == ""
    assert "Calibrated spectrum with id 0" in f


@pytest.mark.parametrize("callistfile", ["tests/share/callist.cal"])
def test_cmd_cal_pos_list_clear(callistfile):
    hdtvcmd(f"cal position list read {callistfile}")
    f, ferr = hdtvcmd("cal position list clear")
    assert ferr == ""
    assert "Unsetting calibration of spectrum with id 0" in f


@pytest.mark.parametrize("callistfile", ["tests/share/callist.cal"])
def test_cmd_cal_pos_list_write(callistfile, temp_file):
    hdtvcmd(f"cal position list read {callistfile}")
    f, ferr = hdtvcmd(f"cal position list write -F {temp_file}")
    assert ferr == ""
    assert f == ""
    assert filecmp.cmp(callistfile, temp_file)


def test_cmd_cal_pos_recalibrate():
    hdtvcmd("fit peakfind -a -t 0.005")
    hdtvcmd("fit position assign 3.0 1173.228(3) 5.0 1332.492(4)")
    f, ferr = hdtvcmd("calibration position recalibrate")
    assert ferr == ""
    assert "Calibrated spectrum with id 0" in f
    assert "Chi" in f


@pytest.mark.parametrize("calfile", ["tests/share/osiris_bg.cal"])
def test_cmd_cal_pos_read(calfile):
    f, ferr = hdtvcmd(f"calibration position read {calfile}")
    assert ferr == ""
    assert "Calibrated spectrum with id 0" in f


@pytest.mark.parametrize("nuclide", ["Co-60", "Cs-137"])
def test_cmd_nuclide(nuclide):
    f, ferr = hdtvcmd(f"nuclide {nuclide}")
    assert ferr == ""
    assert "Nuclide:" in f
    assert "energy" in f
    assert "intensity" in f


@pytest.mark.parametrize(
    "parameters, function",
    [
        ("0.1,0.2,0.3,0.4,0.5", "pow"),
        ("0.1,0.2,0.3,0.4,0.5", "exp"),
        ("0.1,0.2,0.3,0.4,0.5", "poly"),
        ("0.1,0.2,0.3,0.4,0.5", "wiedenhoever"),
        ("0.1,0.2,0.3,0.4,0.5", "wunder"),
    ],
)
def test_cmd_cal_eff_set(parameters, function):
    f, ferr = hdtvcmd(f"calibration efficiency set -p {parameters} {function}")
    assert ferr == ""
    assert f == ""


@pytest.mark.parametrize("args", ["", "0", "all", "0 1", "0,1"])
def test_cmd_cal_eff_list(args):
    f, ferr = hdtvcmd(f"calibration efficiency list {args}")
    assert ferr == ""
    assert "Parameter" in f


@pytest.mark.parametrize(
    "parfile, efffunction", [("tests/share/osiris_bg.par", "wunder")]
)
def test_cmd_cal_eff_read_par(parfile, efffunction):
    hdtvcmd(f"calibration efficiency set {efffunction}")
    f, ferr = hdtvcmd(f"calibration efficiency read parameter {parfile}")
    assert ferr == ""
    assert f == ""


@pytest.mark.parametrize(
    "parfile, covfile, efffunction",
    [("tests/share/osiris_bg.par", "tests/share/osiris_bg.cov", "wunder")],
)
def test_cmd_cal_eff_read_cov(parfile, covfile, efffunction):
    hdtvcmd(f"calibration efficiency set {efffunction}")
    hdtvcmd(f"calibration efficiency read parameter {parfile}")
    f, ferr = hdtvcmd(f"calibration efficiency read covariance {covfile}")
    assert ferr == ""
    assert f == ""


@pytest.mark.skipif(
    sys.version_info < (3, 0), reason="Floating Point differences in py2"
)
@pytest.mark.parametrize(
    "parfile, covfile, efffunction",
    [("tests/share/osiris_bg.par", "tests/share/osiris_bg.cov", "wunder")],
)
def test_cmd_cal_eff_write_par(parfile, covfile, efffunction, temp_file):
    hdtvcmd(f"calibration efficiency set {efffunction}")
    hdtvcmd(f"calibration efficiency read parameter {parfile}")
    hdtvcmd(f"calibration efficiency read covariance {covfile}")
    f, ferr = hdtvcmd(f"cal efficiency write parameter {temp_file}")
    assert ferr == ""
    assert f == ""
    assert filecmp.cmp(parfile, temp_file)


@pytest.mark.skipif(
    sys.version_info < (3, 0), reason="Floating Point differences in py2"
)
@pytest.mark.parametrize(
    "parfile, covfile, efffunction",
    [("tests/share/osiris_bg.par", "tests/share/osiris_bg.cov", "wunder")],
)
def test_cmd_cal_eff_write_cov(parfile, covfile, efffunction, temp_file):
    hdtvcmd(f"calibration efficiency set {efffunction}")
    hdtvcmd(f"calibration efficiency read parameter {parfile}")
    hdtvcmd(f"calibration efficiency read covariance {covfile}")
    f, ferr = hdtvcmd(f"cal efficiency write covariance {temp_file}")
    assert ferr == ""
    assert f == ""
    assert filecmp.cmp(covfile, temp_file)


@pytest.mark.skip(reason="Sample spectrum not sufficient for test?")
def test_cmd_cal_pos_nuclide():
    raise NotImplementedError


@pytest.mark.skip(reason="Sample spectrum not sufficient for test?")
def test_cmd_cal_eff_fit():
    raise NotImplementedError


@pytest.mark.skip(reason="Hard to test")
def test_cmd_cal_eff_plot():
    raise NotImplementedError
