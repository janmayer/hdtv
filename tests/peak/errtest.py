#!/usr/bin/env python3

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
# Program to test handling of spectra with explicit errors in hdtv
# -------------------------------------------------------------------------

# Spectra that are directly recorded usually have errors \sqrt{n} for each bin,
# where n is the number of counts in the bin. However, after scaling, this is
# no longer true. Thus, scaled spectra need to specify the bin errors
# explicitly.
# This program can be used to test the handling of spectra with explicit
# errors in hdtv.

import peakgen
import ROOT

spec = peakgen.Spectrum(1024, -0.5, 1023.5)
spec.func.background = peakgen.PolyBg([10.0])
spec.func.peaks.append(peakgen.TheuerkaufPeak(515, 3000.0, 10.0))

rfile = ROOT.TFile("errtest.root", "RECREATE")

nsamples = int(3e3)

# unscaled histogram
h1 = spec.GetSampledHist(nsamples, "unscaled")

# scaled histogram WITHOUT correct errors
h2 = spec.GetSampledHist(nsamples, "scaled_no_error")
h2.Scale(0.1)

# scaled histogram with correct errors
h3 = spec.GetSampledHist(nsamples, "scaled_with_error")
h3.Sumw2()
h3.Scale(0.1)

# Dump histograms to text files
peakgen.write_hist(h1, "unscaled.txt", include_x=True, include_err=True)
peakgen.write_hist(h2, "scaled_no_error.txt", include_x=True, include_err=True)
peakgen.write_hist(h3, "scaled_with_error.txt", include_x=True, include_err=True)

# Write ROOT file (histogram have been added automatically)
rfile.Write()
rfile.Close()
