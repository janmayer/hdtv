#!/usr/bin/python -i
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This very simple example shows how to create a hdtv-window, 
# load a spectrum and do a fit.
#
#-------------------------------------------------------------------------------

# set the pythonpath
import sys
sys.path.append("..")

#import some modules
import ROOT
from hdtv.window import Window

# Don't add created spectra to the ROOT directory
ROOT.TH1.AddDirectory(ROOT.kFALSE)

# spectrum with calibration
specfile = "spectra/60Co_gamma.lc2"
cal = [-39.0135, 0.1705]
# create all needed input for the fit
region = [1100.,1400.]
peaks = [1170.,1333.]
backgrounds = [[1130.,1140.],[1190.,1200.],[1300.,1320.],[1350.,1360.]]

# create a standard window, with one view
win = Window()
view = win.AddView("60Co - gamma spectrum")
# load a spectrum to that view
spec = view.AddSpec(specfile, cal, update=False)
# show the new view with the spectrum
win.ShowView(0)
win.Expand()

# add the fit to spectrum
fit = spec.AddFit(region, peaks, backgrounds, lTail=-1, rTail=-1)
# Do the Fit
peaks = fit.DoFit()

for peak in peaks:
	print peak













