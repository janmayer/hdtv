#!/usr/bin/python
from __future__ import with_statement

import sys
import math
import time
from array import *
from libpeaks import *

import ROOT
from ROOT import std

class Autoshift:
	def __init__(self):
		self.fRefPeaks = None
		self.fPeaks = None
		self.fPeakAssocs = None
		self.fAllPeakAssocs = None
		self.p0 = None
		self.p1 = None
		self.chi2 = None
		
	def ReadRefPeaks(self, fname):
		with open(fname) as f:
			self.fRefPeaks = map(lambda s: float(s), f.read().split())
			
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
					
				chiList.sort()
				chi = sum(chiList[0:-3])
				
				# Prevent degenerate cases
				if abs(p1 - 1.0) > 5.0:
					chi += 10000.0
					
				if abs(p0) > 10000.0:
					chi += 10000.0
				
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

