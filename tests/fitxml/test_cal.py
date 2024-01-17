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

"""
This script tests the interplay of fitting and restoring fits with calibration
"""

import os

import pytest
from numpy import linspace, ones, savetxt, sqrt
from scipy.stats import norm

from hdtv.util import monkey_patch_ui
from tests.helpers.utils import isclose, redirect_stdout, setup_io

monkey_patch_ui()

import __main__
import hdtv.session

try:
    __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass
spectra = __main__.spectra

from hdtv.plugins.fitInterface import fit_interface
from hdtv.plugins.fitlist import fitxml
from hdtv.plugins.specInterface import spec_interface

testspectrum = os.path.join(os.path.curdir, "tests", "share", "osiris_bg.spc")


NBINS = 2000
BG_PER_BIN = 0.0
PEAK_VOLUME = 1e6
PEAK_WIDTH = 15.0


@pytest.fixture(autouse=True)
def prepare(tmp_path):
    fit_interface.ResetFitterParameters()
    hdtv.options.Set("table", "classic")
    hdtv.options.Set("uncertainties", "short")
    spec_interface.LoadSpectra(testspectrum)
    yield
    spectra.Clear()


def get_markers(fit=None):
    if fit is None:
        fit = spectra.workFit
    return [
        fit.regionMarkers[0].p1.pos_uncal,
        fit.regionMarkers[0].p1.pos_cal,
        fit.regionMarkers[0].p2.pos_uncal,
        fit.regionMarkers[0].p2.pos_cal,
        fit.peakMarkers[0].p1.pos_uncal,
        fit.peakMarkers[0].p1.pos_cal,
    ]


def markers_consistent(calfactor=1.0, region1=None, region2=None, fit=None):
    markers = get_markers(fit)
    assert isclose(markers[0], markers[1] / calfactor)
    assert isclose(markers[2], markers[3] / calfactor)
    assert isclose(markers[4], markers[5] / calfactor)
    if region1:
        assert isclose(markers[1], region1)
    if region2:
        assert isclose(markers[3], region2)


def list_fit():
    f, ferr = setup_io(2)
    with redirect_stdout(f, ferr):
        fit_interface.ListFits()
        fit_interface.ListIntegrals()
    assert ferr.getvalue().strip() == ""
    return f.getvalue().strip()


@pytest.mark.parametrize("region1, region2, peak", [(1450.0, 1470.0, 1460.0)])
def test_mark(region1, region2, peak):
    """
    Set Marker and calibrate afterwards
    Marker will be kept fixed, but the spectrum changes
    """
    spectra.SetMarker("region", region1)
    spectra.SetMarker("region", region2)
    spectra.SetMarker("peak", peak)
    markers_before = get_markers()
    assert markers_before == [region1, region1, region2, region2, peak, peak]
    return markers_before


@pytest.mark.parametrize("region1, region2, peak", [(1450.0, 1470.0, 1460.0)])
def test_mark_and_calibrate(region1, region2, peak):
    """
    Set Marker and calibrate afterwards
    Marker will be kept fixed, but the spectrum changes
    """
    markers_before = test_mark(region1, region2, peak)
    spectra.ApplyCalibration("0", [0, 2])
    markers_after = get_markers()
    assert all(x == y for (x, y) in zip(markers_before, markers_after))


@pytest.mark.parametrize("region1, region2, peak", [(2900.0, 2940.0, 2920.0)])
def test_marker_in_calibrated_spectrum(region1, region2, peak):
    """
    Set Marker in calibrated spectrum
    Marker should be appear at the right position relative to spectrum
    """
    spectra.ApplyCalibration("0", [0, 2])
    test_mark(region1, region2, peak)


@pytest.mark.parametrize("calfactor", [2.0])
@pytest.mark.parametrize("region1, region2, peak", [(2900.0, 2940.0, 2920.0)])
def test_fit_in_calibrated_spectrum(region1, region2, peak, calfactor):
    """
    Fit in calibrated spectrum
    Fit should be fixed relative to spectrum
    """
    spectra.ApplyCalibration("0", [0, calfactor])
    spectra.SetMarker("region", region1)
    spectra.SetMarker("region", region2)
    spectra.SetMarker("peak", peak)
    spectra.ExecuteFit()
    markers_consistent(calfactor, region1, region2)


