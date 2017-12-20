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

import pytest

from test.helpers.utils import redirect_stdout, hdtvcmd

import hdtv.cmdline
import hdtv.options
import hdtv.session

import __main__
# We don’t want to see the GUI. Can we prevent this?
try:
    __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass

#__main__.spectra.window.viewer.CloseWindow()

import hdtv.plugins.rootInterface

@pytest.fixture(autouse=True)
def prepare(request):
    #original_wd = os.path.abspath(os.path.join(__file__, os.pardir))
    original_wd = os.getcwd()
    os.chdir(original_wd)
    yield
    os.chdir(original_wd)

def test_cmd_root_pwd():
    f, ferr = hdtvcmd("root pwd")
    assert f == os.getcwd()

@pytest.mark.parametrize("start, cd, target", [
    ('/', '/tmp', '/tmp'),
    ('/tmp', '..', '/'),
    ('/', 'tmp', '/tmp'),
    ('/tmp', '', '/tmp')])
def test_cmd_root_cd(start, cd, target):
    os.chdir(start)
    hdtvcmd('root cd ' + cd)
    assert os.getcwd() == target

def test_cmd_root_browse():
    hdtvcmd('root browse')
    assert hdtv.plugins.rootInterface.r.browser.GetName() == 'Browser'
    hdtv.plugins.rootInterface.r.browser.SetName('Test')
    assert hdtv.plugins.rootInterface.r.browser.GetName() == 'Test'
    hdtv.plugins.rootInterface.r.browser = None
