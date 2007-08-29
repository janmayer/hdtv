#!/usr/bin/python
from __future__ import with_statement

import sys
import math
import time
from array import *

# Start ROOT in batch mode
# sys.argv += ["-b"]
import ROOT
from ROOT import std

ROOT.gSystem.Load("gspec.so")
from specreader import *

# Do a polynomial fit, i.e. E = a + b*x + c*x**2 + d*x**3
def fit_poly(positions, energies):
	linfit = ROOT.TLinearFitter(1, "pol3", "")
	v = array('d', [0.0])
		
	for (x,y) in zip(positions, energies):
		v[0] = x
		linfit.AddPoint(v,y)
		
	linfit.Eval()
	
	return map(lambda i: linfit.GetParameter(i), [0,1,2,3])
	
# Do a linear fit, i.e. E = a + b*x (presently not used)
def fit_linear(positions, energies):
	linfit = ROOT.TLinearFitter(1, "hyp1", "")
	v = array('d', [0.0])
		
	for (x,y) in zip(positions, energies):
		v[0] = x
		linfit.AddPoint(v,y)
		
	linfit.Eval()
	
	return [linfit.GetParameter(0), linfit.GetParameter(1)]
	
# Invoke ROOT's peak finder
def find_peaks(hist):
	spec = ROOT.TSpectrum(100)
	npk = spec.Search(hist, 2.0, "goff", 0.005)
	pks = spec.GetPositionX()
	peaks = []
	
	# Copy peaks to a python list
	# (otherwise, things like len() won't work)
	for i in range(0, npk):
		peaks.append(pks[i])
		
	return peaks
	
# Fit the peak, using a Gaussian with linear background
# in a region 40 channels wide
def fit_peak(hist, pos, left_neighbour, right_neighbour):
	left_pos = (pos + left_neighbour) / 2.0
	right_pos = (pos + right_neighbour) / 2.0
	
	if(pos - left_pos > 20):
		left_pos = pos - 20
		
	if(right_pos - pos > 20):
		right_pos = pos + 20
		
	#a = hist.GetBinContent(int(left_pos)) - hist.GetBinContent(int(right_pos))
	#a /= (left_pos - right_pos)
	#b = hist.GetBinContent(int(left_pos)) - a*left_pos
	
	a = (hist.GetBinContent(int(left_pos)) + hist.GetBinContent(int(right_pos))) / 2.0
	
	par = array('d', [hist.GetBinContent(int(pos)), pos, 10.0, 0.0, a])

	func = ROOT.TF1("func", "gaus(0) + [3] * x + [4]")
	func.SetParameters(par)
	hist.Fit(func, "QN", "", pos-20, pos+20)
	func.GetParameters(par)
	
	fit_pos = par[1]
	fit_vol = math.sqrt(2 * math.pi) * par[0] * par[2]
	
	return (fit_pos, fit_vol)
	
# Find peak closest to a given position
# Assumes peaks to be a sorted list
# NB: This implementation is probably not optimal in
# terms of run time
def find_nearest(peaks, pos):
	best = None
	min_dist = 10000000
	peaks.append(10000000)
	i = 0
	
	while True:
		dist = abs(peaks[i] - pos)
		
		if dist > min_dist:
			break
			
		min_dist = dist
		i += 1
		
	peaks.pop()
		
	return (i-1)

# Match the peaks in the spectrum to the peaks expected
# Assumes that every expected peak can be seen
def match_peaks(peaks, src_energies):
	if len(src_energies) < 2:
		raise RuntimeError, "Too few literature energies given"

	best_chi = 1E10
		
	e1 = src_energies[0]
	e2 = src_energies[len(src_energies)-1]

	# (i1, i2) is the index of the candidate for the
	# (first, second) literature peak
	for i1 in range(0, len(peaks)):
		for i2 in range(i1+4, len(peaks)):
			x1 = peaks[i1]
			x2 = peaks[i2]
			
			# Do a linear calibration
			b = (e2 - e1) / (x2 - x1)
			a = e1 - b * x1
			
			# Calculate squared sum of position deviations
			chi = 0.0
			
			if abs(a) > 100.0:
				chi += 10000
				
			if abs(b - 1.0) > 0.5:
				chi += 10000
			
			for i in range(0, len(src_energies)):
				src_pos = (src_energies[i] - a) / b
				i_n = find_nearest(peaks, src_pos)
				dist = abs(peaks[i_n] - src_pos)
				chi += dist**2
				
				if chi > best_chi:
					break
				
			# print "%d %d %.2f %.2f %.2f" % (i1, i2, a, b, chi)
				
			if chi < best_chi:
				best_i1 = i1
				best_i2 = i2
				best_chi = chi
				
			#if abs(a) < 100 and abs(b-1.0) < 0.5:
			#	print i1, i2, chi
			
	# Calculate association of literature to source peaks
	# for the best match
	assoc_peaks = []
		
	x1 = peaks[best_i1]
	x2 = peaks[best_i2]
	b = (e2 - e1) / (x2 - x1)
	a = e1 - b * x1
	
	for i in range(0, len(src_energies)):
		src_pos = (src_energies[i] - a) / b
		assoc_peaks.append(find_nearest(peaks, src_pos))
	
	return assoc_peaks
	
def ch2e(x, polypar):
	res = polypar[0]
	xn = x
	
	for i in range(1, len(polypar)):
		res += polypar[i] * xn
		xn *= x
		
	return res

for det in range(0,16):
	with open("data/ge%d.sig" % det) as f:
		src_energies = map(lambda s: float(s), f.read().split())

	for n in range(28,50):
		path = "/mnt/braun/88Zr_angle_singles/%04d/ge%d.%04d" % (n,det,n)
		hist = SpecReader().Get(path, "spec_%d_%d" % (det,n), "spec")
		
		peaks = [0.0] + find_peaks(hist) + [8192.0]
		peaks.sort()
		
		#print peaks
		
		# print peaks
		
		fit_peaks = []
		for i in range(1,len(peaks)-1):
			#fit = fit_peak(hist, peaks[i], peaks[i-1], peaks[i+1])
			fit = [peaks[i], 1.0]
			
			if abs(fit[0] - peaks[i]) < 20.0:
				fit_peaks.append(fit)
				#viewer.SetMarker(fit[0])
				
		fit_peaks.sort()
		
		#print src_energies
		#print map(lambda x: x[0], fit_peaks)
		
		assoc_peaks = match_peaks(map(lambda x: x[0], fit_peaks), src_energies)
		
		polypar = fit_linear(map(lambda i: fit_peaks[i][0], assoc_peaks), src_energies)
		
		#print "  FitPos   CalcEn    LitEn      Vol"
	
		#for i in range(0, len(src_energies)):
		#	fit_pos = fit_peaks[assoc_peaks[i]][0]
		#	fit_vol = fit_peaks[assoc_peaks[i]][1]
		#	print "%8.2f %8.2f %8.2f %8.0f" % (fit_pos, ch2e(fit_pos, polypar), src_energies[i], fit_vol)
			# viewer.SetMarker(fit_pos)
		
		
		if abs(polypar[0]) > 10.0 or abs(polypar[1] - 1.0) > 0.1:
			print "Warning: %d %d: " % (det, n) + " ".join(map(lambda x: str(x), polypar))

