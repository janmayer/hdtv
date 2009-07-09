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

# Preliminary ROOT file interface for hdtv

import ROOT
import os
import hdtv.cmdline
import hdtv.tabformat
import hdtv.spectrum
import fnmatch
import readline
import hdtv.rfile_utils

class RootFile:
	def __init__(self, window, spectra, caldict):
		print "Loaded user interface for working with root files"
		self.window = window
		self.spectra = spectra
		self.caldict = caldict
		self.rootfile = None
		self.browser = None
		self.matviews = list()
		
		hdtv.cmdline.AddCommand("root browse", self.RootBrowse, nargs=0)
		hdtv.cmdline.AddCommand("root ls", self.RootLs, maxargs=1)
		hdtv.cmdline.AddCommand("root ll", self.RootLL, maxargs=1, level=2)
		hdtv.cmdline.AddCommand("root open", self.RootOpen, nargs=1, fileargs=True)
		hdtv.cmdline.AddCommand("root close", self.RootClose, nargs=0)
		hdtv.cmdline.AddCommand("root cd", self.RootCd, nargs=1,
		                        completer=self.RootCd_Completer)
		hdtv.cmdline.AddCommand("root pwd", self.RootPwd, nargs=0)

		parser = hdtv.cmdline.HDTVOptionParser(prog="root get", usage="%prog [OPTIONS] <pattern>")
		parser.add_option("-r", "--replace", action="store_true",
    		              default=False, help="replace existing histogram list")
		parser.add_option("-c", "--load-cal", action="store_true",
		                  default=False, help="load calibration from calibration dictionary")
		parser.add_option("-v", "--invisible", action="store_true",
		                  default=False, help="do not make histograms visible, only add to display list")
		hdtv.cmdline.AddCommand("root get", self.RootGet, minargs=1, completer=self.RootGet_Completer,
		                        parser=parser)
		
		hdtv.cmdline.AddCommand("root matrix", self.RootMatrix, minargs=1,
		                        completer=self.RootGet_Completer,
		                        usage="root matrix <matname>")
		                        
		hdtv.cmdline.RegisterInteractive("gRootFile", self.rootfile)
	
	def RootBrowse(self, args):
		self.browser = ROOT.TBrowser()
		
		if self.rootfile != None and not self.rootfile.IsZombie():
			self.rootfile.Browse(self.browser)

	def RootLs(self, args):
		keys = ROOT.gDirectory.GetListOfKeys()
		if not keys:
			return
		
		names = [k.GetName() for k in keys]
	
		if len(args) > 0:
			names = fnmatch.filter(names, args[0])
		
		names.sort()
		hdtv.tabformat.tabformat(names)
	
	def RootLL(self, args):
		if len(args) == 0:
			ROOT.gDirectory.ls()
		else:
			ROOT.gDirectory.ls(args[0])
			
	def RootCd(self, args):
		if self.rootfile:
			cur_root_dir = ROOT.gDirectory
		else:
			cur_root_dir = None
	
		(posix_path, rfile, root_dir) = hdtv.rfile_utils.GetRelDirectory(os.getcwd(), cur_root_dir, args[0])
		if (posix_path, rfile, root_dir) == (None, None, None):
			print "Error: invalid path specified."
			return
			
		os.chdir(posix_path)
			
		# If root_dir is None, we moved outside the ROOT file and are now in
		# a POSIX directory. If rfile is not None, we *changed* the ROOT file.
		if root_dir == None or rfile != None:
			if self.rootfile != None:
				print "Info: closing old root file %s" % self.rootfile.GetName()
				self.rootfile.Close()
			self.rootfile = rfile
			if self.rootfile != None:
				print "Info: opened new root file %s" % self.rootfile.GetName()
			
		if root_dir != None:
			root_dir.cd()
		
	def RootPwd(self, args):
		if self.rootfile != None:
			ROOT.gDirectory.pwd()
		else:
			print os.getcwd()
			
	def RootOpen(self, args):
		return self.RootCd(args)
		
	def RootClose(self, args):
		if self.rootfile == None:
			print "Info: no root file open, no action taken"
		else:
			self.rootfile.Close()
			self.rootfile = None
			
	def RootGet_Completer(self, text):
		return self.Completer(text, dirs_only=False)
		
	def RootCd_Completer(self, text):
		return self.Completer(text, dirs_only=True)
		
	def Completer(self, text, dirs_only):
		buf = readline.get_line_buffer()
		if buf == "":
			# This should not happen...
			return []
			
		if self.rootfile:
			cur_root_dir = ROOT.gDirectory
		else:
			cur_root_dir = None
		
		if buf[-1] == " ":
			return hdtv.rfile_utils.PathComplete(".", cur_root_dir, "", text, dirs_only)
		else:
			path = buf.rsplit(None, 1)[-1]
			dirs = path.rsplit("/", 1)
			
			# Handle absolute paths
			if dirs[0] == "":
				dirs[0] = "/"
			
			if len(dirs) == 1:
				return hdtv.rfile_utils.PathComplete(".", cur_root_dir, "", text, dirs_only)
			else:
				return hdtv.rfile_utils.PathComplete(".", cur_root_dir, dirs[0], text, dirs_only)
		
	def RootMatrix(self, args):
		"""
		Load a 2D histogram (``matrix'') from a ROOT file and display it.
		
		Note: Unlike RootGet(), this function does not support shell-style
		pattern expansion, as this make it too easy to undeliberately load
		too many histograms. As they use a lot of memory, this would likely
		lead to a crash of the program.
		"""
		for path in args:
			dirs = path.rsplit("/", 1)
			if len(dirs) == 1:
				# Load 2d histogram from current directory
				hist = ROOT.gDirectory.Get(dirs[0])
			else:
				if self.rootfile:
					cur_root_dir = ROOT.gDirectory
				else:
					cur_root_dir = None
			
				(posix_path, rfile, root_dir) = hdtv.rfile_utils.GetRelDirectory(os.getcwd(), cur_root_dir, dirs[0])
			
				if root_dir:
					hist = root_dir.Get(dirs[1])
				else:
					hist = None
				
				if rfile:
					rfile.Close()
		
			if hist == None or not isinstance(hist, ROOT.TH2):
				print "Error: %s is not a 2d histogram" % args[0]
				return
		
			title = hist.GetTitle()
			viewer = ROOT.HDTV.Display.MTViewer(400, 400, hist, title)
			self.matviews.append(viewer)
	
	def RootGet(self, args, options):
		if self.rootfile:
			cur_root_dir = ROOT.gDirectory
		else:
			cur_root_dir = None
			
		objs = []
		for pat in args:
			objs += hdtv.rfile_utils.Get(".", cur_root_dir, pat)
	
		if options.replace:
			self.spectra.RemoveAll()
			
		nloaded = 0
		self.window.viewport.LockUpdate()
		try:  # We should really use a context manager here...
			for obj in objs:
				if isinstance(obj, ROOT.TH1):
					spec = hdtv.spectrum.Spectrum(obj)
					ID = self.spectra.Add(spec)
					spec.SetColor(hdtv.color.ColorForID(ID))
					
					if options.load_cal:
						if obj.GetName() in self.caldict:
							spec.SetCal(self.caldict[obj.GetName()])
						else:
							print "Warning: no calibration found for %s" % obj.GetName()
				
					if options.invisible:
						self.spectra.HideObjects(ID)
					else:
						self.spectra.ActivateObject(ID)
				
					nloaded += 1
				else:
					print "Warning: %s is not a 1D histogram object" % obj.GetName()
					
			print "%d spectra loaded" % nloaded
		finally:
			self.window.viewport.UnlockUpdate()
		
	def Draw(self, hist):
		spec = hdtv.spectrum.Spectrum(hist)
		ID = self.spectra.Add(spec)
		spec.SetColor(hdtv.color.ColorForID(ID))
		self.spectra.ActivateObject(ID)


# plugin initialisation
import __main__
import specInterface 
r = RootFile(__main__.window, __main__.spectra, __main__.s.caldict)
__main__.Draw = r.Draw
