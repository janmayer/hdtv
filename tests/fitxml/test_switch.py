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

import pytest

from hdtv.util import monkey_patch_ui, strip_tags
from tests.helpers.utils import redirect_stdout, setup_io

monkey_patch_ui()

import __main__
import hdtv.session

try:
    __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass
spectra = __main__.spectra

import hdtv.plugins.fitlist
from hdtv.plugins.fitInterface import fit_interface
from hdtv.plugins.specInterface import spec_interface

testspectrum = os.path.join(os.path.curdir, "tests", "share", "osiris_bg.spc")


@pytest.fixture(autouse=True)
def prepare():
    fit_interface.ResetFitterParameters()
    hdtv.options.Set("table", "classic")
    hdtv.options.Set("uncertainties", "short")
    spec_interface.LoadSpectra(testspectrum)
    for i in range(5):
        spec_interface.LoadSpectra(testspectrum)
        spectra.Get(str(i)).cal = [0, (i + 1) * 0.5]
    yield
    spectra.Clear()


def get_list(no_err=True):
    f, ferr = setup_io(2)
    with redirect_stdout(f, ferr):
        spec_interface.ListSpectra()
    if no_err:
        assert ferr.getvalue().strip() == ""
        return strip_tags(f.getvalue())
    else:
        return strip_tags(f.getvalue()), ferr.getvalue()


def test_spectra_loaded():
    res = get_list()
    for i in range(5):
        assert str(i) + " |    V | osiris_bg.spc |    0" in res
    assert "5 |   AV | osiris_bg.spc |    0" in res


def test_spectra_show_first():
    spectra.ShowFirst()
    res = get_list()
    assert "0 |   AV | osiris_bg.spc |    0" in res
    for i in range(1, 6):
        assert str(i) + " |      | osiris_bg.spc |    0" in res


def test_spectra_show_next():
    spectra.ShowFirst()
    for i in range(1, 6):
        spectra.ShowNext()
        res = get_list()
        for j in range(6):
            if j == i:
                assert str(j) + " |   AV | osiris_bg.spc |    0" in res
            else:
                assert str(j) + " |      | osiris_bg.spc |    0" in res


def test_spectra_show_last():
    spectra.ShowLast()
    res = get_list()
    for j in range(6):
        if j == 5:
            assert str(j) + " |   AV | osiris_bg.spc |    0" in res
        else:
            assert str(j) + " |      | osiris_bg.spc |    0" in res


def test_spectra_show_prev():
    spectra.ShowLast()
    for i in range(4, 0, -1):
        spectra.ShowPrev()
        res = get_list()
        for j in range(6):
            if j == i:
                assert str(j) + " |   AV | osiris_bg.spc |    0" in res
            else:
                assert str(j) + " |      | osiris_bg.spc |    0" in res


def test_spectra_show_number():
    for i in range(6):
        spectra.ShowObjects(hdtv.util.ID.ParseIds(str(i), __main__.spectra))
        res = get_list()
        for j in range(6):
            if j == i:
                assert str(j) + " |   AV | osiris_bg.spc |    0" in res
            else:
                assert str(j) + " |      | osiris_bg.spc |    0" in res


def test_spectra_show_all():
    spectra.ShowLast()
    spectra.ShowAll()
    res = get_list()
    for j in range(6):
        if j == 5:
            assert str(j) + " |   AV | osiris_bg.spc |    0" in res
        else:
            assert str(j) + " |    V | osiris_bg.spc |    0" in res


def test_spectra_activate_number():
    spectra.ShowAll()
    for i in range(6):
        spectra.ActivateObject(str(i))
        res = get_list()
        for j in range(6):
            if j == i:
                assert str(j) + " |   AV | osiris_bg.spc |    0" in res
            else:
                assert str(j) + " |    V | osiris_bg.spc |    0" in res


def test_spectra_show_active():
    spectra.ShowAll()
    spectra.ActivateObject(str(5))
    spectra.ShowObjects(spectra.activeID)
    res = get_list()
    for j in range(6):
        if j == 5:
            assert str(j) + " |   AV | osiris_bg.spc |    0" in res
        else:
            assert str(j) + " |      | osiris_bg.spc |    0" in res


def test_spectra_activate_hidden():
    spectra.ShowAll()
    spectra.ActivateObject(str(5))
    spectra.ShowObjects(spectra.activeID)
    spectra.ActivateObject("4")
    res = get_list()
    for j in range(6):
        if j == 5:
            assert str(j) + " |    V | osiris_bg.spc |    0" in res
        elif j == 4:
            assert str(j) + " |   AV | osiris_bg.spc |    0" in res
        else:
            assert str(j) + " |      | osiris_bg.spc |    0" in res


def test_spectra_remove_one():
    spectra.Pop("3")
    res = get_list()
    assert "3 | " not in res


def test_spectra_reload_one():
    spectra.Pop("3")
    spec_interface.LoadSpectra(testspectrum)
    res = get_list()
    assert "3 |   AV" in res


def test_spectra_show_next_overflow():
    spectra.ShowObjects(hdtv.util.ID.ParseIds(str(3), __main__.spectra))
    for i in range(3, 10):
        spectra.ShowNext()
        res = get_list()
        for j in range(6):
            if j == (i + 1) % 6:
                assert str(j) + " |   AV | osiris_bg.spc |    0" in res
            else:
                assert str(j) + " |      | osiris_bg.spc |    0" in res
