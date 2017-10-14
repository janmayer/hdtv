#!/usr/bin/env python

import io
import os

import pytest

from helpers.utils import redirect_stdout

import hdtv.cmdline
import hdtv.options
import hdtv.session

import __main__
__main__.spectra = hdtv.session.Session()

# We don’t want to see the GUI. Can we prevent this?
__main__.spectra.window.viewer.CloseWindow()

import hdtv.plugins.rootInterface


def test_cmd_root_pwd():
    f = io.StringIO()
    with redirect_stdout(f):
        hdtv.cmdline.command_line.DoLine("root pwd")
    assert f.getvalue().strip() == os.getcwd()

@pytest.mark.parametrize("start, cd, target", [
    ('/', '/tmp', '/tmp'),
    ('/tmp', '..', '/'),
    ('/', 'tmp', '/tmp'),
    ('/tmp', '', '/tmp')])
def test_cmd_root_cd(start, cd, target):
    os.chdir(start)
    hdtv.cmdline.command_line.DoLine('root cd ' + cd)
    assert os.getcwd() == target

def test_cmd_root_browse():
    hdtv.cmdline.command_line.DoLine('root browse')
    assert hdtv.plugins.rootInterface.r.browser.GetName() == 'Browser'
    hdtv.plugins.rootInterface.r.browser.GetName('Test')
    assert hdtv.plugins.rootInterface.r.browser.GetName() == 'Test'
    hdtv.plugins.rootInterface.r.browser = None
