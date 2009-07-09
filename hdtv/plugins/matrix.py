# -*- coding: utf-8 -*-

# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2009  The HDTV development team (see file AUTHORS)
#
# This file is part of HDTV.
#
# HDTV is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# HDTV is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with HDTV; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

#-------------------------------------------------------------------------------
# Matrix interface for hdtv
#-------------------------------------------------------------------------------

import hdtv.cmdline
import hdtv.dlmgr
import hdtv.marker
import os.path
import hdtv.color
from hdtv.specreader import SpecReaderError

import math
import ROOT

class CutSpectrum(hdtv.spectrum.Spectrum):
	def __init__(self, hist, matrix, color=None, cal=None):
		self.matrix = matrix
		hdtv.spectrum.Spectrum.__init__(self, hist, color, cal)

class Matrix(hdtv.spectrum.Spectrum):
	def __init__(self, proj, title, color, cal):
		self.cuts = []
		self.cutRegions = []
		self.title = title
		hdtv.spectrum.Spectrum.__init__(self, proj, color, cal)
		
	def E2CutBin(self, e):
		if self.cal:
			ch = self.cal.E2Ch(e)
		else:
			ch = e

		return self.vmat.FindCutBin(ch)
		
	def AddCutRegion(self, e1, e2):
		b1 = self.E2CutBin(e1)
		b2 = self.E2CutBin(e2)
		self.cutRegions.append((b1, b2))
		self.vmat.AddCutRegion(b1, b2)
		
	def AddBgRegion(self, e1, e2):
		self.vmat.AddBgRegion(self.E2CutBin(e1), self.E2CutBin(e2))
		
	def ResetRegions(self):
		self.vmat.ResetRegions()
		self.cutRegions = []
		
	def Cut(self):
		title = self.title
		for (b1,b2) in self.cutRegions:
			title += "_c%d-%d" % (b1, b2)
				
		hist = self.vmat.Cut(title, title)
		self.cuts.append(CutSpectrum(hist, self, cal=self.cal))
		return self.cuts[-1]
		
class MFMatrix(Matrix):
	"""
	mfile-backed matrix
	"""
	def __init__(self, fname, fmt=None, color=None, cal=None):
		self.fname = fname
			
		hdtv.dlmgr.LoadLibrary("mfile-root")
		self.mhist = ROOT.MFileHist()

		if not fmt or fmt.lower() == 'mfile':
			result = self.mhist.Open(self.fname)
		else:
			result = self.mhist.Open(self.fname, fmt)
			
		if result != ROOT.MFileHist.ERR_SUCCESS:
			raise SpecReaderError, mhist.GetErrorMsg()

		self.vmat = ROOT.VMatrix(self.mhist, 0)
		
		# Load the projection (FIXME)
		mhist_pry = ROOT.MFileHist()
		result = mhist_pry.Open(self.fname.rsplit('.', 1)[0] + ".pry")
		if result != ROOT.MFileHist.ERR_SUCCESS:
			raise SpecReaderError, mhist_pry.GetErrorMsg()
			
		hist = mhist_pry.ToTH1D(self.fname + "_pry", self.fname + "_pry", 0, 0)
		if not hist:
			raise SpecReaderError, mhist_pry.GetErrorMsg()
		
		Matrix.__init__(self, hist, self.fname, color, cal)
		
	def __del__(self):
		# Explicitly deconstruct C++ objects in the right order
		self.vmat = None
		ROOT.SetOwnership(self.mhist, True)
		self.mhist = None

