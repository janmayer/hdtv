import ROOT
from specreader import SpecReader

if ROOT.gSystem.Load("mattest.so") < 0:
	raise RuntimeError, "Library not found (mattest.so)"
	
mat = SpecReader().GetMatrix("/home/braun/Diplom/full_test/mat/all/all.mtx", "all.mtx", "all.mtx")
	
viewer = ROOT.MTViewer(400, 400, mat, "mattest")
