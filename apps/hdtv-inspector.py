#!/usr/bin/python -i
# -*- coding: utf-8 -*-

from __future__ import with_statement


# set the pythonpath
import sys
sys.path.append("/home/braun/gspec/pylib")

import ROOT
from hdtv import HDTV
from diploma import Horus88Zr

class Inspector(HDTV):
	def __init__(self):
		HDTV.__init__(self)
		self.experiment = Horus88Zr()
		self.cal = [None] * 16
		self.LoadCalibrations()
		self.fSpecIDs = []
		self.fOverviewMode = True
		
		self.fCurRun = 8
		self.fCurDet = 0
		self.fKeyLocked = False
		
	def LoadCalibrations(self):
		for det in range(0, self.experiment.fNumDetectors):
			self.cal[det] = self.LoadCalibration(self.experiment.CalFile(det))
			
	def LoadCalibration(self, fname):
		with open(fname) as f:
			calPoly = map(lambda s: float(s), f.read().split())
			
		if len(calPoly) != 4:
			raise RuntimeError, "Calibration should be a third-order polynomial"
			
		return ROOT.GSCalibration(calPoly[0], calPoly[1], calPoly[2], calPoly[3])
		
	def LoadSpec(self, n, det, color=5, update=True):
		specID = HDTV.LoadSpec(self, self.experiment.SpecFile(n, det), color, False)
		self.fViewport.GetDisplaySpec(specID).SetCal(self.cal[det])
		self.fSpecIDs.append(specID)
		
		if update:
			self.fViewport.Update(True)
		
	def SpecsGet(self, n, update=True):
		for det in range(0, self.experiment.fNumDetectors):
			self.LoadSpec(n, det, det+30, False)
			
		if update:
			self.fViewport.Update(True)
			
	def DeleteAllSpecs(self, update=True):
		for sid in self.fSpecIDs:
			self.fViewport.DeleteSpec(sid, False)
			
		self.fSpecIDs = []
		if update:
			self.fViewport.Update(True)
		
	def SyncSpecs(self):
		self.DeleteAllSpecs(False)
	
		if self.fOverviewMode:
			self.SpecsGet(self.fCurRun)
			self.SetTitle("Overview: Run #%d" % self.fCurRun)
		else:
			self.LoadSpec(self.fCurRun, self.fCurDet)
			self.SetTitle("ge%d: Run #%d" % (self.fCurDet, self.fCurRun))
		
	def KeyHandler(self, key):
		if HDTV.KeyHandler(self, key):
			pass
		elif key == ROOT.kKey_Up:
			self.fCurRun += 1
			self.SyncSpecs()
		elif key == ROOT.kKey_Down:
			self.fCurRun -= 1
			self.SyncSpecs()
		elif key == ROOT.kKey_PageUp:
			self.fCurRun += 10
			self.SyncSpecs()
		elif key == ROOT.kKey_PageDown:
			self.fCurRun -= 10
			self.SyncSpecs()
		elif key == ROOT.kKey_Left:
			if not self.fOverviewMode and self.fCurDet > 0:
				self.fCurDet -= 1
				self.SyncSpecs()
		elif key == ROOT.kKey_Right:
			if not self.fOverviewMode and self.fCurDet < (self.experiment.fNumDetectors - 1):
				self.fCurDet += 1
				self.SyncSpecs()
		elif key == ROOT.kKey_Home:
			if not self.fOverviewMode:
				self.fCurDet = 0
				self.SyncSpecs()
		elif key == ROOT.kKey_End:
			if not self.fOverviewMode:
				self.fCurDet = self.experiment.fNumDetectors - 1
				self.SyncSpecs()		
		elif key == ROOT.kKey_o:
			self.fOverviewMode = not self.fOverviewMode
			self.SyncSpecs()
		
fInspect = Inspector()
fInspect.RegisterKeyHandler("fInspect.KeyHandler")
fInspect.SyncSpecs()

