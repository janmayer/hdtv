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

spectra = __main__.spectra
spectra.RemoveAll()

testspectrum= os.path.join(__main__.hdtvpath, "test", "fitxml", "osiris_bg.spc")
testXML = os.path.join(__main__.hdtvpath, "test", "fitxml", "test.xml")

__main__.s.LoadSpectra(testspectrum)
spec = spectra[0]


# get fitElement
tree = ET.parse(testXML)
root = tree.getroot()


for specElement in root.findall("spectrum"):
    for fitElement in specElement.findall("fit"):
        ET.dump(fitElement)

print "-------------------------------------------------------------------------"
print "Case 1: Restore without calibration"
print "-------------------------------------------------------------------------"
print "Restore fit"
f = hdtv.fitxml.FitXml(spectra)
(fit, success) = f.Xml2Fit(fitElement)
fit.Restore(spec)

print "Draw"
ID = spec.Add(fit)
spec.ActivateObject(ID)

print fit

__main__.window.GoToPosition(1460)
raw_input('Press enter to continue ')

spec.RemoveAll()
spec.SetCal(None)
print "-------------------------------------------------------------------------"
print "Case 2: set cal after Restore"
print "-------------------------------------------------------------------------"
print "Restore fit"
f = hdtv.fitxml.FitXml(spectra)
(fit, success) = f.Xml2Fit(fitElement)
fit.Restore(spec)

print "Draw"
ID = spec.Add(fit)
spec.ActivateObject(ID)

print "SetCal"
spec.SetCal([0,2])

print fit

__main__.window.GoToPosition(2920)
raw_input('Press enter to continue ')

spec.RemoveAll()
spec.SetCal(None)
print "-------------------------------------------------------------------------"
print "Case 3: set cal before Restore"
print "-------------------------------------------------------------------------"
print "SetCal"
spec.SetCal([0,0.5])


print "Restore fit"
f = hdtv.fitxml.FitXml(spectra)
(fit, success) = f.Xml2Fit(fitElement)
fit.Restore(spec)

print "Draw"
ID = spec.Add(fit)
spec.ActivateObject(ID)

print fit

__main__.window.GoToPosition(730)
raw_input('Press enter to continue ')

spec.RemoveAll()
spec.SetCal(None)
print "-------------------------------------------------------------------------"
print "Case 4: Fit without calibration"
print "-------------------------------------------------------------------------"
print "Fit"
fit = __main__.f.GetActiveFit()
fit.PutRegionMarker(1450)
fit.PutRegionMarker(1470)
fit.PutPeakMarker(1460)
__main__.f.Fit(peaks=True)

__main__.window.GoToPosition(1460)
raw_input('Press enter to continue ')

__main__.f.ClearFit()
spec.RemoveAll()
spec.SetCal(None)
print "-------------------------------------------------------------------------"
print "Case 5: SetCal after Fit"
print "-------------------------------------------------------------------------"
print "Fit"
fit = __main__.f.GetActiveFit()
fit.PutRegionMarker(1450)
fit.PutRegionMarker(1470)
fit.PutPeakMarker(1460)

__main__.f.Fit(peaks=True)

print "SetCal"
spec.SetCal([0,2])

print fit

__main__.window.GoToPosition(2920)
raw_input('Press enter to continue ')

__main__.f.ClearFit()
spec.RemoveAll()
print "-------------------------------------------------------------------------"
print "Case 6: SetCal before Fit"
print "-------------------------------------------------------------------------"
print "SetCal"
spec.SetCal([0,0.5])

print "Fit"
fit = __main__.f.GetActiveFit()
fit.PutRegionMarker(725)
fit.PutRegionMarker(735)
fit.PutPeakMarker(730)

__main__.f.Fit(peaks=True)

print fit

__main__.window.GoToPosition(730)
raw_input('Press enter to continue ')

__main__.f.ClearFit()
spec.RemoveAll()
print "-------------------------------------------------------------------------"
print "Case 7: Change calibration between Fit and Restore"
print "-------------------------------------------------------------------------"
print "SetCal"
spec.SetCal([0,0.5])

print "Fit"
fit = __main__.f.GetActiveFit()
fit.PutRegionMarker(725)
fit.PutRegionMarker(735)
fit.PutPeakMarker(730)
__main__.f.Fit()

print "Saving fits"
__main__.f.StoreFit()
__main__.fitxml.WriteFitlist(testXML)
spec.RemoveAll()

print "Change calibration"
spec.SetCal([0,2])

print "Reading fits"
__main__.fitxml.ReadFitlist(testXML)

print spec[0]
__main__.window.GoToPosition(2920)
raw_input('Press enter to continue ')

__main__.f.ClearFit()
spec.RemoveAll()
print "-------------------------------------------------------------------------"
print "Case 8: Load old calibration during Restore"
print "-------------------------------------------------------------------------"
print "SetCal"
spec.SetCal([0,0.5])

print "Fit"
fit = __main__.f.GetActiveFit()
fit.PutRegionMarker(725)
fit.PutRegionMarker(735)
fit.PutPeakMarker(730)
__main__.f.Fit()

print "Saving fits"
__main__.f.StoreFit()
__main__.fitxml.WriteFitlist(testXML)

print "Change calibration"
spec.SetCal([0,2])

print spec[0]

spec.RemoveAll()
print "Reading fits"
__main__.fitxml.ReadFitlist(testXML, calibrate=True)

print spec[0]
__main__.window.GoToPosition(730)

raw_input("Press enter to continue ")

__main__.f.ClearFit()
spec.RemoveAll()
print "-------------------------------------------------------------------------"
print "Case 9: Pur background fit without calibration"
print "-------------------------------------------------------------------------"
spec.SetCal(None)
fit = __main__.f.GetActiveFit()
fit.PutBgMarker(1440)
fit.PutBgMarker(1450)
fit.PutBgMarker(1470)
fit.PutBgMarker(1480)
__main__.f.Fit(peaks=False)

__main__.window.GoToPosition(1460)

raw_input("Press enter to continue ")

__main__.f.ClearFit()
spec.RemoveAll()
print "-------------------------------------------------------------------------"
print "Case 9: Pur background fit with calibration"
print "-------------------------------------------------------------------------"
print "Set cal"
spec.SetCal([0,0.5])

fit = __main__.f.GetActiveFit()
fit.PutBgMarker(720)
fit.PutBgMarker(725)
fit.PutBgMarker(735)
fit.PutBgMarker(740)
__main__.f.Fit(peaks=False)

__main__.window.GoToPosition(730)

raw_input("Press enter to continue ")

__main__.f.ClearFit()
spec.RemoveAll()


