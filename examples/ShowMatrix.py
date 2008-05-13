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

#import some modules
import ROOT
import hdtv.gspec
from hdtv.specreader import SpecReader

# Don't add created spectra to the ROOT directory
ROOT.TH1.AddDirectory(ROOT.kFALSE)

mat = SpecReader().GetMatrix("/home/braun/Diplom/full_test/mat/all/all.mtx", "all.mtx", "all.mtx")
	
viewer = ROOT.MTViewer(400, 400, mat, "mattest")
