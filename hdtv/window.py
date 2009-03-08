# -*- coding: utf-8 -*-

# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2009  The HDTV development team (see file AUTHORS)
#
# This file is part of HDTV.
#
# HDTV is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# HDTV is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with HDTV; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import ROOT
import hdtv.dlmgr
import hdtv.options
import config
from hdtv.marker import MarkerCollection

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

		# Parent class must provide self.viewer and self.viewport!
		
	
	def EnterEditMode(self, prompt, handler):
		"""
		Enter edit mode (mode where the status line is used as a text entry)
		"""
		self.fEditMode = True
		self.fEditStr = ""
		self.fEditPrompt = prompt
		self.fEditHandler = handler
		self.viewport.SetStatusText(self.fEditPrompt)

		
	def EditKeyHandler(self):
		"""
		Key handler in edit mode
		"""
		if self.viewer.fKeySym == ROOT.kKey_Backspace:
			self.fEditStr = self.fEditStr[0:-1]
			self.viewport.SetStatusText(self.fEditPrompt + self.fEditStr)
		elif self.viewer.fKeySym == ROOT.kKey_Return:
			self.fEditMode = False
			self.viewport.SetStatusText("")
			self.fEditHandler(self.fEditStr)
		elif self.viewer.fKeyStr != "":
			self.fEditStr += self.viewer.fKeyStr
			self.viewport.SetStatusText(self.fEditPrompt + self.fEditStr)
		else:
			return False
			
		return True
	

	def KeyHandler(self):
		""" 
		Key handler (handles hotkeys and calls EditKeyHandler in edit mode)
		"""
		# Filter unknown and modifier keys
		if self.viewer.fKeySym in self.MODIFIER_KEYS or \
		   self.viewer.fKeySym == ROOT.kKey_Unknown:
			return
			
		# ESC aborts
		if self.viewer.fKeySym == ROOT.kKey_Escape:
			self.ResetHotkeyState()
			self.fEditMode = False
			self.keyString = ""
			self.viewport.SetStatusText("")
			return True
			
		# There are two modes: the ``edit'' mode, in which the status
		# bar is abused as a text entry, and the normal mode, in which
		# the keys act as hotkeys.
		if self.fEditMode:
			handled = self.EditKeyHandler()
		else:
			keyStr = self.viewer.fKeyStr
		
			if not keyStr:
				keyStr = "<?>"
		
			handled = self.HandleHotkey(self.viewer.fKeySym)
			
			if handled == None:
				self.keyString += keyStr
				self.viewport.SetStatusText("Command: %s" % self.keyString)
			elif handled == False:
				self.keyString += keyStr
				self.viewport.SetStatusText("Invalid hotkey %s" % self.keyString)
				self.keyString = ""
			else:
				if not self.fEditMode:
					self.viewport.SetStatusText("")
				self.keyString = ""

		return handled



