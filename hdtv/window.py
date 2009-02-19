import ROOT
import hdtv.dlmgr
from hdtv.marker import Marker

from types import *

hdtv.dlmgr.LoadLibrary("display")

class HotkeyList:
	"Class to handle multi-key hotkeys."
	def __init__(self):
		self.fKeyCmds = dict()
		self.fCurNode = self.fKeyCmds
		
	def AddHotkey(self, key, cmd):
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
						raise RuntimeError, "Refusing to overwrite non-matching hotkey"
				except KeyError:
					curNode[k] = dict()
					curNode = curNode[k]
			
			key = key[-1]

		curNode[key] = cmd
		
	def HandleHotkey(self, key):
		"""
		Handles a key press. Returns True if the input was a
		valid hotkey, False if it was not, and None if further
		input is needed (i.e. if the input could be part of a
		multi-key hotkey)
		"""
		try:
			node = self.fCurNode[key]
		except KeyError:
			self.ResetHotkeyState()
			return False
		
		if type(node) == DictType:
			self.fCurNode = node
			return None
		else:
			node()
			self.ResetHotkeyState()
			return True
		
		
	def ResetHotkeyState(self):
		"""
		Reset possible waiting state for a multi-key hotkey.
		"""
		self.fCurNode = self.fKeyCmds
		

class KeyHandler(HotkeyList):
	"""
	Hotkey handler, adding support for a status line (that can be (ab)used as
	a text entry)
	"""
	def __init__(self):
		HotkeyList.__init__(self)
	
		self.fEditMode = False   # Status bar currently used as text entry
		# Modifier keys
		self.MODIFIER_KEYS = (ROOT.kKey_Shift,
                              ROOT.kKey_Control,
                              ROOT.kKey_Meta,
                              ROOT.kKey_Alt,
                              ROOT.kKey_CapsLock,
                              ROOT.kKey_NumLock,
                              ROOT.kKey_ScrollLock)

		# Parent class must provide self.fViewer and self.fViewport!
		
	
	def EnterEditMode(self, prompt, handler):
		"""
		Enter edit mode (mode where the status line is used as a text entry)
		"""
		self.fEditMode = True
		self.fEditStr = ""
		self.fEditPrompt = prompt
		self.fEditHandler = handler
		self.fViewport.SetStatusText(self.fEditPrompt)

		
	def EditKeyHandler(self):
		"""
		Key handler in edit mode
		"""
		if self.fViewer.fKeySym == ROOT.kKey_Backspace:
			self.fEditStr = self.fEditStr[0:-1]
			self.fViewport.SetStatusText(self.fEditPrompt + self.fEditStr)
		elif self.fViewer.fKeySym == ROOT.kKey_Return:
			self.fEditMode = False
			self.fViewport.SetStatusText("")
			self.fEditHandler(self.fEditStr)
		elif self.fViewer.fKeyStr != "":
			self.fEditStr += self.fViewer.fKeyStr
			self.fViewport.SetStatusText(self.fEditPrompt + self.fEditStr)
		else:
			return False
			
		return True
	

	def KeyHandler(self):
		""" 
		Key handler (handles hotkeys and calls EditKeyHandler in edit mode)
		"""
		# Filter unknown and modifier keys
		if self.fViewer.fKeySym in self.MODIFIER_KEYS or \
		   self.fViewer.fKeySym == ROOT.kKey_Unknown:
			return
			
		# ESC aborts
		if self.fViewer.fKeySym == ROOT.kKey_Escape:
			self.ResetHotkeyState()
			self.fEditMode = False
			self.fKeyString = ""
			self.fViewport.SetStatusText("")
			return True
			
		# There are two modes: the ``edit'' mode, in which the status
		# bar is abused as a text entry, and the normal mode, in which
		# the keys act as hotkeys.
		if self.fEditMode:
			handled = self.EditKeyHandler()
		else:
			keyStr = self.fViewer.fKeyStr
		
			if not keyStr:
				keyStr = "<?>"
		
			handled = self.HandleHotkey(self.fViewer.fKeySym)
			
			if handled == None:
				self.fKeyString += keyStr
				self.fViewport.SetStatusText("Command: %s" % self.fKeyString)
			elif handled == False:
				self.fKeyString += keyStr
				self.fViewport.SetStatusText("Invalid hotkey %s" % self.fKeyString)
				self.fKeyString = ""
			else:
				if not self.fEditMode:
					self.fViewport.SetStatusText("")
				self.fKeyString = ""

		return handled



