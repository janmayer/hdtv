# -*- coding: utf-8 -*-

import io

import pytest

from helpers.utils import redirect_stdout

import hdtv.cmdline
import hdtv.options
import hdtv.window
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
import hdtv.plugins.config
import hdtv.plugins.dblookup
import hdtv.plugins.fittex
import hdtv.plugins.matInterface
import hdtv.plugins.rootInterface
import hdtv.plugins.run
import hdtv.plugins.fitlist
import hdtv.plugins.printing

cmdlist = [
    "calibration efficiency fit",
    "calibration efficiency list",
    "calibration efficiency plot",
    "calibration efficiency read covariance",
    "calibration efficiency read parameter",
    "calibration efficiency set",
    "calibration efficiency write covariance",
    "calibration efficiency write parameter",
    "calibration position assign",
    "calibration position copy",
    "calibration position enter",
    "calibration position list",
    "calibration position list clear",
    "calibration position list read",
    "calibration position list write",
    "calibration position nuclide",
    "calibration position read",
    "calibration position recalibrate",
    "calibration position set",
    "calibration position unset",
    "config reset",
    "config set",
    "config show",
    "cut activate",
    "cut clear",
    "cut delete",
    "cut execute",
    "cut hide",
    "cut marker",
    "cut show",
    "cut store",
    "db info",
    "db list",
    "db lookup",
    "db set",
    "fit activate",
    "fit clear",
    "fit delete",
    "fit execute",
    "fit focus",
    "fit function peak activate",
    "fit getlists",
    "fit hide",
    "fit hide decomposition",
    "fit list",
    "fit marker",
    "fit parameter",
    "fit peakfind",
    "fit position assign",
    "fit position erase",
    "fit position map",
    "fit read",
    "fit savelists",
    "fit show",
    "fit show decomposition",
    "fit store",
    "fit tex",
    "fit write",
    #"matrix delete",
    "matrix get",
    "matrix list",
    #"matrix project",
    "matrix view",
    "nuclide",
    "print",
    "root cut delete",
    "root cut view",
    "root get",
    "root matrix get",
    "root matrix view",
    "spectrum activate",
    "spectrum add",
    "spectrum calbin",
    "spectrum copy",
    "spectrum delete",
    "spectrum get",
    "spectrum hide",
    "spectrum info",
    "spectrum list",
    "spectrum multiply",
    "spectrum name",
    "spectrum normalize",
    "spectrum rebin",
    "spectrum show",
    "spectrum substract",
    "spectrum update",
    "spectrum write",
    "window view center",
    "window view region",
]

@pytest.mark.parametrize("command", cmdlist)
def test_cmd_help(command):
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("{} --help".format(command))
    assert ferr.getvalue().strip() == ""
    assert "usage" in f.getvalue()
    assert "--help" in f.getvalue()

@pytest.mark.parametrize("command", cmdlist)
def test_cmd_unrecognized_arg(command):
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("{} --invalidarg".format(command))
    assert "ERROR" in ferr.getvalue().strip()
    assert "usage" in f.getvalue()
