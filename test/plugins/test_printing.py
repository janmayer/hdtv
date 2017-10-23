# -*- coding: utf-8 -*-

import io
import os
import tempfile

import pytest

from helpers.utils import redirect_stdout

import hdtv.cmdline
import hdtv.options
import hdtv.session

import __main__
# We don’t want to see the GUI. Can we prevent this?
try:
    __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass

import hdtv.plugins.printing

def test_cmd_printing():
    try:
        outfile = tempfile.mkstemp(".svg", "hdtv_ptest_")[1]
        f = io.StringIO()
        ferr = io.StringIO()
        with redirect_stdout(f, ferr):
            hdtv.cmdline.command_line.DoLine(
                "print -y 'my_ylabel' -x 'my_xlabel' -t 'my_title' -F {}".format(outfile))
        assert f.getvalue().strip() == ""
        assert ferr.getvalue().strip() == ""
        with open(outfile, 'r') as fout:
            result = fout.read()
        assert 'my_ylabel' in result
        assert 'my_xlabel' in result
        assert 'my_title' in result
    finally:
        os.remove(outfile)

@pytest.mark.parametrize("fmt", [
    "eps", "pdf", "png", "ps", "raw", "rgba", "svg",
    "svgz", "jpeg", "tiff"])
def test_cmd_printing_formats(fmt):
    try:
        outfile = tempfile.mkstemp("." + fmt, "hdtv_pftest_")[1]
        f = io.StringIO()
        ferr = io.StringIO()
        with redirect_stdout(f, ferr):
            hdtv.cmdline.command_line.DoLine(
                "print -y 'my_ylabel' -x 'my_xlabel' -t 'my_title' -F {}".format(outfile))
        assert f.getvalue().strip() == ""
        assert ferr.getvalue().strip() == ""
    finally:
        os.remove(outfile)
