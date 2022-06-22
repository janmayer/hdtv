#!/usr/bin/env python3


import hdtv.efficiency as eff

e = eff.WiedenhoeverEff()

e.load("eff_wiedenhoever.par", "eff_wiedenhoever.cov")

for i in range(1, 10000, 100):
    print("Wiedenhoefer-Efficiency @", i, " keV = ", e(i))
