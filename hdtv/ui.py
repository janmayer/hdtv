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

# ----------------------------------------------------------------------
# Basic user interface functions (Input/Output, etc)
# ----------------------------------------------------------------------

import sys
import os

import hdtv.options
from hdtv.color import tcolors


class SimpleUI(object):
    """
    Very simple UserInterface
    """

    def __init__(self):
        #
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.stdin = sys.stdin
        self.debugout = self.stderr

        self.linesep = os.linesep

    def msg(self, text, newline=True):
        self.stdout.write(text)

        if newline and text and text[-1] != self.linesep:
            self.stdout.write(self.linesep)

    def info(self, text, newline=True):
        """
        Print informational message
        """
        text = "INFO: " + text
        self.stdout.write(text)

        if newline:
            self.stdout.write(self.linesep)

    def warn(self, text, newline=True):
        """
        Print warning message
        """
        self.stderr.write(tcolors.WARNING + "WARNING: " + text + tcolors.ENDC)

        if newline:
            self.stderr.write(self.linesep)

    def error(self, text, newline=True):
        """
        Print error message
        """
        self.stderr.write(tcolors.FAIL + "ERROR: " + text + tcolors.ENDC)

        if newline:
            self.stderr.write(self.linesep)

    def debug(self, text, level=1, newline=True):
        """
        Debugging output. The higher the level, the more specific is
        the debug message.
        """
        self.debugout.write(tcolors.DEBUG + "DEBUG: " + text + tcolors.ENDC)

        if newline:
            self.debugout.write(self.linesep)

    def newline(self):
        self.msg("", newline=True)


# Initialization
ui = SimpleUI()


def msg(text, newline=True):
    ui.msg(text, newline=newline)


def info(text, newline=True):
    ui.info(text, newline=newline)


def warn(text, newline=True):
    ui.warn(text, newline=newline)


def error(text, newline=True):
    ui.error(text, newline=newline)


def debug(text, level=1, newline=True):
    if level > hdtv.options.Get('debuglevel'):
        return
    else:
        ui.debug(text, level=level, newline=newline)


def newline():
    ui.newline()


opt = hdtv.options.Option(
    default=0,
    parse=lambda x: int(x))
hdtv.options.RegisterOption('debuglevel', opt)
