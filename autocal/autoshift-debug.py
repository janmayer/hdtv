import ROOT
from specreader import *
import sys
from diploma import Horus88Zr

from hdtv import *
from libpeaks import *
from autoshift import *

ROOT.TH1.AddDirectory(ROOT.kFALSE)

#global fCurrentSpec, fCurRun, fCurDet, shiftCal, fViewer

class AutoshiftDebug(HDTV):
	def __init__(self):
		HDTV.__init__(self)
		self.experiment = Horus88Zr()
		self.fCurRun = 0
		self.fCurDet = 7
		
		self.fUnshiftCal = ROOT.GSCalibration()
		self.fShiftCal = ROOT.GSCalibration()
		
		self.fSpecID = None
		self.fRefID = None
		
		self.fCanvas = ROOT.TCanvas()
		#self.fFuncGraph = ROOT.TGraph(2)
		#self.fFuncGraph.Draw("AL")
		self.fPeakGraph = None
		self.fCurShift = None
		
	def KeyHandler(self, key):
		if HDTV.KeyHandler(self, key):
			pass
		elif key == ROOT.kKey_Down:
			if self.fCurRun > 0:
				self.fCurRun -= 1
				self.SyncSpec()
		elif key == ROOT.kKey_Up:
	  		if self.fCurRun < len(self.experiment.fGoodRuns) - 1:
	  			self.fCurRun += 1
				self.SyncSpec()
		elif key == ROOT.kKey_i:
			self.PrintAutoshiftInfo()
				
	def SyncTitle(self):
		self.SetTitle("ge%d.%04d" % (self.fCurDet, self.experiment.fGoodRuns[self.fCurRun]))
				
	def SyncRef(self):
		if self.fRefID != None:
			self.fViewport.DeleteSpec(self.fRefID, False)
	
		self.fRefID = self.SpecGet(self.experiment.SpecFile(self.experiment.fRefRun, self.fCurDet),
								   6, False)
		self.fViewport.GetDisplaySpec(self.fRefID).SetCal(self.fUnshiftCal)
		self.fViewport.Update(True)
		self.SyncTitle()
		
	def PrintAutoshiftInfo(self):
		print "*** Autoshift Info for Run %d, Det. %d ***" % \
			(self.experiment.fGoodRuns[self.fCurRun], self.fCurDet)
		print "p0 = %.2f, p1 = %.4f, \chi^2 = %.3f" % \
			(self.fCurShift.p0, self.fCurShift.p1, self.fCurShift.chi2)
		print ""
		for i in range(0, len(self.fCurShift.fRefPeaks)):
			y = self.fCurShift.fRefPeaks[i]
			x = self.fCurShift.fPeaks[self.fCurShift.fAllPeakAssocs[i]]
			
			if self.fCurShift.fPeakAssocs[i]:
				print "*",
			else:
				print " ",
				
			print "%8.2f  %8.2f  %8.2f" % (y, x, x - (y - self.fCurShift.p0) / self.fCurShift.p1)
	
	def SyncSpec(self):
		self.fViewport.DeleteAllMarkers(False)
		
		if self.fSpecID != None:
			self.fViewport.DeleteSpec(self.fSpecID, False)
			
		self.fSpecID = self.SpecGet(self.experiment.SpecFile(self.experiment.fGoodRuns[self.fCurRun],
															 self.fCurDet), 5, False)
		fCurrentSpec = self.fViewport.GetDisplaySpec(self.fSpecID)
		self.SyncTitle()
				
		fCurrentSpec.SetCal(self.fShiftCal)

		autoshift = Autoshift()
		autoshift.ReadRefPeaks("../autocal/ge%d.sig" % self.fCurDet)

		autoshift.FindPeaks(fCurrentSpec.GetSpec())
		autoshift.MatchPeaks()
		autoshift.Fit()
		
		self.fCurShift = autoshift
		
		if not self.fPeakGraph:
			self.fPeakGraph = ROOT.TGraph(len(autoshift.fRefPeaks))
			self.fPeakGraph.Draw("AP")
			self.fPeakGraph.SetMarkerStyle(2)
			
		for i in range(0, len(autoshift.fRefPeaks)):
			y = autoshift.fRefPeaks[i]
			x = autoshift.fPeaks[autoshift.fAllPeakAssocs[i]] - (y - autoshift.p0) / autoshift.p1
			
			self.fPeakGraph.SetPoint(i, x, y)
	
		for i in range(0,len(autoshift.fRefPeaks)):
			self.fViewport.AddMarker(autoshift.fRefPeaks[i], 6)
	
		for i in range(0,len(autoshift.fAllPeakAssocs)):
			pos = autoshift.fPeaks[autoshift.fAllPeakAssocs[i]]
			mid = self.fViewport.AddMarker(pos, 5)
			self.fViewport.GetMarker(mid).SetCal(self.fShiftCal)
			
		#for i in range(0,len(autoshift.fPeaks)):
		#	self.fViewport.AddMarker(autoshift.fPeaks[i], 2)
			
	
		#for pos in a.peaks:
		#	fVp.AddMarker(pos)

		#print "%.2f %.4f" % (a.p0, a.p1)
		
		
		#self.fFuncGraph.SetPoint(0, 0.0, autoshift.p0)
		#self.fFuncGraph.SetPoint(1, 10000.0, autoshift.p0 + 10000.0 * autoshift.p1)
		self.fCanvas.Update()
		
		self.fShiftCal.SetCal(autoshift.p0, autoshift.p1)
		self.fViewport.Update(True)
	

fDebug = AutoshiftDebug()
fDebug.RegisterKeyHandler("fDebug.KeyHandler")
fDebug.SyncRef()
fDebug.SyncSpec()

def go(runNo):
	runID = None

	for i in range(0, len(fDebug.experiment.fGoodRuns)):
		if fDebug.experiment.fGoodRuns[i] == runNo:
			runID = i
			break
			
	if runID:
		fDebug.fCurRun = runID
		fDebug.SyncSpec()
	else:
		print "Warning, run not found."


#unshiftCal = ROOT.GSCalibration()
#shiftCal = ROOT.GSCalibration()

#fRefSpec = s_zr(74, fCurDet, 15)
#fRefSpec.SetCal(unshiftCal)

#load_spec(fRuns[fCurRun])

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

go(98)
