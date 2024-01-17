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
import sys
import tempfile

import pytest


@pytest.fixture(scope="function")
def temp_file(request):
    """
    pytest fixture that provides a temporary file for writing
    """
    filename = tempfile.mkstemp(prefix="hdtv_")[1]
    os.remove(filename)
    yield filename
    try:
        os.remove(filename)
    except OSError:
        pass


@pytest.fixture(
    scope="function",
    params=[
        ".gz",
        pytest.param(
            ".xz",
            marks=pytest.mark.skipif(
                sys.version_info < (3, 0), reason="no module lzma in python2"
            ),
        ),
        pytest.param(
            ".bz2",
            marks=pytest.mark.skipif(
                sys.version_info < (3, 0), reason="no module bz2 in python2"
            ),
        ),
        "",
    ],
)
def temp_file_compressed(request):
    """
    pytest fixture that provides a temporary file for writing
    """
    filename = tempfile.mkstemp(prefix="hdtv_", suffix=str(request.param))[1]
    os.remove(filename)
    yield filename
    try:
        os.remove(filename)
    except OSError:
        pass
