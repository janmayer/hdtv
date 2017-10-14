#!/usr/bin/env python

import io
import os

import pytest

from helpers.utils import redirect_stdout

import hdtv.cmdline
import hdtv.plugins.ls

def test_cmd_pwd():
    f = io.StringIO()
    with redirect_stdout(f):
        hdtv.cmdline.command_line.DoLine("pwd")
    assert f.getvalue().strip() == os.getcwd()

@pytest.mark.parametrize("start, cd, target", [
    ('/', '/tmp', '/tmp'),
    ('/tmp', '..', '/'),
    ('/', 'tmp', '/tmp'),
    ('/', '~', os.path.expanduser("~")),
    ('/tmp', '', os.path.expanduser("~"))])
def test_cmd_cd(start, cd, target):
    os.chdir(start)
    hdtv.cmdline.command_line.DoLine('cd ' + cd)
    assert os.getcwd() == target

def test_cmd_cd_minus():
    hdtv.cmdline.command_line.DoLine('cd /')
    hdtv.cmdline.command_line.DoLine('cd /tmp')
    hdtv.cmdline.command_line.DoLine('cd -')
    assert os.getcwd() == '/'

@pytest.mark.parametrize("cd, output", [
    ('/tmp', '/tmp'),
    ('~', os.path.expanduser("~")),
    ('/', '/')])
def test_cmd_cd_output(cd, output):
    f = io.StringIO()
    with redirect_stdout(f):
        hdtv.cmdline.command_line.DoLine('cd ' + cd)
    assert f.getvalue().strip() == output

def test_cmd_ls():
    os.chdir(os.path.abspath(os.sep))
    f = io.StringIO()
    with redirect_stdout(f):
        hdtv.cmdline.command_line.DoLine("ls")
    assert 'tmp' in f.getvalue()
