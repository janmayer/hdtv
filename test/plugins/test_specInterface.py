#!/usr/bin/env python

import io
import re
import os
import sys
import warnings
import tempfile
import shutil

import pytest

from helpers.utils import redirect_stdout

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

s = __main__.s

@pytest.yield_fixture(autouse=True)
def prepare():
    for (ID, _) in dict(s.spectra.dict).items():
        s.spectra.Pop(ID)

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_spectrum_get(specfile):
    assert len(s.spectra.dict) == 0
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    out = f.getvalue()
    res_specfile, specid = re.search('Loaded (.*) into (\d+)', f.getvalue().strip()).groups()
    assert len(s.spectra.dict) == 1
    assert res_specfile == specfile
    for (ID, obj) in s.spectra.dict.items():
        assert str(ID) == specid
        assert type(obj) == hdtv.spectrum.Spectrum

@pytest.mark.parametrize("specfile, slot", [
    ("test/share/example_Co60.tv", 3),
    ("test/share/example_Co60.tv", 1000000)])
def test_cmd_spectrum_get_slot(specfile, slot):
    assert len(s.spectra.dict) == 0
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("spectrum get -s {} {}".format(
            slot, specfile))
    out = f.getvalue()
    res_specfile, specid = re.search('Loaded (.*) into (\d+)', f.getvalue().strip()).groups()
    assert len(s.spectra.dict) == 1
    assert res_specfile == specfile
    assert specid == str(slot)
    for (ID, obj) in s.spectra.dict.items():
        assert str(ID) == specid
        assert type(obj) == hdtv.spectrum.Spectrum

@pytest.mark.parametrize("specfile, num", [
    ("test/share/example_Co60.tv", 4),
    ("test/share/example_Co60.tv", 40)])
def test_cmd_spectrum_get_repeated(specfile, num):
    assert len(s.spectra.dict) == 0
    query = " ".join([specfile]*num)
    hdtv.cmdline.command_line.DoLine("spectrum get {}".format(query))
    assert len(s.spectra.dict) == num

@pytest.mark.parametrize("pattern", [
    "test/share/example_Co60.*"])
def test_cmd_spectrum_get_pattern(pattern):
    assert len(s.spectra.dict) == 0
    hdtv.cmdline.command_line.DoLine("spectrum get {}".format(pattern))
    assert len(s.spectra.dict) == 2

@pytest.mark.parametrize("specfiles", [
    ["test/share/example_Co60.tv", "test/share/example_Co60.cal"]])
def test_cmd_spectrum_get_multi(specfiles):
    assert len(s.spectra.dict) == 0
    query = " ".join(specfiles)
    hdtv.cmdline.command_line.DoLine("spectrum get {}".format(query))
    assert len(s.spectra.dict) == len(specfiles)

@pytest.mark.parametrize("specfile, numspecs", [
    ("test/share/example_Co60.tv", 1),
    ("test/share/example_Co60.tv", 10)])
def test_cmd_spectrum_list(specfile, numspecs):
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("spectrum list".format(specfile))
    out = f.getvalue()
    assert len(s.spectra.dict) == numspecs
    assert len(out.strip().split('\n')) == numspecs + 2

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_spectrum_delete(specfile):
    assert len(s.spectra.dict) == 0
    f = io.StringIO()
    with redirect_stdout(f):
        hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    out = f.getvalue()
    res_specfile, specid = re.search('Loaded (.*) into (\d+)', f.getvalue().strip()).groups()
 
    assert len(s.spectra.dict) == 1

    f = io.StringIO()
    with redirect_stdout(f):
        hdtv.cmdline.command_line.DoLine("spectrum delete {}".format(specid))
    out = f.getvalue()

    assert len(s.spectra.dict) == 0

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_spectrum_delete_none(specfile):
    assert len(s.spectra.dict) == 0
    hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 1

    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("spectrum delete")
    assert "WARNING: Nothing to do" in ferr.getvalue()
    assert len(s.spectra.dict) == 1

@pytest.mark.parametrize("specfile, numspecs", [
    ("test/share/example_Co60.tv", 1),
    ("test/share/example_Co60.tv", 5)])
def test_cmd_spectrum_delete_all(specfile, numspecs):
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == numspecs

    hdtv.cmdline.command_line.DoLine("spectrum delete all")
    assert len(s.spectra.dict) == 0

