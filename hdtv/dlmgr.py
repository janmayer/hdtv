#!/bin/false
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# HDTV dynamic (C++) library manager
#-------------------------------------------------------------------------------
import os
import stat
import ROOT

class DLImportError(Exception):
	pass

path = list()

def FindLibrary(name):
	"""
	Find a dynamic library in the path. Returns the full filename.
	"""
	global path
	for p in path:
		fname = "%s/%s.so" % (p, name)
		try:
			mode = os.stat(fname)[stat.ST_MODE]
			if stat.S_ISREG(mode):
				return fname
		except OSError:
			# Ignore the file if stat failes
			pass
	return None
	
def LoadLibrary(name):
	fname = FindLibrary(name)
	if not fname:
		raise DLImportError, "Failed to find library %s" % name

	if ROOT.gSystem.Load(fname) < 0:
		raise DLImportError, "Failed to load library %s" % fname

