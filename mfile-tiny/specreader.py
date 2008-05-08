import ROOT

class TextSpecReader:
	def __init__(self, filename):
		self.f = open(filename, 'r')

	def Probe(self):
		probe = True
	
		self.f.seek(64)
		chars = self.f.read(32)
			
		if(len(chars) == 0):
			probe = False
		else:
			for c in chars:
				if not(c.isspace() or c.isdigit() or c in ["+", "-", ".", "\n"]):
					probe = False
					break
			
		return probe
		
	def Close(self):
		self.f.close()
		
	def GetNumBins(self):
		bins = 0
		self.f.seek(0)
		
		for line in self.f:
			if line.strip() != "":
				bins += 1
				
		return bins
		
	def Fill(self, hist):
		# Bin 0 is the underflow bin
	
		n = 1
		self.f.seek(0)
		
		for line in self.f:
			line = line.strip()
			if line != "" and line[0] != "#":
				hist.SetBinContent(n, float(line))
				n += 1
				
class LC2SpecReader:
	def __init__(self, filename):
		if ROOT.gSystem.Load("/home/braun/projects/hdtv/lib/lc2reader.so") < 0:
			raise RuntimeError, "Library not found (lc2reader.so)"
			
		self.reader = ROOT.LC2Reader()
		
		self._handle_error(self.reader.Open(filename))
		
			
	def _handle_error(self, retval):
		if retval == -1:
			raise RuntimeError
		elif retval == -2:
			raise IOError
		elif retval == -3:
			raise MemoryError
			
		return retval
			
	def Probe(self):
		retval = self._handle_error(self.reader.Probe())
		
		if retval == 1:
			return True
		else:
			return False
			
	def Close(self):
		self._handle_error(self.reader.Close())
		
	def GetNumBins(self):
		return self._handle_error(self.reader.GetNumBins())
		
	def GetNumLines(self):
		return self._handle_error(self.reader.GetNumLines())
		
	def Fill(self, hist):
		self._handle_error(self.reader.Fill(hist))
		
	def FillMatrix(self, hist):
		self._handle_error(self.reader.FillMatrix(hist))
		
class SpecReader:
	def __init__(self):
		pass

	def Get(self, filename, histname, histtitle):
		hist = None
	
		for readerClass in [LC2SpecReader, TextSpecReader]:
			reader = readerClass(filename)
			
			if reader.Probe():
				nbins = reader.GetNumBins()
				hist = ROOT.TH1D(histname, histtitle, nbins, -0.5, nbins - 0.5)
				reader.Fill(hist)
				reader.Close()
				ROOT.SetOwnership(hist, True)
				break
			else:
				reader.Close()
		
		return hist
		
	def GetMatrix(self, filename, histname, histtitle):
		hist = None
	
		reader = LC2SpecReader(filename)
			
		if reader.Probe():
			nbins = reader.GetNumBins()
			nlines = reader.GetNumLines()
			hist = ROOT.TH2I(histname, histtitle, nbins, -0.5, nbins - 0.5, nlines, -0.5, nlines - 0.5)
			reader.FillMatrix(hist)
			ROOT.SetOwnership(hist, True)
		
		reader.Close()

		return hist