class Window(KeyHandler):
	"""
	Base class of a window object 

	This class provides a basic key handling for zooming and scrolling.
	"""
	def __init__(self):
		KeyHandler.__init__(self)
	
		self.fViewer = ROOT.HDTV.Display.Viewer()
		self.fViewport = self.fViewer.GetViewport()
		
		self.fXZoomMarkers = []
		self.fYZoomMarkers = []

		# Key Handling
		self.fKeyDispatch = ROOT.TPyDispatcher(self.KeyHandler)
		self.fViewer.Connect("KeyPressed()", "TPyDispatcher", 
							 self.fKeyDispatch, "Dispatch()")
		
		self.fKeyString = ""
		self.AddHotkey(ROOT.kKey_u, lambda: self.fViewport.Update())
		# toggle spectrum display
		self.AddHotkey(ROOT.kKey_l, self.fViewport.ToggleLogScale)
		self.AddHotkey(ROOT.kKey_A, self.fViewport.ToggleYAutoScale)
		self.AddHotkey(ROOT.kKey_Exclam, self.fViewport.ToggleUseNorm)
		# x directions
		self.AddHotkey(ROOT.kKey_Space, self.PutXZoomMarker)
		self.AddHotkey(ROOT.kKey_f, self.ExpandX)
		self.AddHotkey(ROOT.kKey_Right, lambda: self.fViewport.ShiftXOffset(0.1))
		self.AddHotkey(ROOT.kKey_Left, lambda: self.fViewport.ShiftXOffset(-0.1))
		self.AddHotkey(ROOT.kKey_1, lambda: self.fViewport.XZoomAroundCursor(2.0))
		self.AddHotkey(ROOT.kKey_0, lambda: self.fViewport.XZoomAroundCursor(0.5))
		# y direction
		self.AddHotkey(ROOT.kKey_h, self.PutYZoomMarker)
		self.AddHotkey(ROOT.kKey_y, self.ExpandY)
		self.AddHotkey(ROOT.kKey_Up, lambda: self.fViewport.ShiftYOffset(0.1))
		self.AddHotkey(ROOT.kKey_Down, lambda: self.fViewport.ShiftYOffset(-0.1))
		self.AddHotkey(ROOT.kKey_Z, lambda: self.fViewport.YZoomAroundCursor(2.0))
		self.AddHotkey(ROOT.kKey_X, lambda: self.fViewport.YZoomAroundCursor(0.5))
		# expand in all directions
		self.AddHotkey(ROOT.kKey_e, self.Expand)

		self.AddHotkey(ROOT.kKey_i, lambda: self.EnterEditMode(prompt="Position: ",
		                                                    handler=self.GoToPosition))

	
	def GoToPosition(self, arg):
		try:
			center = float(arg)
		except ValueError:
			self.fViewport.SetStatusText("Invalid position: %s" % arg)
			return
		
		self.fViewport.SetXVisibleRegion(100.)
		self.fViewport.SetXCenter(center)
	
	
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
  			zm.Remove()
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
		# FIXME: I am not sure, if this belongs here. It maybe better 
		#        to include it into the marker class
		if xy == "X" or xy == "x":
			pos = self.fViewport.GetCursorX()
		elif xy == "Y" or xy == "y":
			pos = self.fViewport.GetCursorY()
		else:
			raise RuntimeError, "Parameter xy must be either x or y"

		if len(collection)>0 and collection[-1].p2==None:
			pending = collection[-1]
			pending.p2 = pos
			pending.Refresh()
		elif maxnum and len(collection)== maxnum:
			pending = collection.pop(0)
			pending.p1 = pos
			pending.p2 = None
			pending.Refresh()
			collection.append(pending)
		else:
			pending = Marker(mtype, pos, color=None)
			collection.append(pending)
			pending.Draw(self.fViewport)
