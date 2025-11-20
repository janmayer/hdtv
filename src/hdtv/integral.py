# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2018  The HDTV development team (see file AUTHORS)
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

import ROOT
from uncertainties import ufloat


def Integrate(spec, bg, region):
    hist = spec.hist.hist
    region.sort()

    int_tot = ROOT.HDTV.Fit.TH1Integral(hist, region[0], region[1])
    int_bac = (
        ROOT.HDTV.Fit.BgIntegral(bg, region[0], region[1], hist.GetXaxis())
        if bg
        else None
    )
    int_sub = (
        ROOT.HDTV.Fit.TH1BgsubIntegral(hist, bg, region[0], region[1]) if bg else None
    )

    return {
        kind: get_integral_info(spec, integral)
        for (kind, integral) in zip(("tot", "bg", "sub"), (int_tot, int_bac, int_sub))
    }


def get_integral_info(spec, integral):
    if not integral:
        return None
    pos = ufloat(integral.GetMean(), abs(integral.GetMeanError()))
    width = ufloat(integral.GetWidth(), abs(integral.GetWidthError()))
    vol = ufloat(integral.GetIntegral(), abs(integral.GetIntegralError()))
    skew = ufloat(integral.GetRawSkewness(), abs(integral.GetRawSkewnessError()))
    integral_info = {"uncal": {"pos": pos, "width": width, "vol": vol, "skew": skew}}

    if spec.cal:
        return calibrate_integral(integral_info, spec.cal)
    return integral_info


def calibrate_integral(integral_info, cal):
    pos = integral_info["uncal"]["pos"]
    width = integral_info["uncal"]["width"]

    pos_cal = ufloat(
        cal.Ch2E(pos.nominal_value), abs(cal.dEdCh(pos.nominal_value) * pos.std_dev)
    )
    hwhm_uncal = width.nominal_value / 2
    width_cal_n = cal.Ch2E(pos.nominal_value + hwhm_uncal) - cal.Ch2E(
        pos.nominal_value - hwhm_uncal
    )
    # This is only an approximation, valid as d(width_cal_n)/d(pos.nominal_value) ≈ 0
    #  (which is true for Ch2E ≈ linear)
    width_cal_std_dev = abs(
        (
            cal.dEdCh(pos.nominal_value + hwhm_uncal) / 2.0
            + cal.dEdCh(pos.nominal_value - hwhm_uncal) / 2.0
        )
        * width.std_dev
    )
    width_cal = ufloat(width_cal_n, abs(width_cal_std_dev))
    # TODO: Does it make sense to calibrate the skewness?
    # Not relevant for calibrations with degree < 2

    cal = {"pos": pos_cal, "width": width_cal, "vol": integral_info["uncal"]["vol"]}
    integral_info.update({"cal": cal})

    return integral_info
