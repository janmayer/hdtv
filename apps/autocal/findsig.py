#!/usr/bin/python
from __future__ import with_statement

import ROOT
import math
import sys
from specreader import *
from libpeaks import *
from diploma import Horus88Zr

if ROOT.gSystem.Load("../lib/gspec.so") < 0:
	raise RuntimeError, "Library not found (gspec.so)"
	
experiment = Horus88Zr()
det = int(sys.argv[1])
	
def LoadCalibration(fname):
		with open(fname) as f:
			calPoly = map(lambda s: float(s), f.read().split())
			
		if len(calPoly) != 4:
			raise RuntimeError, "Calibration should be a third-order polynomial"
			
		return ROOT.GSCalibration(calPoly[0], calPoly[1], calPoly[2], calPoly[3])

lit_energies = [232, 1057]
lowerE = 150.0
sig_peaks = []

fname = experiment.SpecFile(74, det)
hist = SpecReader().Get(fname, fname, "hist")
fList = PeakList()
fList.fit(hist)

peakList = fList.peak_list()

cal = LoadCalibration(experiment.CalFile(det))

for e in lit_energies:
	pos = cal.E2Ch(e)
	min_dist = 1e10
	best = None
	
	for peak in peakList:
		if abs(peak.pos() - pos) < min_dist:
			min_dist = abs(peak.pos() - pos)
			best = peak
			
	sig_peaks.append(best)
	
fList.reject_bad_groups(2000.0, 15.0)

peakList = fList.peak_list_by_vol()
add_peaks = []

for peak in peakList:
	if not peak in sig_peaks and cal.Ch2E(peak.pos()) > lowerE:
		add_peaks.append(peak)
		
	if len(add_peaks) >= 10:
		break
		
for peak in sig_peaks:
	print peak.pos()
	
for peak in add_peaks:
	print peak.pos()
