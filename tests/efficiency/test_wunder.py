#!/usr/bin/env python3


import hdtv.efficiency as eff

e = eff.WunderEff()

e.load("eff_wunder.par", "eff_wunder.cov")

for i in range(1, 10000, 100):
    print("Wunder-Efficiency @", i, " keV = ", e(i))
