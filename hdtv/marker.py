import ROOT
from hdtv.drawable import Drawable

class Marker(Drawable):
	""" 
	Markers in X or in Y direction
	
	Currently there are the following kinds of markers available:
	X: BACKGROUND", "CUT_BG", "REGION", "CUT", "PEAK", "XZOOM
	Y: YZOOM
	"""
	def __init__(self, mtype, p1, color=None):
		Drawable.__init__(self, color)
		self.mtype = mtype
		self.p1 = p1
		self.p2 = None
		# define the xytype of the marker
		if mtype in ["BACKGROUND", "CUT_BG", "REGION", "CUT", "PEAK", "XZOOM"]:
		    self.xytype = "X"
		if mtype in ["YZOOM"]:
		    self.xytype = "Y"
		# define the color
		if color:
			self.color = color
		else: # set to default color
			if mtype in ["BACKGROUND","CUT_BG"]:
				self.color = 11
			elif mtype in ["REGION","CUT"]:
				self.color = 38
			elif mtype in ["PEAK"]:
				self.color = 50
			elif mtype in ["XZOOM", "YZOOM"]:
				self.color = 10
		

	def __str__(self):
		return '%s marker at %s' %(self.mtype, self.p1)
	
		
	def Draw(self, viewport):
		""" 
		Draw the marker
		"""
		# Marker can only be drawn to a single viewport
		if self.fViewport != None:
			raise RuntimeError, "Marker cannot be realized on multiple viewports"
		self.fViewport = viewport
		# Lock updates
		self.fViewport.LockUpdate()
		if self.p2 == None:
			n = 1
			p2 = 0.0
		else:
			n = 2
			p2 = self.p2
		# X or Y?
		if self.xytype == "X":
			constructor = ROOT.HDTV.Display.XMarker
		elif self.xytype == "Y":
			constructor = ROOT.HDTV.Display.YMarker
		self.fDisplayObj = constructor(self.fViewport, n, self.p1, p2, self.color)
		# finally update the viewport
		self.fViewport.UnlockUpdate()


	def UpdatePos(self):
		""" 
		Update the position of the marker
		"""
		if self.fDisplayObj:
			if self.p2:
				self.fDisplayObj.SetN(2)
				self.fDisplayObj.SetPos(self.p1, self.p2)
			else:
				self.fDisplayObj.SetN(1)
				self.fDisplayObj.SetPos(self.p1)


