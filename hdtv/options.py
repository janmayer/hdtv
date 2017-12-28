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
# Infrastructure for configuration variables
# ----------------------------------------------------------------------

from collections import OrderedDict
from hdtv.color import tcolors

class Option(object):
    """
    A configuration variable
    """

    def __init__(self, default=None,
                 parse=lambda x: x,
                 toStr=lambda x: str(x),
                 changeCallback=None):
        self.defaultValue = default
        self.value = self.defaultValue
        self.parse = parse
        self.ToStr = toStr
        self.ChangeCallback = changeCallback

    def __bool__(self):
        """
        How to convert option to 'bool'
        """
        return bool(self.value)

    def Set(self, value):
        """
        Set the variable to the specified value
        """
        self.value = value
        if self.ChangeCallback:
            self.ChangeCallback(self)

    def ParseAndSet(self, rawValue):
        """
        Parses rawValue and sets the variable to the result
        """
        self.Set(self.parse(rawValue))

    def Get(self):
        """
        Return the value of the variable
        """
        return self.value

    def Reset(self):
        """
        Reset the variable to its default value
        """
        self.Set(self.defaultValue)

    def __str__(self):
        """
        Returns the value as a string
        """
        return self.ToStr(self.value)


def RegisterOption(varname, variable):
    """
    Adds a configuration variable
    """
    global variables
    if varname in list(variables.keys()):
        raise RuntimeError(
            "Refusing to overwrite existing configuration variable")
    variables[varname] = variable


def Set(varname, rawValue):
    """
    Sets the variable specified by varname. Raises a KeyError if it does not exist.
    """
    global variables
    variables[varname].ParseAndSet(rawValue)


def Get(varname):
    """
    Gets the value of the variable varname. Raises a KeyError if it does not exist.
    """
    global variables
    return variables[varname].Get()


def Reset(varname):
    """
    Resets value of variable varname to default. Raises KeyError if it does not exist.
    """
    global variables
    return variables[varname].Reset()


def ResetAll():
    """
    Resets value of all variables to default.
    """
    global variables
    for (k, v) in variables.items():
        variables[k].Reset()


def Show(varname):
    """
    Shows the value of the variable varname
    """
    global variables
    return "%s: %s" % (tcolors.bold(varname), str(variables[varname]))


def Str():
    """
    Returns all options as a string
    """
    global variables
    string = ""
    ordered_options = OrderedDict(sorted(variables.items()))
    for (k, v) in ordered_options.items():
        string += "%s: %s\n" % (tcolors.bold(k), str(v))
    return string


def parse_bool(x):
    """
    Parse boolean options
    """
    if x.lower() == "true":
        return True
    elif x.lower() == "false":
        return False
    else:
        raise ValueError("Valid options: True, False.")

def parse_choices(choices):
    def _parse_choices(x):
        if x in choices:
            return x
        else:
            raise ValueError("Valid options: " + ", ".join(choices) + ".")
    return _parse_choices



variables = dict()
