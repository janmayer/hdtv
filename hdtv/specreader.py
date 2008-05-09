import ROOT

class SpecReader:
	def __init__(self):
		if ROOT.gSystem.Load("../lib/mfile-root.so") < 0:
			raise RuntimeError, "Library not found (mfile-root.so)"

	def Get(self, filename, histname, histtitle):
		mhist = ROOT.MFileHist()
		mhist.Open(filename)
		return mhist.ToTH1D(histname, histtitle, 0, 0)
		
	def GetMatrix(self, filename, histname, histtitle):
		return None
