from autocal import Autocal, AutocalDebug
from specreader import *

global fViewer, fViewport

def KeyHandler(key):
	handled = True
	
	if key == ROOT.kKey_u:
		fViewport.Update(True)
	elif key == ROOT.kKey_z:
		fViewport.XZoomAroundCursor(2.0)
	elif key == ROOT.kKey_x:
		fViewport.XZoomAroundCursor(0.5)
	elif key == ROOT.kKey_l:
		fViewport.ToggleLogScale()
	elif key == ROOT.kKey_0:
		fViewport.ToBegin()
	elif key == ROOT.kKey_f:
		fViewport.ShowAll()
	else:
		handled = False
			
	return handled

def do_inical(sname, det):
	hist = SpecReader().Get(sname, "spec", "spec")
	
	#fViewport.AddSpec(hist, 6, True)
	
	ac = AutocalDebug()
	ac.SetReferencePeaks([186.2, 242.0, 295.2, 351.9, 609.3, 1120.3, 1764.5])
	ac.FindPeaks(hist)
	ac.MatchPeaks()
	
	#for ch in ac.fPeaks_Ch:
	#	fViewport.AddMarker(ch, 5)
	
	(ch1, e1) = ac.GetMatchPair(0)
	(ch2, e2) = ac.GetMatchPair(6)
	
	print "./raene.tv ge%d.sum %.3f %.2f %.3f %.2f" % (det, ch1, e1, ch2, e2)
	#ac.ShowPeakAssocs()
	
#fViewer = ROOT.GSViewer()
#fViewport = fViewer.GetViewport()
#fViewer.RegisterKeyHandler("KeyHandler")

print "#!/bin/bash"

for i in range(0,16):
	do_inical("/mnt/omega/braun/effcal/ge%d.sum" % i, i)


#self.fAC = None
	
#self.DoAutocal()
#self.fAC.ShowPeakAssocs()




