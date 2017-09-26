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

import os
import glob
import __main__

spectra = __main__.spectra
spectra.Clear()

testspectrum = os.path.join(
    __main__.hdtvpath, "test", "fitxml", "osiris_bg.spc")

fnames = os.path.join(__main__.hdtvpath, "test", "fitxml", "osiris_bg_v*.xml")
testXMLs = sorted(glob.glob(fnames))

newXML = os.path.join(__main__.hdtvpath, "test", "fitxml", "osiris_bg.xml")

__main__.s.LoadSpectra(testspectrum)
__main__.s.ListSpectra()

input("Press enter to continue\n")

for testXML in testXMLs:
    spectra.dict["0"].Clear()
    print('Reading fits from file %s' % testXML)
    __main__.fitxml.ReadFitlist(testXML)
    __main__.f.ListFits()
    input("Press enter to continue\n")

print('Saving fits to file %s' % newXML)
__main__.fitxml.WriteFitlist(newXML)
print('Deleting all fits')
__main__.spectra.dict["0"].Clear()
print('Reading fits from file %s' % newXML)
__main__.fitxml.ReadFitlist(newXML)
__main__.f.ListFits()

input("Press enter to continue\n")
