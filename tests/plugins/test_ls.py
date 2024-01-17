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

import hdtv.plugins.ls  # noqa: F401
from tests.helpers.utils import hdtvcmd


@pytest.fixture(autouse=True)
def prepare(request):
    # original_wd = os.path.abspath(os.path.join(__file__, os.pardir))
    original_wd = os.getcwd()
    os.chdir(original_wd)
    yield
    os.chdir(original_wd)


def test_cmd_pwd():
    f, ferr = hdtvcmd("pwd")
    assert f == os.getcwd()


@pytest.mark.parametrize(
    "start, cd, target",
    [
        ("/", "/tmp", "/tmp"),
        ("/tmp", "..", "/"),
        ("/", "tmp", "/tmp"),
        ("/", "~", os.path.expanduser("~")),
        ("/tmp", "", os.path.expanduser("~")),
    ],
)
def test_cmd_cd(start, cd, target):
    os.chdir(start)
    hdtvcmd("cd " + cd)
    assert os.getcwd() == os.path.realpath(target)


def test_cmd_cd_minus():
    hdtvcmd("cd /")
    hdtvcmd("cd /tmp")
    hdtvcmd("cd -")
    assert os.getcwd() == "/"


@pytest.mark.parametrize(
    "cd, output", [("/tmp", "/tmp"), ("~", os.path.expanduser("~")), ("/", "/")]
)
def test_cmd_cd_output(cd, output):
    f, ferr = hdtvcmd("cd " + cd)
    assert f == output


def test_cmd_ls():
    os.chdir(os.path.abspath(os.sep))
    f, ferr = hdtvcmd("ls")
    assert "tmp" in f
