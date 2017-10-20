import io
import re
import os
import sys

import pytest

from helpers.utils import redirect_stdout

from hdtv.cmdline import command_line
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
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("calibration position set 1 2")
    assert ferr.getvalue().strip() == ""
    assert "Calibrated spectrum with id 0" in f.getvalue()

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_set_3(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("calibration position set 1 2 0.0001")
    assert ferr.getvalue().strip() == ""
    assert "Calibrated spectrum with id 0" in f.getvalue()

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_unset(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    command_line.DoLine("calibration position set 1 2")
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("calibration position unset")
    assert ferr.getvalue().strip() == ""
    assert "Unsetting calibration of spectrum with id 0" in f.getvalue()

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_copy(specfile):
    for _ in range(2):
        s.tv.specIf.LoadSpectra(specfile, None)
    command_line.DoLine("calibration position set 1 2 -s 0")
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("calibration position copy 0 1")
    assert ferr.getvalue().strip() == ""
    assert "Calibrated spectrum with id 1" in f.getvalue()

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_enter(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("calibration position enter 1543 1173.228(3) 1747 1332.492(4)")
    assert ferr.getvalue().strip() == ""
    assert "Calibrated spectrum with id 0" in f.getvalue()
    assert "Chi^2" in f.getvalue()

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_enter_underdefined(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("calibration position enter -d 2 1543 1173.228(3) 1747 1332.492(4)")
    assert "usage" in f.getvalue().strip()
    assert "You must specify at least" in ferr.getvalue()

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_enter_deg2(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine(
            "calibration position enter -d 2 1543 1173.228(3) 1747 1332.492(4) 3428 2614.5")
    assert ferr.getvalue().strip() == ""
    assert "Calibrated spectrum with id 0" in f.getvalue()

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_enter_table(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("calibration position enter -t 1543 1173.228(3) 1747 1332.492(4)")
    assert ferr.getvalue().strip() == ""
    assert "Residual" in f.getvalue()

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_assign(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    command_line.DoLine("fit peakfind -a -t 0.005")
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("cal position assign 3.0 1173.228(3) 5.0 1332.492(4)")
    assert ferr.getvalue().strip() == ""
    assert "Calibrated spectrum with id 0" in f.getvalue()

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_list(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    command_line.DoLine("cal pos set 1 2")
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("cal position list")
    assert ferr.getvalue().strip() == ""
    assert "example_Co60.tv: 1.0   2.0" in f.getvalue()

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_cal_pos_recalibrate(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    command_line.DoLine("fit peakfind -a -t 0.005")
    command_line.DoLine("fit position assign 3.0 1173.228(3) 5.0 1332.492(4)")
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("calibration position recalibrate")
    assert ferr.getvalue().strip() == ""
    assert "Calibrated spectrum with id 0" in f.getvalue()
    assert "Chi^2" in f.getvalue()

@pytest.mark.parametrize("specfile, calfile", [
    ("test/share/example_Co60.tv", "test/share/example_Co60.cal")])
def test_cmd_cal_pos_read(specfile, calfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("calibration position read {}".format(calfile))
    assert ferr.getvalue().strip() == ""
    assert "Calibrated spectrum with id 0" in f.getvalue()


# TODO: No tests for:
# calibration position nuclide
