# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2019  The HDTV development team (see file AUTHORS)
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
Test the different implemented background models with an artificial spectrum.
The test spectrum is a sequence of step functions with increasing step height. On each step, a normal-distributed peak is located. No artificial fluctuations are introduced to give simple verifiable results.
Specific background models (for example the exponential background) may require particular shapes of the background, so their steps may be superimposed by another function.
"""

import os
import xml.etree.ElementTree as ET

import pytest
from numpy import exp, log, sqrt

from hdtv.util import monkey_patch_ui
from tests.helpers.create_test_spectrum import ArtificialSpec, ArtificialSpecProp
from tests.helpers.utils import hdtvcmd, isclose

monkey_patch_ui()

import __main__
import hdtv.cmdline
import hdtv.options
import hdtv.session

try:
    __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass

from hdtv.plugins.fitlist import fitxml
from hdtv.plugins.specInterface import spec_interface

spectra = __main__.spectra

BG_MARKER_TOLERANCE = 0.5
SIGMA_TO_FWHM = 2.3548299450  # = 2*sqrt(2*ln(2))
N_SIGMA = (
    2  # This number determines how many standard deviations (sigma) a fitted quantity
)
# may deviate from the ideal value. Sigma is either provided by some fitting algorithm or by
# statistical considerations here.
# For the former case, this test is self-consistent and assumes that the algorithm estimates the
# uncertainty correctly.
WRITE_BATCHFILE = False  # Determines whether the batch files of the test fits should be written to file.

# Initialize the test spectrum properties which are needed for the parameterized tests
ts_prop = ArtificialSpecProp()


@pytest.fixture()
def test_spectrum(tmp_path):
    ts = ArtificialSpec(path=tmp_path)
    ts.create()
    return ts


@pytest.mark.parametrize(
    # nparams is the true number of parameters. The length n of the list bgparams
    # only determines that the first n parameters will be checked.
    # This is useful, for example, when a cubic or even quartic model is fit
    # to a constant background. Since Chi2 of the fit depends very strongly on the
    # values of the higher-order parameters (and even oscillates: third order cancels second order, ...),
    # the algorithm will terminate at some arbitrary
    # low value, and give a false estimate of the uncertainty.
    "model, nparams, step, nregions, settings, errormessage, bgparams, bg_volume",
    [
        #        ("polynomial", 2, 0, 3, "", "", [10., 0.], 0.),
        #        ("polynomial", 2, 0, 3, "fit parameter background 2", "", [10., 0.], 0.),
        (
            "polynomial",
            3,
            0,
            3,
            "fit parameter background 3",
            "",
            [10.0, 0.0, 0.0],
            0.0,
        ),
        ("polynomial", 3, 0, 3, "fit parameter background free", "", [10.0, 0.0], 0.0),
        ("polynomial", 4, 0, 4, "fit parameter background free", "", [10.0, 0.0], 0.0),
        ("interpolation", 6, 0, 2, "", "Background fit failed.", [], 0.0),
        (
            "interpolation",
            6,
            0,
            3,
            "",
            "",
            [
                0.5
                * (ts_prop.bg_regions[0][0] + ts_prop.bg_regions[0][1])
                * ts_prop.nbins_per_step,
                ts_prop.bg_per_bin,
                0.5
                * (ts_prop.bg_regions[1][0] + ts_prop.bg_regions[1][1])
                * ts_prop.nbins_per_step,
                ts_prop.bg_per_bin,
                0.5
                * (ts_prop.bg_regions[2][0] + ts_prop.bg_regions[2][1])
                * ts_prop.nbins_per_step,
                ts_prop.bg_per_bin,
            ],
            0.0,
        ),
        (
            "exponential",
            2,
            1,
            3,
            "fit parameter background 2",
            "",
            [log(ts_prop.bg_per_bin) + 2.0, -1.0 / (0.5 * ts_prop.nbins_per_step)],
            0.5
            * ts_prop.nbins_per_step
            * exp(log(ts_prop.bg_per_bin) + 2.0)
            * (
                exp(
                    -(
                        1.5 * ts_prop.nbins_per_step
                        - 3.0 * ts_prop.peak_width * ts_prop.nbins_per_step
                    )
                    / (0.5 * ts_prop.nbins_per_step)
                )
                - exp(
                    -(
                        1.5 * ts_prop.nbins_per_step
                        + 3.0 * ts_prop.peak_width * ts_prop.nbins_per_step
                    )
                    / (0.5 * ts_prop.nbins_per_step)
                )
            ),
        ),
    ],
)
def test_backgroundRegions(
    model,
    nparams,
    step,
    nregions,
    settings,
    errormessage,
    bgparams,
    bg_volume,
    temp_file,
    test_spectrum,
):
    spec_interface.LoadSpectra(test_spectrum.filename)
    command = ["fit function background activate " + model]
    if settings != "":
        command.append(settings)
    for i in range(nregions):
        command.append(
            "fit marker background set %f"
            % ((step + test_spectrum.bg_regions[i][0]) * test_spectrum.nbins_per_step)
        )
        command.append(
            "fit marker background set %f"
            % ((step + test_spectrum.bg_regions[i][1]) * test_spectrum.nbins_per_step)
        )
    command.append(
        "fit marker region set %f"
        % (
            (step + 0.5) * test_spectrum.nbins_per_step
            - 3.0 * test_spectrum.peak_width * test_spectrum.nbins_per_step
        )
    )
    command.append(
        "fit marker region set %f"
        % (
            (step + 0.5) * test_spectrum.nbins_per_step
            + 3.0 * test_spectrum.peak_width * test_spectrum.nbins_per_step
        )
    )
    command.append(
        "fit marker peak set %f" % ((step + 0.5) * test_spectrum.nbins_per_step)
    )

    command.append("fit execute")
    command.append("fit store")
    for i in range(nregions):
        command.append("fit marker background delete %i" % (i))
    command.append("fit marker region delete 0")
    command.append("fit marker peak delete 0")
    f, ferr = hdtvcmd(*command)

    if WRITE_BATCHFILE:
        batchfile = os.path.join(
            os.path.curdir,
            "test",
            "share",
            model + "_" + str(nparams) + "_" + str(step) + "_background.hdtv",
        )
        bfile = open(batchfile, "w")
        bfile.write("spectrum get " + test_spectrum.filename + "\n")
        for c in command:
            bfile.write(c + "\n")
        bfile.close()

    if errormessage != "":
        hdtvcmd("fit delete 0", "spectrum delete 0")
        assert errormessage in ferr
    else:
        assert ferr == ""

        fitxml.WriteXML(spectra.Get("0").ID, temp_file)
        fitxml.ReadXML(spectra.Get("0").ID, temp_file, refit=True, interactive=False)
        hdtvcmd("fit delete 0", "spectrum delete 0")

        # Parse xml file manually and check correct output
        tree = ET.parse(temp_file)
        root = tree.getroot()

        # Check the number of fits
        fits = root.findall("fit")
        assert len(fits) == 1

        # Check the number and positions of background markers
        bgMarkers = fits[0].findall("bgMarker")
        assert len(bgMarkers) == nregions
        for i in range(len(bgMarkers)):
            assert isclose(
                float(bgMarkers[i].find("begin").find("cal").text),
                (step + test_spectrum.bg_regions[i][0]) * test_spectrum.nbins_per_step,
                abs_tol=BG_MARKER_TOLERANCE,
            )
            assert isclose(
                float(bgMarkers[i].find("end").find("cal").text),
                (step + test_spectrum.bg_regions[i][1]) * test_spectrum.nbins_per_step,
                abs_tol=BG_MARKER_TOLERANCE,
            )
        # Check the number (and values) of background parameters
        background = fits[0].find("background")
        assert background.get("backgroundModel") == model
        assert int(background.get("nparams")) == nparams

        # Check the background parameters
        if len(bgparams) > 0:
            params = background.findall("param")
            for i in range(len(params)):
                if i < len(bgparams):
                    assert isclose(
                        float(params[i].find("value").text),
                        bgparams[i],
                        abs_tol=N_SIGMA * float(params[i].find("error").text),
                    )

        # Check the fit result
        # All results will be compared
        assert isclose(
            float(fits[0].find("peak").find("cal").find("vol").find("value").text),
            test_spectrum.peak_volume,
            abs_tol=N_SIGMA
            * float(fits[0].find("peak").find("cal").find("vol").find("error").text),
        )
        assert isclose(
            float(fits[0].find("peak").find("cal").find("width").find("value").text),
            SIGMA_TO_FWHM * test_spectrum.peak_width * test_spectrum.nbins_per_step,
            abs_tol=N_SIGMA
            * float(fits[0].find("peak").find("cal").find("width").find("error").text),
        )

        # Check the integration result
        integrals = fits[0].findall("integral")
        assert len(integrals) == 3

        assert integrals[0].get("integraltype") == "tot"
        assert integrals[1].get("integraltype") == "bg"
        assert integrals[2].get("integraltype") == "sub"
        # Peak volume
        assert isclose(
            float(integrals[2].find("uncal").find("vol").find("value").text),
            test_spectrum.peak_volume,
            abs_tol=N_SIGMA
            * float(integrals[2].find("uncal").find("vol").find("error").text),
        )
        # Background volume
        if bg_volume > 0.0:
            assert isclose(
                float(integrals[1].find("uncal").find("vol").find("value").text),
                bg_volume,
                abs_tol=sqrt(bg_volume),
            )
        else:
            assert isclose(
                float(integrals[1].find("uncal").find("vol").find("value").text),
                test_spectrum.bg_per_bin
                * 6.0
                * test_spectrum.peak_width
                * test_spectrum.nbins_per_step,
                abs_tol=N_SIGMA
                * sqrt(
                    test_spectrum.bg_per_bin
                    * 6.0
                    * test_spectrum.peak_width
                    * test_spectrum.nbins_per_step
                ),
            )
