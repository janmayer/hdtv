import ROOT
import gspec

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
	
	def UpdatePos(self, viewport, update=True):
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
			if update:
				viewport.Update(True)
		
	def Realize(self, viewport, update=True):
		""" Realize the marker"""
		if self.mid == None:
			addMarker = getattr(viewport, "Add%sMarker" %self.xytype)
			self.mid = addMarker(self.p1, self.color, update)
			
	def Delete(self, viewport, update=True):
		""" delete the marker"""
		if self.mid != None:
			deleteMarker = getattr(viewport, "Delete%sMarker"  % self.xytype)
			deleteMarker(self.mid, update)
			self.mid = None
