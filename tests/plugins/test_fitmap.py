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


import hdtv.plugins.calInterface
import hdtv.plugins.fitInterface
import hdtv.plugins.fitmap
import hdtv.plugins.peakfinder
from hdtv.plugins.specInterface import spec_interface

spectra = __main__.spectra

testspectrum = os.path.join(os.path.curdir, "tests", "share", "osiris_bg.spc")


def count_peak_positions():
    count = 0
    spec = __main__.spectra.dict[__main__.spectra.activeID]
    for fit in spec.dict.values():
        for peak in fit.peaks:
            if "pos_lit" in peak.extras:
                count += 1
    return count


@pytest.fixture(autouse=True)
def prepare():
    spectra.Clear()
    yield
    spectra.Clear()


def test_cmd_fit_position():
    spec_interface.tv.specIf.LoadSpectra(testspectrum, None)
    hdtvcmd("fit peakfind -a -t 0.05")
    f, ferr = hdtvcmd(
        "fit position assign 10.0 1173.228(3) 12.0 1332.492(4)",
        "fit position erase 10.0 12.0",
    )
    assert ferr == ""


def test_cmd_fit_position_map():
    spec_interface.tv.specIf.LoadSpectra(testspectrum, None)
    hdtvcmd("fit peakfind -a -t 0.002")
    f, ferr = hdtvcmd("fit position map tests/share/osiris_bg.map")
    assert ferr == ""
    assert "Mapped 3 energies to peaks" in f


def test_cmd_fit_position_map_tolerance():
    spec_interface.tv.specIf.LoadSpectra(testspectrum, None)
    hdtvcmd("fit peakfind -a -t 0.002")
    f, ferr = hdtvcmd("fit position map -t 8 tests/share/osiris_bg.map")
    assert ferr == ""
    assert "Mapped 2 energies to peaks" in f


def test_cmd_fit_position_map_overwrite():
    test_cmd_fit_position_map()
    assert count_peak_positions() == 3
    f, ferr = hdtvcmd("fit position map -t 2 -o tests/share/osiris_bg.map")
    assert ferr == ""
    assert "Mapped 0 energies to peaks" in f
    assert count_peak_positions() == 0
