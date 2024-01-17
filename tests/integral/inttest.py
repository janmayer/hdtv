#!/usr/bin/env python3

import sys

sys.path.append("/home/braun/projects/hdtv")
import ROOT

import hdtv.specreader
from hdtv.errvalue import ErrValue


def test(bgdeg):
    int_tot = ROOT.HDTV.Fit.TH1Integral(h, 6, 12)

    bg = ROOT.HDTV.Fit.PolyBg(bgdeg)
    bg.AddRegion(-0.1, 5.1)
    bg.AddRegion(12.9, 18.1)
    bg.Fit(h)

    for i in range(bg.GetDegree() + 1):
        par = ErrValue(bg.GetFunc().GetParameter(i), bg.GetFunc().GetParError(i))
        print("bg[%d]: %10s" % (i, par.fmt()))

    int_bac = ROOT.HDTV.Fit.BgIntegral(bg, 6, 12, h.GetXaxis())
    int_sub = ROOT.HDTV.Fit.TH1BgsubIntegral(h, bg, 6, 12)

    print("")
    print("type        position           width          volume        skewness")
    for integral, kind in zip((int_tot, int_bac, int_sub), ("tot:", "bac:", "sub:")):
        pos = ErrValue(integral.GetMean(), integral.GetMeanError())
        width = ErrValue(integral.GetWidth(), integral.GetWidthError())
        vol = ErrValue(integral.GetIntegral(), integral.GetIntegralError())
        skew = ErrValue(integral.GetRawSkewness(), integral.GetRawSkewnessError())

        print(
            "%s %15s %15s %15s %15s"
            % (kind, pos.fmt(), width.fmt(), vol.fmt(), skew.fmt())
        )


reader = hdtv.specreader.SpecReader()
h = reader.GetSpectrum("test.asc")

h.Sumw2()

print("bgdeg=1")
test(1)

print("")
print("bgdeg=2")
test(2)
