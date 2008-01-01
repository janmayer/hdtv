#!/usr/bin/python
import sys
import math
import time
from array import *
from libpeaks import *

# Start ROOT in batch mode
# sys.argv += ["-b"]
import ROOT
from ROOT import std

# Energies of the calibration source
# src_energies = [186.2, 242.0, 295.2, 351.9, 609.3, 1120.3, 1764.5, 2447.8] 

from specreader import *

if ROOT.gSystem.Load("../lib/gspec.so") < 0:
	raise RuntimeError, "Library not found (gspec.so)"

class Autocal:
	def __init__(self):
		self.fRefPeaks = [186.2, 242.0, 295.2, 351.9, 609.3, 1120.3, 1764.5, 2447.8]
		self.fPeaks = None
		self.fPeakAssocs = None
		self.fAllPeakAssocs = None
		self.p0 = None
		self.p1 = None
		self.chi2 = None
			
	def FindPeaks(self, hist):
		fList = PeakList()
		fList.fit(hist)
		# fList.reject_bad_groups(2000.0, 15.0)
		self.fPeaks = map(lambda p: p.pos(), fList.peak_list_by_pos())

	# Do a linear fit, i.e. E = a + b*x
	def Fit(self):
		linfit = ROOT.TLinearFitter(1, "hyp1", "")
		v = array('d', [0.0])
			
		for i in range(0, len(self.fPeakAssocs)):
			if self.fPeakAssocs[i] != None:
				x = self.fPeaks[self.fPeakAssocs[i]]
				y = self.fRefPeaks[i]
				
				v[0] = x
				linfit.AddPoint(v,y)
					
		linfit.Eval()
	
		self.p0 = linfit.GetParameter(0)
		self.p1 = linfit.GetParameter(1)
		self.chi2 = linfit.GetChisquare()

	# Find peak closest to a given position
	# Assumes peaks to be a sorted list
	# NB: This implementation is probably not optimal in
	# terms of run time
	def FindNearest(self, pos):
		best = None
		min_dist = 1E10
		self.fPeaks.append(1E11)
		i = 0
	
		while True:
			dist = abs(self.fPeaks[i] - pos)
			
			if dist > min_dist:
				break
				
			min_dist = dist
			i += 1
			
		self.fPeaks.pop()
			
		return (i-1)

	# Match the peaks in the spectrum to the peaks expected
	# Assumes that the first two peaks in the list can be seen
	def MatchPeaks(self):
		if not self.fRefPeaks or len(self.fRefPeaks) < 2:
			raise RuntimeError, "Too few reference peaks given"

		best_chi = 1E10
		
		e1 = self.fRefPeaks[0]
		e2 = self.fRefPeaks[1]
		
		if not self.fPeaks or len(self.fPeaks) < len(self.fRefPeaks):
			raise RuntimeError, "Too few peaks found"

		# (i1, i2) is the index of the candidate for the	
		# (first, second) literature peak
		for i1 in range(0, len(self.fPeaks)):
			for i2 in range(i1 + 1, len(self.fPeaks)):
				x1 = self.fPeaks[i1]
				x2 = self.fPeaks[i2]
				
				# Do a linear calibration: e(x) = p1 * x + p0
				p1 = (e2 - e1) / (x2 - x1)
				p0 = e1 - p1 * x1
					
				# Calculate squared sum of position deviations
				chiList = []
					
				for i in range(0, len(self.fRefPeaks)):
					lit_pos = (self.fRefPeaks[i] - p0) / p1
					i_n = self.FindNearest(lit_pos)
					dist = abs(self.fPeaks[i_n] - lit_pos)
					chiList.append(dist**2)
					
				#chiList.sort()
				#chi = sum(chiList[0:-3])
				chi = sum(chiList)
				
				# print "%d %d %.2f %.2f %.2f" % (i1, i2, a, b, chi)
					
				if chi < best_chi:
					best_i1 = i1
					best_i2 = i2
					best_chi = chi
					
				#if abs(a) < 100 and abs(b-1.0) < 0.5:
				#	print i1, i2, chi
				
		# Calculate association of literature to source peaks
		# for the best match
		self.fAllPeakAssocs = []
		self.fPeakAssocs = []
		distances = []
			
		x1 = self.fPeaks[best_i1]
		x2 = self.fPeaks[best_i2]
		p1 = (e2 - e1) / (x2 - x1)
		p0 = e1 - p1 * x1
		
		for i in range(0, len(self.fRefPeaks)):
			lit_pos = (self.fRefPeaks[i] - p0) / p1
			i_n = self.FindNearest(lit_pos)
			dist = abs(self.fPeaks[i_n] - lit_pos)
			self.fAllPeakAssocs.append(i_n)
			self.fPeakAssocs.append(i_n)
			distances.append([i, dist])
			
		distances.sort(None, lambda l: l[1], False)
		
		self.fPeakAssocs[distances[-1][0]] = None
		self.fPeakAssocs[distances[-2][0]] = None
		self.fPeakAssocs[distances[-3][0]] = None
		
	def ShowPeakAssocs(self):
		for i in range(0, len(self.fRefPeaks)):
			print "%10.2f %10.2f" % (self.fRefPeaks[i], self.fPeaks[self.fAllPeakAssocs[i]])