class MatrixInterface:
	def __init__(self, window, spectra):
		self.window = window
		self.spectra = spectra
		self.CutRegionMarkers = hdtv.marker.MarkerCollection("X", paired=True,
		                                         color=hdtv.color.cut)
		self.CutRegionMarkers.Draw(self.window.viewport)
		self.CutBgMarkers = hdtv.marker.MarkerCollection("X", paired=True,
		                                     color=hdtv.color.cut, connecttop=False)
		self.CutBgMarkers.Draw(self.window.viewport)
		
		# Register hotkeys
		self.window.AddHotkey(ROOT.kKey_c, self.HotkeyCutMarker)
		self.window.AddHotkey([ROOT.kKey_Comma, ROOT.kKey_c], self.HotkeyCutRegionMarker)
		self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_C], self.HotkeyClearCutMarkers)
		self.window.AddHotkey(ROOT.kKey_C, self.HotkeyCreateCut)
		self.window.AddHotkey(ROOT.kKey_Tab, self.HotkeySwitch)
	
		# Register commands
		hdtv.cmdline.AddCommand("matrix open", self.MatrixOpen, nargs=1,
		                        usage="%prog <filename>", fileargs=True)

		print "Loaded user interface for working with matrices (2d histograms)"
		
	def HotkeySwitch(self):
		"""
		Switch between a cut and the corresponding full projection, or the
		full projection and the most recent cut
		"""
		spec = self.spectra.GetActiveObject()
		if isinstance(spec, Matrix):
			try:
				target = spec.cuts[-1]
			except IndexError:
				return
		elif isinstance(spec, CutSpectrum):
			target = spec.matrix
		else:
			return
			
		try:
			targetID = self.spectra.Index(target)
		except ValueError:
			return
		
		self.window.viewport.LockUpdate()
		self.spectra.HideObjects([self.spectra.activeID])
		self.spectra.ShowObjects([targetID])
		self.spectra.ActivateObject(targetID)
		self.window.viewport.UnlockUpdate()
		
	def HotkeyCutRegionMarker(self):
		"""
		sets a cut region marker, even if a pair of cut region markers already
		exists
		"""
		pos = self.window.viewport.GetCursorX()
		self.CutRegionMarkers.PutMarker(pos)
		
	def HotkeyCutMarker(self):
		"""
  		set a cut marker
  		"""
  		pos = self.window.viewport.GetCursorX()
		if len(self.CutRegionMarkers) < 1 or self.CutRegionMarkers.IsPending():
			self.CutRegionMarkers.PutMarker(pos)
		else:
			self.CutBgMarkers.PutMarker(pos)
		
	def HotkeyCreateCut(self):
		"""
		perform a cut on the matrix
		"""
		if len(self.CutRegionMarkers) < 1:
			return
			
		matrix = self.spectra.GetActiveObject()
		if isinstance(matrix, CutSpectrum):
			matrix = matrix.matrix
		elif not isinstance(matrix, Matrix):
			return
			
		self.window.viewport.LockUpdate()
		
		# Hide the current spectrum
		self.spectra.HideObjects([self.spectra.activeID])
		
		matrix.ResetRegions()
		
		for region in self.CutRegionMarkers:
			matrix.AddCutRegion(region.p1, region.p2)
			
		for bg in self.CutBgMarkers:
			matrix.AddBgRegion(bg.p1, bg.p2)
			
		cut = matrix.Cut()
		cutid = self.spectra.Add(cut)
		cut.SetColor(hdtv.color.ColorForID(cutid))
		self.spectra.ActivateObject(cutid)
		
		# Remove cut markers
		self.CutRegionMarkers.Clear()
		self.CutBgMarkers.Clear()
		
		self.window.viewport.UnlockUpdate()
		
	def HotkeyClearCutMarkers(self):
		self.window.viewport.LockUpdate()
		self.CutRegionMarkers.Clear()
		self.CutBgMarkers.Clear()
		self.window.viewport.UnlockUpdate()
		
	def MatrixOpen(self, args):
		# put fmt if available
		p = args[0].rsplit("'", 1)
		if len(p) == 1 or not p[1]:
			(fname, fmt) = (p[0], None)
		else:
			(fname, fmt) = p

		try:
			fname = os.path.expanduser(fname)
			spec = Matrix(fname, fmt)
		except (OSError, SpecReaderError):
			print "Error: failed to open matrix %s" % args[0]
			return False
		
		sid = self.spectra.Add(spec)
		spec.SetColor(hdtv.color.ColorForID(sid))
		self.spectra.ActivateObject(sid)
		self.window.Expand()
		
		
# plugin initialisation
import __main__
if not hasattr(__main__,"window"):
	import hdtv.window
	__main__.window = hdtv.window.Window()
if not hasattr(__main__, "spectra"):
	import hdtv.drawable
	__main__.spectra = hdtv.drawable.DrawableCompound(__main__.window.viewport)

__main__.mat = MatrixInterface(__main__.window, __main__.spectra)
