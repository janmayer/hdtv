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
			if mtype in ["BACKGROUND", "CUT_BG"]:
				self.color = 11
			elif mtype in ["REGION", "CUT"]:
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
		if self.viewport:
			if self.viewport == viewport:
				# this marker has already been drawn
				self.Show()
				return
			else:
				# Marker can only be drawn to a single viewport
				raise RuntimeError, "Marker cannot be realized on multiple viewports"
		self.viewport = viewport
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
		self.displayObj = constructor(n, self.p1, p2, self.color)
		self.displayObj.Draw(self.viewport)
		

	def Refresh(self):
		""" 
		Update the position of the marker
		"""
		if self.displayObj:
			if self.p2:
				self.displayObj.SetN(2)
				self.displayObj.SetPos(self.p1, self.p2)
			else:
				self.displayObj.SetN(1)
				self.displayObj.SetPos(self.p1)

	def UpdatePos(self):
		print 'Marker.UpdatePos is deprecated, use Refresh instead.'
		self.Refresh()
