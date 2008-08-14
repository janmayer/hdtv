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
	
#
# Autocal: automatic extraction of calibration parameters from
#           calibration spectra
#

class Autocal:
	def __init__(self):
		self.fRefPeaks_E = None     # List of *energies* where peaks are expected
		self.fPeaks_Ch = None       # List of *channels* where peaks we found in the histogram
		self.fPeakAssocs = None     # For each reference peak, this list contains
		                            # the index of the histogram peak it was identified with
		
		# Parameters of the fit polynom (limited to linear for now)
		self.p0 = None
		self.p1 = None
		self.chi2 = None
		
	# Sets the list of expected peak energies (reference peaks)
	def SetReferencePeaks(self, refPeaks):
		self.fRefPeaks_E = refPeaks
		
	# Initialises fPeaks_Ch by doing a peak search in the histogram hist
	# FIXME: Optionally, it can reject peak groups that could not be fitted properly
	def FindPeaks(self, hist):
		fList = PeakList()
		fList.fit(hist)
		# fList.reject_bad_groups(2000.0, 15.0)
		self.fPeaks_Ch = map(lambda p: p.pos(), fList.peak_list_by_pos())

	
	# Match the peaks in the spectrum to the reference peaks
	# FIXME: Currently assumes that the first two peaks in the list can be seen
	# FIXME: Specify a number n so that the n peaks that fit worst are ignored
	def MatchPeaks(self):
		if not self.fPeaks_Ch:
			raise RuntimeError, "List of actual peaks not initialized (did you call FindPeaks() ?)"
	
		if not self.fRefPeaks_E or len(self.fRefPeaks_E) < 2:
			raise RuntimeError, "Too few reference peaks given"
			
		if len(self.fPeaks_Ch) < len(self.fRefPeaks_E):
			raise RuntimeError, "Too few peaks found in given histogram"

		best_chi = 1E10
		
		e1 = self.fRefPeaks_E[0]
		e2 = self.fRefPeaks_E[1]
		
		# (i1, i2) is the index of the candidate for the	
		# (first, second) literature peak
		for i1 in range(0, len(self.fPeaks_Ch)):
			for i2 in range(i1 + 1, len(self.fPeaks_Ch)):
				x1 = self.fPeaks_Ch[i1]
				x2 = self.fPeaks_Ch[i2]
				
				# Do a linear calibration: e(x) = p1 * x + p0
				p1 = (e2 - e1) / (x2 - x1)
				p0 = e1 - p1 * x1
					
				# Calculate squared sum of position deviations
				chiList = []
					
				for i in range(0, len(self.fRefPeaks_E)):
					lit_pos = (self.fRefPeaks_E[i] - p0) / p1
					i_n = self.FindNearest(lit_pos)
					dist = abs(self.fPeaks_Ch[i_n] - lit_pos)
					chiList.append(dist**2)
					
				#chiList.sort()
				#chi = sum(chiList[0:-3])
				chi = sum(chiList)
				
				# print "%d %d %.2f %.2f %.2f" % (i1, i2, a, b, chi)
					
				if p1 > 0.1 and p1 < 10 and chi < best_chi:
					best_i1 = i1
					best_i2 = i2
					best_chi = chi
					
				#if abs(a) < 100 and abs(b-1.0) < 0.5:
				#	print i1, i2, chi
				
		# Calculate association of literature to source peaks
		# for the best match
		#self.fAllPeakAssocs = []
		self.fPeakAssocs = []
		#distances = []
			
		x1 = self.fPeaks_Ch[best_i1]
		x2 = self.fPeaks_Ch[best_i2]
		p1 = (e2 - e1) / (x2 - x1)
		p0 = e1 - p1 * x1
		
		for i in range(0, len(self.fRefPeaks_E)):
			lit_pos = (self.fRefPeaks_E[i] - p0) / p1
			i_n = self.FindNearest(lit_pos)
			#dist = abs(self.fPeaks[i_n] - lit_pos)
			#self.fAllPeakAssocs.append(i_n)
			self.fPeakAssocs.append(i_n)
			#distances.append([i, dist])
			
		#distances.sort(None, lambda l: l[1], False)
		
		#self.fPeakAssocs[distances[-1][0]] = None
		#self.fPeakAssocs[distances[-2][0]] = None
		#self.fPeakAssocs[distances[-3][0]] = None
		
	# Use the reference peaks found in the histogram to fit the actual
	# calibration function
	# FIXME: allow degree > 2
	def FitCal(self):
		if not self.fPeakAssocs:
			raise RuntimeError, "No peak association list (did you call MatchPeaks() ?)"
	
		linfit = ROOT.TLinearFitter(1, "hyp1", "")
		v = array('d', [0.0])
			
		for i in range(0, len(self.fPeakAssocs)):
			if self.fPeakAssocs[i] != None:
				ch = self.fPeaks_Ch[self.fPeakAssocs[i]]
				e = self.fRefPeaks_E[i]
				
				v[0] = ch
				linfit.AddPoint(v,e)
					
		linfit.Eval()
	
		self.p0 = linfit.GetParameter(0)
		self.p1 = linfit.GetParameter(1)
		self.chi2 = linfit.GetChisquare()
		
	# Get the (channel, energy) pair corresponding to the ith reference peak
	def GetMatchPair(self, i):
		return (self.fPeaks_Ch[self.fPeakAssocs[i]], self.fRefPeaks_E[i])

	# *** These function are FOR INTERNAL USE ONLY ***
	
	# Find peak closest to a given position
	# Assumes peaks to be a sorted list
	# NB: This implementation is probably not optimal in
	# terms of run time
	def FindNearest(self, pos):
		best = None
		min_dist = 1E10
		self.fPeaks_Ch.append(1E11)
		i = 0
	
		while True:
			dist = abs(self.fPeaks_Ch[i] - pos)
			
			if dist > min_dist:
				break
				
			min_dist = dist
			i += 1
			
		self.fPeaks_Ch.pop()
			
		return (i-1)
		
class AutocalDebug(Autocal):
	def __init__(self):
		Autocal.__init__(self)
		
	def ShowPeakAssocs(self):
		print "Channel    Energy"
	
		for i in range(0, len(self.fRefPeaks_E)):
			print "%10.2f %10.2f" % self.GetMatchPair(i)


# Do a polynomial fit, i.e. E = a + b*x + c*x**2 + d*x**3
def fit_poly(positions, energies):
	linfit = ROOT.TLinearFitter(1, "pol3", "")
	v = array('d', [0.0])
		
	for (x,y) in zip(positions, energies):
		v[0] = x
		linfit.AddPoint(v,y)
		
	linfit.Eval()
	
	return map(lambda i: linfit.GetParameter(i), [0,1,2,3])
	
	
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
		
	