# Do a polynomial fit, i.e. E = a + b*x + c*x**2 + d*x**3
def fit_poly(positions, energies):
	linfit = ROOT.TLinearFitter(1, "pol3", "")
	v = array('d', [0.0])
		
	for (x,y) in zip(positions, energies):
		v[0] = x
		linfit.AddPoint(v,y)
		
	linfit.Eval()
	
	return map(lambda i: linfit.GetParameter(i), [0,1,2,3])
	
	
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
	excess = len(peaks) - len(src_energies)
		
	e1 = src_energies[0]
	e2 = src_energies[1]

	# (i1, i2) is the index of the candidate for the
	# (first, second) literature peak
	for i1 in range(0, excess):
		for i2 in range(i1+1, excess+1):
			x1 = peaks[i1]
			x2 = peaks[i2]
			
			# Do a linear calibration
			b = (e2 - e1) / (x2 - x1)
			a = e1 - b * x1
			
			# Calculate squared sum of position deviations
			chi = 0.0
			for i in range(2, len(src_energies)):
				src_pos = (src_energies[i] - a) / b
				i_n = find_nearest(peaks, src_pos)
				dist = abs(peaks[i_n] - src_pos)
				chi += dist**2
				
			# print "%d %d %.2f %.2f %.2f" % (i1, i2, a, b, chi)
				
			if chi < best_chi:
				best_i1 = i1
				best_i2 = i2
				best_chi = chi
			
	# Calculate association of literature to source peaks
	# for the best match
	assoc_peaks = []
	assoc_peaks.append(best_i1)
	assoc_peaks.append(best_i2)
	
	x1 = peaks[best_i1]
	x2 = peaks[best_i2]
	b = (e2 - e1) / (x2 - x1)
	a = e1 - b * x1
			
	for i in range(2, len(src_energies)):
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

def test():
	#viewer = ROOT.GSViewer()
	hist = SpecReader().Get("specs/ge11.0072", "spec", "spec")
	
	#viewer.LoadSpectrum(ROOT.GSSpectrum(hist))

	peaks = [0.0] + find_peaks(hist) + [8192.0]

	peaks.sort()

	fit_peaks = []
	for i in range(1,len(peaks)-1):
		fit = fit_peak(hist, peaks[i], peaks[i-1], peaks[i+1])
		if abs(fit[0] - peaks[i]) < 5.0:
			fit_peaks.append(fit)
		
	assoc_peaks = match_peaks(map(lambda x: x[0], fit_peaks), src_energies)

	polypar = fit_poly(map(lambda i: fit_peaks[i][0], assoc_peaks), src_energies)

	print "  FitPos   CalcEn    LitEn      Vol"

	for i in range(0, len(src_energies)):
		fit_pos = fit_peaks[assoc_peaks[i]][0]
		fit_vol = fit_peaks[assoc_peaks[i]][1]
		print "%8.2f %8.2f %8.2f %8.0f" % (fit_pos, ch2e(fit_pos, polypar), src_energies[i], fit_vol)
	#	viewer.SetMarker(fit_pos)
	
	
	#for i in range(0, len(fit_peaks)):
	#	pos = peaks[i]
	#	fit_pos = fit_peaks[i]
	#	print "%8.2f %8.2f" % (pos, fit_pos)
	
	print ""

	print " ".join(map(lambda x: str(x), polypar))

	f = open("test.cal", "w")
	f.write("\n".join(map(lambda x: str(x), polypar)))
	f.close()


class Debug:
	def __init__(self):
		self.fHist = SpecReader().Get("/mnt/omega/braun/88Zr_angle_singles/0108/ge1.0108", "spec", "spec")
		self.fViewer = ROOT.GSViewer()
		self.fViewport = self.fViewer.GetViewport()
		self.fAC = None
		
		self.DoAutocal()
		self.fAC.ShowPeakAssocs()
		
		self.fViewer.RegisterKeyHandler("debug.KeyHandler")
	
		self.fViewport.AddSpec(self.fHist, 6, True)
		
	def DoAutocal(self):
		self.fAC = Autocal()
	
		self.fAC.FindPeaks(self.fHist)
		self.fAC.MatchPeaks()
		#a.Fit()
		
	def KeyHandler(self, key):
		handled = True
		
		if key == ROOT.kKey_u:
			self.fViewport.Update(True)
		elif key == ROOT.kKey_z:
			self.fViewport.XZoomAroundCursor(2.0)
		elif key == ROOT.kKey_x:
			self.fViewport.XZoomAroundCursor(0.5)
		elif key == ROOT.kKey_l:
			self.fViewport.ToggleLogScale()
		elif key == ROOT.kKey_0:
			self.fViewport.ToBegin()
		elif key == ROOT.kKey_f:
			self.fViewport.ShowAll()
		else:
			handled = False
			
		return handled

debug = Debug()
