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
import filecmp

import pytest

from helpers.utils import redirect_stdout, hdtvcmd
from helpers.fixtures import temp_file

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

@pytest.yield_fixture(autouse=True)
def prepare():
    for (ID, _) in dict(s.spectra.dict).items():
        s.spectra.Pop(ID)

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_set(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    f, ferr = hdtvcmd("calibration position set 1 2")
    assert ferr == ""
    assert "Calibrated spectrum with id 0" in f

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_set_3(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    f, ferr = hdtvcmd("calibration position set 1 2 0.0001")
    assert ferr == ""
    assert "Calibrated spectrum with id 0" in f

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_unset(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    hdtvcmd("calibration position set 1 2")
    f, ferr = hdtvcmd("calibration position unset")
    assert ferr == ""
    assert "Unsetting calibration of spectrum with id 0" in f

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_copy(specfile):
    for _ in range(2):
        s.tv.specIf.LoadSpectra(specfile, None)
    hdtvcmd("calibration position set 1 2 -s 0")
    f, ferr = hdtvcmd("calibration position copy 0 1")
    assert ferr == ""
    assert "Calibrated spectrum with id 1" in f

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_enter(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    f, ferr = hdtvcmd("calibration position enter 1543 1173.228(3) 1747 1332.492(4)")
    assert ferr == ""
    assert "Calibrated spectrum with id 0" in f
    assert "Chi^2" in f

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_enter_underdefined(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    f, ferr = hdtvcmd("calibration position enter -d 2 1543 1173.228(3) 1747 1332.492(4)")
    assert "usage" in f
    assert "You must specify at least" in ferr

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_enter_deg2(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    f, ferr = hdtvcmd(
            "calibration position enter -d 2 1543 1173.228(3) 1747 1332.492(4) 3428 2614.5")
    assert ferr == ""
    assert "Calibrated spectrum with id 0" in f

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_enter_table(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    f, ferr = hdtvcmd("calibration position enter -t 1543 1173.228(3) 1747 1332.492(4)")
    assert ferr == ""
    assert "Residual" in f

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_assign(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    hdtvcmd("fit peakfind -a -t 0.005")
    f, ferr = hdtvcmd("cal position assign 3.0 1173.228(3) 5.0 1332.492(4)")
    assert ferr == ""
    assert "Calibrated spectrum with id 0" in f

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_list(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    hdtvcmd("cal pos set 1 2")
    f, ferr = hdtvcmd("cal position list")
    assert ferr == ""
    assert "example_Co60.tv: 1.0   2.0" in f

@pytest.mark.parametrize("specfile, callistfile", [
    ("test/share/example_Co60.tv", "test/share/callist.cal")])
def test_cmd_cal_pos_list_read(specfile, callistfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    f, ferr = hdtvcmd("cal position list read {}".format(callistfile))
    assert ferr == ""
    assert "Calibrated spectrum with id 0" in f

@pytest.mark.parametrize("specfile, callistfile", [
    ("test/share/example_Co60.tv", "test/share/callist.cal")])
def test_cmd_cal_pos_list_clear(specfile, callistfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    hdtvcmd("cal position list read {}".format(callistfile))
    f, ferr = hdtvcmd("cal position list clear")
    assert ferr == ""
    assert "Unsetting calibration of spectrum with id 0" in f

@pytest.mark.parametrize("specfile, callistfile", [
    ("test/share/example_Co60.tv", "test/share/callist.cal")])
def test_cmd_cal_pos_list_write(specfile, callistfile, temp_file):
    s.tv.specIf.LoadSpectra(specfile, None)
    hdtvcmd("cal position list read {}".format(callistfile))
    f, ferr = hdtvcmd("cal position list write -F {}".format(temp_file))
    assert ferr == ""
    assert f == ""
    assert filecmp.cmp(callistfile, temp_file)

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_recalibrate(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    hdtvcmd("fit peakfind -a -t 0.005")
    hdtvcmd("fit position assign 3.0 1173.228(3) 5.0 1332.492(4)")
    f, ferr = hdtvcmd("calibration position recalibrate")
    assert ferr == ""
    assert "Calibrated spectrum with id 0" in f
    assert "Chi^2" in f

@pytest.mark.parametrize("specfile, calfile", [
    ("test/share/example_Co60.tv", "test/share/example_Co60.cal")])
def test_cmd_cal_pos_read(specfile, calfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    f, ferr = hdtvcmd("calibration position read {}".format(calfile))
    assert ferr == ""
    assert "Calibrated spectrum with id 0" in f

@pytest.mark.parametrize("nuclide", [
    "Co-60", "Cs-137"])
def test_cmd_nuclide(nuclide):
    f, ferr = hdtvcmd("nuclide {}".format(nuclide))
    assert ferr == ""
    assert "Data of the nuclide" in f
    assert "Energy" in f
    assert "Intensity" in f

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
@pytest.mark.parametrize("parameters, function", [
    ("0.1,0.2,0.3,0.4,0.5", "pow"),
    ("0.1,0.2,0.3,0.4,0.5", "exp"),
    ("0.1,0.2,0.3,0.4,0.5", "poly"),
    ("0.1,0.2,0.3,0.4,0.5", "wiedenhoever"),
    ("0.1,0.2,0.3,0.4,0.5", "wunder")])
def test_cmd_cal_eff_set(specfile, parameters,function):
    s.tv.specIf.LoadSpectra(specfile, None)
    f, ferr = hdtvcmd(
            "calibration efficiency set -p {} {}".format(parameters, function))
    assert ferr == ""
    assert f == ""

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
@pytest.mark.parametrize("args", [
    "", "0", "all", "0 1", "0,1"])
def test_cmd_cal_eff_list(specfile, args):
    for _ in range(3):
        s.tv.specIf.LoadSpectra(specfile, None)
    f, ferr = hdtvcmd(
            "calibration efficiency list {}".format(args))
    assert ferr == ""
    assert "Parameter" in f

@pytest.mark.parametrize("specfile, parfile, efffunction", [(
    "test/share/example_Co60.tv",
    "test/share/example_Co60.par",
    "wunder")])
def test_cmd_cal_eff_read_par(specfile, parfile, efffunction):
    s.tv.specIf.LoadSpectra(specfile, None)
    hdtvcmd(
        "calibration efficiency set {}".format(efffunction))
    f, ferr = hdtvcmd(
            "calibration efficiency read parameter {}".format(parfile))
    assert ferr == ""
    assert f == ""

@pytest.mark.parametrize("specfile, parfile, covfile, efffunction", [(
    "test/share/example_Co60.tv",
    "test/share/example_Co60.par",
    "test/share/example_Co60.cov",
    "wunder")])
def test_cmd_cal_eff_read_cov(specfile, parfile, covfile, efffunction):
    s.tv.specIf.LoadSpectra(specfile, None)
    hdtvcmd(
        "calibration efficiency set {}".format(efffunction))
    hdtvcmd(
        "calibration efficiency read parameter {}".format(parfile))
    f, ferr = hdtvcmd(
            "calibration efficiency read covariance {}".format(covfile))
    assert ferr == ""
    assert f == ""

@pytest.mark.parametrize("specfile, parfile, covfile, efffunction", [(
    "test/share/example_Co60.tv",
    "test/share/example_Co60.par",
    "test/share/example_Co60.cov",
    "wunder")])
def test_cmd_cal_eff_write_par(specfile, parfile, covfile, efffunction, temp_file):
    s.tv.specIf.LoadSpectra(specfile, None)
    hdtvcmd(
        "calibration efficiency set {}".format(efffunction))
    hdtvcmd(
        "calibration efficiency read parameter {}".format(parfile))
    hdtvcmd(
        "calibration efficiency read covariance {}".format(covfile))
    f, ferr = hdtvcmd("cal efficiency write parameter {}".format(temp_file))
    assert ferr == ""
    assert f == ""
    assert filecmp.cmp(parfile, temp_file)

@pytest.mark.parametrize("specfile, parfile, covfile, efffunction", [(
    "test/share/example_Co60.tv",
    "test/share/example_Co60.par",
    "test/share/example_Co60.cov",
    "wunder")])
def test_cmd_cal_eff_write_cov(specfile, parfile, covfile, efffunction, temp_file):
    s.tv.specIf.LoadSpectra(specfile, None)
    hdtvcmd(
        "calibration efficiency set {}".format(efffunction))
    hdtvcmd(
        "calibration efficiency read parameter {}".format(parfile))
    hdtvcmd(
        "calibration efficiency read covariance {}".format(covfile))
    f, ferr = hdtvcmd("cal efficiency write covariance {}".format(temp_file))
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
