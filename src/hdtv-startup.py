import ROOT
from specreader import *
import sys
from diploma import Horus88Zr

from libpeaks import *
from autoshift import *

ROOT.TH1.AddDirectory(ROOT.kFALSE)

global fCurrentSpec, fCurRun, fCurDet, shiftCal, fViewer

if ROOT.gSystem.Load("../lib/gspec.so") < 0:
	raise RuntimeError, "Library not found (gspec.so)"
	
fViewer = ROOT.GSViewer()
fVp = fViewer.GetViewport()
fViewer.RegisterKeyHandler("key_handler")
fCurRun = 1
fCurDet = 15

experiment = Horus88Zr()
fRuns = experiment.fGoodRuns

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
	
def print_info(marker_id):
	marker_id >>= 1
	peak = None

	for _group in fList.groups:
		for _peak in _group.peaks:
			if _peak.marker_id == marker_id:
				peak = _peak
				break
		if peak:
			break
			
	if peak:
		print "%.6f %.2f %.0f %.2f" % (peak.pos(), peak.fwhm(), peak.vol(), peak.group.func.GetChisquare())


def s_get(fname, color=5):
	global fViewer

	hist = SpecReader().Get(fname, fname, "hist")
	spec_id = fVp.AddSpec(hist, color)
	#fVp.ShowAll()
	fViewer.SetWindowName(fname)
	return fVp.GetDisplaySpec(spec_id)
	
def s_zr(n, det, color=5):
	return s_get("/mnt/omega/braun/88Zr_angle_singles/%04d/ge%d.%04d" % (n, det, n), color)
	
def load_spec(curRun):
	global fCurrentSpec, shiftCal, fCurDet
	
	fCurrentSpec = s_zr(curRun, fCurDet)
	fCurrentSpec.SetCal(shiftCal)

	a = Autoshift()
	a.read_lit_energies("../autocal/ge%d.sig" % fCurDet)

	a.find_peaks(fCurrentSpec.GetSpec())
	a.match_peaks()
	a.fit()
	
	for i in range(0,len(a.lit_energies)):
		fVp.AddMarker(a.lit_energies[i], 2)
	
	for i in range(0,len(a.assoc_peaks)):
		fVp.AddMarker(a.peaks[a.assoc_peaks[i]], 3)
	
	#for pos in a.peaks:
	#	fVp.AddMarker(pos)

	print "%.2f %.4f" % (a.p0, a.p1)

	#shiftCal.SetCal(a.p0, a.p1)
	fVp.Update()
	
def key_handler(key):
	global fCurRun, fCurrentSpec

	if key == ROOT.kKey_u:
	  fVp.Update(True)
	elif key == ROOT.kKey_i:
	  print_info(fVp.FindMarkerNearestCursor())
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
	elif key == ROOT.kKey_Left:
	  if fCurRun > 1:
	    fCurRun -= 1
	    fVp.DeleteSpec(1)
	    load_spec(fRuns[fCurRun])
	elif key == ROOT.kKey_Right:
	  if fCurRun < len(fRuns) - 1:
	    fCurRun += 1
	    fVp.DeleteSpec(1)
	    load_spec(fRuns[fCurRun])

print "Welcome to HDTV!"

unshiftCal = ROOT.GSCalibration()
shiftCal = ROOT.GSCalibration()

fRefSpec = s_zr(74, fCurDet, 15)
fRefSpec.SetCal(unshiftCal)

load_spec(fRuns[fCurRun])

#fCurrentSpec = s_zr(26,8)

#fList = PeakList()
#fList.fit(fCurrentSpec.GetSpec())
# fList.reject_bad_groups(2000.0, 15.0)

#for group in fList.groups:
#	fVp.AddFunc(group.func, 10)
	
#	for peak in group.peaks:
#		peak.marker_id = fVp.AddMarker(peak.pos())

#if len(sys.argv) > 1:
#	s_get(sys.argv[1])


