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
ID = spec.GetFreeID()
spec[ID]=fit
spec.ActivateObject(ID)
fit.Draw(spec.viewport)

print fit

__main__.window.GoToPosition(1460)
raw_input('Press enter to continue ')

spec.RemoveAll()
spec.SetCal(None)
print "-------------------------------------------------------------------------"
print "Case 2: set cal after Restore and Draw"
print "-------------------------------------------------------------------------"
print "Restore fit"
f = hdtv.fitxml.FitXml(spectra)
(fit, success) = f.Xml2Fit(fitElement)
fit.Restore(spec)

print "Draw"
ID = spec.GetFreeID()
spec[ID]=fit
spec.ActivateObject(ID)
fit.Draw(spec.viewport)

print "SetCal"
spec.SetCal([0,2])

print fit

__main__.window.GoToPosition(2920)
raw_input('Press enter to continue ')

spec.RemoveAll()
spec.SetCal(None)
print "-------------------------------------------------------------------------"
print "Case 3: set cal before Restore and Draw"
print "-------------------------------------------------------------------------"
print "SetCal"
spec.SetCal([0,0.5])


print "Restore fit"
f = hdtv.fitxml.FitXml(spectra)
(fit, success) = f.Xml2Fit(fitElement)
fit.Restore(spec)

print "Draw"
ID = spec.GetFreeID()
spec[ID]=fit
spec.ActivateObject(ID)
fit.Draw(spec.viewport)

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
fit.FitPeakFunc(spec)

print "Draw"
ID = spec.GetFreeID()
spec[ID]=fit
spec.ActivateObject(ID)
fit.Draw(spec.viewport)

print fit

__main__.window.GoToPosition(1460)
raw_input('Press enter to continue ')

spec.RemoveAll()
spec.SetCal(None)
print "-------------------------------------------------------------------------"
print "Case 5: SetCal after Fit and Draw"
print "-------------------------------------------------------------------------"
print "Fit"
fit = __main__.f.GetActiveFit()
fit.PutRegionMarker(1450)
fit.PutRegionMarker(1470)
fit.PutPeakMarker(1460)
fit.FitPeakFunc(spec)

print "Draw"
ID = spec.GetFreeID()
spec[ID]=fit
spec.ActivateObject(ID)
fit.Draw(spec.viewport)

print "SetCal"
spec.SetCal([0,2])

print fit

__main__.window.GoToPosition(2920)
raw_input('Press enter to continue ')

spec.RemoveAll()
print "-------------------------------------------------------------------------"
print "Case 6: SetCal before Fit and Draw"
print "-------------------------------------------------------------------------"
print "SetCal"
spec.SetCal([0,0.5])

print "Fit"
fit = __main__.f.GetActiveFit()
fit.PutRegionMarker(725)
fit.PutRegionMarker(735)
fit.PutPeakMarker(730)
fit.FitPeakFunc(spec)

print "Draw"
ID = spec.GetFreeID()
spec[ID]=fit
spec.ActivateObject(ID)
fit.Draw(spec.viewport)

print fit

__main__.window.GoToPosition(730)
