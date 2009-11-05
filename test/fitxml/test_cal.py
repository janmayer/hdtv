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
################################################################################
# This script tests the interplay of fitting and restoring fits with calibration
################################################################################
import os
import hdtv.fitxml
import xml.etree.cElementTree as ET

import __main__

testspectrum= os.path.join(__main__.hdtvpath, "test", "fitxml", "osiris_bg.spc")
testXML = os.path.join(__main__.hdtvpath, "test", "fitxml", "fit.xml")

spectra = __main__.spectra
spectra.Clear()

__main__.s.LoadSpectra(testspectrum)
print "-------------------------------------------------------------------------"
print " Case 0: Set Marker and calibrate afterwards"
print " Marker will be kept fixed, but the spectrum changes"
print "-------------------------------------------------------------------------"
spectra.SetMarker("region", 1450)
spectra.SetMarker("region", 1470)
spectra.SetMarker("peak", 1460)
spectra.window.GoToPosition(1460)
spectra.ApplyCalibration("0", [0,2])

raw_input("Press enter to continue...")

print "-------------------------------------------------------------------------"
print " Case 1: Set Marker in calibrated spectrum"
print " Marker should be appear at the right position relative to spectrum"
print "-------------------------------------------------------------------------"
spectra.ClearFit()
spectra.SetMarker("region", 2900)
spectra.SetMarker("region", 2940)
spectra.SetMarker("peak", 2920)
spectra.window.GoToPosition(2920)

raw_input("Press enter to continue...")


print "-------------------------------------------------------------------------"
print " Case 2: Fit in calibrated spectrum"
print " Fit should be fixed relative to spectrum"
print "-------------------------------------------------------------------------"
spectra.ExecuteFit()
__main__.f.PrintWorkFit()

raw_input("Press enter to continue...")

print "-------------------------------------------------------------------------"
print " Case 3: Change calibration after fit is executed"
print " Fit should move with spectrum to new position"
print "-------------------------------------------------------------------------"
spectra.ApplyCalibration("0", [0,0.5])
spectra.window.GoToPosition(730)
__main__.f.PrintWorkFit()

raw_input("Press enter to continue...")

print "-------------------------------------------------------------------------"
print " Case 4: Store fit"
print " Stored fit and aktive markers should stay fixed relative to spectrum"
print "-------------------------------------------------------------------------"
spectra.StoreFit()
__main__.f.ListFits()

raw_input("Press enter to continue...")

print "-------------------------------------------------------------------------"
print " Case 5: Reactivate stored fit"
print " Active markers should appear at the same position as the stored fit"
print "-------------------------------------------------------------------------"
spectra.ActivateFit("0")

raw_input("Press enter to continue...")

print "-------------------------------------------------------------------------"
print " Case 6: Execute reactivated fit"
print " New fit should be at the same position as stored fit"
print "-------------------------------------------------------------------------"
spectra.ExecuteFit()
__main__.f.ListFits()

raw_input("Press enter to continue...")

print "-------------------------------------------------------------------------"
print " Case 7: Change calibration after fit is stored"
print " Stored fit should move with spectrum to new position"
print "-------------------------------------------------------------------------"
spectra.ActivateFit(None)
spectra.ClearFit()
spectra.ApplyCalibration("0", [0,2])
spectra.window.GoToPosition(2920)
__main__.f.ListFits()

raw_input("Press enter to continue...")

print "-------------------------------------------------------------------------"
print " Case 8: Reactivate fit after calibration has changed"
print " Active markers should appear at the same position as fit"
print "-------------------------------------------------------------------------"
spectra.ActivateFit("0")

raw_input("Press enter to continue...")

print "-------------------------------------------------------------------------"
print " Case 9: Execute reactivated fit"
print " New fit should be at the same position as the stored fit"
print "-------------------------------------------------------------------------"
spectra.ExecuteFit()
__main__.f.ListFits()

raw_input("Press enter to continue...")

print "-------------------------------------------------------------------------"
print " Case 10: Write/read fit to/from xml"
print " Fit should appear at the same position as before"
print "-------------------------------------------------------------------------"
spectra.ActivateFit(None)
spectra.ClearFit()
__main__.fitxml.WriteFitlist(testXML)
spectra.dict["0"].Clear()
__main__.fitxml.ReadFitlist(testXML)
__main__.f.ListFits()

raw_input("Press enter to continue...")


print "-------------------------------------------------------------------------"
print " Case 11: Write/Read fit and calibrate afterwards"
print " Fit should move with spectrum to new calibration"
print "-------------------------------------------------------------------------"
spectra.ApplyCalibration("0", [0,0.5])
spectra.window.GoToPosition(730)
__main__.f.ListFits()

raw_input("Press enter to continue...")

print "-------------------------------------------------------------------------"
print " Case 12: Write/Read fit and change calibration in between"
print " Fit should appear at the new calibrated position"
print "-------------------------------------------------------------------------"
__main__.fitxml.WriteFitlist(testXML)
spectra.dict["0"].Clear()
spectra.ApplyCalibration("0", [0,2])
spectra.window.GoToPosition(2920)
__main__.fitxml.ReadFitlist(testXML)
__main__.f.ListFits()

raw_input("Press enter to continue...")


