# -*- coding: utf-8 -*-

# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2011  The HDTV development team (see file AUTHORS)
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

from __future__ import print_function

import ROOT
import hdtv.ui
from hdtv.errvalue import ErrValue

def Integrate(spec, bg, region):
    hist = spec.hist.hist

    region.sort()
    int_tot = ROOT.HDTV.Fit.TH1Integral(hist, region[0], region[1])

    int_bac = None
    int_sub = None

    if bg:
        for i in range(0, bg.GetDegree()+1):
            par = ErrValue(bg.GetFunc().GetParameter(i), bg.GetFunc().GetParError(i))
            print("bg[%d]: %10s" % (i, par.fmt()))

        int_bac = ROOT.HDTV.Fit.BgIntegral(bg, region[0], region[1], hist.GetXaxis())
        int_sub = ROOT.HDTV.Fit.TH1BgsubIntegral(hist, bg, region[0], region[1])

    hdtv.ui.msg("")
    hdtv.ui.msg("type        position           width          volume        skewness")
    for (integral, kind) in zip((int_tot, int_bac, int_sub), ("tot:", "bac:", "sub:")):
        if integral:
            pos = ErrValue(integral.GetMean(), integral.GetMeanError())
            width = ErrValue(integral.GetWidth(), integral.GetWidthError())
            vol = ErrValue(integral.GetIntegral(), integral.GetIntegralError())
            skew = ErrValue(integral.GetRawSkewness(), integral.GetRawSkewnessError())

            msg = "%s %15s %15s %15s %15s" % \
                (kind, pos.fmt(), width.fmt(), vol.fmt(), skew.fmt())
            hdtv.ui.msg(msg)

    if spec.cal:
        hdtv.ui.msg("")
        hdtv.ui.msg("type  position (cal)     width (cal)")
        for (integral, kind) in zip((int_tot, int_bac, int_sub), ("tot:", "bac:", "sub:")):
            if integral:
                pos_uncal = integral.GetMean()
                pos_err_uncal = integral.GetMeanError()
                pos_cal = spec.cal.Ch2E(pos_uncal)
                pos_err_cal = abs(spec.cal.dEdCh(pos_uncal) * pos_err_uncal)

                hwhm_uncal = integral.GetWidth()/2
                width_err_uncal = integral.GetWidthError()
                width_cal = spec.cal.Ch2E(pos_uncal + hwhm_uncal) - spec.cal.Ch2E(pos_uncal - hwhm_uncal)
                # This is only an approximation, valid as d(width_cal)/d(pos_uncal) \approx 0
                #  (which is true for Ch2E \approx linear)
                width_err_cal = abs( (spec.cal.dEdCh(pos_uncal + hwhm_uncal) / 2. +
                                      spec.cal.dEdCh(pos_uncal - hwhm_uncal) / 2.   ) * width_err_uncal)
                msg = "%s %15s %15s" % \
                    (kind, ErrValue(pos_cal, pos_err_cal).fmt(), \
                     ErrValue(width_cal, width_err_cal).fmt())
                hdtv.ui.msg(msg)
