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

import pytest

from hdtv.util import monkey_patch_ui

monkey_patch_ui()

import __main__
import hdtv.session

try:
    __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass
spectra = __main__.spectra

from hdtv.plugins.fitInterface import fit_interface
from hdtv.plugins.fitlist import fitxml
from hdtv.plugins.specInterface import spec_interface

testspectrum = os.path.join(os.path.curdir, "tests", "share", "osiris_bg.spc")

test_versions = ["0.1", "1.0", "1.1", "1.3", "1.4", "1.5"]

test_XMLs = [
    os.path.join(os.path.curdir, "tests", "share", "osiris_bg_v" + ver + ".xml")
    for ver in test_versions
]


@pytest.fixture(autouse=True)
def prepare():
    fit_interface.ResetFitterParameters()
    hdtv.options.Set("table", "classic")
    hdtv.options.Set("uncertainties", "short")
    spec_interface.LoadSpectra(testspectrum)
    yield
    spectra.Clear()


@pytest.mark.parametrize("xmlfile", test_XMLs)
def test_old_xml(xmlfile):
    # Check whether hdtv recognizes the format of the XML file at all
    # by invoking the general ReadXML function.
    # Note that this does not ensure the correct reading of the XML file.
    fitxml.ReadXML(spectra.Get("0").ID, xmlfile, refit=True, interactive=False)


"""
print('Saving fits to file %s' % newXML)
fitxml.WriteFitlist(newXML)
print('Deleting all fits')
__main__.spectra.dict["0"].Clear()
print('Reading fits from file %s' % newXML)
fitxml.ReadFitlist(newXML)
fit_interface.ListFits()
"""
