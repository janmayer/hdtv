#!/usr/bin/python
# -*- coding: utf-8 -*-

# Simple Monte Carlo simulation to test propagation of covariance.
#
# x and y are two statistically independant, Gaussian distributed random
# variables with var(x) = 1, var(y) = 4, and cov(x, y) = 0. We then form
# new variables
#    f = 3*x + 2*y + 5
#    g = x - 3*y - 10
# with
#    var(f)   = 9 * var(x) + 4 * var(y) =  25
#    var(g)   = 1 * var(x) + 9 * var(y) =  37
#    cov(f,g) = 3 * var(x) - 6 * var(y) = -21
# and, from these,
#    a = f +   g - 10
#    b = f - 2*g - 10
# with
#    cov(a, b) = var(f) + (1-2)*cov(f,g) - 2*var(g) = -28
#
# This result is then compared to a Monte Carlo simulation.
import ROOT

rand = ROOT.TRandom2()

h = ROOT.TH2I("test", "test", 300, -60, 40, 300, -60., 100.)

for i in range(0,1000000):
    x = rand.Gaus(0., 1.)
    y = rand.Gaus(0., 2.)
    f = 3*x+2*y+5.
    g = x-3*y-10.
    
    h.Fill(f+g-10., f-2*g-10.)
    
print("MC result: %.6f" % h.GetCovariance())
print("Expected: -28")
