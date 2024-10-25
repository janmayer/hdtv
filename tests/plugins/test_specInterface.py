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
import re
import warnings
from math import ceil

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


import hdtv.plugins.specInterface

s = hdtv.plugins.specInterface.spec_interface
spectra = __main__.spectra

testspectrum = os.path.join(os.path.curdir, "tests", "share", "osiris_bg.spc")


@pytest.fixture(autouse=True)
def prepare():
    hdtv.options.Set("table", "classic")
    hdtv.options.Set("uncertainties", "short")
    spectra.Clear()
    yield
    spectra.Clear()


def test_cmd_spectrum_get():
    assert len(s.spectra.dict) == 0
    f, ferr = hdtvcmd(f"spectrum get {testspectrum}")
    res_specfile, specid = re.search(r"Loaded (.*) into (\d+)", f).groups()
    assert len(s.spectra.dict) == 1
    assert res_specfile == testspectrum
    for ID, obj in s.spectra.dict.items():
        assert str(ID) == specid
        assert isinstance(obj, hdtv.spectrum.Spectrum)


@pytest.mark.parametrize("slot", [3, 1000000])
def test_cmd_spectrum_get_slot(slot):
    assert len(s.spectra.dict) == 0
    f, ferr = hdtvcmd(f"spectrum get -s {slot} {testspectrum}")
    res_specfile, specid = re.search(r"Loaded (.*) into (\d+)", f).groups()
    assert len(s.spectra.dict) == 1
    assert res_specfile == testspectrum
    assert specid == str(slot)
    for ID, obj in s.spectra.dict.items():
        assert str(ID) == specid
        assert isinstance(obj, hdtv.spectrum.Spectrum)


@pytest.mark.parametrize("num", [4, 40])
def test_cmd_spectrum_get_repeated(num):
    assert len(s.spectra.dict) == 0
    query = " ".join([testspectrum] * num)
    hdtvcmd(f"spectrum get {query}")
    assert len(s.spectra.dict) == num


@pytest.mark.parametrize("pattern", ["tests/share/osiris_[a-z][a-z].spc"])
def test_cmd_spectrum_get_pattern(pattern):
    assert len(s.spectra.dict) == 0
    hdtvcmd(f"spectrum get {pattern}")
    assert len(s.spectra.dict) == 1


# Loading cal as spec file. This is really stupid, but it works.
@pytest.mark.parametrize(
    "specfiles", [["tests/share/osiris_bg.spc", "tests/share/osiris_bg.cal"]]
)
def test_cmd_spectrum_get_multi(specfiles):
    assert len(s.spectra.dict) == 0
    query = " ".join(specfiles)
    hdtvcmd(f"spectrum get {query}")
    assert len(s.spectra.dict) == len(specfiles)


@pytest.mark.parametrize("numspecs", [1, 10])
def test_cmd_spectrum_list(numspecs):
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtvcmd(f"spectrum get {testspectrum}")
    f, ferr = hdtvcmd("spectrum list")
    assert len(s.spectra.dict) == numspecs
    assert len(f.split("\n")) == numspecs + 2


def test_cmd_spectrum_delete():
    assert len(s.spectra.dict) == 0
    f, ferr = hdtvcmd(f"spectrum get {testspectrum}")
    res_specfile, specid = re.search(r"Loaded (.*) into (\d+)", f).groups()

    assert len(s.spectra.dict) == 1

    f, ferr = hdtvcmd(f"spectrum delete {specid}")
    assert len(s.spectra.dict) == 0


def test_cmd_spectrum_delete_none():
    assert len(s.spectra.dict) == 0
    hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == 1

    f, ferr = hdtvcmd("spectrum delete")
    assert "WARNING: Nothing to do" in ferr
    assert len(s.spectra.dict) == 1


@pytest.mark.parametrize("numspecs", [1, 5])
def test_cmd_spectrum_delete_all(numspecs):
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == numspecs

    hdtvcmd("spectrum delete all")
    assert len(s.spectra.dict) == 0


@pytest.mark.parametrize("numspecs", [1, 5])
def test_cmd_spectrum_delete_several(numspecs):
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == numspecs

    specs = " ".join(str(e) for e in range(numspecs))
    hdtvcmd(f"spectrum delete {specs}")
    assert len(s.spectra.dict) == 0


