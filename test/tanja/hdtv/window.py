import ROOT
import math
import os
from specreader import *

class Spectrum:
	def __init__(self, fname=None, hist=None, cal=None):
		self.fname = fname
		self.hist = hist
		self.cal = cal
		self.sid = None
		
	def Realize(self, viewport, update=True):
		if self.sid == None and self.hist != None:
			self.sid = viewport.AddSpec(self.hist, 2, update)
			if self.cal:
				viewport.GetDisplaySpec(self.sid).SetCal(self.cal)
			
	def Delete(self, viewport, update=True):
		if self.sid != None:
			viewport.DeleteSpec(self.sid, update)
			self.sid = None
			
	def E2Ch(self, e):
		if self.cal:
			return self.cal.E2Ch(e)
		else:
			return e
			
	def Ch2E(self, ch):
		if self.cal:
			return self.cal.Ch2E(ch)
		else:
			return ch
		
class XMarker:
	def __init__(self, mtype, e1):
		self.mtype = mtype
		self.e1 = e1
		self.e2 = None
		self.mid = None
		
		if self.mtype == "BACKGROUND" or self.mtype == "CUT_BG":
			self.color = 11
		elif self.mtype == "REGION" or self.mtype == "CUT":
			self.color = 38
		elif self.mtype == "PEAK":
			self.color = 50
		elif self.mtype == "XZOOM":
			self.color = 10
			
	def Realize(self, viewport, update=True):
		if self.mid == None:
			self.mid = viewport.AddXMarker(self.e1, self.color, update)
			
	def UpdatePos(self, viewport):
		if self.mid != None:
			marker = viewport.GetXMarker(self.mid)
			if self.e2 != None:
				marker.SetN(2)
				marker.SetPos(self.e1, self.e2)
			else:
				marker.SetN(1)
				marker.SetPos(self.e1)
			viewport.Update(True)
			
	def Delete(self, viewport, update=True):
		if self.mid != None:
			viewport.DeleteXMarker(self.mid, update)
			self.mid = None
			
class YMarker:
	def __init__(self, mtype, p1):
		self.mtype = mtype
		self.p1 = p1
		self.p2 = None
		self.mid = None
		self.color = 0
		
		if self.mtype == "YZOOM":
			self.color = 10
			
	def Realize(self, viewport, update=True):
		if self.mid == None:
			self.mid = viewport.AddYMarker(self.p1, self.color, update)
			
	def UpdatePos(self, viewport):
		if self.mid != None:
			marker = viewport.GetYMarker(self.mid)
			if self.p2 != None:
				marker.SetN(2)
				marker.SetPos(self.p1, self.p2)
			else:
				marker.SetN(1)
				marker.SetPos(self.p1)
			viewport.Update(True)
			
	def Delete(self, viewport, update=True):
		if self.mid != None:
			viewport.DeleteYMarker(self.mid, update)
			self.mid = None
			
