from __future__ import with_statement
import math

class WiedenhoeferEff:
	def __init__(self):
		self.fPars = None
		self.fParErrors = None
		
		# Optional correction factor, assumed to be uncorrelated with the other parameters
		self.fF = 1.0
		self.fFErr = 0.0
		
	def eff(self, E):
		if not self.fPars or len(self.fPars) != 5:
			raise ValueError, "Incorrect number of parameters"
		
		(a, b, c, d, e) = self.fPars
		
		return self.fF * a * math.exp(-b * math.log(E - c + d * math.exp(-e*E)))
		
	def effErr(self, E):
		if not self.fPars or len(self.fPars) != 5:
			raise ValueError, "Incorrect number of parameters"
			
		if not self.fParErrors or len(self.fParErrors) != 5:
			raise ValueError, "Incorrect number of parameter errors"
			
		(a, b, c, d, e) = self.fPars
		eff = self.eff(E)
		
		dEff_dP = [0,0,0,0,0]
		dEff_dP[0] = eff / a
		dEff_dP[1] = -eff * math.log(E - c + d * math.exp(-e*E))
		dEff_dP[2] = eff * b / (E - c + d * math.exp(-e*E))
		dEff_dP[3] = -eff * b / (E - c + d * math.exp(-e*E)) * math.exp(-e*E)
		dEff_dP[4] = eff * b / (E - c + d * math.exp(-e*E)) * d * math.exp(-e*E) * e
		
		errSqr = 0.0
		for i in range(0, 5):
			if len(self.fParErrors[i]) != 5:
				raise ValueError, "Incorrect number of parameter errors"
			
			for j in range(0, 5):
				errSqr += dEff_dP[i] * dEff_dP[j] * self.fParErrors[i][j]
				
		errSqr += (eff / self.fF * self.fFErr)**2

		return math.sqrt(errSqr)
		
	def fromfile(self, parfile, covfile=None):
		vals = []
	
		with open(parfile) as f:
			for line in f:
				line = line.strip()
				if line != '':
					vals.append(float(line))
					
		if len(vals) != 5:
			raise RuntimeError, "Incorrect number of parameters found in file"
		self.fPars = vals
		
		if covfile:
			vals = []
			
			with open(covfile) as f:
				for line in f:
					line = line.strip()
					if line != '':
						val_row = map(lambda s: float(s), line.split())
						
						if len(val_row) != 5:
							raise RuntimeError, "Incorrect format of parameter error file"
						vals.append(val_row)
						
			if len(vals) != 5:
				raise RuntimeError, "Incorrect format of parameter error file"
				
			self.fParErrors = vals
