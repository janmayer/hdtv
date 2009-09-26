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
spectra.RemoveAll()

testspectrum= os.path.join(__main__.hdtvpath, "test", "fitxml", "osiris_bg.spc")
testXML = os.path.join(__main__.hdtvpath, "test", "fitxml", "osiris_bg.xml")


__main__.s.LoadSpectra(testspectrum)

print "-------------------------------------------------------------------------"
print "case 0: all parameter free, just one peak, no background, theuerkauf model"
print "-------------------------------------------------------------------------"
__main__.f.SetPeakModel("theuerkauf", default=True)
__main__.f.ResetParameters(default=True)
__main__.f.workFit.PutRegionMarker(1450)
__main__.f.workFit.PutRegionMarker(1470)
__main__.f.workFit.PutPeakMarker(1460)
__main__.f.Fit()
__main__.window.GoToPosition(1460)

raw_input("Press enter to continue")

__main__.f.StoreFit()
print 'Saving fits to file %s' % testXML
__main__.fitxml.WriteFitlist(testXML)
print 'Deleting all fits'
__main__.spectra[0].fits.RemoveAll()
print 'Reading fits from file %s' %testXML
__main__.fitxml.ReadFitlist(testXML)

raw_input("Press enter to continue")

print "-------------------------------------------------------------------------"
print "case 1: all parameter free, just one peak, background"
print "-------------------------------------------------------------------------"
fit = __main__.f.workFit
__main__.f.workFit.PutRegionMarker(500)
__main__.f.workFit.PutRegionMarker(520)
__main__.f.workFit.PutPeakMarker(511)
__main__.f.workFit.PutBgMarker(480)
__main__.f.workFit.PutBgMarker(490)
__main__.f.workFit.PutBgMarker(530)
__main__.f.workFit.PutBgMarker(540)
__main__.f.Fit()
__main__.window.GoToPosition(511)

raw_input("Press enter to continue")

__main__.f.StoreFit()
print 'Saving fits to file %s' % testXML
__main__.fitxml.WriteFitlist(testXML)
print 'Deleting all fits'
__main__.spectra[0].fits.RemoveAll()
print 'Reading fits from file %s' %testXML
__main__.fitxml.ReadFitlist(testXML)

raw_input("Press enter to continue")

print "-------------------------------------------------------------------------"
print "case 1: all parameter free, more than one peak"
print "-------------------------------------------------------------------------"
__main__.f.workFit.PutRegionMarker(1395)
__main__.f.workFit.PutRegionMarker(1415)
__main__.f.workFit.PutPeakMarker(1400)
__main__.f.workFit.PutPeakMarker(1410)
__main__.f.workFit.PutBgMarker(1350)
__main__.f.workFit.PutBgMarker(1355)
__main__.f.workFit.PutBgMarker(1420)
__main__.f.workFit.PutBgMarker(1425)
__main__.f.Fit()
__main__.window.GoToPosition(1405)

raw_input("Press enter to continue")

__main__.f.StoreFit()
print 'Saving fits to file %s' % testXML
__main__.fitxml.WriteFitlist(testXML)
print 'Deleting all fits'
__main__.spectra[0].fits.RemoveAll()
print 'Reading fits from file %s' %testXML
__main__.fitxml.ReadFitlist(testXML)

raw_input("Press enter to continue")

print "-------------------------------------------------------------------------"
print "case 3: one parameter status!=free, but equal for all peaks"
print "-------------------------------------------------------------------------"
__main__.f.workFit.PutRegionMarker(960)
__main__.f.workFit.PutRegionMarker(975)
__main__.f.workFit.PutPeakMarker(965)
__main__.f.workFit.PutPeakMarker(970)
__main__.f.workFit.PutBgMarker(950)
__main__.f.workFit.PutBgMarker(955)
__main__.f.workFit.PutBgMarker(980)
__main__.f.workFit.PutBgMarker(985)
__main__.f.SetParameter("pos", "hold")
__main__.f.Fit()
__main__.window.GoToPosition(970)

raw_input("Press enter to continue")

__main__.f.StoreFit()
print 'Saving fits to file %s' % testXML
__main__.fitxml.WriteFitlist(testXML)
print 'Deleting all fits'
__main__.spectra[0].fits.RemoveAll()
print 'Reading fits from file %s' %testXML
__main__.fitxml.ReadFitlist(testXML)

raw_input("Press enter to continue")

print "-------------------------------------------------------------------------"
print "case 4: different parameter status for each peak"
print "-------------------------------------------------------------------------"
__main__.f.workFit.PutRegionMarker(1750)
__main__.f.workFit.PutRegionMarker(1780)
__main__.f.workFit.PutPeakMarker(1765)
__main__.f.workFit.PutPeakMarker(1770)
__main__.f.workFit.PutBgMarker(1700)
__main__.f.workFit.PutBgMarker(1710)
__main__.f.workFit.PutBgMarker(1800)
__main__.f.workFit.PutBgMarker(1810)
__main__.f.Fit()
__main__.window.GoToPosition(1770)

raw_input("Press enter to continue")

__main__.f.StoreFit()
print 'Saving fits to file %s' % testXML
__main__.fitxml.WriteFitlist(testXML)
print 'Deleting all fits'
__main__.spectra[0].fits.RemoveAll()
print 'Reading fits from file %s' %testXML
__main__.fitxml.ReadFitlist(testXML)

raw_input("Press enter to continue")

print "-------------------------------------------------------------------------"
print "case 5: ee peak (just proof of concept, not a thorough test)"
print "-------------------------------------------------------------------------"
__main__.f.SetPeakModel("ee")
__main__.f.workFit.PutRegionMarker(1115)
__main__.f.workFit.PutRegionMarker(1125)
__main__.f.workFit.PutPeakMarker(1120)
__main__.f.Fit()
__main__.window.GoToPosition(1120)

raw_input("Press enter to continue")

__main__.f.StoreFit()
print 'Saving fits to file %s' % testXML
__main__.fitxml.WriteFitlist(testXML)
print 'Deleting all fits'
__main__.spectra[0].fits.RemoveAll()
print 'Reading fits from file %s' %testXML
__main__.fitxml.ReadFitlist(testXML)





