import ROOT

if ROOT.gSystem.Load("../lib/gspec.so") < 0:
	raise RuntimeError, "Library not found (gspec.so)"
