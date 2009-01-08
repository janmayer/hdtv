#!/usr/bin/python -i
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This very simple example shows how to display a two-dimensional histogram
# (``matrix'')
#
#-------------------------------------------------------------------------------

# set the pythonpath
import sys
sys.path.append("..")

# Set the library search path
import hdtv.dlmgr
hdtv.dlmgr.path.append("../lib")
hdtv.dlmgr.LoadLibrary("display")

#import some modules
import ROOT
from hdtv.specreader import SpecReader

# Don't add created spectra to the ROOT directory
ROOT.TH1.AddDirectory(ROOT.kFALSE)

mat = SpecReader().GetMatrix("/home/braun/Diplom/full_test/mat/all/all.mtx", "mfile", "all.mtx", "all.mtx")
	
viewer = ROOT.HDTV.Display.MTViewer(400, 400, mat, "mattest")
