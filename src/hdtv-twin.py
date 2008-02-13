from __future__ import with_statement

import ROOT
import math
import atexit
from window import Window, XMarker
from diploma import Horus88Zr

if ROOT.gSystem.Load("../lib/gspec.so") < 0:
	raise RuntimeError, "Library not found (gspec.so)"

class Marker:
	def __init__(self, pos, color=6):
		self.pos = pos
		self.mid = None
		self.color = color
		self.dash = False
		
	def SetPos(self, viewport, pos):
		self.pos = pos
		if self.mid != None:
			viewport.GetXMarker(self.mid).SetPos(pos)
			viewport.Update(True)
			
	def SetDash(self, viewport, dash):
		self.dash = dash
		if self.mid != None:
			viewport.GetXMarker(self.mid).SetDash(self.dash)
			viewport.Update(True)
		
	def Realize(self, viewport, update=True):
		if self.mid == None:
			self.mid = viewport.AddXMarker(self.pos, self.color, update)
			
	def Delete(self, viewport, update=True):
		if self.mid != None:
			viewport.DeleteXMarker(self.mid, update)
			self.mid = None

class TWin(Window):
	def __init__(self):
		Window.__init__(self)
		self.experiment = Horus88Zr()
		self.fCurN = 0
		self.fSpecNames = []
		self.GenSpecNames()
		self.leftMarker = None
		self.rightMarker = None
		self.grabbedMarker = None
		
		self.fMarkers = []
		self.ReadPos()
			
		atexit.register(self.ExitHandler)
			
	def ExitHandler(self):
		with open("twin.dat", "w") as f:
			for markers in self.fMarkers:
				f.write(" ".join(map(lambda m: "%d" % int(m.pos), markers)))
				f.write("\n")
				
		with open("time.win", "w") as f:
			for markers in self.fMarkers:
				if len(markers) == 4:
					markers.sort(None, lambda x: x.pos)
				
					peakArea = int(markers[2].pos - markers[1].pos)
					bg1Area = int(peakArea / 2)
					bg2Area = peakArea - bg1Area
					
					f.write("%d " % (int(markers[0].pos) - bg1Area))
					f.write("%d " % int(markers[0].pos))
					f.write("%d " % int(markers[1].pos))
					f.write("%d " % int(markers[2].pos))
					f.write("%d " % int(markers[3].pos))
					f.write("%d\n" % (int(markers[3].pos) + bg2Area))
				else:
					f.write("200 1000 1200 2800 3000 3800\n")
					print "Warning: defaults used in time.win"
			
	def ReadPos(self):
		try:
			with open("twin.dat") as f:
				for l in f:
					markers = map(lambda x: Marker(int(x)), l.split())
					self.fMarkers.append(markers)
	
		except IOError:
			for i in range(0,120):
				self.fMarkers.append([])
		
	def GenSpecNames(self):
		for i in range(0,16):
			for j in range(i+1,16):
				self.fSpecNames.append("%d/%d" % (i,j))
		
	def SyncSpec(self, step):
		for marker in self.fMarkers[self.fCurN]:
			marker.Delete(self.fViewport, False)
		self.fViewport.DeleteSpec(0, False)
		
		self.fCurN += step
		
		self.SpecGet(self.experiment.TWinFile(self.fCurN), None, False)
		for marker in self.fMarkers[self.fCurN]:
			marker.Realize(self.fViewport, False)	
		
		self.SetTitle(self.fSpecNames[self.fCurN])
		self.UpdateBorders()
		self.fViewport.Update(True)
		
	def UpdateBorders(self):
		if len(self.fMarkers[self.fCurN]) == 4:
			markers = self.fMarkers[self.fCurN]
			markers.sort(None, lambda x: x.pos)
				
			peakArea = int(markers[2].pos - markers[1].pos)
			bg1Area = int(peakArea / 2)
			bg2Area = peakArea - bg1Area
			
			if self.leftMarker:
				self.leftMarker.SetPos(self.fViewport, markers[0].pos - bg1Area)
			else:
				self.leftMarker = Marker(markers[0].pos - bg1Area, 3)
			self.leftMarker.Realize(self.fViewport)
				
			if self.rightMarker:
				self.rightMarker.SetPos(self.fViewport, markers[3].pos + bg2Area)
			else:
				self.rightMarker = Marker(markers[3].pos + bg2Area, 3)
			self.rightMarker.Realize(self.fViewport)
		else:
			if self.leftMarker:
				self.leftMarker.Delete(self.fViewport)
			if self.rightMarker:
				self.rightMarker.Delete(self.fViewport)
						
	def KeyHandler(self, key):
		if Window.KeyHandler(self, key):
			pass
		elif key == ROOT.kKey_m:
			if len(self.fMarkers[self.fCurN]) < 4:
				pos = math.ceil(self.fViewport.GetCursorX() - 0.5)
		  		self.fMarkers[self.fCurN].append(Marker(pos))
		  		self.fMarkers[self.fCurN][-1].Realize(self.fViewport)
		  		self.UpdateBorders()
		  		
		elif key == ROOT.kKey_g:
			if not self.grabbedMarker:
				marker = self.fViewport.FindMarkerNearestCursor()
				if marker >= 0:
					marker >>= 1
					markerObj = filter(lambda m: m.mid == marker, self.fMarkers[self.fCurN])
					if len(markerObj) > 0:
						self.grabbedMarker = markerObj[0]
						self.grabbedMarker.SetDash(self.fViewport, True)
			else:
				pos = math.ceil(self.fViewport.GetCursorX() - 0.5)
				self.grabbedMarker.SetPos(self.fViewport, pos)
				self.grabbedMarker.SetDash(self.fViewport, False)
				self.grabbedMarker = None
				self.UpdateBorders()
	
		elif key == ROOT.kKey_Up:
			if self.fCurN < 119:
				self.SyncSpec(1)
	
		elif key == ROOT.kKey_Down:
			if self.fCurN > 0:
				self.SyncSpec(-1)
		
fTWin = TWin()
fTWin.RegisterKeyHandler("fTWin.KeyHandler")
fTWin.SyncSpec(0)
fTWin.fViewport.ShowAll()
