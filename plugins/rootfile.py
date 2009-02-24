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
import hdtv.cmdline
import hdtv.tabformat
import hdtv.spectrum
import fnmatch
import tvSpecInterface

def RootBrowse(args):
	global fBrowser, fRootFile
	fBrowser = ROOT.TBrowser()
	
	if fRootFile != None and not fRootFile.IsZombie():
		fRootFile.Browse(fBrowser)

def RootLs(args):
	global fRootFile
	if fRootFile == None or fRootFile.IsZombie():
		print "Error: no root file"
		return
	
	keys = fRootFile.GetListOfKeys()
	names = [k.GetName() for k in keys]

	if len(args) > 0:
		names = fnmatch.filter(names, args[0])
	
	names.sort()
	hdtv.tabformat.tabformat(names)
	
def RootLL(args):
	global fRootFile
	if fRootFile == None or fRootFile.IsZombie():
		print "Error: no root file"
		return
		
	if len(args) == 0:
		fRootFile.ls()
	else:
		fRootFile.ls(args[0])
		
def RootCd(args):
	global fRootFile
	if fRootFile != None:
		fRootFile.Close()
	
	fRootFile = ROOT.TFile(args[0])
	if fRootFile.IsZombie():
		print "Error: failed to open file"
		fRootFile = None
		
	hdtv.cmdline.RegisterInteractive("gRootFile", fRootFile)
	
def RootGet_Completer(text):
	global fRootFile
	if fRootFile == None or fRootFile.IsZombie():
		# Autocompleter must not complain...
		return
		
	keys = fRootFile.GetListOfKeys()
	names = [k.GetName() for k in keys]

	options = []
	l = len(text)
	for name in names:
		if name[0:l] == text:
			options.append(name)
			
	return options

def RootGet(args, options):
	global fRootFile
	if fRootFile == None or fRootFile.IsZombie():
		print "Error: no root file"
		return
		
	# FIXME: we *really* need a better plugin concept...
	specmgr = tvSpecInterface.plugin
		
	if options.replace:
		specmgr.DeleteObjects(specmgr.keys())
		
	keys = fRootFile.GetListOfKeys()
	for key in keys:
		if fnmatch.fnmatch(key.GetName(), args[0]):
			obj = key.ReadObj()
			if isinstance(obj, ROOT.TH1):
				specmgr.fWindow.fViewport.LockUpdate()
				spec = hdtv.spectrum.Spectrum(obj)
				ID = specmgr.GetFreeID()
				spec.SetColor(specmgr.ColorForID(ID, 1., 1.))
				specmgr[ID] = spec
				specmgr.ActivateObject(ID)
				specmgr.fWindow.fViewport.UnlockUpdate()
			else:
				print "Warning: %s is not a 1D histogram object" % key.GetName()

fRootFile = None
fBrowser = None

hdtv.cmdline.AddCommand("root browse", RootBrowse, nargs=0)
hdtv.cmdline.AddCommand("root ls", RootLs, maxargs=1)
hdtv.cmdline.AddCommand("root ll", RootLL, maxargs=1, level=2)
hdtv.cmdline.AddCommand("root cd", RootCd, nargs=1, fileargs=True)

parser = hdtv.cmdline.HDTVOptionParser(prog="root get", usage="%prog [OPTIONS] <pattern>")
parser.add_option("-r", "--replace", action="store_true",
                  default=False, help="replace existing histogram list")
hdtv.cmdline.AddCommand("root get", RootGet, nargs=1, completer=RootGet_Completer,
                        parser=parser)
