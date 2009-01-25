import ROOT

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
		self.fDisplayMarker = None
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
	
	def UpdatePos(self, viewport):
		""" update the position of the marker"""
		if self.fDisplayMarker != None:
			if self.p2 != None:
				self.fDisplayMarker.SetN(2)
				self.fDisplayMarker.SetPos(self.p1, self.p2)
			else:
				self.fDisplayMarker.SetN(1)
				self.fDisplayMarker.SetPos(self.p1)
		
	def Realize(self, viewport):
		""" Realize the marker"""
		if self.fDisplayMarker != None:
			raise RuntimeError, "Marker cannot be realized on multiple viewports"
		
		if self.p2 == None:
			n = 1
			p2 = 0.0
		else:
			n = 2
			p2 = self.p2
		
		if self.xytype == "X":
			constructor = ROOT.HDTV.Display.XMarker
		elif self.xytype == "Y":
			constructor = ROOT.HDTV.Display.YMarker
			
		self.fDisplayMarker = constructor(viewport, n, self.p1, p2, self.color)
			
	def Delete(self):
		"""Delete the marker"""
		del self.fDisplayMarker
		self.fDisplayMarker = None