# Check that bin sizes are handled in fitted peak volume (see also test_root_fit_volume_with_binning)
@pytest.mark.parametrize(
    "calfactor, region1, region2, peak, expected_volume",
    [
        (1.0, 500.0, 1500.0, 1000.0, PEAK_VOLUME),
        (2.0, 500.0, 1500.0, 1000.0, PEAK_VOLUME),
    ],
)
def test_mfile_fit_volume_with_binning(
    region1, region2, peak, expected_volume, calfactor, temp_file
):
    spectra.Clear()

    bins = linspace(0.5, NBINS + 0.5, int(NBINS / calfactor))
    spectrum = 1.0 / calfactor * BG_PER_BIN * ones(int(NBINS / calfactor))
    spectrum = spectrum + calfactor * PEAK_VOLUME * norm.pdf(
        bins, loc=0.5 * NBINS, scale=PEAK_WIDTH
    )
    savetxt(temp_file, spectrum)

    spec_interface.LoadSpectra(temp_file)
    spectra.ApplyCalibration("0", [0, calfactor])

    spectra.SetMarker("region", region1)
    spectra.SetMarker("region", region2)
    spectra.SetMarker("peak", peak)
    spectra.ExecuteFit()
    fit = spectra.workFit
    fit_volume = fit.ExtractParams()[0][0]["vol"].nominal_value
    integral_volume = fit.ExtractIntegralParams()[0][0]["vol"].nominal_value

    assert isclose(integral_volume, expected_volume, abs_tol=sqrt(PEAK_VOLUME))
    assert isclose(fit_volume, expected_volume, abs_tol=sqrt(PEAK_VOLUME))


@pytest.mark.parametrize("calfactor1", [2.1, 1.9])
@pytest.mark.parametrize("calfactor2", [0.4, 0.6])
@pytest.mark.parametrize("region1, region2, peak", [(2900.0, 2940.0, 2920.0)])
def test_change_calibrated_fit(region1, region2, peak, calfactor1, calfactor2):
    """
    Change calibration after fit is executed
    Fit should move with spectrum to new position
    """
    test_fit_in_calibrated_spectrum(region1, region2, peak, calfactor1)
    spectra.ApplyCalibration("0", [0, calfactor2])
    markers_consistent(
        calfactor2, region1 / calfactor1 * calfactor2, region2 / calfactor1 * calfactor2
    )


@pytest.mark.parametrize("calfactor1", [2.1, 1.9])
@pytest.mark.parametrize("calfactor2", [0.4, 0.6])
@pytest.mark.parametrize("region1, region2, peak", [(2900.0, 2940.0, 2920.0)])
def test_store_fit(region1, region2, peak, calfactor1, calfactor2):
    """
    Store fit
    Stored fit and active markers should stay fixed relative to spectrum
    """
    test_change_calibrated_fit(region1, region2, peak, calfactor1, calfactor2)
    spectra.StoreFit()
    markers_consistent(
        calfactor2, region1 / calfactor1 * calfactor2, region2 / calfactor1 * calfactor2
    )
    fit = list(spectra.Get("0").dict.items())[0][1]
    markers_consistent(
        calfactor2,
        region1 / calfactor1 * calfactor2,
        region2 / calfactor1 * calfactor2,
        fit=fit,
    )


@pytest.mark.parametrize("calfactor1", [2.1, 1.9])
@pytest.mark.parametrize("calfactor2", [0.4, 0.6])
@pytest.mark.parametrize("region1, region2, peak", [(2900.0, 2940.0, 2920.0)])
def test_reactivate_fit(region1, region2, peak, calfactor1, calfactor2):
    """
    Reactivate stored fit
    Active markers should appear at the same position as the stored fit
    """
    test_store_fit(region1, region2, peak, calfactor1, calfactor2)
    spectra.ActivateFit("0")
    markers_consistent(
        calfactor2, region1 / calfactor1 * calfactor2, region2 / calfactor1 * calfactor2
    )


