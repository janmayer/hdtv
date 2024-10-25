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
For each model implemented on the C++ side, we have a corresponding Python
class to handle fitter setup and data transfer to the Python side
"""


# Base class for all background models
class BackgroundModel:
    """
    A background model is a function used to fit the quasi-continuous background
    of a spectrum. The user can choose how to fit its parameters (and whether to
    include them at all). After everything has been configured, the background
    model produces a C++ fitter object.
    """

    def __init__(self):
        self.fGlobalParams = {}
        self.requiredBgRegions = 1

    def ResetGlobalParams(self):
        self.fGlobalParams.clear()

    def OptionsStr(self):
        """
        Returns a string describing the currently set parameters of the model
        """
        statstr = ""

        for name, status in self.fParStatus.items():
            # Short format for multiple values...
            if isinstance(status, list):
                statstr += "%s: " % name
                sep = ""
                for stat in status:
                    statstr += sep
                    if stat in ("free", "equal", "hold", "none", "calculated"):
                        statstr += stat
                    else:
                        statstr += "%.3f" % stat
                    sep = ", "
                statstr += "\n"

            # ... long format for a single value
            else:
                if status == "free":
                    statstr += "%s: (individually) free\n" % name
                elif status == "equal":
                    statstr += "%s: free and equal\n" % name
                elif status == "hold":
                    statstr += "%s: held at default value\n" % name
                elif status == "none":
                    statstr += "%s: none (disabled)\n" % name
                elif status == "calculated":
                    statstr += "%s: calculated from fit result\n" % name
                else:
                    statstr += f"{name}: fixed at {status:.3f}\n"

        return statstr

    def ParseParamStatus(self, parname, status):
        """
        Parse a parameter status specification string
        Raises ValueError when the status is not legal for this parameter
        """
        # Case-insensitive matching
        status = status.strip().lower()

        # Check to see if status corresponds, possibly abbreviated,
        #  to a number of special keywords
        stat = None
        if len(status) < 1:
            raise ValueError
        elif "free"[0 : len(status)] == status:
            stat = "free"

        # If status was a keyword, see if this setting is legal for the
        # parameter
        if stat is not None:
            if stat not in self.fValidParStatus[parname]:
                msg = f"Status {stat} not allowed for parameter {parname} in peak model {self.name}"
                raise ValueError(msg)
            return stat

        # If status was not a keyword, try to parse it as an integer. If that
        # fails, we are out of options.
        try:
            val = int(status)
        except ValueError:
            msg = "Failed to parse status specifier `%s'" % status
            raise ValueError(msg)

        # Check if a numeric value is legal for the parameter
        if int not in self.fValidParStatus[parname]:
            msg = f"Invalid status {status} for parameter {parname} in peak model {self.name}"
            raise ValueError(msg)
        return val

    def SetParameter(self, parname, status):
        """
        Set status for a certain parameter. Status is a string describing the
        desired status. Raises ValueError in case of invalid input.

        status may be a string or a number, depending on the parameter type
        """
        parname = parname.strip().lower()

        if parname not in list(self.fValidParStatus.keys()):
            raise ValueError(
                f"Invalid parameter name {parname} for background model {self.name}"
            )

        self.fParStatus[parname] = self.ParseParamStatus(parname, status)
