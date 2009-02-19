import ROOT
import os
import hdtv.dlmgr
from hdtv.color import *

hdtv.dlmgr.LoadLibrary("display")

class Drawable:
	def __init__(self, color=None):
		self.fViewport = None
		self.fDisplayObj = None
		self.fColor = color

	def __str__(self):
		return 'drawable object'

	def Draw(self, viewport):
		"""
		This function must create the appropriate object from the underlying
		C++ display code and call its draw function.
		Attention: Unlike the Display object of the underlying implementation,
		python objects can only be drawn on a single viewport
		"""
		pass
		
	def Refresh(self):
		"""
		Refresh the objects data (e.g. reload a Spectrum from disk)
		"""
		pass

	def Remove(self):
		"""
		Remove the object (or objects if fDisplayObj is a list)
		"""
		if not self.fViewport:
			return
		self.fViewport.LockUpdate()
		if not isinstance(self.fDisplayObj,list):
			self.fDisplayObj= [self.fDisplayObj]
		for i in self.fDisplayObj:
			# Delete this object
			i.Remove()
		self.fDisplayObj = None
		self.fViewport.UnlockUpdate()
		# finally remove the viewport from this object
		self.fViewport = None


	def Show(self):
		"""
		Show the object (or objects if fDisplayObj is a list)
		"""
		self.fViewport.LockUpdate()
		if not isinstance(self.fDisplayObj,list):
			self.fDisplayObj= [self.fDisplayObj]
		for i in self.fDisplayObj:
			i.Show()
		self.fViewport.UnlockUpdate()
		

	def Hide(self):
		"""
		Hide the object (or objects if fDisplayObj is a list)
		"""
		self.fViewport.LockUpdate()
		if not isinstance(self.fDisplayObj,list):
			self.fDisplayObj= [self.fDisplayObj]
		for i in self.fDisplayObj:
			i.Hide()
		self.fViewport.UnlockUpdate()


	def SetColor(self, color):
		"""
		set color of the object (or objects if fDisplayObj is a list)
		"""
		if color:
			self.fColor = color
		# update the display if needed
		self.fViewport.LockUpdate()
		if not isinstance(self.fDisplayObj,list):
			self.fDisplayObj= [self.fDisplayObj]
		for i in self.fDisplayObj:
			i.SetColor(color)
		self.fViewport.UnlockUpdate()