@pytest.mark.parametrize("calfactor1", [2.1, 1.9])
@pytest.mark.parametrize("calfactor2", [0.4, 0.6])
@pytest.mark.parametrize("region1, region2, peak", [(2900.0, 2940.0, 2920.0)])
def test_execute_reactivated_fit(region1, region2, peak, calfactor1, calfactor2):
    """
    Execute reactivated fit
    New fit should be at the same position as stored fit
    """
    test_change_calibrated_fit(region1, region2, peak, calfactor1, calfactor2)
    spectra.StoreFit()
    out_original = list_fit()
    spectra.ActivateFit("0")
    test_reactivate_fit(region1, region2, peak, calfactor1, calfactor2)
    spectra.ExecuteFit()
    assert out_original == list_fit().replace("AV", " V")


@pytest.mark.parametrize("calfactor1", [2.1])
@pytest.mark.parametrize("calfactor2", [0.4])
@pytest.mark.parametrize("calfactor3", [1.9])
@pytest.mark.parametrize("region1, region2, peak", [(2900.0, 2940.0, 2920.0)])
def test_change_calibration_while_stored(
    region1, region2, peak, calfactor1, calfactor2, calfactor3
):
    """
    Change calibration after fit is stored
    Stored fit should move with spectrum to new position
    """
    test_execute_reactivated_fit(region1, region2, peak, calfactor1, calfactor2)
    spectra.ActivateFit(None)
    spectra.ClearFit()

    fit = list(spectra.Get("0").dict.items())[0][1]
    markers_initial = get_markers(fit)
    spectra.ApplyCalibration("0", [0, calfactor3])
    markers_final = get_markers(fit)

    assert isclose(markers_initial[1], markers_final[1] / calfactor3 * calfactor2)
    assert isclose(markers_initial[3], markers_final[3] / calfactor3 * calfactor2)
    assert isclose(markers_initial[5], markers_final[5] / calfactor3 * calfactor2)


@pytest.mark.parametrize("calfactor1", [2.1])
@pytest.mark.parametrize("calfactor2", [0.4])
@pytest.mark.parametrize("calfactor3", [1.9])
@pytest.mark.parametrize("region1, region2, peak", [(2900.0, 2940.0, 2920.0)])
def test_change_calibration_while_stored_activate(
    region1, region2, peak, calfactor1, calfactor2, calfactor3
):
    """
    Reactivate fit after calibration has changed
    Active markers should appear at the same position as fit
    """
    test_execute_reactivated_fit(region1, region2, peak, calfactor1, calfactor2)
    spectra.ActivateFit(None)
    spectra.ClearFit()
    spectra.ApplyCalibration("0", [0, calfactor3])

    fit = list(spectra.Get("0").dict.items())[0][1]
    markers_initial = get_markers(fit)
    spectra.ActivateFit("0")
    markers_final = get_markers()

    assert isclose(markers_initial[1], markers_final[1])
    assert isclose(markers_initial[3], markers_final[3])
    assert isclose(markers_initial[5], markers_final[5])


@pytest.mark.parametrize("calfactor1", [2.1])
@pytest.mark.parametrize("calfactor2", [0.4])
@pytest.mark.parametrize("calfactor3", [1.9])
@pytest.mark.parametrize("region1, region2, peak", [(2900.0, 2940.0, 2920.0)])
def test_execute_reactivated_calibrated_fit(
    region1, region2, peak, calfactor1, calfactor2, calfactor3
):
    """
    Execute reactivated fit
    New fit should be at the same position as the stored fit
    """
    test_execute_reactivated_fit(region1, region2, peak, calfactor1, calfactor2)
    spectra.ActivateFit(None)
    spectra.ClearFit()
    spectra.ApplyCalibration("0", [0, calfactor3])
    spectra.ActivateFit("0")

    spectra.ExecuteFit()

    fit = list(spectra.Get("0").dict.items())[0][1]
    markers_work = get_markers(fit)
    markers_stored = get_markers()

    assert isclose(markers_stored[1], markers_work[1], rel_tol=1e-7)
    assert isclose(markers_stored[3], markers_work[3], rel_tol=1e-7)
    assert isclose(markers_stored[5], markers_work[5], rel_tol=1e-7)


