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

# -------------------------------------------------------------------------
# Infrastructure for generation of artificial spectra
# -------------------------------------------------------------------------


import math

import ROOT


class PolyBg:
    "Polynomial background"

    def __init__(self, coeff):
        self.coeff = coeff

    def value(self, x):
        y = 0.0
        for c in reversed(self.coeff):
            y = y * x + c
        return y


class TheuerkaufPeak:
    "Classic TV peak (a.k.a. Theuerkauf peak)"

    def __init__(self, pos, vol, fwhm, tl=None, tr=None, sh=None, sw=None):
        self.pos = pos
        self.sigma = fwhm / (2 * math.sqrt(2 * math.log(2)))
        self.tl = tl
        self.tr = tr
        self.sh = sh
        self.sw = sw

        # Calculate normalization
        # Contribution from left tail and left half of truncated Gaussian
        if self.tl:
            norm = (
                self.sigma**2 / self.tl * math.exp(-(self.tl**2) / (2 * self.sigma**2))
            )
            norm += (
                math.sqrt(math.pi / 2)
                * self.sigma
                * ROOT.TMath.Erf(self.tl / (math.sqrt(2) * self.sigma))
            )
        else:
            norm = math.sqrt(math.pi / 2) * self.sigma

        # Contribution from right tail and right half of truncated Gaussian
        if self.tr:
            norm += (
                self.sigma**2 / self.tr * math.exp(-(self.tr**2) / (2 * self.sigma**2))
            )
            norm += (
                math.sqrt(math.pi / 2)
                * self.sigma
                * ROOT.TMath.Erf(self.tr / (math.sqrt(2) * self.sigma))
            )
        else:
            norm += math.sqrt(math.pi / 2) * self.sigma

        # Calculate amplitude
        self.amp = vol / norm

    def step(self, x):
        if self.sw is not None and self.sh is not None:
            dx = x - self.pos
            _y = math.pi / 2.0 + math.atan(self.sw * dx / (math.sqrt(2) * self.sigma))
            return self.sh * _y
        else:
            return 0.0

    def value(self, x):
        dx = x - self.pos
        if self.tl is not None and dx < -self.tl:
            _y = self.tl / (self.sigma**2) * (dx + self.tl / 2)
        elif self.tr is not None and dx > self.tr:
            _y = -self.tr / (self.sigma**2) * (dx - self.tr / 2)
        else:
            _y = -(dx**2) / (2 * self.sigma**2)

        return self.amp * (math.exp(_y) + self.step(x))


class EEPeak:
    "Electron-electron scattering peak"

    def __init__(self, pos, amp, sigma1, sigma2, eta, gamma):
        self.pos = pos
        self.amp = amp
        self.sigma1 = sigma1
        self.sigma2 = sigma2
        self.eta = eta
        self.gamma = gamma

    def value(self, x):
        dx = x - self.pos
        if dx <= 0:
            _y = math.exp(-math.log(2) * dx**2 / self.sigma1**2)
        elif dx <= self.eta * self.sigma2:
            _y = math.exp(-math.log(2) * dx**2 / self.sigma2**2)
        else:
            B = self.sigma2 * self.gamma - 2.0 * self.sigma2 * self.eta**2 * math.log(2)
            B /= 2.0 * self.eta * math.log(2)
            A = 2 ** (-(self.eta**2)) * (self.sigma2 * self.eta + B) ** self.gamma
            _y = A / (B + dx) ** self.gamma

        return _y * self.amp


class SpecFunc:
    """
    Sum of background and (several) peak functions, describing a complete
    spectrum
    """

    def __init__(self):
        self.background = None
        self.peaks = []

    def __call__(self, x):
        y = 0.0

        if self.background:
            y += self.background.value(x[0])

        for peak in self.peaks:
            y += peak.value(x[0])

        return y


class Spectrum:
    "Class to generate artificial spectra"

    def __init__(self, nbins, xmin, xmax):
        self.func = SpecFunc()
        self.nbins = nbins
        self.xmin = xmin
        self.xmax = xmax

    def GetFunc(self, name="specfunc"):
        """
        Return the underlying function as a ROOT TF1 object.
        name is the name to be used by ROOT.
        """
        return ROOT.TF1(name, self.func, self.xmin, self.xmax, 0)

    def GetExactHist(self, name="spec_exact"):
        """
        Return a ROOT TH1D object with each bin containing exactly the value
        of the spectrum function at its center.
        """
        hist = ROOT.TH1D(name, name, self.nbins, self.xmin, self.xmax)

        bincenter = hist.GetXaxis().GetBinCenter
        for bin in range(1, hist.GetNbinsX() + 1):
            hist.SetBinContent(bin, self.func([bincenter(bin)]))

        return hist

    def GetSampledHist(self, nsamples, name="spec_sampled"):
        """
        Return a ROOT TH1I object filled with nsamples samples from the spectrum
        function.
        """
        # Due to limitations in ROOT, we cannot pass a TF1 object to FillRandom(),
        # but the function must be loaded from the ROOT function dictionary.
        # We need to choose a "special" name in order to not interfere with
        # any functions the user may have defined.
        func = self.GetFunc("__samplefunc__")

        hist = ROOT.TH1D(name, name, self.nbins, self.xmin, self.xmax)
        hist.FillRandom("__samplefunc__", nsamples)

        del func

        return hist


def write_hist(hist, fname, include_x=False, include_err=False):
    """
    Dump a ROOT histogram object to a textfile. We write the content of all
    bins, exculding the under- and overflow bins, seperated by newlines. The
    parameters include_x and include_err control if the bin center and the bin
    error are to be included. If the resulting file should be readable by the
    old tv program, they must both be set to False.
    """
    f = open(fname, "w")

    axis = hist.GetXaxis()
    for bin in range(1, hist.GetNbinsX() + 1):
        if include_x:
            f.write("%f " % axis.GetBinCenter(bin))
        f.write("%f" % hist.GetBinContent(bin))
        if include_err:
            f.write(" %f" % hist.GetBinError(bin))
        f.write("\n")

    f.close()
