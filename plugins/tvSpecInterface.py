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

import ROOT
import os
import glob

import hdtv.cmdline
import hdtv.cmdhelper
import hdtv.color
 
from hdtv.spectrum import Spectrum, FileSpectrum
from hdtv.specreader import SpecReaderError

#import config

# Don't add created spectra to the ROOT directory
ROOT.TH1.AddDirectory(ROOT.kFALSE)

class TVSpecInterface():
	"""
	This class tries to model an interface to hdtv that is a close to the good 
	old tv as possible. 
	"""
	def __init__(self, window, spectra):
		print "Loaded commands for 1-d histograms"
	
		self.window = window
		self.spectra= spectra
		
		# register common tv hotkeys
		self.window.AddHotkey([ROOT.kKey_N, ROOT.kKey_p], self.spectra.ShowPrev)
		self.window.AddHotkey([ROOT.kKey_N, ROOT.kKey_n], self.spectra.ShowNext)
		self.window.AddHotkey(ROOT.kKey_Equal, self.spectra.RefreshAll)
		self.window.AddHotkey(ROOT.kKey_t, self.spectra.RefreshVisible)
		self.window.AddHotkey(ROOT.kKey_Greater, lambda: self.window.fViewport.ShiftXOffset(0.1))
		self.window.AddHotkey(ROOT.kKey_Less, lambda: self.window.fViewport.ShiftXOffset(-0.1))
		self.window.AddHotkey(ROOT.kKey_Return, lambda: self.window.fViewport.Update(True))
		self.window.AddHotkey(ROOT.kKey_Bar,
		        lambda: self.window.fViewport.SetXCenter(self.window.fViewport.GetCursorX()))
		self.window.AddHotkey(ROOT.kKey_n,
		        lambda: self.window.EnterEditMode(prompt="Show spectrum: ",
		                                   handler=self.HotkeyShow))
		self.window.AddHotkey(ROOT.kKey_a,
		        lambda: self.window.EnterEditMode(prompt="Activate spectrum: ",
		                                   handler=self.HotkeyActivate))
		
		# register tv commands
		hdtv.cmdline.command_tree.SetDefaultLevel(1)
		hdtv.cmdline.AddCommand("spectrum get", self.SpectrumGet, level=0, minargs=1, fileargs=True)
		hdtv.cmdline.AddCommand("spectrum list", self.SpectrumList, nargs=0)
		hdtv.cmdline.AddCommand("spectrum delete", self.SpectrumDelete, minargs=1)
		hdtv.cmdline.AddCommand("spectrum activate", self.SpectrumActivate, nargs=1)
		hdtv.cmdline.AddCommand("spectrum show", self.SpectrumShow, minargs=1)
		hdtv.cmdline.AddCommand("spectrum update", self.SpectrumUpdate, minargs=1)
		hdtv.cmdline.AddCommand("spectrum write", self.SpectrumWrite, minargs=1, maxargs=2)
			
		hdtv.cmdline.AddCommand("cd", self.Cd, level=2, maxargs=1, dirargs=True)
		
		hdtv.cmdline.AddCommand("calibration position read", self.CalPosRead, nargs=1, fileargs=True)
		hdtv.cmdline.AddCommand("calibration position enter", self.CalPosEnter, nargs=4)
		hdtv.cmdline.AddCommand("calibration position set", self.CalPosSet, minargs=2)
		

#		# Register configuration variables
#		opt = hdtv.options.Option(default = self.fWindow.fViewport.GetYMinVisibleRegion(),
#                                  parse = lambda(x): float(x),
#                                  changeCallback = self.YMinVisibleRegionChanged)
#		config.RegisterOption("display.YMinVisibleRegion", opt)

