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
# Test program to compare fitting results of tv and hdtv
# -------------------------------------------------------------------------

import peakgen

spec = peakgen.Spectrum(1024, -0.5, 1023.5)
spec.func.background = peakgen.PolyBg([10.0])
# spec.func.peaks.append(peakgen.TheuerkaufPeak(500, 300.0, 10.0, sh=0.3, sw=1.0))
spec.func.peaks.append(peakgen.TheuerkaufPeak(515, 3000.0, 10.0))
# spec.peaks.append(peakgen.EEPeak(300, 100, 4.5, 6.0, 1.5, 0.7))
# spec.peaks.append(peakgen.EEPeak(400, 30, 4.5, 6.0, 1.5, 0.7))

nsamples = int(3e3)
hs = spec.GetSampledHist(nsamples)
# hs.Draw()

he = spec.GetExactHist()
scale = nsamples / he.GetSumOfWeights()
he.Scale(scale)

# he.SetLineColor(ROOT.kRed)
# he.Draw("SAME")

peakgen.write_hist(he, "test_exact.asc")
peakgen.write_hist(hs, "test_sampled.asc")
