#!/usr/bin/python -i
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This very simple example shows how to create a hdtv-window, 
# load a spectrum, add an calibration and show everything to the user.
#
#-------------------------------------------------------------------------------

# set the pythonpath
import sys
sys.path.append("..")

#import some modules
import ROOT
from hdtv.display import Window

# Don't add created spectra to the ROOT directory
ROOT.TH1.AddDirectory(ROOT.kFALSE)

# create a standard window
win = Window()

# add a calibration
win.fDefaultCal = ROOT.GSCalibration(-39.0135, 0.1705)
# load the spectrum 
win.LoadSpec("spectra/60Co_gamma.lc2")
# show full range of spectrum
win.ShowFull()


