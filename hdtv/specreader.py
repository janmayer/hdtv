import ROOT
import hdtv.dlmgr

class SpecReaderError(Exception):
	pass

class SpecReader:
	def __init__(self):
		self.fDefaultFormat = "mfile"
		
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
			hdtv.dlmgr.LoadLibrary("cracowio")
			cio = ROOT.CracowIO()
			hist = cio.GetCracowSpectrum(fname, histname, histtitle)
			if not hist:
				raise SpecReaderError, cio.GetErrorMsg()
			return hist
		else:
			hdtv.dlmgr.LoadLibrary("mfile-root")
			mhist = ROOT.MFileHist()

			if fmt.lower() == 'mfile':
				fmt = None
			
			if mhist.Open(fname, fmt) != ROOT.MFileHist.ERR_SUCCESS:
				raise SpecReaderError, mhist.GetErrorMsg()
			hist = mhist.ToTH1D(histname, histtitle, 0, 0)
			if not hist:
				raise SpecReaderError, mhist.GetErrorMsg()
			return hist
		
	def GetMatrix(self, filename, fmt, histname, histtitle):
		hdtv.dlmgr.Loadlibrary("mfile-root")
		mhist = ROOT.MFileHist()
		mhist.Open(filename)
		return mhist.ToTH2D(histname, histtitle, 0)
		
	def WriteSpectrum(self, hist, fname, fmt):
		hdtv.dlmgr.LoadLibrary("mfile-root")
		result = ROOT.MFileHist.WriteTH1(hist, fname, fmt)
		if result != ROOT.MFileHist.ERR_SUCCESS:
			raise SpecReaderError, ROOT.MFileHist.GetErrorMsg(result)
