import ROOT
import math

class Peak:
	def __init__(self):
		# f(x) = [0] * exp(-0.5 * ((x - [1]) / [2])**2)
	
		self.p0 = 0.0
		self.p1 = 0.0
		self.p2 = 0.0
		
		self.group = None
		self.marker_id = None
		
	def pos(self):
		return self.p1
		
	def vol(self):
		return math.sqrt(2.0 * math.pi) * self.p0 * self.p2
		
	def fwhm(self):
		return 2.0 * math.sqrt(2.0 * math.log(2.0)) * self.p2
		
class PeakGroup:
	def __init__(self):
		self.peaks = []
		self.bg0 = 0.0
		self.func = None
		
	def add_peak(self, peak):
		peak.group = self
		self.peaks.append(peak)
		
	def _fit_peaks(self, hist, pos_list):
		left_end = min(pos_list) - 15
		right_end = max(pos_list) + 15
		cts_min = hist.GetBinContent(int(right_end))
		
		# Find minimum in range as background estimate
		for ch in range(int(left_end), int(right_end)):
			cts = hist.GetBinContent(ch)
		
			if cts < cts_min:
				cts_min = hist.GetBinContent(ch)
		
		# Generate fit function
		n = 1
		func_str = "[0]"
		
		for pos in pos_list:
			func_str += "+gaus(%d)" % n
			n += 3
				
		func = ROOT.TF1("func", func_str, left_end, right_end)
		func.SetParameter(0, cts_min)
		
		# Estimate peak parameters
		n = 1
		for pos in pos_list:
			ctr_ch = int(pos)
			cts = hist.GetBinContent(ctr_ch)
			
			func.SetParameter(n, cts - cts_min)
			func.SetParameter(n+1, pos)
			func.SetParameter(n+2, 3.0)
			
			n += 3
		
		# Do the fit
		hist.Fit(func, "RQN")
				
		# Save the fit values
		self.bg0 = func.GetParameter(0)
		
		n = 1
		for i in range(0, len(pos_list)):
			peak = Peak()
			peak.p0 = func.GetParameter(n)
			peak.p1 = func.GetParameter(n+1)
			peak.p2 = func.GetParameter(n+2)
			self.add_peak(peak)
			n += 3
	
		# self.func = func
		ROOT.SetOwnership(func, True)
			
class PeakList:
	def __init__(self):
		self.groups = []
				
	def fit(self, hist):
		raw_pos = self._find_peaks(hist)
		
		for pos_group in raw_pos:
			group = PeakGroup()
			group._fit_peaks(hist, pos_group)
			self.groups.append(group)
			
		return raw_pos
		
	def reject_bad_groups(self, max_chi2, max_fwhm):
		accepted = []
		
		for group in self.groups:
			if group.func.GetChisquare() <= max_chi2:
				ok = True
				for peak in group.peaks:
					if peak.fwhm() > max_fwhm:
						ok = False
						break
				if ok:
					accepted.append(group)
				
		self.groups = accepted
		
	def peak_list(self):
		peaks = []
		
		for group in self.groups:
			for peak in group.peaks:
				peaks.append(peak)
				
		return peaks
		
	def peak_list_by_pos(self):
		peaks = self.peak_list()
		peaks.sort(None, lambda x: x.p1)
		return peaks
		
	def peak_list_by_vol(self):
		peaks = self.peak_list()
		peaks.sort(None, lambda x: x.p0 * x.p2, True)
		return peaks
		
	def add_group(self):
		self.groups.append(PeakGroup())
		return self.groups[len(self.groups)-1]
		
	def _find_peaks(self, hist):	
		# Invoke ROOT's peak finder
		spec = ROOT.TSpectrum(256)
		npk = spec.Search(hist, 2.0, "goff", 0.01)
		
		if npk < 30:
			npk = spec.Search(hist, 2.0, "goff", 0.005)	
		
		posx = spec.GetPositionX()
		positions = []
		
		# Copy peaks to a python list
		# (otherwise, things like len() won't work)
		for i in range(0, npk):
			positions.append(posx[i])
			
		# Group peaks close together
		positions.sort()
		n_positions = len(positions)
	
		groups = [[]]
		g = 0
		
		groups[g] = []
		groups[g].append(positions[0])
		
		for i in range(1, n_positions):
			if (positions[i] - positions[i-1]) > 20.0:
				g += 1
				groups.append([])
			groups[g].append(positions[i])
		
		return groups

