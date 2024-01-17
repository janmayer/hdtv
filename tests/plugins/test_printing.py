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
import tempfile

import pytest

from hdtv.util import monkey_patch_ui
from tests.helpers.utils import hdtvcmd

monkey_patch_ui()

import __main__
import hdtv.cmdline
import hdtv.options
import hdtv.session
import hdtv.ui

try:
    __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass

import hdtv.plugins.printing


@pytest.fixture(autouse=True)
def prepare():
    hdtv.options.Set("ui.out.level", "3")


def test_cmd_printing():
    try:
        outfile = tempfile.mkstemp(".svg", "hdtv_ptest_")[1]
        f, ferr = hdtvcmd(
            f"print -y 'my_ylabel' -x 'my_xlabel' -t 'my_title' -F {outfile}"
        )
        print(f)
        print(ferr)
        assert f == ""
        assert ferr == ""
        with open(outfile) as fout:
            result = fout.read()
        assert "my_ylabel" in result
        assert "my_xlabel" in result
        assert "my_title" in result
    finally:
        os.remove(outfile)


@pytest.mark.parametrize("fmt", ["eps", "pdf", "png", "ps", "raw", "rgba", "svg"])
# "svgz", "jpeg", "tiff" <- fail for no good reason
def test_cmd_printing_formats(fmt):
    try:
        outfile = tempfile.mkstemp("." + fmt, "hdtv_pftest_")[1]
        f, ferr = hdtvcmd(
            f"print -y 'my_ylabel' -x 'my_xlabel' -t 'my_title' -F {outfile}"
        )
        print(f)
        print(ferr)
        assert f == ""
        assert ferr == ""
    finally:
        os.remove(outfile)
