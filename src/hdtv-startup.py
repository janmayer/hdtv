import ROOT
from specreader import *
import sys

from libpeaks import *

global fCurrentSpec

if ROOT.gSystem.Load("../lib/gspec.so") < 0:
	raise RuntimeError, "Library not found (gspec.so)"
	
fViewer = ROOT.GSViewer()
fVp = fViewer.GetViewport()
fViewer.RegisterKeyHandler("key_handler")

def quick_fit(ctr):
	ctr_ch = int(ctr)

	cts_max = 0
	cts_min = 1e10
	ctr = 0
	for ch in range(ctr_ch-5, ctr_ch+5):
		cts = fCurrentSpec.GetBinContent(ch)
		
		if cts > cts_max:
			cts_max = fCurrentSpec.GetBinContent(ch)
			ctr = ch
			
	for ch in range(ctr_ch-20, ctr_ch+20):
		cts = fCurrentSpec.GetBinContent(ch)
		
		if cts < cts_min:
			cts_min = fCurrentSpec.GetBinContent(ch)
			
	fFunc = ROOT.TF1("func", "gaus(0) + [3]", ctr - 20, ctr + 20)
	fFunc.SetParameter(0, cts_max - cts_min)
	fFunc.SetParameter(1, ctr)
	fFunc.SetParameter(2, 3.0)
	fFunc.SetParameter(3, cts_min)
	
	fCurrentSpec.GetSpec().Fit(fFunc, "RQN")
	
	fVp.AddFunc(fFunc, 10)

def s_get(fname):
	hist = SpecReader().Get(fname, fname, "hist")
	spec_id = fVp.AddSpec(hist)
	fVp.ShowAll()
	return fVp.GetDisplaySpec(spec_id)
	
def s_zr(n, det):
	return s_get("/mnt/omega/braun/88Zr_angle_singles/%04d/ge%d.%04d" % (n, det, n))
	
def key_handler(key):
	if key == ROOT.kKey_u:
	  fVp.Update(True)
	elif key == ROOT.kKey_z:
	  fVp.XZoomAroundCursor(2.0)
	elif key == ROOT.kKey_x:
	  fVp.XZoomAroundCursor(0.5)
	elif key == ROOT.kKey_l:
	  fVp.ToggleLogScale()
	elif key == ROOT.kKey_0:
	  fVp.ToBegin()
	elif key == ROOT.kKey_f:
	  fVp.ShowAll()
	elif key == ROOT.kKey_m:
	  fVp.AddMarker(fVp.GetCursorX())
	elif key == ROOT.kKey_q:
	  quick_fit(fVp.GetCursorX())

print "Welcome to HDTV!"

fCurrentSpec = s_zr(8,8)

fList = PeakList()
raw_pos = fList.fit(fCurrentSpec.GetSpec())

for group in raw_pos:
	for pos in group:
		fVp.AddMarker(pos)

for group in fList.groups:
	fVp.AddFunc(group.func, 10)

#if len(sys.argv) > 1:
#	s_get(sys.argv[1])


