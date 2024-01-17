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
from tests.helpers.utils import hdtvcmd, isclose

monkey_patch_ui()

import __main__
import hdtv.session

try:
    __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass
session = __main__.spectra

import hdtv.cmdline
import hdtv.options
import hdtv.plugins.rootInterface
import hdtv.plugins.specInterface
import hdtv.rfile_utils
from hdtv.plugins.fitInterface import fit_interface


@pytest.fixture(autouse=True)
def prepare(request):
    fit_interface.ResetFitterParameters()
    # original_wd = os.path.abspath(os.path.join(__file__, os.pardir))
    original_wd = os.getcwd()
    os.chdir(original_wd)
    yield
    os.chdir(original_wd)
    session.Clear()


def test_cmd_root_pwd():
    f, ferr = hdtvcmd("root pwd")
    assert f == os.getcwd()


@pytest.mark.parametrize(
    "start, cd, target",
    [
        ("/", "/tmp", "/tmp"),
        ("/tmp", "..", "/"),
        ("/", "tmp", "/tmp"),
        ("/tmp", "", "/tmp"),
    ],
)
def test_cmd_root_cd(start, cd, target):
    os.chdir(start)
    hdtvcmd("root cd " + cd)
    assert os.getcwd() == target


@pytest.mark.skip(reason="opens TBrowser GUI")
def test_cmd_root_browse():
    hdtvcmd("root browse")
    assert hdtv.plugins.rootInterface.r.browser.GetName() == "Browser"
    hdtv.plugins.rootInterface.r.browser.SetName("Test")
    assert hdtv.plugins.rootInterface.r.browser.GetName() == "Test"
    hdtv.plugins.rootInterface.r.browser = None


# Check that bin sizes are handled in fitted peak volume (see also test_mfile_fit_volume_with_binning)
@pytest.mark.parametrize("spectrum", ["h", "h2"])
@pytest.mark.parametrize(
    "region1, region2, peak, expected_volume", [(500.0, 1500.0, 1000.0, 1000000.0)]
)
def test_root_fit_volume_with_binning(
    region1, region2, peak, expected_volume, spectrum
):
    # Mock parser so RootGet can be used
    # args = mock.Mock()
    args = type("Test", (object,), {})
    args.pattern = [os.path.join("tests", "share", "binning.root", spectrum)]
    args.replace = False
    args.load_cal = False
    args.invisible = False
    hdtv.plugins.rootInterface.r.RootGet(args)

    session.SetMarker("region", region1)
    session.SetMarker("region", region2)
    session.SetMarker("peak", peak)
    session.ExecuteFit()
    fit = session.workFit
    fit_volume = fit.ExtractParams()[0][0]["vol"].nominal_value
    integral_volume = fit.ExtractIntegralParams()[0][0]["vol"].nominal_value

    assert isclose(integral_volume, expected_volume, abs_tol=10)
    assert isclose(fit_volume, expected_volume, abs_tol=200)
    hdtv.plugins.rootInterface.r.RootClose(None)


def test_root_to_root_conversion_for_unconventional_binning():
    # Mock parser so RootGet can be used
    # args = mock.Mock()
    args = type("Test", (object,), {})
    args.replace = False
    args.load_cal = False
    args.invisible = False
    args.pattern = [os.path.join("tests", "share", "binning.root", "h")]
    hdtv.plugins.rootInterface.r.RootGet(args)
    args.pattern = [os.path.join("tests", "share", "binning.root", "h2")]
    hdtv.plugins.rootInterface.r.RootGet(args)

    assert not get_spec(0).cal
    assert isclose(get_spec(1).cal.GetCoeffs()[1], 0.5)


def get_spec(specid):
    s = hdtv.plugins.specInterface.spec_interface
    return s.spectra.dict.get([x for x in list(s.spectra.dict) if x.major == specid][0])
