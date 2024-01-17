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

"""
Infrastructure for configuration variables
"""

from html import escape


class Option:
    """
    A configuration variable
    """

    def __init__(
        self,
        default=None,
        parse=lambda x: x,
        toStr=lambda x: str(x),
        changeCallback=None,
    ):
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


class _OptionManager(dict):
    """Manages a set of options"""

    def RegisterOption(self, varname, value):
        """
        Adds a configuration variable
        """
        if varname in self.__dict__:
            msg = "Option {!r} already exists with, refusing to overWrite"
            raise RuntimeError(msg.format(varname))
        self.__dict__[varname] = value

    def Set(self, varname, rawValue):
        """
        Sets the variable specified by varname. Raises a KeyError if it does not exist.
        """
        self.__dict__[varname].ParseAndSet(rawValue)

    def Get(self, varname):
        """
        Gets the value of the variable varname. Raises a KeyError if it does not exist.
        """
        return self.__dict__[varname].Get()

    def Reset(self, varname):
        """
        Resets value of variable varname to default. Raises KeyError if it does not exist.
        """
        self.__dict__[varname].Reset()

    def ResetAll(self):
        """
        Resets value of all variables to default.
        """
        for key in self.__dict__.keys():
            self.__dict__[key].Reset()

    def Show(self, varname):
        """
        Shows the value of the variable varname
        """
        return f"<b>{escape(varname)}</b>: {escape(str(self.__dict__[varname]))}"

    def Str(self):
        """
        Returns all options as a string
        """
        string = ""
        for k, v in sorted(self.__dict__.items()):
            string += f"<b>{escape(k)}</b>: {escape(str(v))}\n"
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


OptionManager = _OptionManager()

RegisterOption = OptionManager.RegisterOption
Set = OptionManager.Set
Get = OptionManager.Get
Reset = OptionManager.Reset
ResetAll = OptionManager.ResetAll
Show = OptionManager.Show
Str = OptionManager.Str