@pytest.mark.parametrize("numspecs", [2, 5])
def test_cmd_spectrum_hide(numspecs):
    numhidespecs = max(1, numspecs // 2)
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == numspecs

    specs = " ".join(str(e) for e in range(numhidespecs))
    hdtvcmd(f"spectrum hide {specs}")

    f, ferr = hdtvcmd("spectrum list -v")
    assert len(s.spectra.dict) == numspecs
    assert len(f.split("\n")) == numspecs - numhidespecs + 2


@pytest.mark.parametrize("numspecs", [2, 5])
def test_cmd_spectrum_show(numspecs):
    numshowspecs = max(1, numspecs // 2)
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == numspecs

    specs = " ".join(str(e) for e in range(numshowspecs))
    hdtvcmd(f"spectrum show {specs}")

    f, ferr = hdtvcmd("spectrum list -v")
    assert len(s.spectra.dict) == numspecs
    assert len(f.split("\n")) == numshowspecs + 2


@pytest.mark.parametrize("numspecs", [1, 2, 5])
def test_cmd_spectrum_activate(numspecs):
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == numspecs

    for specid in range(numspecs):
        hdtvcmd(f"spectrum activate {specid}")
        f, ferr = hdtvcmd("spectrum list")
        for i, line in enumerate(f.split("\n")):
            if i == specid + 2:
                assert "|   AV |" in line
            elif i > 2:
                assert "|    V |" in line


@pytest.mark.parametrize("numspecs", [0, 1, 2, 5])
def test_cmd_spectrum_activate_multi(numspecs):
    assert len(s.spectra.dict) == 0
    for _ in range(numspecs):
        hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == numspecs

    f, ferr = hdtvcmd("spectrum activate all")
    if numspecs > 1:
        assert "Can only activate one spectrum" in ferr
    else:
        assert ferr == ""
        assert f == ""


def test_cmd_spectrum_info():
    assert len(s.spectra.dict) == 0
    hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == 1

    f, ferr = hdtvcmd("spectrum info")
    assert ferr == ""
    # If lots of stuff is printed, `spectrum info` is doing its job.
    assert len(f.split("\n")) == 9


@pytest.mark.parametrize("name", ["myname"])
def test_cmd_spectrum_name(name):
    assert len(s.spectra.dict) == 0
    hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == 1

    f, ferr = hdtvcmd(f"spectrum name {name}")
    print(ferr)
    print(f)
    assert ferr == ""
    assert f"Renamed spectrum 0 to &#x27;{name}&#x27;" in f

    f, ferr = hdtvcmd("spectrum list")
    assert name in f


def test_cmd_spectrum_normalize():
    assert len(s.spectra.dict) == 0
    for _ in range(3):
        hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == 3
    for specids, norm in [("0", 0.3), ("0 1 2", 0.2)]:
        hdtvcmd(f"spectrum normalize {specids} {norm}")
        assert get_spec(0).norm == norm
    assert get_spec(2).norm == 0.2
    # TODO: Is there anything else supposed to happen when normalizing?


@pytest.mark.parametrize("ngroup", [2, 20])
def test_cmd_spectrum_rebin(ngroup):
    assert len(s.spectra.dict) == 0
    hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == 1

    with warnings.catch_warnings(record=True):
        f, ferr = hdtvcmd(f"spectrum rebin 0 {ngroup}")
        assert f"Rebinning 0 with {ngroup} bins per new bin" in f
        assert get_spec(0).hist.hist.GetNbinsX() == 8192 // ngroup


@pytest.mark.parametrize("binsize", [1, 0.5, 1.1])
def test_cmd_spectrum_calbin_binsize(binsize):
    assert len(s.spectra.dict) == 0
    hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == 1

    with warnings.catch_warnings(record=True):
        f, ferr = hdtvcmd(f"spectrum calbin -b {binsize} 0")
        assert f"Calbinning 0 with binsize={binsize}" in f
        assert get_spec(0).hist.hist.GetNbinsX() == int(ceil(8191 / binsize)) + 1


@pytest.mark.parametrize("parameter", ["-t", "-r"])
def test_cmd_spectrum_calbin_root_tv(parameter):
    assert len(s.spectra.dict) == 0
    hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == 1

    with warnings.catch_warnings(record=True):
        f, ferr = hdtvcmd(f"spectrum calbin {parameter} 0")
        assert "Calbinning 0 with binsize=" in f


@pytest.mark.parametrize("spline_order", [1, 3, 5])
def test_cmd_spectrum_calbin_spline_order(spline_order):
    assert len(s.spectra.dict) == 0
    hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == 1

    with warnings.catch_warnings(record=True):
        f, ferr = hdtvcmd(f"spectrum calbin -k {spline_order} 0")
        assert "Calbinning 0 with" in f


def test_cmd_spectrum_calbin_calibrated():
    assert len(s.spectra.dict) == 0
    hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == 1
    hdtvcmd("calibration position set 5 2.2")

    with warnings.catch_warnings(record=True):
        f, ferr = hdtvcmd("spectrum calbin -d 0")
        assert "Calbinning 0 with" in f


def test_cmd_spectrum_resample():
    assert len(s.spectra.dict) == 0
    hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == 1

    with warnings.catch_warnings(record=True):
        f, ferr = hdtvcmd("spectrum resample 0")
        assert "Total area changed by" in f


@pytest.mark.parametrize(
    "copy, matches",
    [
        ("0", ["0 to 3"]),
        ("0 1", ["0 to 3", "1 to 4"]),
        ("2 -s 3000", ["2 to 3000"]),
        ("0,1 -s 8,7", ["0 to 7", "1 to 8"]),
        ("0-2", ["0 to 3", "1 to 4", "2 to 5"]),
        ("2 -s 0", ["2 to 0"]),
    ],
)
def test_cmd_spectrum_copy(copy, matches):
    assert len(s.spectra.dict) == 0
    for _ in range(3):
        hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == 3
    f, ferr = hdtvcmd(f"spectrum copy {copy}")
    for match in matches:
        assert f"Copied spectrum {match}" in f


def test_cmd_spectrum_copy_nonexistant():
    assert len(s.spectra.dict) == 0
    f, ferr = hdtvcmd("spectrum copy 0")
    assert "WARNING: Non-existent id 0" in ferr
    assert "WARNING: Nothing to do" in ferr


@pytest.mark.parametrize("fmt", ["lc", "txt"])
def test_cmd_spectrum_write(fmt, temp_file, suffix=""):
    assert len(s.spectra.dict) == 0
    hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == 1
    f, ferr = hdtvcmd(f"spectrum write {temp_file} {fmt}{suffix}")
    assert f"Wrote spectrum with id 0 to file {temp_file}" in f
    assert os.path.getsize(temp_file) > 0


@pytest.mark.parametrize("fmt", ["lc", "txt"])
def test_cmd_spectrum_write_withid(fmt, temp_file):
    test_cmd_spectrum_write(fmt, temp_file, suffix=" 0")


def test_cmd_spectrum_write_invalid_format(temp_file):
    assert len(s.spectra.dict) == 0
    hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == 1
    f, ferr = hdtvcmd(f"spectrum write {temp_file} invalid 0")
    assert os.path.getsize(temp_file) == 0
    assert "Failed to write spectrum: Invalid format specified" in ferr


@pytest.mark.parametrize(
    "factor, specids, response",
    [
        (0.1, "0", ["0"]),
        (0.2, "0,1", ["0", "1"]),
        (0.5, "0 2", ["0", "2"]),
        (20, "0-2", ["0", "1", "2"]),
        (2, "0", ["0"]),
    ],
)
def test_cmd_spectrum_multiply(factor, specids, response):
    assert len(s.spectra.dict) == 0
    for _ in range(3):
        hdtvcmd(f"spectrum get {testspectrum}")
    assert len(s.spectra.dict) == 3
    orig_count = get_spec(0).hist.hist.GetSum()
    f, ferr = hdtvcmd(f"spectrum multiply {specids} {factor}")
    for spec in response:
        assert f"Multiplying {spec} with {factor}" in f
    new_count = get_spec(0).hist.hist.GetSum()
    assert orig_count * factor - new_count < 0.00001 * new_count


@pytest.mark.parametrize("specfile0, specfile1", [(testspectrum, testspectrum)])
def test_cmd_spectrum_add(specfile0, specfile1):
    assert len(s.spectra.dict) == 0
    hdtvcmd(f"spectrum get {specfile0}")
    hdtvcmd(f"spectrum get {specfile1}")
    assert len(s.spectra.dict) == 2
    spec0_count = get_spec(0).hist.hist.GetSum()
    spec1_count = get_spec(1).hist.hist.GetSum()
    f, ferr = hdtvcmd("spectrum add 2 0 1")
    assert "Adding 0 to 2" in f
    spec2_count = get_spec(2).hist.hist.GetSum()
    assert spec0_count + spec1_count - spec2_count < 0.00001 * spec2_count


@pytest.mark.parametrize("specfile0, specfile1", [(testspectrum, testspectrum)])
def test_cmd_spectrum_add_normalize(specfile0, specfile1):
    assert len(s.spectra.dict) == 0
    hdtvcmd(f"spectrum get {specfile0}")
    hdtvcmd(f"spectrum get {specfile1}")
    assert len(s.spectra.dict) == 2
    spec0_count = get_spec(0).hist.hist.GetSum()
    spec1_count = get_spec(1).hist.hist.GetSum()
    f, ferr = hdtvcmd("spectrum add -n 2 0 1")
    assert "Adding 0 to 2" in f
    spec2_count = get_spec(2).hist.hist.GetSum()
    assert spec0_count + spec1_count - 2 * spec2_count < 0.00001 * spec2_count


@pytest.mark.parametrize("specfile0, specfile1", [(testspectrum, testspectrum)])
def test_cmd_spectrum_subtract(specfile0, specfile1):
    assert len(s.spectra.dict) == 0
    hdtvcmd(f"spectrum get {specfile0}")
    hdtvcmd(f"spectrum get {specfile1}")
    assert len(s.spectra.dict) == 2
    spec0_count = get_spec(0).hist.hist.GetSum()
    spec1_count = get_spec(1).hist.hist.GetSum()
    f, ferr = hdtvcmd("spectrum subtract 0 1")
    assert "Subtracting 1 from 0" in f
    new_count = get_spec(0).hist.hist.GetSum()
    assert spec0_count - spec1_count - new_count < 0.00001 * spec0_count


@pytest.mark.skip(reason="What is spectrum update supposed to do?")
def test_cmd_spectrum_update():
    pass


def get_spec(specid):
    return s.spectra.dict.get([x for x in list(s.spectra.dict) if x.major == specid][0])
