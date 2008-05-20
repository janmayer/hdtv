#!/usr/bin/python -i
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This very simple example shows how to create a hdtv-window, 
# It just adds creates a window, adds one view and loads one spectrum with 
# a calibration to that window.
#-------------------------------------------------------------------------------

# set the pythonpath
import sys
sys.path.append("..")

#import some modules
import ROOT
from hdtv.window import Window

# Don't add created spectra to the ROOT directory
ROOT.TH1.AddDirectory(ROOT.kFALSE)

# create a standard window
win = Window()

# add a view
view = win.AddView("60Co - gamma spectrum")
# add a calibrated spectrum to the new view
spec = view.AddSpec("spectra/60Co_gamma.lc2", [-39.0135, 0.1705], update=False)
# show the new view
win.ShowView(0)

# show full range of spectrum
win.Expand()




