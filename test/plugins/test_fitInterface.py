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
import hdtv.plugins.fitInterface
import hdtv.plugins.peakfinder

s = __main__.s

@pytest.yield_fixture(autouse=True)
def prepare():
    hdtv.options.Set("table", "classic")
    hdtv.options.Set("uncertainties", "short")
    for (ID, _) in dict(s.spectra.dict).items():
        s.spectra.Pop(ID)

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_fit_various(specfile):
    command_line.DoLine("fit function peak activate theuerkauf")
    s.tv.specIf.LoadSpectra(specfile, None)
    assert len(s.spectra.dict) == 1
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        setup_fit()
    assert f.getvalue().strip() == ""
    assert ferr.getvalue().strip() == ""
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("fit execute 0")
    assert "WorkFit on spectrum: 0" in f.getvalue()
    assert "WARNING: Non-existent id 0" in ferr.getvalue()
    assert ".0 |" in f.getvalue()
    assert ".1 |" in f.getvalue()
    assert "2 peaks in WorkFit" in f.getvalue()
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("fit store")
    assert f.getvalue().strip() == "Storing workFit with ID 0"
    assert ferr.getvalue().strip() == ""
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("fit clear")
        command_line.DoLine("fit list")
    assert ferr.getvalue().strip() == ""
    assert "Fits in Spectrum 0" in f.getvalue().strip()
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("fit hide 0")
        command_line.DoLine("fit show 0")
        command_line.DoLine("fit show decomposition 0")
        command_line.DoLine("fit hide decomposition 0")
    assert ferr.getvalue().strip() == ""
    assert f.getvalue().strip() == ""
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("fit activate 0")
    assert "Activating fit 0" in f.getvalue().strip()
    assert ferr.getvalue().strip() == ""
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("fit delete 0")
        command_line.DoLine("fit function peak activate ee")
    assert ferr.getvalue().strip() == ""
    assert f.getvalue().strip() == ""

@pytest.mark.parametrize("specfile", [
    "test/share/example_Co60.tv"])
def test_cmd_fit_peakfind(specfile):
    s.tv.specIf.LoadSpectra(specfile, None)
    assert len(s.spectra.dict) == 1
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        command_line.DoLine("fit peakfind -a -t 0.005")
    assert "Search Peaks in region" in f.getvalue()
    assert "Found 8 peaks" in f.getvalue()
    assert ferr.getvalue().strip() == ""

def setup_fit():
    command_line.DoLine("fit parameter background set 2")
    command_line.DoLine("fit marker peak set 1543")
    command_line.DoLine("fit marker peak set 1747")
    command_line.DoLine("fit marker background set 1400")
    command_line.DoLine("fit marker background set 1520")
    command_line.DoLine("fit marker background set 1760")
    command_line.DoLine("fit marker background set 1860")
    command_line.DoLine("fit marker region set 1520")
    command_line.DoLine("fit marker region set 1760")


# More tests are still needed for:
#
# fit focus
# fit getlists
# fit read
# fit savelists
# fit tex
# fit write