class Fit:
	def __init__(self, peakFunc=None, bgFunc=None, cal=None):
		self.peakFunc = peakFunc
		self.bgFunc = bgFunc
		self.cal = cal
		self.peakFuncId = None
		self.bgFuncId = None
		self.fPeakMarkerIDs = []
		
	def Realize(self, viewport, update=True):
		""" 
		Display the resulting fit 
		"""
		if self.bgFunc and self.bgFuncId == None:
			self.bgFuncId = viewport.AddFunc(self.bgFunc, 25, False)
			if self.cal:
				viewport.GetDisplayFunc(self.bgFuncId).SetCal(self.cal)
		if self.peakFunc and self.peakFuncId == None:
			self.peakFuncId = viewport.AddFunc(self.peakFunc, 10, False)
			if self.cal:
				viewport.GetDisplayFunc(self.peakFuncId).SetCal(self.cal)
		if self.peakFunc and self.fPeakMarkerIDs == []:
			numPeaks = int(self.peakFunc.GetParameter(0))
			for i in range(0, numPeaks):
				pos = ROOT.GSFitter.GetPeakPos(self.peakFunc, i)
				if self.cal:
					pos = self.cal.Ch2E(pos)
					
				mid = viewport.AddXMarker(pos, 50, False)
				self.fPeakMarkerIDs.append(mid)
		
		if update:
			viewport.Update(True)
			
	def Delete(self, viewport, update=True):
		if self.bgFuncId != None:
			viewport.DeleteFunc(self.bgFuncId)
			self.bgFuncId = None
		if self.peakFuncId != None:
			viewport.DeleteFunc(self.peakFuncId)
			self.peakFuncId = None
		for mid in self.fPeakMarkerIDs:
			viewport.DeleteXMarker(mid)
		self.fPeakMarkerIDs = []
			
		if update:
			viewport.Update(True)
			
	def Update(self, viewport):
		self.Delete(False)
		self.Realize()
		
	def Report(self, panel=None):
		"""
		Report the results of a fit to the user either via a fitpanel or 
	    if no panel is defined via stdout.
		"""
		if not self.peakFunc:
			return
	
		text = ""
		func = self.peakFunc
		numPeaks = int(func.GetParameter(0))
		
		# general information
		text += "Chi^2: %.3f\n" % self.peakFunc.GetChisquare()
		text += "Background: %.2f %.4f\n" % (func.GetParameter(1),
											 func.GetParameter(2))
		
		# information for each peak
		for i in range(0, numPeaks):
			# position (uncalibrated or calibrated)
			pos= ROOT.GSFitter.GetPeakPos(func, i)
			if self.cal:
				pos = self.cal.Ch2E(pos)
			# fwhm (uncalibrated or calibrated)
			fwhm = ROOT.GSFitter.GetPeakFWHM(func, i)
			if self.cal:
				fwhm = self.cal.Ch2E(pos+fwhm)-self.cal.Ch2E(pos-fwhm)
			# volume
			vol = ROOT.GSFitter.GetPeakVol(func, i)
			
			# create the output
			text += "%10.3f "  % pos
			text += "%7.3f "  % fwhm
			text += "%8.1f "  % vol
			
			# left tail
			lt = ROOT.GSFitter.GetPeakLT(func, i)
			if lt > 1000:
				text += "None   "
			else:
				text += "%7.3f "  % lt
				
			# right tail
			rt = ROOT.GSFitter.GetPeakRT(func, i)
			if rt > 1000:
				text += "None   "
			else:
				text += "%7.3f "  % rt
		
			text += "\n"
	
		if panel:
			# output to fitpanel 
			panel.SetText(text)
		else:
			# or to stdout
			print text
		
	def GetVolume(self, cor=1.0):
		vol = ROOT.GSFitter.GetPeakVol(self.peakFunc, 0)
		return (vol * cor, math.sqrt(vol) * cor)
		
class View:
	def __init__(self, title=None):
		self.fTitle = title
		self.fSpectra = []
		self.fCurrentFit = None
		self.fMarkers = []
		self.fRealized = False
		
	def AddSpec(self, spec, viewport, update=True):
		self.fSpectra.append(spec)
		if self.fRealized:
			spec.Realize(viewport, update)
			
	def SetCurrentFit(self, fit, viewport, update=True):
		if self.fCurrentFit != None:
			self.fCurrentFit.Delete(viewport)
			self.fCurrentFit = None
			
		self.fCurrentFit = fit
		if self.fRealized:
			self.fCurrentFit.Realize(viewport, update)
	
	def AddMarker(self, marker, viewport, update):
		self.fMarkers.append(marker)
		if self.fRealized:
			marker.Realize(viewport, update)
		
	def Realize(self, viewport, update=True):
		if not self.fRealized:
			for spec in self.fSpectra:
				spec.Realize(viewport, False)
			
			if self.fCurrentFit:
				self.fCurrentFit.Realize(viewport, False)
			
			for marker in self.fMarkers:
				marker.Realize(viewport, False)
				
			if update:
				viewport.Update()
				
			self.fRealized = True
		
	def Delete(self, viewport, update=True):
		if self.fRealized:
			for spec in self.fSpectra:
				spec.Delete(viewport, False)
				
			if self.fCurrentFit:
				self.fCurrentFit.Delete(viewport, False)
				
			for marker in self.fMarkers:
				marker.Delete(viewport, False)
				
			if update:
				viewport.Update()
	
			self.fRealized = False
			

