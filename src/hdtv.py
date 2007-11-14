import ROOT
import os
from specreader import *

ROOT.TH1.AddDirectory(ROOT.kFALSE)

if ROOT.gSystem.Load("../lib/gspec.so") < 0:
	raise RuntimeError, "Library not found (gspec.so)"
	
class Spectrum:
	def __init__(self, fname=None, hist=None, sid=None):
		self.fname = fname
		self.hist = hist
		self.sid = sid
		
class Marker:
	def __init__(self, mtype, e1):
		self.mtype = mtype
		self.e1 = e1
		self.e2 = None
		self.mid = None
		
		if self.mtype == "BACKGROUND":
			self.color = 11
		elif self.mtype == "REGION":
			self.color = 38
		elif self.mtype == "PEAK":
			self.color = 50
			
	def DoFit(self):
		pass
		
	def Realize(self, viewport, update=True):
		if self.mid == None:
			self.mid = viewport.AddMarker(self.e1, self.color, update)
			
	def UpdatePos(self, viewport):
		if self.mid != None:
			marker = viewport.GetMarker(self.mid)
			if self.e2 != None:
				marker.SetN(2)
				marker.SetPos(self.e1, self.e2)
			else:
				marker.SetN(1)
				marker.SetPos(self.e1)
			viewport.Update(True)
			
	def Delete(self, viewport, update=True):
		if self.mid != None:
			viewport.DeleteMarker(self.mid, update)
			self.mid = None
	
class HDTV:
	def __init__(self):
		self.fViewer = ROOT.GSViewer()
		self.fViewport = self.fViewer.GetViewport()
		self.fSpectra = {}
		self.fSpecPath = ""
		self.fMarkers = []
		self.fPendingMarker = None
		
	def RegisterKeyHandler(self, cmd):
		self.fViewer.RegisterKeyHandler(cmd)
		
	def FileExists(self, fname):
		try:
			os.stat(fname)
			return True
		except OSError:
			return False
		
	def SpecGet(self, fname, update=True):
		if self.FileExists(fname):
			pass
		elif self.fSpecPath and self.FileExists(self.fSpecPath + "/" + fname):
			fname = self.fSpecPath + "/" + fname
		else:
			fname = None
	
		if fname:
			hist = SpecReader().Get(fname, fname, "hist")
			sid = self.fViewport.AddSpec(hist, len(self.fSpectra) + 2, update)
			self.fSpectra[sid] = Spectrum(fname, hist, sid)
			self.fViewport.ShowAll()
		else:
			print "Error: File not found"
		
	def SpecList(self):
		if len(self.fSpectra) == 0:
		    print "Spectra currently loaded: None"
		else:
		    print "Spectra currently loaded:"
		    for (sid, spec) in self.fSpectra.iteritems():
			    print "%d %s" % (sid, spec.fname)
			    
	def SpecDel(self, sid):
		if self.fSpectra.has_key(sid):
			self.fViewport.DeleteSpec(sid, True)
			del self.fSpectra[sid]
		else:
			print "WARNING: No spectrum with this id, no action taken."
		
	def SetTitle(self, title):
		self.fViewer.SetWindowName(title)
		
	def PutRegionMarker(self, mtype):
		pos = self.fViewport.GetCursorX()
			
		if self.fPendingMarker:
			if self.fPendingMarker.mtype == mtype:
				self.fPendingMarker.e2 = pos
				self.fPendingMarker.UpdatePos(self.fViewport)
				self.fPendingMarker = None
		else:
	  		self.fMarkers.append(Marker(mtype, pos))
	  		self.fMarkers[-1].Realize(self.fViewport)
	  		self.fPendingMarker = self.fMarkers[-1]
		
	def KeyHandler(self, key):
		handled = True
		
		if key == ROOT.kKey_u:
			self.fViewport.Update(True)
		elif key == ROOT.kKey_b:
			self.PutRegionMarker("BACKGROUND")
	  	elif key == ROOT.kKey_r:
			self.PutRegionMarker("REGION")
	  	elif key == ROOT.kKey_p:
			pos = self.fViewport.GetCursorX()
	  		self.fMarkers.append(Marker("PEAK", pos))
	  		self.fMarkers[-1].Realize(self.fViewport)
	  	elif key == ROOT.kKey_Escape:
	  		for marker in self.fMarkers:
	  			marker.Delete(self.fViewport)
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
