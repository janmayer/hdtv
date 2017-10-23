# -*- coding: utf-8 -*-

import io
import re
import os
import sys

import pytest

from helpers.utils import redirect_stdout

from hdtv.cmdline import command_line
import hdtv.options
import hdtv.session

import __main__
# We don’t want to see the GUI. Can we prevent this?
try:
    __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass


import hdtv.plugins.specInterface
import hdtv.plugins.calInterface
import hdtv.plugins.fitInterface
import hdtv.plugins.peakfinder
import hdtv.plugins.fitmap

s = __main__.s

@pytest.yield_fixture(autouse=True)
def prepare():
    for (ID, _) in dict(s.spectra.dict).items():
        s.spectra.Pop(ID)

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_fit_position(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    command_line.DoLine("fit peakfind -a -t 0.005")
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("fit position assign 3.0 1173.228(3) 5.0 1332.492(4)")
        command_line.DoLine("fit position erase 3.0 5.0")
    assert ferr.getvalue().strip() == ""

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_fit_position_map(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    command_line.DoLine("fit peakfind -a -t 0.005")
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("fit position map test/share/example_Co60.map")
    assert ferr.getvalue().strip() == ""
    assert "Mapped 2 energies to peaks" in f.getvalue()
