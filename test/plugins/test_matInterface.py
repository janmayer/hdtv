# -*- coding: utf-8 -*-

import io
import re
import os
import sys
import warnings
import tempfile
import shutil

import pytest

from helpers.utils import redirect_stdout

import hdtv.cmdline
import hdtv.options
import hdtv.session

import __main__
# We don’t want to see the GUI. Can we prevent this?
try:
    if not __main__.spectra:
        __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass

import hdtv.plugins.specInterface
import hdtv.plugins.matInterface

s = __main__.s

@pytest.yield_fixture(autouse=True)
def prepare():
    hdtv.options.Set("table", "classic")
    hdtv.options.Set("uncertainties", "short")
    for (ID, _) in dict(s.spectra.dict).items():
        s.spectra.Pop(ID)

@pytest.mark.skip(reason="need example matrix")
def test_cmd_matrix_get_sym(matrix):
    raise NotImplementedError

@pytest.mark.skip(reason="need example matrix")
def test_cmd_matrix_get_asym(matrix):
    raise NotImplementedError

@pytest.mark.skip(reason="need example matrix")
def test_cmd_matrix_list(matrix):
    raise NotImplementedError

@pytest.mark.skip(reason="need example matrix; hard to test")
def test_cmd_matrix_view(matrix):
    raise NotImplementedError

@pytest.mark.skip(reason="need example matrix")
def test_cmd_cut_marker(matrix):
    raise NotImplementedError

@pytest.mark.skip(reason="need example matrix")
def test_cmd_cut_execute(matrix):
    raise NotImplementedError

@pytest.mark.skip(reason="need example matrix")
def test_cmd_cut_activate(matrix):
    raise NotImplementedError

@pytest.mark.skip(reason="need example matrix")
def test_cmd_cut_clear(matrix):
    raise NotImplementedError

@pytest.mark.skip(reason="need example matrix")
def test_cmd_cut_store(matrix):
    raise NotImplementedError

@pytest.mark.skip(reason="need example matrix")
def test_cmd_cut_delete(matrix):
    raise NotImplementedError
