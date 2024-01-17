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
Test whether the calbin algorithm conserves the statistical properties of the spectrum by fitting a peak before and after calbinning.
"""

import os
import xml.etree.ElementTree as ET
from math import sqrt

import pytest

from hdtv.util import monkey_patch_ui
from tests.helpers.create_test_spectrum import ArtificialSpec
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

spectra = __main__.spectra

N_SIGMA = 3  # Determines how many standard deviations (sigma) a fitted quantity
# may deviate from the ideal value.
# Sigma is provided by the fitting algorithm .
UNCERTAINTY_RELATIVE_TOLERANCE = 0.2  # Determines how large the relative deviation, after calbinning, of the fit uncertainties from the original uncertainty may be.
WRITE_BATCHFILE = False  # Determines whether the batch files of the test fits should be written to file.


@pytest.fixture()
def test_spectrum(tmp_path):
    ts = ArtificialSpec(path=tmp_path)
    ts.create()
    return ts


def test_calbin(temp_file, test_spectrum):
    command = ["spectrum get " + test_spectrum.filename]

    step = 2  # Use the third spectrum which has a constant background and Poissonian fluctuations
    # Fit the peak in step 2
    command.append(
        "fit marker background set %f"
        % ((step + test_spectrum.bg_regions[0][0]) * test_spectrum.nbins_per_step)
    )
    command.append(
        "fit marker background set %f"
        % ((step + test_spectrum.bg_regions[0][1]) * test_spectrum.nbins_per_step)
    )
    command.append(
        "fit marker background set %f"
        % ((step + test_spectrum.bg_regions[1][0]) * test_spectrum.nbins_per_step)
    )
    command.append(
        "fit marker background set %f"
        % ((step + test_spectrum.bg_regions[1][1]) * test_spectrum.nbins_per_step)
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
    f, ferr = hdtvcmd(*command)

    if WRITE_BATCHFILE:
        batchfile = os.path.join(os.path.curdir, "test", "share", "calbin.hdtv")
        with open(batchfile, "w") as bfile:
            for c in command:
                bfile.write(c + "\n")

        assert ferr == ""

    # Write the fit result to a temporary XML file
    fitxml.WriteXML(spectra.Get("0").ID, temp_file)
    fitxml.ReadXML(spectra.Get("0").ID, temp_file, refit=True, interactive=False)

    # Parse XML file manually
    tree = ET.parse(temp_file)
    root = tree.getroot()

    # Check the number of fits
    fits = root.findall("fit")
    assert len(fits) == 1

    # Read out the main fitted peak properties (position, volume, width) and their uncertainties
    pos_value_init = float(
        fits[0].find("peak").find("cal").find("pos").find("value").text
    )
    pos_error_init = abs(
        float(fits[0].find("peak").find("cal").find("pos").find("error").text)
    )
    vol_value_init = float(
        fits[0].find("peak").find("cal").find("vol").find("value").text
    )
    vol_error_init = abs(
        float(fits[0].find("peak").find("cal").find("vol").find("error").text)
    )
    width_value_init = float(
        fits[0].find("peak").find("cal").find("width").find("value").text
    )
    width_error_init = abs(
        float(fits[0].find("peak").find("cal").find("width").find("error").text)
    )

    # Calbin the spectrum with standard settings, read in the fitted value again and check whether they have changed
    command = ["spectrum calbin 0 -s 1"]
    command.append("fit execute")
    command.append("fit store")
    f, ferr = hdtvcmd(*command)
    assert ferr == ""

    if WRITE_BATCHFILE:
        batchfile = os.path.join(os.path.curdir, "test", "share", "calbin.hdtv")
        with open(batchfile, "a") as bfile:
            for c in command:
                bfile.write(c + "\n")

        assert ferr == ""

    fitxml.WriteXML(spectra.Get("0").ID, temp_file)
    fitxml.ReadXML(spectra.Get("0").ID, temp_file, refit=False, interactive=False)

    tree = ET.parse(temp_file)
    root = tree.getroot()

    fits = root.findall("fit")
    # It is a little bit unsatisfactory to accumulate the fits multiple times in temp_file, but I found no way to erase the content of temp_file
    # open(temp_file, 'w').close() wouldn't work
    assert len(fits) == 3

    pos_value_1 = float(fits[2].find("peak").find("cal").find("pos").find("value").text)
    pos_error_1 = abs(
        float(fits[2].find("peak").find("cal").find("pos").find("error").text)
    )
    vol_value_1 = float(fits[2].find("peak").find("cal").find("vol").find("value").text)
    vol_error_1 = abs(
        float(fits[2].find("peak").find("cal").find("vol").find("error").text)
    )
    width_value_1 = float(
        fits[2].find("peak").find("cal").find("width").find("value").text
    )
    width_error_1 = abs(
        float(fits[2].find("peak").find("cal").find("width").find("error").text)
    )

    # For the fit of the position, allow it to deviate by N_SIGMA times the combined standard deviations of the fitted positions PLUS the width of a single bin.
    assert isclose(
        pos_value_init - pos_value_1,
        0.0,
        abs_tol=N_SIGMA
        * sqrt(pos_error_init * pos_error_init + pos_error_1 * pos_error_1)
        + 1.0,
    )
    assert isclose(
        vol_value_init - vol_value_1,
        0.0,
        abs_tol=N_SIGMA
        * sqrt(vol_error_init * vol_error_init + vol_error_1 * vol_error_1),
    )
    assert isclose(
        width_value_init - width_value_1,
        0.0,
        abs_tol=N_SIGMA
        * sqrt(width_error_init * width_error_init + width_error_1 * width_error_1),
    )

    # Calbin the spectrum with a factor of 2, read in the fitted value again and check whether they have changed
    command = ["spectrum calbin 0 -b 2 -s 0"]
    command.append("fit execute")
    command.append("fit store")
    f, ferr = hdtvcmd(*command)
    assert ferr == ""

    if WRITE_BATCHFILE:
        batchfile = os.path.join(os.path.curdir, "test", "share", "calbin.hdtv")
        with open(batchfile, "a") as bfile:
            for c in command:
                bfile.write(c + "\n")

        assert ferr == ""

    fitxml.WriteXML(spectra.Get("0").ID, temp_file)
    fitxml.ReadXML(spectra.Get("0").ID, temp_file, refit=False, interactive=False)

    tree = ET.parse(temp_file)
    root = tree.getroot()

    fits = root.findall("fit")
    assert len(fits) == 7

    pos_value_2 = float(fits[6].find("peak").find("cal").find("pos").find("value").text)
    pos_error_2 = abs(
        float(fits[6].find("peak").find("cal").find("pos").find("error").text)
    )
    vol_value_2 = float(fits[6].find("peak").find("cal").find("vol").find("value").text)
    vol_error_2 = abs(
        float(fits[6].find("peak").find("cal").find("vol").find("error").text)
    )
    width_value_2 = float(
        fits[6].find("peak").find("cal").find("width").find("value").text
    )
    width_error_2 = abs(
        float(fits[6].find("peak").find("cal").find("width").find("error").text)
    )

    assert isclose(
        pos_value_init - pos_value_2,
        0.0,
        abs_tol=N_SIGMA
        * sqrt(pos_error_init * pos_error_init + pos_error_2 * pos_error_2)
        + 2.0,
    )
    assert isclose(
        vol_value_init - vol_value_2,
        0.0,
        abs_tol=N_SIGMA
        * sqrt(vol_error_init * vol_error_init + vol_error_2 * vol_error_2),
    )
    assert isclose(
        width_value_init - width_value_2,
        0.0,
        abs_tol=N_SIGMA
        * sqrt(width_error_init * width_error_init + width_error_2 * width_error_2),
    )

    assert isclose(pos_error_init, pos_error_2, rel_tol=0.2)
    assert isclose(vol_error_init, vol_error_2, rel_tol=0.2)
    assert isclose(pos_error_init, pos_error_2, rel_tol=0.2)
