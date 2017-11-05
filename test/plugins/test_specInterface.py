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
import warnings
import shutil

import pytest

from test.helpers.utils import redirect_stdout, hdtvcmd
from test.helpers.fixtures import temp_file

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
    hdtv.options.Set("table", "classic")
    hdtv.options.Set("uncertainties", "short")
    for (ID, _) in dict(s.spectra.dict).items():
        s.spectra.Pop(ID)

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_spectrum_get(specfile):
    assert len(s.spectra.dict) == 0
    f, ferr = hdtvcmd("spectrum get {}".format(specfile))
    res_specfile, specid = re.search('Loaded (.*) into (\d+)', f).groups()
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
    f, ferr = hdtvcmd("spectrum get -s {} {}".format(
            slot, specfile))
    res_specfile, specid = re.search('Loaded (.*) into (\d+)', f).groups()
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
    hdtvcmd("spectrum get {}".format(query))
    assert len(s.spectra.dict) == num

@pytest.mark.parametrize("pattern", [
    "test/share/example_Co[0-9][0-9].tv"])
def test_cmd_spectrum_get_pattern(pattern):
    assert len(s.spectra.dict) == 0
    hdtvcmd("spectrum get {}".format(pattern))
    assert len(s.spectra.dict) == 1

@pytest.mark.parametrize("specfiles", [
    ["test/share/example_Co60.tv", "test/share/example_Co60.cal"]])
def test_cmd_spectrum_get_multi(specfiles):
    assert len(s.spectra.dict) == 0
    query = " ".join(specfiles)
    hdtvcmd("spectrum get {}".format(query))
    assert len(s.spectra.dict) == len(specfiles)

@pytest.mark.parametrize("specfile, numspecs", [
    ("test/share/example_Co60.tv", 1),
    ("test/share/example_Co60.tv", 10)])
