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

import os

import numpy as np
from numpy import arange, exp, log, ones, savetxt
from numpy.random import poisson
from scipy.stats import norm


# Set properties of the background spectrum
# The properties are implemented in a separate class
# to be able to access them before the actual spectrum has
# been created
class ArtificialSpecProp:
    def __init__(self):
        self.nsteps = 3
        self.bg_regions = [[0.1, 0.35], [0.65, 0.775], [0.775, 0.9], [0.9, 0.95]]
        self.peak_width = 0.03
        self.nbins_per_step = 300
        self.bg_per_bin = 10.0
        self.peak_volume = 500.0
        self.bg_type = ["constant", "exponential", "constant"]
        self.poisson_fluctuations = [False, False, True]


class ArtificialSpec:
    def __init__(self, path, prop=None):
        prop = prop or ArtificialSpecProp()
        self.nsteps = prop.nsteps
        self.bg_regions = prop.bg_regions
        self.peak_width = prop.peak_width
        self.nbins_per_step = prop.nbins_per_step
        self.bg_per_bin = prop.bg_per_bin
        self.peak_volume = prop.peak_volume
        self.bg_type = prop.bg_type
        self.poisson_fluctuations = prop.poisson_fluctuations
        self.spectrum = ones(self.nsteps * self.nbins_per_step)
        self.filename = os.path.join(path, "test_spectrum_background.tv")

    def create(self):
        """Create the test spectrum (if not already done)"""

        np.random.seed(0)

        if not os.path.isfile(self.filename):
            # Create an array for the bin centers
            bins = arange(self.nsteps * self.nbins_per_step) + 0.5
            spectrum = ones(self.nsteps * self.nbins_per_step)
            # Create the steps with increasing height
            for i in range(self.nsteps):
                if self.bg_type[i] == "constant":
                    spectrum[
                        i * self.nbins_per_step : (i + 1) * self.nbins_per_step
                    ] = self.bg_per_bin * ones(self.nbins_per_step)
                elif self.bg_type[i] == "exponential":
                    spectrum[
                        i * self.nbins_per_step : (i + 1) * self.nbins_per_step
                    ] = exp(
                        log(self.bg_per_bin)
                        + bins[i * self.nbins_per_step] / (0.5 * self.nbins_per_step)
                        - bins[i * self.nbins_per_step : (i + 1) * self.nbins_per_step]
                        / (0.5 * self.nbins_per_step)
                    )

                if self.poisson_fluctuations[i]:
                    spectrum[
                        i * self.nbins_per_step : (i + 1) * self.nbins_per_step
                    ] = poisson(
                        spectrum[
                            i * self.nbins_per_step : (i + 1) * self.nbins_per_step
                        ]
                    )

                # The peaks are located exactly in the centers of the steps
                spectrum = spectrum + self.peak_volume * norm.pdf(
                    bins,
                    loc=i * self.nbins_per_step + 0.5 * self.nbins_per_step,
                    scale=self.peak_width * self.nbins_per_step,
                )

            savetxt(self.filename, spectrum)

        return self.filename
