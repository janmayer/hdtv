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
		C++ Sisplay code and call its draw function.
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
		Remove the object
		"""
		if not self.fViewport:
			return

		# Delete this object
		self.fDisplayObj.Remove()
		self.fDisplayObj = None

		# finally remove the viewport from this object
		self.fViewport = None


	def Show(self):
		"""
		Show the object
		"""
		self.fDisplayObj.Show()


	def Hide(self):
		"""
		Hide the object
		"""
		self.fDisplayObj.Hide()


	def SetColor(self, color):
		"""
		set color
		"""
		if color:
			self.fColor = color
		# update the display if needed
		if self.fDisplayObj != None:
			self.fDisplayObj.SetColor(color)

