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
# This script contains some test cases for the writing and reading of fits to XML
# If this test work fine, one also needs to test, how thing behave after changing  
# the calibration back and forth (see test_cal.py for that).
################################################################################
import os
import __main__

spectra = __main__.spectra
spectra.Clear()

testspectrum= os.path.join(__main__.hdtvpath, "test", "fitxml", "osiris_bg.spc")
testXML = os.path.join(__main__.hdtvpath, "test", "fitxml", "osiris_bg.xml")


__main__.s.LoadSpectra(testspectrum)
__main__.s.ListSpectra()

print "-------------------------------------------------------------------------"
print "case 0: all parameter free, just one peak, no background, theuerkauf model"
print "-------------------------------------------------------------------------"
__main__.f.SetPeakModel("theuerkauf", default=True)
__main__.f.ResetFitterParameters(default=True)
spectra.SetFitMarker("region", 1450)
spectra.SetFitMarker("region", 1470)
spectra.SetFitMarker("peak", 1460)
spectra.ExecuteFit()
spectra.window.GoToPosition(1460)
__main__.f.PrintWorkFit()

raw_input("Press enter to continue")

spectra.StoreFit()
spectra.ClearFit()
__main__.f.ListFits()
raw_input("Press enter to continue")

print 'Saving fits to file %s' % testXML
__main__.fitxml.WriteFitlist(testXML)
print 'Deleting all fits'
spectra.dict[0].Clear()
print 'Reading fits from file %s' %testXML
__main__.fitxml.ReadFitlist(testXML)
__main__.f.ListFits()

raw_input("Press enter to continue")

print "-------------------------------------------------------------------------"
print "case 1: all parameter free, just one peak, background"
print "-------------------------------------------------------------------------"
spectra.SetFitMarker("region", 500)
spectra.SetFitMarker("region", 520)
spectra.SetFitMarker("peak", 511)
spectra.SetFitMarker("bg", 480)
spectra.SetFitMarker("bg", 490)
spectra.SetFitMarker("bg", 530)
spectra.SetFitMarker("bg", 540)
spectra.ExecuteFit()
spectra.window.GoToPosition(511)
__main__.f.PrintWorkFit()

raw_input("Press enter to continue")

spectra.StoreFit()
spectra.ClearFit()
__main__.f.ListFits()
raw_input("Press enter to continue")

print 'Saving fits to file %s' % testXML
__main__.fitxml.WriteFitlist(testXML)
print 'Deleting all fits'
spectra.dict[0].Clear()
print 'Reading fits from file %s' %testXML
__main__.fitxml.ReadFitlist(testXML)
__main__.f.ListFits()

raw_input("Press enter to continue")

print "-------------------------------------------------------------------------"
print "case 2: all parameter free, more than one peak"
print "-------------------------------------------------------------------------"
spectra.SetFitMarker("region", 1395)
spectra.SetFitMarker("region", 1415)
spectra.SetFitMarker("peak", 1400)
spectra.SetFitMarker("peak", 1410)
spectra.SetFitMarker("bg", 1350)
spectra.SetFitMarker("bg", 1355)
spectra.SetFitMarker("bg", 1420)
spectra.SetFitMarker("bg", 1425)
spectra.ExecuteFit()
spectra.window.GoToPosition(1405)
__main__.f.PrintWorkFit()

raw_input("Press enter to continue")

spectra.StoreFit()
spectra.ClearFit()
__main__.f.ListFits()
raw_input("Press enter to continue")

print 'Saving fits to file %s' % testXML
__main__.fitxml.WriteFitlist(testXML)
print 'Deleting all fits'
spectra.dict[0].Clear()
print 'Reading fits from file %s' %testXML
__main__.fitxml.ReadFitlist(testXML)
__main__.f.ListFits()

raw_input("Press enter to continue")

print "-------------------------------------------------------------------------"
print "case 3: one parameter status!=free, but equal for all peaks"
print "-------------------------------------------------------------------------"
spectra.SetFitMarker("region", 960)
spectra.SetFitMarker("region", 975)
spectra.SetFitMarker("peak", 965)
spectra.SetFitMarker("peak", 970)
spectra.SetFitMarker("bg", 950)
spectra.SetFitMarker("bg", 955)
spectra.SetFitMarker("bg", 980)
spectra.SetFitMarker("bg", 985)
__main__.f.SetFitterParameter("pos", "hold")
spectra.ExecuteFit()
spectra.window.GoToPosition(970)

__main__.f.PrintWorkFit()

raw_input("Press enter to continue")

spectra.StoreFit()
spectra.ClearFit()
__main__.f.ListFits()
raw_input("Press enter to continue")

print 'Saving fits to file %s' % testXML
__main__.fitxml.WriteFitlist(testXML)
print 'Deleting all fits'
spectra.dict[0].Clear()
print 'Reading fits from file %s' %testXML
__main__.fitxml.ReadFitlist(testXML)
__main__.f.ListFits()

raw_input("Press enter to continue")


print "-------------------------------------------------------------------------"
print "case 4: different parameter status for each peak"
print "-------------------------------------------------------------------------"
spectra.SetFitMarker("region", 1750)
spectra.SetFitMarker("region", 1780)
spectra.SetFitMarker("peak", 1765)
spectra.SetFitMarker("peak", 1770)
spectra.SetFitMarker("bg", 1700)
spectra.SetFitMarker("bg", 1710)
spectra.SetFitMarker("bg", 1800)
spectra.SetFitMarker("bg", 1810)
__main__.f.SetFitterParameter("pos", "hold,free")
spectra.ExecuteFit()
spectra.window.GoToPosition(1770)

__main__.f.PrintWorkFit()

raw_input("Press enter to continue")

spectra.StoreFit()
spectra.ClearFit()
__main__.f.ListFits()
raw_input("Press enter to continue")

print 'Saving fits to file %s' % testXML
__main__.fitxml.WriteFitlist(testXML)
print 'Deleting all fits'
spectra.dict[0].Clear()
print 'Reading fits from file %s' %testXML
__main__.fitxml.ReadFitlist(testXML)
__main__.f.ListFits()

raw_input("Press enter to continue")


print "-------------------------------------------------------------------------"
print "case 5: ee peak (just proof of concept, not a thorough test)"
print "-------------------------------------------------------------------------"
__main__.f.SetPeakModel("ee")
spectra.SetFitMarker("region", 1115)
spectra.SetFitMarker("region", 1125)
spectra.SetFitMarker("peak", 1120)
spectra.ExecuteFit()
spectra.window.GoToPosition(1120)

__main__.f.PrintWorkFit()

raw_input("Press enter to continue")

spectra.StoreFit()
spectra.ClearFit()
__main__.f.ListFits()
raw_input("Press enter to continue")

print 'Saving fits to file %s' % testXML
__main__.fitxml.WriteFitlist(testXML)
print 'Deleting all fits'
spectra.dict[0].Clear()
print 'Reading fits from file %s' %testXML
__main__.fitxml.ReadFitlist(testXML)
__main__.f.ListFits()

raw_input("Press enter to continue")






