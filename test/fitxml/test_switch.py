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

from __future__ import print_function

import __main__

spectra = __main__.spectra
spectra.Clear()

testspectrum= os.path.join(__main__.hdtvpath, "test", "fitxml", "osiris_bg.spc")

print("-------------------------------------------------------------------------")
print("Loading 5 spectra and switch back and forth between them")
print("-------------------------------------------------------------------------")

for i in range(0,5):
    __main__.s.LoadSpectra(testspectrum)
    spectra.Get(i).cal=[0,(i+1)*0.5]
__main__.s.ListSpectra()
    
input("Press enter to continue ")

print("Show First")
spectra.ShowFirst()
__main__.s.ListSpectra()

input("Press enter to continue ")

for i in range(0,5):
    print("Show Next (should be %d)" %((i+1)%5))
    spectra.ShowNext()
    __main__.s.ListSpectra()
    input("Press enter to continue ")
    
print("Show Last")
spectra.ShowLast()
__main__.s.ListSpectra()
input("Press enter to continue ")
    
for i in range(0,5):
    print("Show Prev (should be %d)" %(4-(i+1)%5))
    spectra.ShowPrev()
    __main__.s.ListSpectra()
    input("Press enter to continue ")
    
print("Show 3")
spectra.ShowObjects("3")
__main__.s.ListSpectra()
input("Press enter to continue ")

print("Show 1")
spectra.ShowObjects("1")
__main__.s.ListSpectra()
input("Press enter to continue ")

print("Show All")
spectra.ShowAll()
__main__.s.ListSpectra()
input("Press enter to continue ")

print("Activate 2")
spectra.ActivateObject("2")
__main__.s.ListSpectra()
input("Press enter to continue ")

print("Show only active")
spectra.ShowObjects(spectra.activeID)
__main__.s.ListSpectra()
input("Press enter to continue ")

print("Activate 4 (which was not visible)")
spectra.ActivateObject("4")
__main__.s.ListSpectra()
input("Press enter to continue ")

print("Remove 3")
spectra.Pop("3")
__main__.s.ListSpectra()
input("Press enter to continue ")
    
print("Reload one spectrum")
__main__.s.LoadSpectra(testspectrum)
__main__.s.ListSpectra()
input("Press enter to continue ")

for i in range(3,10):
    print("Show Next (should be %d)" %((i+1)%5))
    spectra.ShowNext()
    __main__.s.ListSpectra()
    input("Press enter to continue ")