class Window:
	def __init__(self):
		self.fViewer = ROOT.GSViewer()
		self.fViewport = self.fViewer.GetViewport()
		self.fViews = []
		self.fCurViewID = 0
		self.fOverlayView = View()
		#self.fSpectra = {}
		self.fSpecPath = ""
		self.fXZoomMarkers = []
		self.fYZoomMarkers = []
		self.fPendingMarker = None
		self.fCurrentFit = None
		self.fDefaultCal = None
		
		self.fOverlayView.Realize(self.fViewport, False)
		
	def E2Ch(self, e):
		if self.fDefaultCal:
			return self.fDefaultCal.E2Ch(e)
		else:
			return e
			
	def Ch2E(self, ch):
		if self.fDefaultCal:
			return self.fDefaultCal.Ch2E(ch)
		else:
			return ch
				
	def RegisterKeyHandler(self, cmd):
		self.fViewer.RegisterKeyHandler(cmd)
		
	def AddView(self, title=None):
		view = View(title)
		self.fViews.append(view)
		return view
		
	def DeleteAllViews(self, update=True):
		for view in self.fViews:
			view.Delete(self.fViewport, False)
		self.fViews = []
			
		if update:
			self.fViewport.Update(True)
		
	def FileExists(self, fname):
		try:
			os.stat(fname)
			return True
		except OSError:
			return False
			
	def SpecGet(self, fname, view=None, update=True):
		spec = None
	
		if self.FileExists(fname):
			pass
		elif self.fSpecPath and self.FileExists(self.fSpecPath + "/" + fname):
			fname = self.fSpecPath + "/" + fname
		else:
			fname = None
	
		if fname:
			hist = SpecReader().Get(fname, fname, "hist")
			if hist:
				spec = Spectrum(fname, hist, self.fDefaultCal)
				if view:
					view.AddSpec(spec, self.fViewport, update)
				else:
					spec.Realize(self.fViewport, update)
			else:
				print "Error: Invalid spectrum format"
		else:
			print "Error: File not found"
			
		return spec
		
	#def SpecList(self):
	#	if len(self.fSpectra) == 0:
	#	    print "Spectra currently loaded: None"
	#	else:
	#	    print "Spectra currently loaded:"
	#	    for (sid, spec) in self.fSpectra.iteritems():
	#		    print "%d %s" % (sid, spec.fname)
			    
	#def SpecDel(self, sid):
	#	if self.fSpectra.has_key(sid):
	#		self.fViewport.DeleteSpec(sid, True)
	#		del self.fSpectra[sid]
	#	else:
	#		print "WARNING: No spectrum with this id, no action taken."
	
	def SetTitle(self, title):
		self.fViewer.SetWindowName(title)
		
	def PutPairedXMarker(self, mtype, collection, maxnum=None):
		pos = self.fViewport.GetCursorX()
			
		if self.fPendingMarker:
			if self.fPendingMarker.mtype == mtype:
				self.fPendingMarker.e2 = pos
				self.fPendingMarker.UpdatePos(self.fViewport)
				self.fPendingMarker = None
		elif not maxnum or len(collection) < maxnum:
	  		collection.append(XMarker(mtype, pos))
	  		collection[-1].Realize(self.fViewport)
	  		self.fPendingMarker = collection[-1]
	  		
	def PutPairedYMarker(self, mtype, collection, maxnum=None):
		pos = self.fViewport.GetCursorY()
			
		if self.fPendingMarker:
			if self.fPendingMarker.mtype == mtype:
				self.fPendingMarker.p2 = pos
				self.fPendingMarker.UpdatePos(self.fViewport)
				self.fPendingMarker = None
		elif not maxnum or len(collection) < maxnum:
	  		collection.append(YMarker(mtype, pos))
	  		collection[-1].Realize(self.fViewport)
	  		self.fPendingMarker = collection[-1]
	  		
  	def ShowFull(self):
  		if len(self.fXZoomMarkers) == 1:
  			zm = self.fXZoomMarkers[0]
  			self.fViewport.SetOffset(min(zm.e1, zm.e2))
  			self.fViewport.SetXVisibleRegion(abs(zm.e2 - zm.e1))
  			self.fXZoomMarkers[0].Delete(self.fViewport)
  			self.fXZoomMarkers = []
  		else:
  			self.fViewport.ShowAll()
  			
  	def ExpandY(self):
  		if len(self.fYZoomMarkers) == 1:
  			zm = self.fYZoomMarkers[0]
  			self.fViewport.SetYOffset(min(zm.p1, zm.p2))
  			self.fViewport.SetYVisibleRegion(abs(zm.p2 - zm.p1))
  			self.fYZoomMarkers[0].Delete(self.fViewport)
  			self.fYZoomMarkers = []
  		else:
  			self.fViewport.YAutoScaleOnce()
  			
  	def PutXZoomMarker(self):
		self.PutPairedXMarker("XZOOM", self.fXZoomMarkers, 1)
		
	def PutYZoomMarker(self):
		self.PutPairedYMarker("YZOOM", self.fYZoomMarkers, 1)
		
	def ToggleYAutoScale(self):
		self.fViewport.SetYAutoScale(not self.fViewport.GetYAutoScale())
		
	def SetView(self, vid):
		if vid != None and vid >= 0 and vid < len(self.fViews):
			self.fViews[self.fCurViewID].Delete(self.fViewport, False)
			self.fCurViewID = vid
			self.fViews[self.fCurViewID].Realize(self.fViewport, True)
			if self.fViews[self.fCurViewID].fTitle:
				self.SetTitle(self.fViews[self.fCurViewID].fTitle)
					
	def KeyHandler(self, key):
		handled = True
		
		if key == ROOT.kKey_u:
			self.fViewport.Update(True)
		elif key == ROOT.kKey_z:
			self.fViewport.XZoomAroundCursor(2.0)
		elif key == ROOT.kKey_x:
			self.fViewport.XZoomAroundCursor(0.5)
		elif key == ROOT.kKey_l:
			self.fViewport.ToggleLogScale()
		elif key == ROOT.kKey_0:
			self.fViewport.ToBegin()
		elif key == ROOT.kKey_Space:
			self.PutXZoomMarker()
		elif key == ROOT.kKey_f:
			self.ShowFull()
		elif key == ROOT.kKey_w:
			self.fViewport.ShiftYOffset(0.1)
		elif key == ROOT.kKey_s:
			self.fViewport.ShiftYOffset(-0.1)
		elif key == ROOT.kKey_Z:
			self.fViewport.YZoomAroundCursor(2.0)
		elif key == ROOT.kKey_X:
			self.fViewport.YZoomAroundCursor(0.5)
		elif key == ROOT.kKey_y:
			self.PutYZoomMarker()
		elif key == ROOT.kKey_e:
			self.ExpandY()
		elif key == ROOT.kKey_a:
			self.ToggleYAutoScale()
		elif key == ROOT.kKey_PageUp:
			self.SetView(self.fCurViewID + 1)
		elif key == ROOT.kKey_PageDown:
			self.SetView(self.fCurViewID - 1)
		else:
			handled = False
			
		return handled
