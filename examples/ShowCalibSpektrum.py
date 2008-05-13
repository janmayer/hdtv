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
win.SpecGet("spectra/60Co_gamma.lc2")
# show everything to the user
win.ShowFull()


