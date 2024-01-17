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
from tests.helpers.utils import hdtvcmd

monkey_patch_ui()

import __main__
import hdtv.cmdline
import hdtv.options
import hdtv.session
import hdtv.window

try:
    __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass


import hdtv.plugins.calInterface
import hdtv.plugins.config
import hdtv.plugins.dblookup
import hdtv.plugins.fitInterface
import hdtv.plugins.fitlist
import hdtv.plugins.fitmap
import hdtv.plugins.fittex
import hdtv.plugins.matInterface
import hdtv.plugins.peakfinder
import hdtv.plugins.printing
import hdtv.plugins.rootInterface
import hdtv.plugins.run
import hdtv.plugins.specInterface

cmdlist = [
    "calibration efficiency fit",
    "calibration efficiency list",
    "calibration efficiency plot",
    "calibration efficiency read covariance",
    "calibration efficiency read parameter",
    "calibration efficiency set",
    "calibration efficiency write covariance",
    "calibration efficiency write parameter",
    "calibration position assign",
    "calibration position copy",
    "calibration position enter",
    "calibration position list",
    "calibration position list clear",
    "calibration position list read",
    "calibration position list write",
    "calibration position nuclide",
    "calibration position read",
    "calibration position recalibrate",
    "calibration position set",
    "calibration position unset",
    "config reset",
    "config set",
    "config show",
    "cut activate",
    "cut clear",
    "cut delete",
    "cut execute",
    "cut hide",
    "cut marker",
    "cut show",
    "cut store",
    "db info",
    "db list",
    "db lookup",
    "db set",
    "fit activate",
    "fit clear",
    "fit delete",
    "fit execute",
    "fit focus",
    "fit function peak activate",
    "fit getlists",
    "fit hide",
    "fit hide decomposition",
    "fit integral list",
    "fit integral execute",
    "fit list",
    "fit marker",
    "fit parameter",
    "fit peakfind",
    "fit position assign",
    "fit position erase",
    "fit position map",
    "fit read",
    "fit savelists",
    "fit show",
    "fit show decomposition",
    "fit store",
    "fit tex",
    "fit write",
    # "matrix delete",
    "matrix get",
    "matrix list",
    # "matrix project",
    "matrix view",
    "nuclide",
    "print",
    "root cut delete",
    "root cut view",
    "root get",
    "root matrix get",
    "root matrix view",
    "spectrum activate",
    "spectrum add",
    "spectrum calbin",
    "spectrum copy",
    "spectrum delete",
    "spectrum get",
    "spectrum hide",
    "spectrum info",
    "spectrum list",
    "spectrum multiply",
    "spectrum name",
    "spectrum normalize",
    "spectrum rebin",
    "spectrum show",
    "spectrum substract",
    "spectrum update",
    "spectrum write",
    "window view center",
    "window view region",
]


@pytest.mark.parametrize("command", cmdlist)
def test_cmd_help(command):
    f, ferr = hdtvcmd(f"{command} --help")
    assert ferr == ""
    assert "usage" in f
    assert "--help" in f


@pytest.mark.parametrize("command", cmdlist)
def test_cmd_unrecognized_arg(command):
    f, ferr = hdtvcmd(f"{command} --invalidarg")
    assert "ERROR" in ferr
    assert "usage" in f
