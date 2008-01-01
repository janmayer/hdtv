import ROOT
import os
from fitpanel import FitPanel
from specreader import *

ROOT.TH1.AddDirectory(ROOT.kFALSE)

if ROOT.gSystem.Load("../lib/gspec.so") < 0:
	raise RuntimeError, "Library not found (gspec.so)"
	
class Spectrum:
	def __init__(self, fname=None, hist=None, sid=None):
		self.fname = fname
		self.hist = hist
		self.sid = sid
		
class Marker:
	def __init__(self, mtype, e1):
		self.mtype = mtype
		self.e1 = e1
		self.e2 = None
		self.mid = None
		
		if self.mtype == "BACKGROUND":
			self.color = 11
		elif self.mtype == "REGION":
			self.color = 38
		elif self.mtype == "PEAK":
			self.color = 50
		elif self.mtype == "ZOOM":
			self.color = 10
			
	def Realize(self, viewport, update=True):
		if self.mid == None:
			self.mid = viewport.AddMarker(self.e1, self.color, update)
			
	def UpdatePos(self, viewport):
		if self.mid != None:
			marker = viewport.GetMarker(self.mid)
			if self.e2 != None:
				marker.SetN(2)
				marker.SetPos(self.e1, self.e2)
			else:
				marker.SetN(1)
				marker.SetPos(self.e1)
			viewport.Update(True)
			
	def Delete(self, viewport, update=True):
		if self.mid != None:
			viewport.DeleteMarker(self.mid, update)
			self.mid = None
			
class Fit:
	def __init__(self, peakFunc=None, bgFunc=None):
		self.peakFunc = peakFunc
		self.bgFunc = bgFunc
		self.peakFuncId = None
		self.bgFuncId = None
		
	def Realize(self, viewport, update=True):
		if self.bgFunc and self.bgFuncId == None:
			self.bgFuncId = viewport.AddFunc(self.bgFunc, False)
		if self.peakFunc and self.peakFuncId == None:
			self.peakFuncId = viewport.AddFunc(self.peakFunc, False)
		
		if update:
			viewport.Update(True)
			
	def Delete(self, viewport, update=True):
		if self.bgFuncId != None:
			viewport.DeleteFunc(self.bgFuncId)
		if self.peakFuncId != None:
			viewport.DeleteFunc(self.peakFuncId)
			
		if update:
			viewport.Update(True)
			
	def Update(self, viewport):
		self.Delete(False)
		self.Realize()
		
	def Report(self, panel):
		text = ""
		par = self.peakFunc.GetParameter
		numPeaks = int(par(0))
		
		text += "Chi: %8.3f\n" % self.peakFunc.GetChisquare()
		text += "Background: %6.2f %6.4f\n" % (par(1), par(2))
		text += "A pos sigma tl tr\n"
		
		for i in range(0, numPeaks):
			text += "%8.3f "  % (par(5*i + 0 + 3))
			text += "%8.3f "  % (par(5*i + 1 + 3))
			text += "%8.5f "  % (par(5*i + 2 + 3))
			text += "%8.5f "  % (par(5*i + 3 + 3))
			text += "%8.2f\n" % (par(5*i + 4 + 3))
		
		panel.SetText(text)
	
