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

import pytest

import __main__

import hdtv.session
try:
    __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass
spectra = __main__.spectra

import hdtv.plugins.specInterface
import hdtv.plugins.fitInterface
import hdtv.plugins.fitlist
import hdtv.fitxml

testspectrum = os.path.join(
    os.path.curdir, "tests", "share", "osiris_bg.spc")

test_versions = ['0.1', '1.0', '1.1', '1.3', '1.4']
test_XMLs = [
    os.path.join(os.path.curdir, 'tests', 'share', 'osiris_bg_v' + ver + '.xml')
    for ver in test_versions]

@pytest.fixture(autouse=True)
def prepare():
    __main__.f.ResetFitterParameters()
    hdtv.options.Set("table", "classic")
    hdtv.options.Set("uncertainties", "short")
    __main__.s.LoadSpectra(testspectrum)
    yield
    spectra.Clear()


@pytest.mark.parametrize("xmlfile", test_XMLs)
def test_old_xml(xmlfile):
    __main__.fitxml.ReadXML(spectra.Get("0").ID, xmlfile, refit=True, interactive=False)
    __main__.f.ListFits()

"""
print('Saving fits to file %s' % newXML)
__main__.fitxml.WriteFitlist(newXML)
print('Deleting all fits')
__main__.spectra.dict["0"].Clear()
print('Reading fits from file %s' % newXML)
__main__.fitxml.ReadFitlist(newXML)
__main__.f.ListFits()
"""
