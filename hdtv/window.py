import ROOT
import gspec
from view import View
from marker import Marker

class Window:
	"""
	Base class of a window object 

	This class provides a default key handling.
	A window can contain several views, which again can contain several spectra.
	To change the currently displayed view, use the PAGEUP and the PAGEDOWN keys.
	"""
	def __init__(self):
		self.fViewer = ROOT.GSViewer()
		self.fViewport = self.fViewer.GetViewport()
		self.fViews = []
		self.fCurViewID = -1
		self.fXZoomMarkers = []
		self.fYZoomMarkers = []
		self.fPendingMarker = None
		
		self.fKeyDispatch = ROOT.TPyDispatcher(self._KeyHandler)
		self.fViewer.Connect("KeyPressed()", "TPyDispatcher", 
							 self.fKeyDispatch, "Dispatch()")

	def AddView(self, title=None):
		"""
		Add a view to this window

		As an empty view without any ingredients is not very 
		interesting, we do not update the display. The user should do that,
		with ShowView when everything is ready.
		"""
		view = View(title)
		vid = len(self.fViews)
		self.fViews.append(view)
		return view

	def DelView(self, vid=None):
		"""
		Delete a view from this window
		
		The parameter vid defines which view should be deleted, 
		if no vid is given the current displayed view is deleted.
		"""
		if not vid:
			vid = self.fCurViewID
		if vid >= 0 and vid < len(self.fViews):
			oldview = self.fViews.pop(vid)
			# do some housekeeping, if needed
			if vid >= self.fCurViewID :
				if not len(self.fViews):
					# this has been the only view
					oldview.Delete(True)
					self.fViewer.SetWindowName("gspec")
					self.fCurViewID=-1
				else:
					oldview.Delete(False)
					if vid==0:
						# show the next view if the first one is deleted
						self.fCurViewID = vid
					else:
						# otherwise show the previous view
						self.fCurViewID = vid-1
					# update the display, to show the current view
					self.fViews[self.fCurViewID].Realize(self.fViewport, True)
					# set title of window to the title of the new view
					if self.fViews[self.fCurViewID].fTitle:
						title= self.fViews[self.fCurViewID].fTitle
						self.fViewer.SetWindowName(title)

	def ShowView(self, vid):
		"""
		Diplay a special view 

		This clears the old view and updates the display 
		to show the new one. It also sets the window title to 
		the title of the new view.
		"""
		if vid >= 0 and vid < len(self.fViews):
			# hide old view
			self.fViews[self.fCurViewID].Delete(False)
			# show new view
			self.fCurViewID = vid
			self.fViews[self.fCurViewID].Realize(self.fViewport, True)
			# set title of window to the title of the current view
			if self.fViews[self.fCurViewID].fTitle:
				title= self.fViews[self.fCurViewID].fTitle
				self.fViewer.SetWindowName(title)
			else:
				# the view has not tite, use default title instead
				self.fViewer.SetWindowName("gspec")
	
	def ClearWindow(self):
		""" 
		Delete everything from the window
		"""
		# clear the display
		self.fViews[self.fCurViewID].Delete(True)
		# delete all views
		self.fViews = []
		self.fCurViewID = -1
		# TODO: delete all markers
		
	def ToggleYAutoScale(self):
		"""
		toggle if spectrum should automatically always be zoom to maximum Y value
		"""
		self.fViewport.SetYAutoScale(not self.fViewport.GetYAutoScale())

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
  			
	def _KeyHandler(self):
		self.KeyHandler(self.fViewer.fKeySym)
		
	def KeyHandler(self, key):
		""" 
		Default Key Handler
		"""
		handled = True
		if key == ROOT.kKey_u:
			self.fViewport.Update(True)
		# toggle spectrum display
		elif key == ROOT.kKey_l:
			self.fViewport.ToggleLogScale()
		elif key == ROOT.kKey_a:
			self.ToggleYAutoScale()
		# x directions
		elif key == ROOT.kKey_Space:
			self.PutXZoomMarker()
		elif key == ROOT.kKey_f:
			self.ExpandX()
		elif key == ROOT.kKey_Left:
			self.fViewport.ShiftXOffset(0.1)
		elif key == ROOT.kKey_Right:
			self.fViewport.ShiftXOffset(-0.1)
		elif key == ROOT.kKey_z:
			self.fViewport.XZoomAroundCursor(2.0)
		elif key == ROOT.kKey_x:
			self.fViewport.XZoomAroundCursor(0.5)
		# Y direction
		elif key == ROOT.kKey_h:
			self.PutYZoomMarker()
		elif key == ROOT.kKey_y:
			self.ExpandY()
		elif key == ROOT.kKey_Up:
			self.fViewport.ShiftYOffset(0.1)
		elif key == ROOT.kKey_Down:
			self.fViewport.ShiftYOffset(-0.1)
		elif key == ROOT.kKey_Z:
			self.fViewport.YZoomAroundCursor(2.0)
		elif key == ROOT.kKey_X:
			self.fViewport.YZoomAroundCursor(0.5)
		# expand in all directions
		elif key == ROOT.kKey_e:
			self.Expand()
		# switch between views
		elif key == ROOT.kKey_PageUp:
			self.ShowView(self.fCurViewID - 1)
		elif key == ROOT.kKey_PageDown:
			self.ShowView(self.fCurViewID + 1)
		elif key== ROOT.kKey_Home:
			self.ShowView(0)
		elif key== ROOT.kKey_End:
			self.ShowView(len(self.fViews)-1)
		else:
			handled = False
			
		return handled
