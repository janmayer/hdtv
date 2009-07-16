#!/usr/bin/env python
import hdtv.efficiency as eff

e = eff.WiedenhoeferEff()

e.fromfile("eff_wieden.par", "eff_wieden.cov")

for i in range(1, 10000, 100):
    print "Wiedenhoefer-Efficiency @", i," keV = ", e(i)



