import io
import re
import os
import sys
import tempfile
import filecmp

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

@pytest.mark.parametrize("specfile, callistfile", [
    ("test/share/example_Co60.tv", "test/share/callist.cal")])
def test_cmd_cal_pos_list_read(specfile, callistfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("cal position list read {}".format(callistfile))
    assert ferr.getvalue().strip() == ""
    assert "Calibrated spectrum with id 0" in f.getvalue()

@pytest.mark.parametrize("specfile, callistfile", [
    ("test/share/example_Co60.tv", "test/share/callist.cal")])
def test_cmd_cal_pos_list_clear(specfile, callistfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    command_line.DoLine("cal position list read {}".format(callistfile))
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("cal position list clear")
    assert ferr.getvalue().strip() == ""
    assert "Unsetting calibration of spectrum with id 0" in f.getvalue()

@pytest.mark.parametrize("specfile, callistfile", [
    ("test/share/example_Co60.tv", "test/share/callist.cal")])
def test_cmd_cal_pos_list_write(specfile, callistfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    command_line.DoLine("cal position list read {}".format(callistfile))
    try:
        outfile = tempfile.mkstemp(".cal", "hdtv_cplwtest_")[1]
        f = io.StringIO()
        ferr = io.StringIO()
        with redirect_stdout(f, ferr):
            command_line.DoLine("cal position list write -F {}".format(outfile))
        assert ferr.getvalue().strip() == ""
        assert f.getvalue().strip() == ""
        assert filecmp.cmp(callistfile, outfile)
    finally:
        os.remove(outfile)

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

@pytest.mark.parametrize("nuclide", [
    "Co-60", "Cs-137"])
def test_cmd_nuclide(nuclide):
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("nuclide {}".format(nuclide))
    assert ferr.getvalue().strip() == ""
    assert "Data of the nuclide" in f.getvalue()
    assert "Energy" in f.getvalue()
    assert "Intensity" in f.getvalue()

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
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine(
            "calibration efficiency set -p {} {}".format(parameters, function))
    assert ferr.getvalue().strip() == ""
    assert f.getvalue().strip() == ""

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
@pytest.mark.parametrize("args", [
    "", "0", "all", "0 1", "0,1"])
def test_cmd_cal_eff_list(specfile, args):
    for _ in range(3):
        s.tv.specIf.LoadSpectra(specfile, None)
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine(
            "calibration efficiency list {}".format(args))
    assert ferr.getvalue().strip() == ""
    assert "Parameter" in f.getvalue()

@pytest.mark.parametrize("specfile, parfile, efffunction", [(
    "test/share/example_Co60.tv",
    "test/share/example_Co60.par",
    "wunder")])
def test_cmd_cal_eff_read_par(specfile, parfile, efffunction):
    s.tv.specIf.LoadSpectra(specfile, None)
    command_line.DoLine(
        "calibration efficiency set {}".format(efffunction))
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine(
            "calibration efficiency read parameter {}".format(parfile))
    assert ferr.getvalue().strip() == ""
    assert f.getvalue().strip() == ""

@pytest.mark.parametrize("specfile, parfile, covfile, efffunction", [(
    "test/share/example_Co60.tv",
    "test/share/example_Co60.par",
    "test/share/example_Co60.cov",
    "wunder")])
def test_cmd_cal_eff_read_cov(specfile, parfile, covfile, efffunction):
    s.tv.specIf.LoadSpectra(specfile, None)
    command_line.DoLine(
        "calibration efficiency set {}".format(efffunction))
    command_line.DoLine(
        "calibration efficiency read parameter {}".format(parfile))
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine(
            "calibration efficiency read covariance {}".format(covfile))
    assert ferr.getvalue().strip() == ""
    assert f.getvalue().strip() == ""

@pytest.mark.parametrize("specfile, parfile, covfile, efffunction", [(
    "test/share/example_Co60.tv",
    "test/share/example_Co60.par",
    "test/share/example_Co60.cov",
    "wunder")])
def test_cmd_cal_eff_write_par(specfile, parfile, covfile, efffunction):
    s.tv.specIf.LoadSpectra(specfile, None)
    command_line.DoLine(
        "calibration efficiency set {}".format(efffunction))
    command_line.DoLine(
        "calibration efficiency read parameter {}".format(parfile))
    command_line.DoLine(
        "calibration efficiency read covariance {}".format(covfile))
    try:
        outfile = tempfile.mkstemp(".par", "hdtv_cewptest_")[1]
        f = io.StringIO()
        ferr = io.StringIO()
        with redirect_stdout(f, ferr):
            command_line.DoLine("cal efficiency write parameter {}".format(outfile))
        assert ferr.getvalue().strip() == ""
        assert f.getvalue().strip() == ""
        assert filecmp.cmp(parfile, outfile)
    finally:
        pass
        #os.remove(outfile)

@pytest.mark.parametrize("specfile, parfile, covfile, efffunction", [(
    "test/share/example_Co60.tv",
    "test/share/example_Co60.par",
    "test/share/example_Co60.cov",
    "wunder")])
def test_cmd_cal_eff_write_cov(specfile, parfile, covfile, efffunction):
    s.tv.specIf.LoadSpectra(specfile, None)
    command_line.DoLine(
        "calibration efficiency set {}".format(efffunction))
    command_line.DoLine(
        "calibration efficiency read parameter {}".format(parfile))
    command_line.DoLine(
        "calibration efficiency read covariance {}".format(covfile))
    try:
        outfile = tempfile.mkstemp(".cov", "hdtv_cewctest_")[1]
        f = io.StringIO()
        ferr = io.StringIO()
        with redirect_stdout(f, ferr):
            command_line.DoLine("cal efficiency write covariance {}".format(outfile))
        assert ferr.getvalue().strip() == ""
        assert f.getvalue().strip() == ""
        assert filecmp.cmp(covfile, outfile)
    finally:
        os.remove(outfile)

@pytest.mark.skip(reason="Sample spectrum not sufficient for test?")
def test_cmd_cal_pos_nuclide():
    raise NotImplementedError

@pytest.mark.skip(reason="Sample spectrum not sufficient for test?")
def test_cmd_cal_eff_fit():
    raise NotImplementedError

@pytest.mark.skip(reason="Hard to test")
def test_cmd_cal_eff_plot():
    raise NotImplementedError
