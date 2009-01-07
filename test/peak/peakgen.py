#!/usr/bin/python
# Infrastructure for generation of artificial spectra
from __future__ import division
import math
import ROOT   # needed for TMath::Erf()

class PolyBg:
	"Polynomial background"
	def __init__(self, coeff):
		self.coeff = coeff
		
	def value(self, x):
		y = 0.0
		for c in reversed(self.coeff):
			y = y*x + c
		return y

class TheuerkaufPeak:
	"Classic TV peak (a.k.a. Theuerkauf peak)"
	def __init__(self, pos, vol, fwhm, tl=None, tr=None, sh=None, sw=None):
		self.pos = pos
		self.sigma = fwhm / (2 * math.sqrt(2 * math.log(2)))
		self.tl = tl
		self.tr = tr
		self.sh = sh
		self.sw = sw
		
		# Calculate normalization
		# Contribution from left tail and left half of truncated Gaussian
		if self.tl:
			norm = self.sigma**2/self.tl * math.exp(-self.tl**2/(2*self.sigma**2))
			norm += math.sqrt(math.pi/2)*self.sigma*ROOT.TMath.Erf(self.tl/(math.sqrt(2)*self.sigma))
		else:
			norm = math.sqrt(math.pi/2)*self.sigma
			
		# Contribution from right tail and right half of truncated Gaussian
		if self.tr:
			norm += self.sigma**2/self.tr * math.exp(-self.tr**2/(2*self.sigma**2))
			norm += math.sqrt(math.pi/2)*self.sigma*ROOT.TMath.Erf(self.tr/(math.sqrt(2)*self.sigma))
		else:
			norm += math.sqrt(math.pi/2)*self.sigma
			
		# Calculate amplitude
		self.amp = vol / norm
		
	def step(self, x):
		if self.sw != None and self.sh != None:
			dx = x - self.pos
			_y = math.pi/2. + math.atan(self.sw*dx/(math.sqrt(2)*self.sigma))
			return self.sh * _y
		else:
			return 0.0
		
	def value(self, x):
		dx = x - self.pos
		if self.tl != None and dx < -self.tl:
			_y = self.tl / (self.sigma**2) * (dx + self.tl/2)
		elif self.tr != None and dx > self.tr:
			_y = -self.tr / (self.sigma**2) * (dx - self.tr/2)
		else:
			_y = -(dx**2)/(2*self.sigma**2)
			
		return self.amp * math.exp(_y) + self.step(x)
		
class EEPeak:
	"Electron-electron scattering peak"
	def __init__(self, pos, amp, sigma1, sigma2, eta, gamma):
		self.pos = pos
		self.amp = amp
		self.sigma1 = sigma1
		self.sigma2 = sigma2
		self.eta = eta
		self.gamma = gamma
		
	def value(self, x):
		dx = x - self.pos
		if dx <= 0:
			_y = math.exp(-math.log(2) * dx**2 / self.sigma1**2)
		elif dx <= self.eta * self.sigma2:
			_y = math.exp(-math.log(2) * dx**2 / self.sigma2**2)
		else:
			B = (self.sigma2*self.gamma - 2.*self.sigma2*self.eta**2*math.log(2))
			B /= 2.*self.eta*math.log(2)
			A = 2**(-self.eta**2) * (self.sigma2*self.eta + B)**self.gamma
			_y = A / (B + dx)**self.gamma
			
		return _y * self.amp

class Spectrum:
	def __init__(self):
		self.background = None
		self.peaks = []
		
	def value(self, x):
		y = 0.
		
		if self.background:
			y += self.background.value(x)
		
		for peak in self.peaks:
			y += peak.value(x)
			
		return y
	
	def write(self, fname, channels):
		f = open(fname, "w")
	
		for x in channels:
			f.write("%f\n" % self.value(x))
			
		f.close()
		
spec = Spectrum()
# spec.background = PolyBg([2.0, 0.01])
spec.peaks.append(TheuerkaufPeak(500, 3000.0, 10.0, None, None, 20.0, 1.0))
spec.peaks.append(TheuerkaufPeak(600, 1000.0, 10.0, None, None, 10.0, 1.0))
# spec.peaks.append(EEPeak(300, 100, 4.5, 6.0, 1.5, 0.7))
# spec.peaks.append(EEPeak(400, 30, 4.5, 6.0, 1.5, 0.7))

spec.write("test.asc", xrange(0, 1024))

