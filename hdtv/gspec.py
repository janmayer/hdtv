import ROOT
import os


path= os.path.dirname(os.path.abspath(__file__))
if ROOT.gSystem.Load("%s/../lib/gspec.so" %path) < 0:
	raise RuntimeError, "Library not found (gspec.so)"
