import ROOT
import gspec
from view import View
from marker import Marker

from types import *

class KeyHandler:
	"Class to handle multi-key hotkeys."
	def __init__(self):
		self.fKeyCmds = dict()
		self.fCurNode = self.fKeyCmds
		
	def AddKey(self, key, cmd):
		"""
		Adds a hotkey to the hotkey table. If key is a list,
		it is taken as a multi-key hotkey. The function refuses
		to overwrite definitions that do not match exactly, i.e.
		once you have defined hotkey x, you can no longer define
		the multi-key combination xy (since that would have to
		overwrite x). You can overwrite matching combinations,
		though (i.e. redefine x in the example above).
		"""
		curNode = self.fKeyCmds
		if type(key) == ListType:
			for k in key[0:-1]:
				try:
					curNode = curNode[k]
					if type(curNode) != DictType:
						raise RuntimeError, "Refusing to non-matching hotkey"
				except KeyError:
					curNode[k] = dict()
					curNode = curNode[k]
			
			key = key[-1]

		curNode[key] = cmd
		
	def HandleKey(self, key):
		"""
		Handles a key press. Returns True if the input was a
		valid hotkey, False if it was not, and None if further
		input is needed (i.e. if the input could be part of a
		multi-key hotkey)
		"""
		try:
			node = self.fCurNode[key]
			if type(node) == DictType:
				self.fCurNode = node
				return None
			else:
				node()
				self.Reset()
				return True
		except KeyError:
			self.Reset()
			return False
		
	def Reset(self):
		"""
		Reset possible waiting state for a multi-key hotkey.
		"""
		self.fCurNode = self.fKeyCmds

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
		
		self.fKeyDispatch = ROOT.TPyDispatcher(self.KeyHandler)
		self.fViewer.Connect("KeyPressed()", "TPyDispatcher", 
							 self.fKeyDispatch, "Dispatch()")
		
		self.fKeyString = ""
		self.fKeys = KeyHandler()
		self.fKeys.AddKey(ROOT.kKey_u, lambda: self.fViewport.Update(True))
		# toggle spectrum display
		self.fKeys.AddKey(ROOT.kKey_l, self.fViewport.ToggleLogScale)
		self.fKeys.AddKey(ROOT.kKey_a, self.ToggleYAutoScale)
		# x directions
		self.fKeys.AddKey(ROOT.kKey_Space, self.PutXZoomMarker)
		self.fKeys.AddKey(ROOT.kKey_f, self.ExpandX)
		self.fKeys.AddKey(ROOT.kKey_Greater, lambda: self.fViewport.ShiftXOffset(0.1))
		self.fKeys.AddKey(ROOT.kKey_Less, lambda: self.fViewport.ShiftXOffset(-0.1))
		self.fKeys.AddKey(ROOT.kKey_1, lambda: self.fViewport.XZoomAroundCursor(2.0))
		self.fKeys.AddKey(ROOT.kKey_0, lambda: self.fViewport.XZoomAroundCursor(0.5))
		# Y direction
		self.fKeys.AddKey(ROOT.kKey_h, self.PutYZoomMarker)
		self.fKeys.AddKey(ROOT.kKey_y, self.ExpandY)
		# self.fKeys.AddKey(ROOT.kKey_Up, lambda: self.fViewport.ShiftYOffset(0.1))
		# self.fKeys.AddKey(ROOT.kKey_Down, lambda: self.fViewport.ShiftYOffset(-0.1))
		# self.fKeys.AddKey(ROOT.kKey_Z, lambda: self.fViewport.YZoomAroundCursor(2.0))
		# self.fKeys.AddKey(ROOT.kKey_X, lambda: self.fViewport.YZoomAroundCursor(0.5))
		# expand in all directions
		self.fKeys.AddKey(ROOT.kKey_e, self.Expand)
		# switch between views
		self.fKeys.AddKey(ROOT.kKey_PageUp, lambda: self.ShowView(self.fCurViewID - 1))
		self.fKeys.AddKey(ROOT.kKey_PageDown, lambda: self.ShowView(self.fCurViewID + 1))
		self.fKeys.AddKey(ROOT.kKey_Home, lambda: self.ShowView(0))
		self.fKeys.AddKey(ROOT.kKey_End, lambda: self.ShowView(len(self.fViews)-1))

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
		if no vid is given the currently displayed view is deleted.
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
		Display a special view 

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
		expand in X and in Y direction
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
		self.PutPairedMarker("X", "XZOOM", self.fXZoomMarkers, 1)
		
	def PutYZoomMarker(self):
		"""
		set a Y zoom marker
		"""
		self.PutPairedMarker("Y", "YZOOM", self.fYZoomMarkers, 1)

	def PutPairedMarker(self, xy, mtype, collection, maxnum=None):
		"""
		set paired markers (either X or Y direction)
		"""
		if xy == "X" or xy == "x":
			pos = self.fViewport.GetCursorX()
		elif xy == "Y" or xy == "y":
			pos = self.fViewport.GetCursorY()
		else:
			raise RuntimeError, "Parameter xy must be either x or y"
			
		if self.fPendingMarker:
			if self.fPendingMarker.mtype == mtype:
				self.fPendingMarker.p2 = pos
				self.fPendingMarker.UpdatePos(self.fViewport)
				self.fPendingMarker = None
		elif not maxnum or len(collection) < maxnum:
	  		collection.append(Marker(mtype, pos))
	  		collection[-1].Realize(self.fViewport)
	  		self.fPendingMarker = collection[-1]
  			
	def KeyHandler(self):
		""" 
		Default Key Handler
		"""
		if self.fViewer.fKeySym == ROOT.kKey_Escape:
			self.fKeys.Reset()
			self.fKeyString = ""
			self.fViewport.SetStatusText("")
			return True
			
		# Do not handle keys like <Ctrl>, <Shift>, etc.
		if not self.fViewer.fKeyStr:
			return False
		
		handled = self.fKeys.HandleKey(self.fViewer.fKeySym)
		
		if handled == None:
			self.fKeyString += self.fViewer.fKeyStr
			self.fViewport.SetStatusText("Command: %s" % self.fKeyString)
		elif handled == False:
			self.fKeyString += self.fViewer.fKeyStr
			self.fViewport.SetStatusText("Invalid hotkey %s" % self.fKeyString)
			self.fKeyString = ""
		else:
			self.fViewport.SetStatusText("")
			self.fKeyString = ""

		return handled
