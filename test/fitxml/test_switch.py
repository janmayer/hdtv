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

import __main__

spectra = __main__.spectra
spectra.RemoveAll()

testspectrum= os.path.join(__main__.hdtvpath, "test", "fitxml", "osiris_bg.spc")

print "-------------------------------------------------------------------------"
print "Case 0: Loading 5 spectra and switch back and forth between them"
print "-------------------------------------------------------------------------"

for i in range(0,5):
    __main__.s.LoadSpectra(testspectrum)
    spectra[i].cal=[0,(i+1)*0.5]
spectra.ListObjects()
    
raw_input("Press enter to continue ")

print "Show First"
spectra.ShowFirst()
spectra.ListObjects()

raw_input("Press enter to continue ")

for i in range(0,5):
    print "Show Next (should be %d)" %((i+1)%5)
    spectra.ShowNext()
    spectra.ListObjects()
    raw_input("Press enter to continue ")
    
print "Show Last"
spectra.ShowLast()
spectra.ListObjects()
raw_input("Press enter to continue ")
    
for i in range(0,5):
    print "Show Prev (should be %d)" %(4-(i+1)%5)
    spectra.ShowPrev()
    spectra.ListObjects()
    raw_input("Press enter to continue ")
    
print "Show 3"
spectra.ShowObjects(3)
spectra.ListObjects()
raw_input("Press enter to continue ")

print "Show 1"
spectra.ShowObjects(1)
spectra.ListObjects()
raw_input("Press enter to continue ")

print "Show All"
spectra.ShowAll()
spectra.ListObjects()
raw_input("Press enter to continue ")

print "Activate 2"
spectra.ActivateObject(2)
spectra.ListObjects()
raw_input("Press enter to continue ")

print "Show only active"
spectra.ShowObjects(spectra.activeID)
spectra.ListObjects()
raw_input("Press enter to continue ")

print "Activate 4 (which was not visible)"
spectra.ActivateObject(4)
spectra.ListObjects()
raw_input("Press enter to continue ")
    

print "-------------------------------------------------------------------------"
print "Case 1: Fit and switch spectrum afterwards"
print "-------------------------------------------------------------------------"
print "Activate first spectrum"
__main__.spectra.ShowObjects([0])
__main__.spectra.ActivateObject(0)

fit = __main__.f.GetActiveFit()
fit.PutRegionMarker(725)
fit.PutRegionMarker(735)
fit.PutPeakMarker(730)
__main__.f.Fit(peaks=True)

__main__.window.GoToPosition(730)

raw_input("Press enter to continue ")

print "Show second spectrum"
__main__.spectra.ShowObjects([1])

raw_input("Press enter to continue ")

print "Show again first spectrum"
__main__.spectra.ShowObjects([0])

raw_input("Press enter to continue ")

print "Activate first spectrum"
__main__.spectra.ActivateObject(0)

raw_input("Press enter to continue ")

__main__.f.ClearFit()
spectra[0].RemoveAll()
print "-------------------------------------------------------------------------"
print "Case 2: Fit, store and switch spectrum afterwards"
print "-------------------------------------------------------------------------"
print "Activate first spectrum"
__main__.spectra.ShowObjects([0])
__main__.spectra.ActivateObject(0)


fit = __main__.f.GetActiveFit()
fit.PutRegionMarker(725)
fit.PutRegionMarker(735)
fit.PutPeakMarker(730)
__main__.f.Fit(peaks=True)
__main__.f.StoreFit()

__main__.window.GoToPosition(730)

raw_input("Press enter to continue ")

print "Show second spectrum"
__main__.spectra.ShowObjects([1])

raw_input("Press enter to continue ")

print "Show again first spectrum"
__main__.spectra.ShowObjects([0])

raw_input("Press enter to continue ")

print "Activate first spectrum"
__main__.spectra.ActivateObject(0)

raw_input("Press enter to continue ")

__main__.f.ClearFit()
spectra[0].RemoveAll()
print "-------------------------------------------------------------------------"
print "Case 3: Background fit and switch spectrum afterwards"
print "-------------------------------------------------------------------------"
print "Activate first spectrum"
__main__.spectra.ShowObjects([0])
__main__.spectra.ActivateObject(0)

fit = __main__.f.GetActiveFit()
fit.PutBgMarker(720)
fit.PutBgMarker(725)
fit.PutBgMarker(735)
fit.PutBgMarker(740)
__main__.f.Fit(peaks=False)


__main__.window.GoToPosition(730)

raw_input("Press enter to continue ")

print "Show second spectrum"
__main__.spectra.ShowObjects([1])

raw_input("Press enter to continue ")

print "Show again first spectrum"
__main__.spectra.ShowObjects([0])

raw_input("Press enter to continue ")

print "Activate first spectrum"
__main__.spectra.ActivateObject(0)

raw_input("Press enter to continue ")

__main__.f.ClearFit()
spectra.RemoveAll()
