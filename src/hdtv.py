import ROOT
from specreader import *

ROOT.TH1.AddDirectory(ROOT.kFALSE)

if ROOT.gSystem.Load("../lib/gspec.so") < 0:
	raise RuntimeError, "Library not found (gspec.so)"
	
class HDTV:
	def __init__(self):
		self.fViewer = ROOT.GSViewer()
		self.fViewport = self.fViewer.GetViewport()
		
	def RegisterKeyHandler(self, cmd):
		self.fViewer.RegisterKeyHandler(cmd)
		
	def SpecGet(self, fname, color=5, update=True):
		hist = SpecReader().Get(fname, fname, "hist")
		return self.fViewport.AddSpec(hist, color, update)
		
	def SetTitle(self, title):
		self.fViewer.SetWindowName(title)
		
	def KeyHandler(self, key):
		handled = True
		
		if key == ROOT.kKey_u:
			self.fViewport.Update(True)
		elif key == ROOT.kKey_z:
			self.fViewport.XZoomAroundCursor(2.0)
		elif key == ROOT.kKey_x:
			self.fViewport.XZoomAroundCursor(0.5)
		elif key == ROOT.kKey_l:
			self.fViewport.ToggleLogScale()
		elif key == ROOT.kKey_0:
			self.fViewport.ToBegin()
		elif key == ROOT.kKey_f:
			self.fViewport.ShowAll()
		else:
			handled = False
			
		return handled
