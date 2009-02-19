import ROOT
import sys
import math
import os.path
import UserDict

import hdtv.util
from hdtv.window import Window

class ObjectManager(UserDict.DictMixin):
	"""
	The ObjectManager is a kind of dictionary of drawable objects. 

	The Manager keeps track of which objects are currently known to the 
	display and which are visible, active or selected.
	A drawable object must have at least the following functions:
	Draw(), Show(), Remove(), Hide() and __repr__().
	It should also be possible to construct compound objects from more
	elementary objects, as long as these functions are provided. 
	"""
	def __init__(self, window=None):
		if not window:
			self.fWindow = Window()
		else:
			self.fWindow = window
		self.fObjects = dict()
		self.fVisible = set()
		self.fActiveID = None

		# Register hotkeys
		self.fWindow.AddHotkey(ROOT.kKey_PageDown, self.ShowNext)
		self.fWindow.AddHotkey(ROOT.kKey_PageUp, self.ShowPrev)
		self.fWindow.AddHotkey(ROOT.kKey_Home, self.ShowFirst)
		self.fWindow.AddHotkey(ROOT.kKey_End, self.ShowLast)

	
	def __getitem__(self, ID):
		return self.fObjects.__getitem__(ID)


	def __setitem__(self, ID, obj):
		self.fObjects.__setitem__(ID, obj)
		obj.Draw(self.fWindow.fViewport)
		self.fWindow.Expand()
		self.fVisible.add(ID)


	def __delitem__(self, ID):
		self.fObjects[ID].Remove()
		if ID in self.fVisible:
			self.fVisible.discard(ID)
		if ID == self.fActiveID:
			self.fActiveID = None
		self.fObjects.__delitem__(ID)


	def keys(self):
		return self.fObjects.keys()


	def Add(self, obj):
		"""
		Adds an object to the first free index in the managers dict.
		"""
		ID = self.GetFreeID()
		self[ID] = obj
		return ID


	def GetFreeID(self):
		"""
		Finds the first free index in the managers dict
		"""
		# Find a free ID
		ID = 0
		while ID in self.keys():
			ID += 1
		return ID


	def ColorForID(self, ID, satur, value):
		"""
		Returns the color corresponding to a certain spectrum ID. The idea is to maximize the
		hue difference between the spectra shown, without knowing beforehand how many spectra
		there will be and without being able to change the color afterwards (that would confuse
		the user). The saturation and value of the color can be set arbitrarily, for example
		to indicate which spectrum is currently active.
		"""
		# Special case
		if ID==0:
			hue = 0.0
		else:
			p = math.floor(math.log(ID) / math.log(2))
			q = ID - 2**p
			hue = 2**(-p-1) + q*2**(-p)
		(r,g,b) = hdtv.util.HSV2RGB(hue*360., satur, value)
		return ROOT.TColor.GetColor(r,g,b)
	

	def DeleteObjects(self, ids):
		"""
		Delete objects from the manager's dict
		"""
		self.fWindow.fViewport.LockUpdate()
		if isinstance(ids, int):
			ids = [ids]
		for ID in ids:
			try:
				self.__delitem__(ID)
			except KeyError:
				print "Warning: ID %d not found" % ID
		self.fWindow.fViewport.UnlockUpdate()


	def ListObjects(self, args=None):
		"""
		List all objects in a human readable way
		"""
		for (ID, obj) in self.fObjects.iteritems():
			stat = " "
			if ID == self.fActiveID:
				stat += "A"
			else:
				stat += " "
			if ID in self.fVisible:
				stat += "V"
			else:
				stat += " "
			print "%d %s %s" % (ID, stat, obj)
	

	def ActivateObject(self, ID):
		if not ID in self.keys():
			print "Error: No such ID"
			return
		self.fActiveID = ID
		
		
	def GetActiveItem(self):
		"Returns the presently active item"
		if self.fActiveID == None:
			return None
		return self[self.fActiveID]
		
	
	def Refresh(self, ids):
		"""
		Refresh objects with ids
		"""
		for ID in ids:
			self[ID].Refresh()
	
		
	def RefreshAll(self):
		"""
		Refresh all objects
		"""
		for obj in self.fObjects.itervalues():
			obj.Refresh()
			
	
	def RefreshVisible(self):
		"""
		Refresh visible objects
		"""
		self.Refresh(self.fVisible)
	

	def Hide(self, ids):
		"""
		Hide objects from the display
		"""
		self.fWindow.fViewport.LockUpdate()
		# if only one object is given
		if isinstance(ids, int):
			ids = [ids]
		for ID in ids:
			if ID in self.fVisible:
				try:
					self.fObjects[ID].Hide()
					self.fVisible.discard(ID)
				except KeyError:
					print "Warning: ID %d not found" % ID
		self.fWindow.fViewport.UnlockUpdate()


	def HideAll(self):
		"""
		Hide all objects
		"""
		self.Hide(self.keys())


	def Show(self, ids, clear=True):
		"""
		Show objects on the display. 

		If the clear parameter is True, the display is cleared first. 
		Otherwise the objects are shown in addition to the ones, that 
		are already visible.
		"""
		self.fWindow.fViewport.LockUpdate()
		if isinstance(ids, int):
			ids = [ids]
		if clear:
			self.HideAll()
		for ID in ids:
			if ID not in self.fVisible:
				try:
					self.fObjects[ID].Show()
					self.fVisible.add(ID)
				except KeyError:
					print "Warning: ID %d not found" % ID
		self.fWindow.fViewport.UnlockUpdate()
		# self.fWindow.Expand() ?????


	def ShowAll(self):
		"""
		Show all objects on the display
		"""
		self.Show(self.keys(), clear=True)


	def ShowNext(self, nb=1):
		"""
		Show next object (by index)

		With the parameter nb, the user can choose how many new spectra
		there should be displayed.
		"""
		if nb > len(self.fObjects):
			self.ShowAll()
			return
		if len(self.fVisible)==0 or len(self.fVisible)==len(self.fObjects):
			self.ShowFirst(nb)
			return
		ids = self.keys()
		ids.sort()
		index = ids.index(max(self.fVisible))
		ids = ids[index+1:index+nb+1]
		self.Show(ids, clear=True)


	def ShowPrev(self, nb=1):
		"""
		Show previous object (by index)

		With the parameter nb, the user can choose how many new spectra
		there should be displayed.
		"""
		if nb > len(self.fObjects):
			self.ShowAll()
			return
		if len(self.fVisible)==0 or len(self.fVisible)==len(self.fObjects):
			self.ShowLast(nb)
			return
		ids = self.keys()
		ids.sort()
		index = ids.index(min(self.fVisible))
		if nb > index:
			ids = ids[0:index]
		else:
			ids = ids[index-nb:index]
		self.Show(ids, clear=True)


	def ShowFirst(self, nb=1):
		"""
		Show the first nb objects
		"""
		if nb > len(self.fObjects):
			self.ShowAll()
			return
		ids = self.keys()
		ids.sort()
		ids = ids[:nb]
		self.Show(ids, clear=True)


	def ShowLast(self, nb=1):
		"""
		Show the last nb objects
		"""
		if nb > len(self.fObjects):
			self.ShowAll()
			return
		ids = self.keys()
		ids.sort()
		ids = ids[len(ids)-nb:]
		self.Show(ids, clear=True)
