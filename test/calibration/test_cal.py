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


import os
import __main__

def GetCal(cal):
    polynome = list()
    for p in cal.GetCoeffs():
        polynome.append(p)
    return polynome

spectra = __main__.spectra
spectra.RemoveAll()

testspectrum= os.path.join(__main__.hdtvpath, "test", "calibration", "osiris_bg.spc")
testXML = os.path.join(__main__.hdtvpath, "test", "calibration", "osiris_bg.xml")

__main__.s.LoadSpectra(testspectrum)
spec = spectra[0]

__main__.f.SetPeakModel("theuerkauf", default=True)
__main__.f.ResetParameters(default=True)
fit = __main__.f.GetActiveFit()
fit.PutRegionMarker(1450)
fit.PutRegionMarker(1470)
fit.PutPeakMarker(1460)
__main__.f.Fit()
__main__.f.KeepFit()

print "\ninitial state: no calibration: ", GetCal(spec.cal)
print "calibration of fit: ", GetCal(spec[0].cal)
print "calibration of peak marker: ", GetCal(spec[0].peakMarkers[0].cal)
print "calibration of peak: ", GetCal(fit.peaks[0].cal)
print spec[0]

# 1. Calibrate after fitting
print '\n\n\ncase 1: Calibrate after fitting'
print 'set new calibration'
spec.SetCal([0,2])
print "\ncalibration is: ", GetCal(spec.cal)
print "calibration of fit: ", GetCal(spec[0].cal)
print "calibration of peak marker: ", GetCal(spec[0].peakMarkers[0].cal)
print "calibration of peak: ", GetCal(spec[0].peaks[0].cal)
print spec[0]


# 2. Save and restore fit
print '\n\n\ncase 2: Save and restore fit'
print 'Saving fits to file'
__main__.fitxml.WriteFitlist(testXML)
print 'Deleting all fits'
__main__.spectra[0].RemoveObjects(spectra[0].keys())
print 'Reading fits from file'
__main__.fitxml.ReadFitlist(testXML)

print "\ncalibration is: ", GetCal(spec.cal)
print "calibration of fit: ", GetCal(spec[0].cal)
print "calibration of peak marker: ", GetCal(spec[0].peakMarkers[0].cal)
print "calibration of peak: ", GetCal(spec[0].peaks[0].cal)
print spec[0]

# 3. Change calibration after fit
print '\n\n\ncase 3: Change calibration after fit'
print 'Deleting all fits'
__main__.spectra[0].RemoveObjects(spectra[0].keys())
print 'new fit'
__main__.f.SetPeakModel("theuerkauf", default=True)
__main__.f.ResetParameters(default=True)
fit = __main__.f.GetActiveFit()
fit.PutRegionMarker(2900)
fit.PutRegionMarker(2940)
fit.PutPeakMarker(2920)
__main__.f.Fit()
__main__.f.KeepFit()
print 'Set new calibration'
spec.SetCal([0,4])

print "\ncalibration is: ", GetCal(spec.cal)
print "calibration of fit: ", GetCal(spec[0].cal)
print "calibration of peak marker: ", GetCal(spec[0].peakMarkers[0].cal)
print "calibration of peak: ", GetCal(spec[0].peaks[0].cal)
print spec[0]


# 4. Save and restore fit
print '\n\n\ncase 4: Save and restore fit again'
print 'Saving fits to file'
__main__.fitxml.WriteFitlist(testXML)
print 'Deleting all fits'
__main__.spectra[0].RemoveObjects(spectra[0].keys())
print 'Reading fits from file'
__main__.fitxml.ReadFitlist(testXML)

print "\ncalibration is: ", GetCal(spec.cal)
print "calibration of fit: ", GetCal(spec[0].cal)
print "calibration of peak marker: ", GetCal(spec[0].peakMarkers[0].cal)
print "calibration of peak: ", GetCal(spec[0].peaks[0].cal)
print spec[0]