def test_cmd_spectrum_list(specfile, numspecs):
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtvcmd("spectrum get {}".format(specfile))
    f, ferr = hdtvcmd("spectrum list".format(specfile))
    assert len(s.spectra.dict) == numspecs
    assert len(f.split('\n')) == numspecs + 2

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_spectrum_delete(specfile):
    assert len(s.spectra.dict) == 0
    f, ferr = hdtvcmd("spectrum get {}".format(specfile))
    res_specfile, specid = re.search('Loaded (.*) into (\d+)', f).groups()
 
    assert len(s.spectra.dict) == 1

    f, ferr = hdtvcmd("spectrum delete {}".format(specid))
    assert len(s.spectra.dict) == 0

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_spectrum_delete_none(specfile):
    assert len(s.spectra.dict) == 0
    hdtvcmd("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 1

    f, ferr = hdtvcmd("spectrum delete")
    assert "WARNING: Nothing to do" in ferr
    assert len(s.spectra.dict) == 1

@pytest.mark.parametrize("specfile, numspecs", [
    ("test/share/example_Co60.tv", 1),
    ("test/share/example_Co60.tv", 5)])
def test_cmd_spectrum_delete_all(specfile, numspecs):
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtvcmd("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == numspecs

    hdtvcmd("spectrum delete all")
    assert len(s.spectra.dict) == 0

@pytest.mark.parametrize("specfile, numspecs", [
    ("test/share/example_Co60.tv", 1),
    ("test/share/example_Co60.tv", 5)])
def test_cmd_spectrum_delete_several(specfile, numspecs):
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtvcmd("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == numspecs

    specs = ' '.join(str(e) for e in range(numspecs))
    hdtvcmd("spectrum delete {}".format(specs))
    assert len(s.spectra.dict) == 0

@pytest.mark.parametrize("specfile, numspecs", [
    ("test/share/example_Co60.tv", 2),
    ("test/share/example_Co60.tv", 5)])
def test_cmd_spectrum_hide(specfile, numspecs):
    numhidespecs = max(1, numspecs//2)
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtvcmd("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == numspecs

    specs = ' '.join(str(e) for e in range(numhidespecs))
    hdtvcmd("spectrum hide {}".format(specs))

    f, ferr = hdtvcmd("spectrum list -v")
    assert len(s.spectra.dict) == numspecs
    assert len(f.split('\n')) == numspecs - numhidespecs + 2

@pytest.mark.parametrize("specfile, numspecs", [
    ("test/share/example_Co60.tv", 2),
    ("test/share/example_Co60.tv", 5)])
def test_cmd_spectrum_show(specfile, numspecs):
    numshowspecs = max(1, numspecs//2)
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtvcmd("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == numspecs

    specs = ' '.join(str(e) for e in range(numshowspecs))
    hdtvcmd("spectrum show {}".format(specs))

    f, ferr = hdtvcmd("spectrum list -v")
    assert len(s.spectra.dict) == numspecs
    assert len(f.split('\n')) == numshowspecs + 2

@pytest.mark.parametrize("specfile, numspecs", [
    ("test/share/example_Co60.tv", 1),
    ("test/share/example_Co60.tv", 2),
    ("test/share/example_Co60.tv", 5)])
def test_cmd_spectrum_activate(specfile, numspecs):
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtvcmd("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == numspecs

    for specid in range(numspecs):
        hdtvcmd("spectrum activate {}".format(specid))
        f, ferr = hdtvcmd("spectrum list")
        for i, line in enumerate(f.split('\n')):
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
        hdtvcmd("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == numspecs

    f, ferr = hdtvcmd("spectrum activate all")
    if numspecs > 1:
        assert "Can only activate one spectrum" in ferr
        assert "usage" in f
    else:
        assert "" == ferr
        assert "" == f

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_spectrum_info(specfile):
    assert len(s.spectra.dict) == 0
    hdtvcmd("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 1

    f, ferr = hdtvcmd("spectrum info")
    assert ferr == ""
    # If lots of stuff is printed, `spectrum info` is doing its job.
    assert len(f.split('\n')) == 9

@pytest.mark.parametrize("specfile, name", [
    ("test/share/example_Co60.tv", "myname")])
def test_cmd_spectrum_name(specfile, name):
    assert len(s.spectra.dict) == 0
    hdtvcmd("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 1

    f, ferr = hdtvcmd("spectrum name {}".format(name))
    print(ferr)
    print(f)
    assert ferr == ""
    assert "Renamed spectrum 0 to '{}'".format(name) in f

    f, ferr = hdtvcmd("spectrum list")
    assert name in f

@pytest.mark.parametrize("specfile", [
    ("test/share/example_Co60.tv")])
def test_cmd_spectrum_normalize(specfile):
    assert len(s.spectra.dict) == 0
    for _ in range(3):
        hdtvcmd("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 3
    for specids, norm in [("0", 0.3), ("0 1 2", 0.2)]:
        hdtvcmd(
            "spectrum normalize {} {}".format(specids, norm))
        assert get_spec(0).norm == norm
    assert get_spec(2).norm == 0.2
    # TODO: Is there anything else supposed to happen when normalizing?

@pytest.mark.parametrize("specfile, ngroup", [
    ("test/share/example_Co60.tv", 2),
    ("test/share/example_Co60.tv", 20)])
def test_cmd_spectrum_rebin(specfile, ngroup):
    assert len(s.spectra.dict) == 0
    hdtvcmd("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 1

    with warnings.catch_warnings(record=True) as w:
        f, ferr = hdtvcmd("spectrum rebin 0 {}".format(ngroup))
        assert "Rebinning 0 with {} bins per new bin".format(ngroup) in f
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
        hdtvcmd("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 3
    f, ferr = hdtvcmd("spectrum copy {}".format(copy))
    for match in matches:
        assert "Copied spectrum {}".format(match) in f

def test_cmd_spectrum_copy_nonexistant():
    assert len(s.spectra.dict) == 0
    f, ferr = hdtvcmd("spectrum copy 0")
    assert "WARNING: Non-existent id 0" in ferr
    assert "WARNING: Nothing to do" in ferr

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
@pytest.mark.parametrize("fmt", [
    "lc", "txt"])
def test_cmd_spectrum_write(specfile, fmt, temp_file, suffix=""):
    assert len(s.spectra.dict) == 0
    hdtvcmd("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 1
    f, ferr = hdtvcmd(
            "spectrum write {} {}{}".format(temp_file, fmt, suffix))
    assert "Wrote spectrum with id 0 to file {}".format(
        temp_file) in f
    assert os.path.getsize(temp_file) > 0

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
@pytest.mark.parametrize("fmt", [
    "lc", "txt"])
def test_cmd_spectrum_write_withid(specfile, fmt, temp_file):
    test_cmd_spectrum_write(specfile, fmt, temp_file, suffix=" 0")

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_spectrum_write_invalid_format(specfile, temp_file):
    assert len(s.spectra.dict) == 0
    hdtvcmd("spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 1
    f, ferr = hdtvcmd(
            "spectrum write {} invalid 0".format(temp_file))
    assert os.path.getsize(temp_file) == 0
    assert "Failed to write spectrum: Invalid format specified" in ferr

@pytest.mark.parametrize("specfile, factor, specids, response", [
    ("test/share/example_Co60.tv", 0.1, "0", ["0"]),
    ("test/share/example_Co60.tv", 0.2, "0,1", ["0", "1"]),
    ("test/share/example_Co60.tv", 0.5, "0 2", ["0", "2"]),
    ("test/share/example_Co60.tv", 20, "0-2", ["0", "1", "2"]),
    ("test/share/example_Co60.tv", 2, "0", ["0"])])
def test_cmd_spectrum_multiply(specfile, factor, specids, response):
    assert len(s.spectra.dict) == 0
    for _ in range(3):
        hdtvcmd(
            "spectrum get {}".format(specfile))
    assert len(s.spectra.dict) == 3
    orig_count = get_spec(0).hist.hist.GetSum()
    f, ferr = hdtvcmd(
            "spectrum multiply {} {}".format(specids, factor))
    for spec in response:
        assert "Multiplying {} with {}".format(spec, factor) in f
    new_count = get_spec(0).hist.hist.GetSum()
    assert orig_count * factor - new_count < 0.00001 * new_count

@pytest.mark.parametrize("specfile0, specfile1", [
    ("test/share/example_Co60.tv", "test/share/example_Co60.tv")])
def test_cmd_spectrum_add(specfile0, specfile1):
    assert len(s.spectra.dict) == 0
    hdtvcmd("spectrum get {}".format(specfile0))
    hdtvcmd("spectrum get {}".format(specfile1))
    assert len(s.spectra.dict) == 2
    spec0_count = get_spec(0).hist.hist.GetSum()
    spec1_count = get_spec(1).hist.hist.GetSum()
    f, ferr = hdtvcmd("spectrum add 2 0 1")
    assert "Adding 0 to 2" in f
    spec2_count = get_spec(2).hist.hist.GetSum()
    assert spec0_count + spec1_count - spec2_count < 0.00001 * spec2_count

@pytest.mark.parametrize("specfile0, specfile1", [
    ("test/share/example_Co60.tv", "test/share/example_Co60.tv")])
def test_cmd_spectrum_add_normalize(specfile0, specfile1):
    assert len(s.spectra.dict) == 0
    hdtvcmd("spectrum get {}".format(specfile0))
    hdtvcmd("spectrum get {}".format(specfile1))
    assert len(s.spectra.dict) == 2
    spec0_count = get_spec(0).hist.hist.GetSum()
    spec1_count = get_spec(1).hist.hist.GetSum()
    f, ferr = hdtvcmd("spectrum add -n 2 0 1")
    assert "Adding 0 to 2" in f
    spec2_count = get_spec(2).hist.hist.GetSum()
    assert spec0_count + spec1_count - 2*spec2_count < 0.00001 * spec2_count

@pytest.mark.parametrize("specfile0, specfile1", [
    ("test/share/example_Co60.tv", "test/share/example_Co60.tv")])
def test_cmd_spectrum_subtract(specfile0, specfile1):
    assert len(s.spectra.dict) == 0
    hdtvcmd("spectrum get {}".format(specfile0))
    hdtvcmd("spectrum get {}".format(specfile1))
    assert len(s.spectra.dict) == 2
    spec0_count = get_spec(0).hist.hist.GetSum()
    spec1_count = get_spec(1).hist.hist.GetSum()
    f, ferr = hdtvcmd("spectrum subtract 0 1")
    assert "Subtracting 1 from 0" in f
    new_count = get_spec(0).hist.hist.GetSum()
    assert spec0_count - spec1_count - new_count < 0.00001 * spec0_count

@pytest.mark.parametrize("oldfile, newfile", [
    ("test/share/example_Co60.cal", "test/share/example_Co60.tv")])
def test_cmd_spectrum_update(oldfile, newfile, temp_file):
    assert len(s.spectra.dict) == 0
    shutil.copyfile(oldfile, temp_file)
    hdtvcmd("spectrum get {}".format(temp_file))
    old_count = get_spec(0).hist.hist.GetSum()
    shutil.copyfile(newfile, temp_file)
    hdtvcmd("spectrum update")
    new_count = get_spec(0).hist.hist.GetSum()
    assert old_count != new_count
    assert len(s.spectra.dict) == 1

@pytest.mark.skip(reason="Implement in test_cal...")
def test_cmd_spectrum_calbin():
    raise NotImplementedError()

def get_spec(specid):
    return s.spectra.dict.get(
        [x for x in list(s.spectra.dict) if x.major == specid][0])
