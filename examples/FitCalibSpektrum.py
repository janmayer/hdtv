#!/usr/bin/python -i
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This very simple example shows how to create a hdtv-window, 
# load a spectrum, add an calibration, do a fit and show everything to the user.
#
#-------------------------------------------------------------------------------

# TODO: Broken at the moment!

# set the pythonpath
import sys
sys.path.append("..")

#import some modules
import ROOT
from hdtv.display import Window, Fit

# Don't add created spectra to the ROOT directory
ROOT.TH1.AddDirectory(ROOT.kFALSE)

# create a standard window
win = Window()
# add a calibration
cal = ROOT.GSCalibration(-39.0135, 0.1705)
# load the spectrum 
spec = win.LoadSpec("spectra/60Co_gamma.lc2", cal=cal)
# show full range of spectrum
win.Expand()
# create all needed input for the fit
region = [1100.,1400.]
peaks = [1170.,1333.]
backgrounds = [[1130.,1140.],[1190.,1200.],[1300.,1320.],[1350.,1360.]]
spec.AddFit(region, peaks, backgrounds)


#fit = win.LoadFit(spec, region, peaks, backgrounds, leftTail=-3.0) 
## report the results
#fit.Report()




