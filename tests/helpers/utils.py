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

import contextlib
import sys

try:  # Python2
    from StringIO import StringIO
except ImportError:  # Python3
    from io import StringIO

import hdtv.cmdline
from hdtv.ui import ui


def setup_io(num=1):
    """
    Setup several StringIOs that can be used for stdout redirection.
    """
    return [StringIO() for _ in range(num)]


@contextlib.contextmanager
def redirect_stdout(target_out, target_err=None, target_debug=None):
    original_out = sys.stdout
    original_out_hdtv = ui.stdout
    sys.stdout = target_out
    ui.stdout = target_out
    if target_err:
        original_err = sys.stderr
        sys.stderr = target_err
        original_err_hdtv = ui.stderr
        ui.stderr = target_err
    if target_debug:
        original_debug_hdtv = ui.debugout
        ui.debugout = target_debug
    yield
    sys.stdout = original_out
    ui.stdout = original_out_hdtv
    if target_err:
        sys.stderr = original_err
        ui.stderr = original_err_hdtv
    if target_debug:
        ui.debugout = original_debug_hdtv


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    """
    Determine if two floats are close to each other.
    """
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def hdtvcmd(*commands):
    """
    Execute hdtv command(s) and return stdout and stderr output.
    """
    f, ferr = setup_io(2)
    with redirect_stdout(f, ferr):
        for command in commands:
            hdtv.cmdline.command_line.DoLine(command)
    return f.getvalue().strip(), ferr.getvalue().strip()