@pytest.mark.parametrize("specfile, numspecs", [
    ("test/share/example_Co60.tv", 1),
    ("test/share/example_Co60.tv", 5)])
def test_cmd_spectrum_delete_several(specfile, numspecs):
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == numspecs

    specs = ' '.join(str(e) for e in range(numspecs))
    hdtv.cmdline.command_line.DoLine("spectrum delete {}".format(specs))
    assert len(s.spectra.dict) == 0

@pytest.mark.parametrize("specfile, numspecs", [
    ("test/share/example_Co60.tv", 2),
    ("test/share/example_Co60.tv", 5)])
def test_cmd_spectrum_hide(specfile, numspecs):
    numhidespecs = max(1, numspecs//2)
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == numspecs

    specs = ' '.join(str(e) for e in range(numhidespecs))
    hdtv.cmdline.command_line.DoLine("spectrum hide {}".format(specs))

    f = io.StringIO()
    with redirect_stdout(f):
        hdtv.cmdline.command_line.DoLine("spectrum list -v")
    out = f.getvalue()
    assert len(s.spectra.dict) == numspecs
    assert len(out.strip().split('\n')) == numspecs - numhidespecs + 2

@pytest.mark.parametrize("specfile, numspecs", [
    ("test/share/example_Co60.tv", 2),
    ("test/share/example_Co60.tv", 5)])
def test_cmd_spectrum_show(specfile, numspecs):
    numshowspecs = max(1, numspecs//2)
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == numspecs

    specs = ' '.join(str(e) for e in range(numshowspecs))
    hdtv.cmdline.command_line.DoLine("spectrum show {}".format(specs))

    f = io.StringIO()
    with redirect_stdout(f):
        hdtv.cmdline.command_line.DoLine("spectrum list -v")
    out = f.getvalue()
    print(out)
    assert len(s.spectra.dict) == numspecs
    assert len(out.strip().split('\n')) == numshowspecs + 2

@pytest.mark.parametrize("specfile, numspecs", [
    ("test/share/example_Co60.tv", 1),
    ("test/share/example_Co60.tv", 2),
    ("test/share/example_Co60.tv", 5)])
def test_cmd_spectrum_activate(specfile, numspecs):
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == numspecs

    for specid in range(numspecs):
        hdtv.cmdline.command_line.DoLine("spectrum activate {}".format(specid))
        f = io.StringIO()
        with redirect_stdout(f):
            hdtv.cmdline.command_line.DoLine("spectrum list")
        for i, line in enumerate(f.getvalue().strip().split('\n')):
            if i == specid+2:
                assert "|   AV |" in line
            elif i>2:
                assert "|    V |" in line 

@pytest.mark.parametrize("specfile, numspecs", [
    ("test/share/example_Co60.tv", 0),
    ("test/share/example_Co60.tv", 1),
    ("test/share/example_Co60.tv", 2),
    ("test/share/example_Co60.tv", 5)])
def test_cmd_spectrum_activate_multi(specfile, numspecs):
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == numspecs

    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("spectrum activate all")
    if numspecs > 1:
        assert "Can only activate one spectrum" in ferr.getvalue()
        assert "usage" in f.getvalue()
    else:
        assert "" == ferr.getvalue().strip()
        assert "" == f.getvalue().strip()

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_spectrum_info(specfile):
    assert len(s.spectra.dict) == 0
    hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 1

    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("spectrum info")
    assert ferr.getvalue().strip() == ""
    # If lots of stuff is printed, `spectrum info` is doing its job.
    assert len(f.getvalue().strip().split('\n')) == 9

@pytest.mark.parametrize("specfile, name", [
    ("test/share/example_Co60.tv", "myname")])
def test_cmd_spectrum_name(specfile, name):
    assert len(s.spectra.dict) == 0
    hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 1

    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("spectrum name {}".format(name))
    print(ferr.getvalue())
    print(f.getvalue())
    assert ferr.getvalue().strip() == ""
    assert "Renamed spectrum 0 to '{}'".format(name) in f.getvalue()

    f = io.StringIO()
    with redirect_stdout(f):
        hdtv.cmdline.command_line.DoLine("spectrum list")
    assert name in f.getvalue()

@pytest.mark.parametrize("specfile", [
    ("test/share/example_Co60.tv")])
def test_cmd_spectrum_normalize(specfile):
    assert len(s.spectra.dict) == 0
    for _ in range(3):
        hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 3
    for specids, norm in [("0", 0.3), ("0 1 2", 0.2)]:
        hdtv.cmdline.command_line.DoLine(
            "spectrum normalize {} {}".format(specids, norm))
        assert get_spec(0).norm == norm
    assert get_spec(2).norm == 0.2
    # TODO: Is there anything else supposed to happen when normalizing?

@pytest.mark.parametrize("specfile, ngroup", [
    ("test/share/example_Co60.tv", 2),
    ("test/share/example_Co60.tv", 20)])
def test_cmd_spectrum_rebin(specfile, ngroup):
    assert len(s.spectra.dict) == 0
    hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 1

    with warnings.catch_warnings(record=True) as w:
        f = io.StringIO()
        with redirect_stdout(f):
            hdtv.cmdline.command_line.DoLine("spectrum rebin 0 {}".format(ngroup))
        assert "Rebinning 0 with {} bins per new bin".format(ngroup) in f.getvalue()
        assert get_spec(0).hist.hist.GetNbinsX() == 16001//ngroup

@pytest.mark.parametrize("specfile, copy, matches", [
    ("test/share/example_Co60.tv", '0', ["0 to 3"]),
    ("test/share/example_Co60.tv", '0 1', ["0 to 3", "1 to 4"]),
    ("test/share/example_Co60.tv", '2 -s 3000', ["2 to 3000"]),
    ("test/share/example_Co60.tv", '0,1 -s 8,7', ["0 to 7", "1 to 8"]),
    ("test/share/example_Co60.tv", '0-2', ["0 to 3", "1 to 4", "2 to 5"]),
    ("test/share/example_Co60.tv", '2 -s 0', ["2 to 0"])])
def test_cmd_spectrum_copy(specfile, copy, matches):
    assert len(s.spectra.dict) == 0
    for _ in range(3):
        hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 3
    f = io.StringIO()
    with redirect_stdout(f):
        hdtv.cmdline.command_line.DoLine("spectrum copy {}".format(copy))
    for match in matches:
        assert "Copied spectrum {}".format(match) in f.getvalue()

def test_cmd_spectrum_copy_nonexistant():
    assert len(s.spectra.dict) == 0
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("spectrum copy 0")
    assert "WARNING: Non-existent id 0" in ferr.getvalue()
    assert "WARNING: Nothing to do" in ferr.getvalue()

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
@pytest.mark.parametrize("fmt", [
    "lc", "txt"])
def test_cmd_spectrum_write(specfile, fmt, suffix=""):
    assert len(s.spectra.dict) == 0
    hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 1
    try:
        outfile = tempfile.mkstemp("." + fmt, "hdtv_swtest_")[1]
        f = io.StringIO()
        with redirect_stdout(f):
            hdtv.cmdline.command_line.DoLine(
                "spectrum write {} {}{}".format(outfile, fmt, suffix))
        assert "Wrote spectrum with id 0 to file {}".format(
            outfile) in f.getvalue()
        assert os.path.getsize(outfile) > 0
    finally:
        os.remove(outfile)

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
@pytest.mark.parametrize("fmt", [
    "lc", "txt"])
def test_cmd_spectrum_write_withid(specfile, fmt):
    test_cmd_spectrum_write(specfile, fmt, suffix=" 0")

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_spectrum_write_invalid_format(specfile):
    assert len(s.spectra.dict) == 0
    hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 1
    outfile = tempfile.mkstemp(".invalid", "hdtv_swtest_")[1]
    try:
        f = io.StringIO()
        ferr = io.StringIO()
        with redirect_stdout(f, ferr):
            hdtv.cmdline.command_line.DoLine(
                "spectrum write {} invalid 0".format(outfile))
        assert os.path.getsize(outfile) == 0
        assert "ERROR: Failed to write spectrum: Invalid format specified" in ferr.getvalue()
    finally:
        os.remove(outfile)

@pytest.mark.parametrize("specfile, factor, specids, response", [
    ("test/share/example_Co60.tv", 0.1, "0", ["0"]),
    ("test/share/example_Co60.tv", 0.2, "0,1", ["0", "1"]),
    ("test/share/example_Co60.tv", 0.5, "0 2", ["0", "2"]),
    ("test/share/example_Co60.tv", 20, "0-2", ["0", "1", "2"]),
    ("test/share/example_Co60.tv", 2, "0", ["0"])])
def test_cmd_spectrum_multiply(specfile, factor, specids, response):
    assert len(s.spectra.dict) == 0
    for _ in range(3):
        hdtv.cmdline.command_line.DoLine(
            "spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 3
    orig_count = get_spec(0).hist.hist.GetSum()
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine(
            "spectrum multiply {} {}".format(specids, factor))
    for spec in response:
        assert "Multiplying {} with {}".format(spec, factor) in f.getvalue()
    new_count = get_spec(0).hist.hist.GetSum()
    assert orig_count * factor - new_count < 0.00001 * new_count

@pytest.mark.parametrize("specfile0, specfile1", [
    ("test/share/example_Co60.tv", "test/share/example_Co60.tv")])
def test_cmd_spectrum_add(specfile0, specfile1):
    assert len(s.spectra.dict) == 0
    hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile0))
    hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile1))
    assert len(s.spectra.dict) == 2
    spec0_count = get_spec(0).hist.hist.GetSum()
    spec1_count = get_spec(1).hist.hist.GetSum()
    f = io.StringIO()
    with redirect_stdout(f):
        hdtv.cmdline.command_line.DoLine("spectrum add 2 0 1")
    assert "Adding 0 to 2" in f.getvalue()
    spec2_count = get_spec(2).hist.hist.GetSum()
    assert spec0_count + spec1_count - spec2_count < 0.00001 * spec2_count

