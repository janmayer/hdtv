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

import pytest

from hdtv.util import monkey_patch_ui

monkey_patch_ui()

import __main__
import hdtv.cmdline
import hdtv.options
import hdtv.session

try:
    if not hasattr(__main__, "spectra"):
        __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass

import hdtv.plugins.matInterface

spectra = __main__.spectra


@pytest.fixture(autouse=True)
def prepare():
    hdtv.options.Set("table", "classic")
    hdtv.options.Set("uncertainties", "short")
    spectra.Clear()
    yield
    spectra.Clear()


@pytest.mark.skip(reason="need example matrix")
def test_cmd_matrix_get_sym(matrix):
    raise NotImplementedError


@pytest.mark.skip(reason="need example matrix")
def test_cmd_matrix_get_asym(matrix):
    raise NotImplementedError


@pytest.mark.skip(reason="need example matrix")
def test_cmd_matrix_list(matrix):
    raise NotImplementedError


@pytest.mark.skip(reason="need example matrix; hard to test")
def test_cmd_matrix_view(matrix):
    raise NotImplementedError


@pytest.mark.skip(reason="need example matrix")
def test_cmd_cut_marker(matrix):
    raise NotImplementedError


@pytest.mark.skip(reason="need example matrix")
def test_cmd_cut_execute(matrix):
    raise NotImplementedError


@pytest.mark.skip(reason="need example matrix")
def test_cmd_cut_activate(matrix):
    raise NotImplementedError


@pytest.mark.skip(reason="need example matrix")
def test_cmd_cut_clear(matrix):
    raise NotImplementedError


@pytest.mark.skip(reason="need example matrix")
def test_cmd_cut_store(matrix):
    raise NotImplementedError


@pytest.mark.skip(reason="need example matrix")
def test_cmd_cut_delete(matrix):
    raise NotImplementedError