class Window(KeyHandler):
	"""
	Base class of a window object 

	This class provides a basic key handling for zooming and scrolling.
	"""
	def __init__(self):
		KeyHandler.__init__(self)
	
		self.viewer = ROOT.HDTV.Display.Viewer()
		self.viewport = self.viewer.GetViewport()
		
		self.XZoomMarkers = MarkerCollection("X", paired=True, maxnum=1, color=10)
		self.XZoomMarkers.Draw(self.viewport)
		self.YZoomMarkers = MarkerCollection("Y", paired=True, maxnum=1, color=10)
		self.YZoomMarkers.Draw(self.viewport)

		# Key Handling
		self.keyDispatch = ROOT.TPyDispatcher(self.KeyHandler)
		self.viewer.Connect("KeyPressed()", "TPyDispatcher", 
							 self.keyDispatch, "Dispatch()")
		
		self.keyString = ""
		self.AddHotkey(ROOT.kKey_u, lambda: self.viewport.Update())
		# toggle spectrum display
		self.AddHotkey(ROOT.kKey_l, self.viewport.ToggleLogScale)
		self.AddHotkey(ROOT.kKey_A, self.viewport.ToggleYAutoScale)
		self.AddHotkey(ROOT.kKey_Exclam, self.viewport.ToggleUseNorm)
		# x directions
		self.AddHotkey(ROOT.kKey_Space, self.PutXZoomMarker)
		self.AddHotkey(ROOT.kKey_x, self.ExpandX)
		self.AddHotkey(ROOT.kKey_Right, lambda: self.viewport.ShiftXOffset(0.1))
		self.AddHotkey(ROOT.kKey_Left, lambda: self.viewport.ShiftXOffset(-0.1))
		self.AddHotkey(ROOT.kKey_Greater, lambda: self.viewport.ShiftXOffset(0.1))
		self.AddHotkey(ROOT.kKey_Less, lambda: self.viewport.ShiftXOffset(-0.1))
		self.AddHotkey(ROOT.kKey_Return, lambda: self.viewport.Update(True))
		self.AddHotkey(ROOT.kKey_Bar,lambda: self.viewport.SetXCenter(self.viewport.GetCursorX()))
		self.AddHotkey(ROOT.kKey_1, lambda: self.viewport.XZoomAroundCursor(2.0))
		self.AddHotkey(ROOT.kKey_0, lambda: self.viewport.XZoomAroundCursor(0.5))
		# y direction
		self.AddHotkey(ROOT.kKey_h, self.PutYZoomMarker)
		self.AddHotkey(ROOT.kKey_y, self.ExpandY)
		self.AddHotkey(ROOT.kKey_Up, lambda: self.viewport.ShiftYOffset(0.1))
		self.AddHotkey(ROOT.kKey_Down, lambda: self.viewport.ShiftYOffset(-0.1))
		self.AddHotkey(ROOT.kKey_Z, lambda: self.viewport.YZoomAroundCursor(2.0))
		self.AddHotkey(ROOT.kKey_X, lambda: self.viewport.YZoomAroundCursor(0.5))
		# expand in all directions
		self.AddHotkey(ROOT.kKey_e, self.Expand)

		self.AddHotkey(ROOT.kKey_i, lambda: self.EnterEditMode(prompt="Position: ",
		                                                    handler=self.GoToPosition))


		# Register configuration variables
		opt = hdtv.options.Option(default = self.viewport.GetYMinVisibleRegion(),
                                  parse = lambda(x): float(x),
                                  changeCallback = self.YMinVisibleRegionChanged)
		config.RegisterOption("display.YMinVisibleRegion", opt)
		
	def YMinVisibleRegionChanged(self, opt):
		self.viewport.SetYMinVisibleRegion(opt.Get())
	
	
	def GoToPosition(self, arg):
		try:
			center = float(arg)
		except ValueError:
			self.viewport.SetStatusText("Invalid position: %s" % arg)
			return
		
		self.viewport.SetXVisibleRegion(100.)
		self.viewport.SetXCenter(center)
		

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
  		
  		zoomMarkers = getattr(self,"%sZoomMarkers" %xytype)
  		if len(zoomMarkers) == 1:
  			zm = zoomMarkers[0] 
  			setOffset = getattr(self.viewport, "Set%sOffset" % xytype)
  			setOffset(min(zm.p1, zm.p2))
  			setVisibleRegion = getattr(self.viewport, "Set%sVisibleRegion" % xytype)
  			setVisibleRegion(abs(zm.p2 - zm.p1))
  			zm.Remove()
  			getattr(self,"%sZoomMarkers" %xytype).pop()
  		else:
  			if xytype == "X":
  				self.viewport.ShowAll()
  			elif xytype == "Y":
  	 			self.viewport.YAutoScaleOnce()

	def PutXZoomMarker(self):
  		"""
  		set a X zoom marker
  		"""
  		pos = self.viewport.GetCursorX()
		self.XZoomMarkers.PutMarker(pos)
		
	def PutYZoomMarker(self):
		"""
		set a Y zoom marker
		"""
		pos = self.viewport.GetCursorY()
		self.YZoomMarkers.PutMarker(pos)