#		# Register variables for interactive use
#		hdtv.cmdline.RegisterInteractive("gSpectra", self)
#		
#		
#	def YMinVisibleRegionChanged(self, opt):
#		self.fWindow.fViewport.SetYMinVisibleRegion(opt.Get())
	
	
#	def CenterXOnCursor(self):
#		self.window.fViewport.SetXCenter(self.window.fViewport.GetCursorX())
#		
			
	
	def HotkeyShow(self, arg):
		try:
			self.SpectrumShow(arg.split())
		except ValueError:
			self.window.fViewport.SetStatusText("Invalid spectrum identifier: %s" % arg)

		
	def HotkeyActivate(self, arg):
		try:
			ID = int(arg)
		except ValueError:
			self.window.fViewport.SetStatusText("Invalid id: %s" % arg)
			return
		try:
			self.spectra.ActivateObject(ID)
		except KeyError:
			self.window.fViewport.SetStatusText("No such id: %d" % ID)

	
	def Cd(self, args):
		"""
		Change current working directory
		"""
		if len(args) == 0:
			print os.getcwdu()
		else:
			try:
				os.chdir(os.path.expanduser(args[0]))
			except OSError, msg:
				print msg

	
	def LoadSpectrum(self, fname, fmt=None):
		"""
		Load a spectrum from file
		
		The spectrum is shown in an appropriate color.
		"""
		try:
			spec = FileSpectrum(fname, fmt)
		except (OSError, SpecReaderError):
			return None
		ID = self.spectra.GetFreeID()
		spec.SetColor(hdtv.color.ColorForID(ID, 1., 1.))
		self.spectra[ID] = spec
		self.spectra.ActivateObject(ID)
		return ID


	def SpectrumGet(self, args):
		"""
		Load a list of spectra
		
		It is possible to use wildcards. 
		"""
		# Avoid multiple updates
		self.window.fViewport.LockUpdate()
		if type(args) == str or type(args) == unicode:
			args = [args]
		nloaded = 0
		for arg in args:
			# PUT FMT IF AVAILABLE
			sparg = arg.rsplit("'", 1)
			if len(sparg) == 1 or not sparg[1]:
				(pat, fmt) = (sparg[0], None)
			else:
				(pat, fmt) = sparg
			path = os.path.expanduser(pat)
			for fname in glob.glob(path):
				if self.LoadSpectrum(fname, fmt) != None:
					nloaded += 1
		if nloaded == 0:
			print "Warning: no spectra loaded."
		elif nloaded == 1:
			print "Loaded 1 spectrum"
		else:
			print "Loaded %d spectra" % nloaded
		# Update viewport if required
		self.window.Expand()
		self.window.fViewport.UnlockUpdate()


	def SpectrumList(self, args):
		"""
		Show all loaded spectra and their status
		"""
		self.spectra.ListObjects()
		
		
	def SpectrumDelete(self, args):
		""" 
		Deletes spectra 
		
		It is possible to use the keyword all to delete 
		all spectra that are currently loaded.
		"""
		ids = hdtv.cmdhelper.ParseRange(args)
		if ids == "NONE":
			return
		elif ids == "ALL":
			ids = self.spectra.keys()
		self.spectra.Remove(ids)
		
		
	def SpectrumActivate(self, args):
		"""
		Activate one spectra
		
		There is only just one single spectrum activated.
		Actions that work only on one spectrum usually 
		work on the activated one.
		"""
		try:
			sid = int(args[0])
		except ValueError:
			print "Usage: spectrum activate <id>"
			return
		self.spectra.ActivateObject(sid)
		
		
	def SpectrumShow(self, args):
		"""
		Shows spectra
		
		One can use the keywords none or all here, 
		or give a list of id numbers with space a seperator
		"""
		ids = hdtv.cmdhelper.ParseRange(args)
		if ids == "NONE":
			self.spectra.HideAll()
		elif ids == "ALL":
			self.spectra.ShowAll()
		else:
			self.spectra.Show(ids)
			
	
	def SpectrumUpdate(self, args):
		ids = hdtv.cmdhelper.ParseRange(args, ["all", "shown"])
		if ids == "ALL":
			self.spectra.RefreshAll()
		elif ids == "SHOWN":
			self.spectra.RefreshVisible()
		else:
			self.spectra.Refresh(ids)
			
			
	def SpectrumWrite(self, args):
		"""
		Writes out a spectrum to file
		
		The user must define the file name and the file format.
		If no id is given this action works on the activated spectrum.
		"""
		try:
			(fname, fmt) = args[0].rsplit("'", 1)
			fname = os.path.expanduser(fname)
			if len(args) == 1:
				if self.spectra.activeID == None:
					print "Warning: No active spectrum, no action taken."
					return False
				spec = self.spectra.GetActiveObject()
				spec.WriteSpectrum(fname, fmt)
			else:
				sid = int(args[1])
				try:				
					self.spectra[sid].WriteSpectrum(fname, fmt)
				except KeyError:
					print "Error: ID %d not found" % sid
		except ValueError:
			print "Usage: spectrum write <filename>'<format> [index]"
		return


	def CalPosRead(self, args):
		"""
		Read calibration from file
		"""
		if self.spectra.activeID == None:
			print "Warning: No active spectrum, no action taken."
			return False
		spec = self.spectra.GetActiveObject()
		spec.ReadCal(args[0])

		
	def CalPosEnter(self, args):
		"""
		Create calibration from two pairs of channel and energy
		"""
		if self.spectra.activeID == None:
			print "Warning: No active spectrum, no action taken."
			return False
		try:
			p0 = [float(args[0]), float(args[1])]
			p1 = [float(args[2]), float(args[3])]
		except ValueError:
			print "Usage: calibration position enter <ch0> <E0> <ch1> <E1>"
			return False
		spec = self.spectra.GetActiveObject()
		spec.CalFromPairs([p0, p1])
	
	
	def CalPosSet(self, args):
		"""
		Create a calibration from the coefficients of a calibration polynom.
		
		Coefficients are ordered from lowest exponent to highes.
		"""
		if self.spectra.activeID == None:
			print "Warning: No active spectrum, no action taken."
			return False
		try:
			for arg in args:
				calpoly = map(lambda s: float(s), args)
		except ValueError:
			print "Usage: calibration position set <p0> <p1> <p2> ..."
			return False
		spec = self.spectra.GetActiveObject()
		spec.SetCal(calpoly)
		