class HDTV:
	def __init__(self):
		self.fViewer = ROOT.GSViewer()
		self.fViewport = self.fViewer.GetViewport()
		self.fSpectra = {}
		self.fSpecPath = ""
		self.fPeakMarkers = []
		self.fRegionMarkers = []
		self.fBgMarkers = []
		self.fZoomMarkers = []
		self.fPendingMarker = None
		self.fCurrentFit = None
		self.fFitPanel = FitPanel()
		
	def RegisterKeyHandler(self, cmd):
		self.fViewer.RegisterKeyHandler(cmd)
		
	def FileExists(self, fname):
		try:
			os.stat(fname)
			return True
		except OSError:
			return False
			
	def Fit(self):
	  	if not self.fPendingMarker and len(self.fRegionMarkers) == 1 and len(self.fPeakMarkers) > 0:
			if self.fCurrentFit:
				self.fCurrentFit.Delete(self.fViewport)
				self.fCurrentFit = None
		  
			fitter = ROOT.GSFitter(self.fRegionMarkers[0].e1, self.fRegionMarkers[0].e2)
			for marker in self.fPeakMarkers:
				fitter.AddPeak(marker.e1)
				
			# Fit left tails
			fitter.SetLeftTails(-1.0)
				
			func = fitter.Fit(self.fSpectra[0].hist)
			
			self.fCurrentFit = Fit(func)
			self.fCurrentFit.Realize(self.fViewport)
			
			if not self.fFitPanel:
				self.fFitPanel = FitPanel()
				
			self.fCurrentFit.Report(self.fFitPanel)
		
	def SpecGet(self, fname, update=True):
		if self.FileExists(fname):
			pass
		elif self.fSpecPath and self.FileExists(self.fSpecPath + "/" + fname):
			fname = self.fSpecPath + "/" + fname
		else:
			fname = None
	
		if fname:
			hist = SpecReader().Get(fname, fname, "hist")
			sid = self.fViewport.AddSpec(hist, len(self.fSpectra) + 2, update)
			self.fSpectra[sid] = Spectrum(fname, hist, sid)
			self.fViewport.ShowAll()
		else:
			print "Error: File not found"
		
	def SpecList(self):
		if len(self.fSpectra) == 0:
		    print "Spectra currently loaded: None"
		else:
		    print "Spectra currently loaded:"
		    for (sid, spec) in self.fSpectra.iteritems():
			    print "%d %s" % (sid, spec.fname)
			    
	def SpecDel(self, sid):
		if self.fSpectra.has_key(sid):
			self.fViewport.DeleteSpec(sid, True)
			del self.fSpectra[sid]
		else:
			print "WARNING: No spectrum with this id, no action taken."
		
	def SetTitle(self, title):
		self.fViewer.SetWindowName(title)
		
	def PutRegionMarker(self):
		self.PutPairedMarker("REGION", self.fRegionMarkers, 1)
			
	def PutBackgroundMarker(self):
		self.PutPairedMarker("BACKGROUND", self.fBgMarkers)
		
	def PutZoomMarker(self):
		self.PutPairedMarker("ZOOM", self.fZoomMarkers, 1)
		
	def PutPairedMarker(self, mtype, collection, maxnum=None):
		pos = self.fViewport.GetCursorX()
			
		if self.fPendingMarker:
			if self.fPendingMarker.mtype == mtype:
				self.fPendingMarker.e2 = pos
				self.fPendingMarker.UpdatePos(self.fViewport)
				self.fPendingMarker = None
		elif not maxnum or len(collection) < maxnum:
	  		collection.append(Marker(mtype, pos))
	  		collection[-1].Realize(self.fViewport)
	  		self.fPendingMarker = collection[-1]
	  		
	def PutPeakMarker(self):
		pos = self.fViewport.GetCursorX()
  		self.fPeakMarkers.append(Marker("PEAK", pos))
  		self.fPeakMarkers[-1].Realize(self.fViewport)
  		
  	def DeleteAllFitMarkers(self):
		for marker in self.fPeakMarkers:
  			marker.Delete(self.fViewport)
		for marker in self.fBgMarkers:
  			marker.Delete(self.fViewport)
  		for marker in self.fRegionMarkers:
  			marker.Delete(self.fViewport)
	  			
  		self.fPendingMarker = None
  		self.fPeakMarkers = []
  		self.fBgMarkers = []
  		self.fRegionMarkers = []
  		
  		if self.fCurrentFit:
			self.fCurrentFit.Delete(self.fViewport)
			self.fCurrentFit = None
  		
  	def ShowFull(self):
  		if len(self.fZoomMarkers) == 1:
  			zm = self.fZoomMarkers[0]
  			self.fViewport.SetOffset(min(zm.e1, zm.e2))
  			self.fViewport.SetXVisibleRegion(abs(zm.e2 - zm.e1))
  			self.fZoomMarkers[0].Delete(self.fViewport)
  			self.fZoomMarkers = []
  		else:
  			self.fViewport.ShowAll()
		
	def KeyHandler(self, key):
		handled = True
		
		if key == ROOT.kKey_u:
			self.fViewport.Update(True)
		elif key == ROOT.kKey_b:
			self.PutBackgroundMarker()
	  	elif key == ROOT.kKey_r:
			self.PutRegionMarker()
	  	elif key == ROOT.kKey_p:
			self.PutPeakMarker()
	  	elif key == ROOT.kKey_Escape:
	  		self.DeleteAllFitMarkers()
	  	elif key == ROOT.kKey_F:
	  		self.Fit()
		elif key == ROOT.kKey_z:
			self.fViewport.XZoomAroundCursor(2.0)
		elif key == ROOT.kKey_x:
			self.fViewport.XZoomAroundCursor(0.5)
		elif key == ROOT.kKey_l:
			self.fViewport.ToggleLogScale()
		elif key == ROOT.kKey_0:
			self.fViewport.ToBegin()
		elif key == ROOT.kKey_Space:
			self.PutZoomMarker()
		elif key == ROOT.kKey_f:
			self.ShowFull()
		else:
			handled = False
			
		return handled
