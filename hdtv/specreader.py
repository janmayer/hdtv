import ROOT
import os

class SpecReader:
	def __init__(self):
		path= os.path.dirname(os.path.abspath(__file__))
		if ROOT.gSystem.Load("%s/../lib/mfile-root.so" %path) < 0:
			raise RuntimeError, "Library not found (mfile-root.so)"

	def Get(self, filename, histname, histtitle):
		mhist = ROOT.MFileHist()
		mhist.Open(filename)
		return mhist.ToTH1D(histname, histtitle, 0, 0)
		
	def GetMatrix(self, filename, histname, histtitle):
		mhist = ROOT.MFileHist()
		mhist.Open(filename)
		return mhist.ToTH2D(histname, histtitle, 0)
