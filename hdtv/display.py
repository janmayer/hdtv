import ROOT
import math
import os
import gspec
from specreader import *

class Spectrum:
	def __init__(self, hist=None, cal=None):
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
		

class Marker:
	""" 
	Markers in X or in Y direction
	
	Currently there are the following kinds of markers available:
	X: BACKGROUND", "CUT_BG", "REGION", "CUT", "PEAK", "XZOOM
	Y: YZOOM
	"""
	def __init__(self, mtype, p1):
		self.mtype = mtype
		self.p1 = p1
		self.p2 = None
		self.mid = None
		self.color = 0
		# define the xytype of the marker
		if mtype in ["BACKGROUND", "CUT_BG", "REGION", "CUT", "PEAK", "XZOOM"]:
		    self.xytype = "X"
		if mtype in ["YZOOM"]:
		    self.xytype = "Y"
		# define the color
		if mtype in ["BACKGROUND","CUT_BG"]:
			self.color = 11
		elif mtype in ["REGION","CUT"]:
			self.color = 38
		elif mtype in ["PEAK"]:
			self.color = 50
		elif mtype in ["XZOOM", "YZOOM"]:
			self.color = 10
			
	def Realize(self, viewport, update=True):
		""" Realize the marker"""
		if self.mid == None:
			addMarker = getattr(viewport, "Add%sMarker" %self.xytype)
			self.mid = addMarker(self.p1, self.color, update)
			
	def UpdatePos(self, viewport):
		""" update the position of the marker"""
		if self.mid != None:
			getMarker = getattr(viewport, "Get%sMarker" % self.xytype)
			marker = getMarker(self.mid)
			if self.p2 != None:
				marker.SetN(2)
				marker.SetPos(self.p1, self.p2)
			else:
				marker.SetN(1)
				marker.SetPos(self.p1)
			viewport.Update(True)
			
	def Delete(self, viewport, update=True):
		""" delete the marker"""
		if self.mid != None:
			deleteMarker = getattr(viewport, "Delete%sMarker"  % self.xytype)
			deleteMarker(self.mid, update)
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
	""" 
	Base class of a View object.
	
	A view is a selection of stuff that can be displayed in a window
	There can be several views in one window. 
	Every view can contain several spectra.
	"""
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
	"""
	Base class of a window object 

	This class provides a default key handling.
	A window can contain several views, which again can contain several windows.
	To change the currently displayed view, use the PAGEUP and the PAGEDOWN keys.
	"""
	def __init__(self):
		self.fViewer = ROOT.GSViewer()
		self.fViewport = self.fViewer.GetViewport()
		self.fViews = []
		self.fCurViewID = -1
		self.fSpecPath = ""
		self.fXZoomMarkers = []
		self.fYZoomMarkers = []
		self.fPendingMarker = None
		self.fCurrentFit = None
		
		self.fKeyDispatch = ROOT.TPyDispatcher(self._KeyHandler)
		self.fViewer.Connect("KeyPressed()", "TPyDispatcher", 
							 self.fKeyDispatch, "Dispatch()")
			
	def _KeyHandler(self):
		self.KeyHandler(self.fViewer.fKeySym)
		
				
	def AddView(self, title=None):
		"""
		Add a view to this window
		"""
		view = View(title)
		self.fViews.append(view)
		return view
		
	def DeleteAllViews(self, update=True):
		"""
		Delete all views
		"""
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
			
	def LoadSpec(self, fname, view=None, cal=None, update=True):
		"""
		Load spectrum from file
		
		This function checks first if the file exists and then calles 
		SpecReader to get the hist. Next it creates a spectrum object 
		with that hist and adds this to the view. If no view is given,
		the current view is used. If there has been no view defined in
		this window so far, a new view is created and used.
		The new spectrum object is returned if everything was successful.
		"""
		# check if file exists
		if self.FileExists(fname):
			pass
		elif self.fSpecPath and self.FileExists(self.fSpecPath + "/" + fname):
			fname = self.fSpecPath + "/" + fname
		else:
			print "Error: File not found"
			return None
		
		# call to SpecReader to get the hist
		hist = SpecReader().Get(fname, fname, "hist")
		if not hist:
			print "Error: Invalid spectrum format"
			return None

		# create spectrum
		spec = Spectrum(hist, cal)
		# figure out to what view this spectrum should belong
		if not view:
		# is there a current view defined?
			if len(self.fViews) == 0:
				# if not: create a new View and add it to the list
				self.fViews.append(View(fname))
				self.fCurViewID=0
			# use the current view
			view = self.fViews[self.fCurViewID]
		# add the spectrum to view
		view.AddSpec(spec, self.fViewport, update)
		# display the view which we have just added a spectrum to
		self.SetView(self.fViews.index(view))
		# return the new spectrum
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
		""" 
		Set title of window
		
		note: this is overwritten by the title of views.
		"""	
		self.fViewer.SetWindowName(title)

		
	def ExpandX(self):
		"""
		expand in X direction
		"""
		self._Expand("X")
		
	def ExpandY(self):
		"""
		expand in Y direction
		"""
		self._Expand("Y")	
		
			
	def Expand(self):
		"""
		exapnd in X and in Y direction
		"""
		self._Expand("X")
		self._Expand("Y")
		
  	
  	def _Expand(self, xytype):
  		"""
  		expand the display to show the region between the zoom markers (X or Y),
		or the full spectrum if not zoom markers are set.
  		"""
  		# check the input
  		if xytype not in ["X","Y"]:
  			print "invalid parameter %s to the private function _expand" % xytype
  			return
  		
  		zoomMarkers = getattr(self,"f%sZoomMarkers" %xytype)
  		if len(zoomMarkers) == 1:
  			zm = zoomMarkers[0] 
  			setOffset = getattr(self.fViewport, "Set%sOffset" % xytype)
  			setOffset(min(zm.p1, zm.p2))
  			setVisibleRegion = getattr(self.fViewport, "Set%sVisibleRegion" % xytype)
  			setVisibleRegion(abs(zm.p2 - zm.p1))
  			zm.Delete(self.fViewport)
  			getattr(self,"f%sZoomMarkers" %xytype).pop()
  		else:
  			if xytype == "X":
  				self.fViewport.ShowAll()
  			elif xytype == "Y":
  	 			self.fViewport.YAutoScaleOnce()

	def PutXZoomMarker(self):
  		"""
  		set a X zoom marker
  		"""
		self._PutPairedMarker("XZOOM", self.fXZoomMarkers, 1)
		
	def PutYZoomMarker(self):
		"""
		set a Y zoom marker
		"""
		self._PutPairedMarker("YZOOM", self.fYZoomMarkers, 1)

	def _PutPairedMarker(self, mtype, collection, maxnum=None):
		"""
		set paired markers (either X or Y direction)
		"""
		if mtype in ['XZOOM']:
			pos = self.fViewport.GetCursorX()
		if mtype in ['YZOOM']:
			pos = self.fViewport.GetCursorY()
			
		if self.fPendingMarker:
			if self.fPendingMarker.mtype == mtype:
				self.fPendingMarker.p2 = pos
				self.fPendingMarker.UpdatePos(self.fViewport)
				self.fPendingMarker = None
		elif not maxnum or len(collection) < maxnum:
	  		collection.append(Marker(mtype, pos))
	  		collection[-1].Realize(self.fViewport)
	  		self.fPendingMarker = collection[-1]
  			
	def ToggleYAutoScale(self):
		"""
		toggle if spectrum should automatically always be zoom to maximum Y value
		"""
		self.fViewport.SetYAutoScale(not self.fViewport.GetYAutoScale())
		
	def SetView(self, vid):
		"""
		define the view, that should be currently displayed
		"""
		if vid >= 0 and vid < len(self.fViews):
			self.fViews[self.fCurViewID].Delete(self.fViewport, False)
			self.fCurViewID = vid
			self.fViews[self.fCurViewID].Realize(self.fViewport, True)
			if self.fViews[self.fCurViewID].fTitle:
				self.SetTitle(self.fViews[self.fCurViewID].fTitle)

		
	def KeyHandler(self, key):
		""" 
		Default Key Handler
		"""
		handled = True
		if key == ROOT.kKey_u:
			self.fViewport.Update(True)
		elif key == ROOT.kKey_z:
			self.fViewport.XZoomAroundCursor(2.0)
		elif key == ROOT.kKey_x:
			self.fViewport.XZoomAroundCursor(0.5)
		elif key == ROOT.kKey_l:
			self.fViewport.ToggleLogScale()
		elif key == ROOT.kKey_a:
			self.ToggleYAutoScale()
		elif key == ROOT.kKey_0:
			self.fViewport.ToBegin()
		elif key == ROOT.kKey_Space:
			self.PutXZoomMarker()
		elif key == ROOT.kKey_y:
			self.ExpandY()
		elif key == ROOT.kKey_f:
			self.ExpandX()
		elif key == ROOT.kKey_h:
			self.PutYZoomMarker()
		elif key == ROOT.kKey_e:
			self.Expand()
		elif key == ROOT.kKey_w:
			self.fViewport.ShiftYOffset(0.1)
		elif key == ROOT.kKey_s:
			self.fViewport.ShiftYOffset(-0.1)
		elif key == ROOT.kKey_Z:
			self.fViewport.YZoomAroundCursor(2.0)
		elif key == ROOT.kKey_X:
			self.fViewport.YZoomAroundCursor(0.5)
		elif key == ROOT.kKey_PageUp:
			self.SetView(self.fCurViewID - 1)
		elif key == ROOT.kKey_PageDown:
			self.SetView(self.fCurViewID + 1)
		else:
			handled = False
			
		return handled