@pytest.mark.parametrize("specfile0, specfile1", [
    ("test/share/example_Co60.tv", "test/share/example_Co60.tv")])
def test_cmd_spectrum_add_normalize(specfile0, specfile1):
    assert len(s.spectra.dict) == 0
    hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile0))
    hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile1))
    assert len(s.spectra.dict) == 2
    spec0_count = get_spec(0).hist.hist.GetSum()
    spec1_count = get_spec(1).hist.hist.GetSum()
    f = io.StringIO()
    with redirect_stdout(f):
        hdtv.cmdline.command_line.DoLine("spectrum add -n 2 0 1")
    assert "Adding 0 to 2" in f.getvalue()
    spec2_count = get_spec(2).hist.hist.GetSum()
    assert spec0_count + spec1_count - 2*spec2_count < 0.00001 * spec2_count

@pytest.mark.parametrize("specfile0, specfile1", [
    ("test/share/example_Co60.tv", "test/share/example_Co60.tv")])
def test_cmd_spectrum_subtract(specfile0, specfile1):
    assert len(s.spectra.dict) == 0
    hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile0))
    hdtv.cmdline.command_line.DoLine("spectrum get {}".format(specfile1))
    assert len(s.spectra.dict) == 2
    spec0_count = get_spec(0).hist.hist.GetSum()
    spec1_count = get_spec(1).hist.hist.GetSum()
    f = io.StringIO()
    with redirect_stdout(f):
        hdtv.cmdline.command_line.DoLine("spectrum subtract 0 1")
    assert "Subtracting 1 from 0" in f.getvalue()
    new_count = get_spec(0).hist.hist.GetSum()
    assert spec0_count - spec1_count - new_count < 0.00001 * spec0_count

@pytest.mark.parametrize("oldfile, newfile", [
    ("test/share/example_Co60.cal", "test/share/example_Co60.tv")])
def test_cmd_spectrum_update(oldfile, newfile):
    assert len(s.spectra.dict) == 0
    try:
        testfile = tempfile.mkstemp(".txt", "hdtv_sutest_")[1]
        shutil.copyfile(oldfile, testfile)
        hdtv.cmdline.command_line.DoLine("spectrum get {}".format(testfile))
        old_count = get_spec(0).hist.hist.GetSum()
        shutil.copyfile(newfile, testfile)
        hdtv.cmdline.command_line.DoLine("spectrum update")
        new_count = get_spec(0).hist.hist.GetSum()
        assert old_count != new_count
        assert len(s.spectra.dict) == 1
    finally:
        os.remove(testfile)
 
def test_cmd_spectrum_calbin():
    raise NotImplementedError()

def get_spec(specid):
    return s.spectra.dict.get(
        [x for x in list(s.spectra.dict) if x.major == specid][0])
