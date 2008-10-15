import ROOT
import os

class SpecReaderError(Exception):
	pass

class SpecReader:
	def __init__(self):
		self.fHasMFile = False
		self.fHasCracow = False
		self.fDefaultFormat = "mfile"
		
	def EnsureMFile(self):
		if not self.fHasMFile:
			self.fHasMFile = True
			path= os.path.dirname(os.path.abspath(__file__))
			if ROOT.gSystem.Load("%s/../lib/mfile-root.so" %path) < 0:
				raise RuntimeError, "Library not found (mfile-root.so)"
				
	def EnsureCracow(self):
		if not self.fHasCracow:
			self.fHasCracow = True

	def GetSpectrum(self, fname, fmt=None, histname=None, histtitle=None):
		"""
		Reads a histogram from a non-ROOT file. fmt specifies the format.
		The following formats are recognized:
		  * cracow  (Cracow from GSI)
		  * mfile   (use libmfile and attempt autodetection)
		  * any format specifier understood by libmfile
		"""
		if not fmt:
			fmt = self.fDefaultFormat
		if histname == None:
			histname = fname
		if histtitle == None:
			histtitle = fname
	
		if fmt.lower() == 'cracow':
			self.EnsureCracow()
			cio = ROOT.CracowIO()
			hist = cio.GetCracowSpectrum(fname, histname, histtitle)
			if not hist:
				raise SpecReaderError, cio.GetErrorMsg()
			return hist
		else:
			self.EnsureMFile()
			mhist = ROOT.MFileHist()
			if mhist.Open(fname) != ROOT.MFileHist.ERR_SUCCESS:
				raise SpecReaderError, mhist.GetErrorMsg()
			hist = mhist.ToTH1D(histname, histtitle, 0, 0)
			if not hist:
				raise SpecReaderError, mhist.GetErrorMsg()
			return hist
		
	def GetMatrix(self, filename, fmt, histname, histtitle):
		mhist = ROOT.MFileHist()
		mhist.Open(filename)
		return mhist.ToTH2D(histname, histtitle, 0)
		
	def PutSpectrum(self, hist, fname, fmt):
		self.EnsureMFile()
		result = ROOT.MFileHist.WriteTH1(hist, fname, fmt)
		if result != ROOT.MFileHist.ERR_SUCCESS:
			raise SpecReaderError, ROOT.MFileHist.GetErrorMsg(result)
