#!/usr/bin/python -i
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This very simple example shows how to create a hdtv-window, 
# load a spectrum, add an calibration, do a fit and show everything to the user.
#
#-------------------------------------------------------------------------------

# set the pythonpath
import sys
sys.path.append("..")

#import some modules
import ROOT
from hdtv.display import Window, Fit

# load gspec library 
ROOT.TH1.AddDirectory(ROOT.kFALSE)
if ROOT.gSystem.Load("../lib/gspec.so") < 0:
	raise RuntimeError, "Library not found (gspec.so)"


# create a standard window
win = Window()
# init key handling for that window
win.RegisterKeyHandler("win.KeyHandler")
# add a calibration
win.fDefaultCal = ROOT.GSCalibration(-39.0135, 0.1705)
# load the spectrum 
spec = win.SpecGet("spectra/60Co_gamma.lc2")
# show everything to the user
win.ShowFull()

# define a fitter and a region
fitter = ROOT.GSFitter(spec.E2Ch(1100.), spec.E2Ch(1400.))
# add two peaks
fitter.AddPeak(spec.E2Ch(1170.))
fitter.AddPeak(spec.E2Ch(1333.))
# add some background regions
fitter.AddBgRegion(spec.E2Ch(1130.), spec.E2Ch(1140.))
fitter.AddBgRegion(spec.E2Ch(1190.), spec.E2Ch(1200.))
fitter.AddBgRegion(spec.E2Ch(1300.), spec.E2Ch(1320.))
fitter.AddBgRegion(spec.E2Ch(1350.), spec.E2Ch(1360.))
# fit with left tail
fitter.SetLeftTails(-3.0)

# first fit the background
bgFunc = fitter.FitBackground(spec.hist)
# then fit the peaks
func = fitter.Fit(spec.hist, bgFunc)
								
# FIXME: why is this needed? Possibly related to some
# subtle issue with PyROOT memory management
# TODO: At least a clean explaination, hopefully a better solution...
fit = Fit(ROOT.TF1(func), ROOT.TF1(bgFunc), spec.cal)
# draw the result to the screen
fit.Realize(win.fViewport)
# print the results
fit.Report()




