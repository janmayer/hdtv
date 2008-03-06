#!/usr/bin/python
import ROOT

spec = ROOT.TH2D("test", "test", 1000, -0.5, 99.5, 1000, -0.5, 99.5)

for _x in range(0,1000):
	for _y in range(0,1000):
		spec.SetBinContent(_x, _y, (_x - 50) ** 2 + (_y - 50) ** 2)
		
spec.Draw("COLZ")
