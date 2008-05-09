#!/usr/bin/python -i
# -*- coding: utf-8 -*-
from __future__ import with_statement

# set the pythonpath
import sys
sys.path.append("/home/braun/hdtv/pylib")


import ROOT
from diploma import Horus88Zr
from window import Window, Fit, XMarker
from hdtv import SpecWindow
from fitpanel import FitPanel
from specreader import *

ROOT.TH1.AddDirectory(ROOT.kFALSE)

if ROOT.gSystem.Load("../lib/gspec.so") < 0:
	raise RuntimeError, "Library not found (gspec.so)"

def ReadCal(fname):
	calpars = []

	with open(fname) as f:
		for line in f:
			line = line.strip()
			if line != '':
				calpars.append(float(line))
				
	return ROOT.GSCalibration(calpars[0], calpars[1], calpars[2], calpars[3])

exp = Horus88Zr()
win = SpecWindow()

win.RegisterKeyHandler("win.KeyHandler")
win.fDefaultCal = ROOT.GSCalibration(0.0, 0.5)

for det in range(0,16):
	view = win.AddView("ge%d" % det)
	# calfile = exp.CalFile(det)
	# calfile = "/mnt/omega/braun/effcal/ge%d.sum.cal" % det
	# win.fDefaultCal = ReadCal(calfile)
	# win.SpecGet("/mnt/omega/braun/88Zr_angle_singles/0070/ge%d.0070" % det, view)
	# win.SpecGet("/mnt/omega/braun/effcal/ge%d.sum" % det, view)
	win.SpecGet("ge%d.sum" % det, view)
	
win.SetView(0)
win.ShowFull()