@pytest.mark.parametrize("calfactor1", [2.1])
@pytest.mark.parametrize("calfactor2", [0.4])
@pytest.mark.parametrize("region1, region2, peak", [(2900.0, 2940.0, 2920.0)])
def test_write_read_xml(temp_file, region1, region2, peak, calfactor1, calfactor2):
    """
    Write/read fit to/from xml
    Fit should appear at the same position as before
    """
    test_store_fit(region1, region2, peak, calfactor1, calfactor2)
    spectra.ActivateFit(None)

    out_original = list_fit()

    spectra.ClearFit()
    fitxml.WriteXML(spectra.Get("0").ID, temp_file)
    spectra.Get("0").Clear()
    fitxml.ReadXML(spectra.Get("0").ID, temp_file)

    assert out_original == list_fit()


@pytest.mark.parametrize("calfactor1", [1.9])
@pytest.mark.parametrize("calfactor2", [0.3])
@pytest.mark.parametrize("calfactor3", [0.7])
@pytest.mark.parametrize("region1, region2, peak", [(2900.0, 2940.0, 2920.0)])
def test_write_read_xml_calibrate(
    temp_file, region1, region2, peak, calfactor1, calfactor2, calfactor3
):
    """
    Write/Read fit and calibrate afterwards
    Fit should move with spectrum to new calibration
    """
    test_write_read_xml(temp_file, region1, region2, peak, calfactor1, calfactor2)

    fit = list(spectra.Get("0").dict.items())[0][1]
    markers_initial = get_markers(fit)
    integral_initial = fit.ExtractIntegralParams()[0][0]

    spectra.ApplyCalibration("0", [0, calfactor3])

    fit = list(spectra.Get("0").dict.items())[0][1]
    markers_final = get_markers(fit)
    integral_final = fit.ExtractIntegralParams()[0][0]

    assert isclose(markers_initial[1], markers_final[1] / calfactor3 * calfactor2)
    assert isclose(markers_initial[3], markers_final[3] / calfactor3 * calfactor2)
    assert isclose(markers_initial[5], markers_final[5] / calfactor3 * calfactor2)
    for key in ["pos", "width_cal"]:
        assert isclose(
            integral_initial[key].nominal_value,
            integral_final[key].nominal_value / calfactor3 * calfactor2,
        )


@pytest.mark.parametrize("calfactor1", [1.9])
@pytest.mark.parametrize("calfactor2", [0.3])
@pytest.mark.parametrize("calfactor3", [0.7])
@pytest.mark.parametrize("region1, region2, peak", [(2900.0, 2940.0, 2920.0)])
def test_reimport_calibrate_write_read(
    temp_file, region1, region2, peak, calfactor1, calfactor2, calfactor3
):
    """
    Write/Read fit and change calibration in between
    Fit should appear at the new calibrated position
    """
    test_store_fit(region1, region2, peak, calfactor1, calfactor2)
    spectra.ActivateFit(None)

    fit = list(spectra.Get("0").dict.items())[0][1]
    markers_initial = get_markers(fit)
    integral_initial = fit.ExtractIntegralParams()[0][0]

    fitxml.WriteXML(spectra.Get("0").ID, temp_file)
    spectra.Get("0").Clear()
    spectra.ApplyCalibration(0, [0, calfactor3])
    fitxml.ReadXML(spectra.Get("0").ID, temp_file)

    fit = list(spectra.Get("0").dict.items())[0][1]
    markers_final = get_markers(fit)
    integral_final = fit.ExtractIntegralParams()[0][0]

    assert isclose(markers_initial[1], markers_final[1] / calfactor3 * calfactor2)
    assert isclose(markers_initial[3], markers_final[3] / calfactor3 * calfactor2)
    assert isclose(markers_initial[5], markers_final[5] / calfactor3 * calfactor2)
    for key in ["pos", "width_cal"]:
        assert isclose(
            integral_initial[key].nominal_value,
            integral_final[key].nominal_value / calfactor3 * calfactor2,
        )
