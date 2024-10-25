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

import ROOT


# Base class for all peak models
class PeakModel:
    """
    A peak model is a function used to fit peaks. The user can choose how to fit
    its parameters (and whether to include them at all, i.e. for tails). After
    everything has been configured, the peak model produces a C++ fitter object.
    """

    def __init__(self):
        self.fGlobalParams = {}

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

        for name, status in self.fOptStatus.items():
            statstr += f"{name}: {status}\n"

        return statstr

    def CheckParStatusLen(self, minlen):
        """
        Checks if each parameter status provided on a peak-by-peak basis
        has at least minlen entires. Raises a ValueError with an appropriate
        error message if the check fails.
        """
        for parname, status in self.fParStatus.items():
            if isinstance(status, list) and len(status) < minlen:
                raise ValueError("Not enough values for status of %s" % parname)

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

        if parname in self.fValidParStatus:
            valid_status = self.fValidParStatus
        elif parname in self.fValidOptStatus:
            valid_status = self.fValidOptStatus
        valid_strings = [p for p in valid_status[parname] if isinstance(p, (bool, str))]

        for valid_string in valid_strings:
            if str(valid_string).lower()[0 : len(status)] == status:
                stat = valid_string

        # If status was a keyword, see if this setting is legal for the
        # parameter
        if stat is not None:
            if stat not in valid_status[parname]:
                msg = f"Status {stat} not allowed for parameter {parname} in peak model {self.name}"
                raise ValueError(msg)
            return stat

        # Check if a numeric value is legal for the parameter
        if float not in valid_status[parname]:
            msg = f"Invalid status {status} for parameter {parname} in peak model {self.name}"
            raise ValueError(msg)

        try:
            val = float(status)
        except ValueError:
            msg = "Failed to parse status specifier `%s'" % status
            raise ValueError(msg)
        return val

    def SetParameter(self, parname, status):
        """
        Set status for a certain parameter. Status is a string describing the
        desired status. Raises ValueError in case of invalid input.

        status may be single string which will be taken for all peaks, or
        list, where each item will be assigned to corresponing peak
        """
        parname = parname.strip().lower()

        try:
            if isinstance(status, list):
                if parname in self.fParStatus:
                    self.fParStatus[parname] = [
                        self.ParseParamStatus(parname, s) for s in status
                    ]
                else:
                    self.fOptStatus[parname] = [
                        self.ParseParamStatus(parname, s) for s in status
                    ]
            else:
                if parname in self.fParStatus:
                    self.fParStatus[parname] = self.ParseParamStatus(parname, status)
                else:
                    self.fOptStatus[parname] = self.ParseParamStatus(parname, status)
        except KeyError:
            raise ValueError(
                f"Invalid parameter name {parname} for peak model {self.name}"
            )

    def GetParam(self, name, peak_id, pos_uncal, cal, ival=None):
        """
        Return an appropriate HDTV.Fit.Param object for the specified parameter
        """
        # See if the parameter status has been specified for each peak
        # individually, or for all peaks at once
        if isinstance(self.fParStatus[name], list):
            parStatus = self.fParStatus[name][peak_id]
        else:
            parStatus = self.fParStatus[name]
        # Switch according to parameter status
        if parStatus == "equal":
            if name not in self.fGlobalParams:
                if ival is None:
                    self.fGlobalParams[name] = self.fFitter.AllocParam()
                else:
                    self.fGlobalParams[name] = self.fFitter.AllocParam(ival)
            return self.fGlobalParams[name]
        elif parStatus == "free":
            if ival is None:
                return self.fFitter.AllocParam()
            else:
                return self.fFitter.AllocParam(ival)
        elif parStatus == "hold":
            if ival is None:
                return ROOT.HDTV.Fit.Param.Fixed()
            else:
                return ROOT.HDTV.Fit.Param.Fixed(ival)
        elif parStatus == "none":
            return ROOT.HDTV.Fit.Param.Empty()
        elif isinstance(parStatus, float):
            return ROOT.HDTV.Fit.Param.Fixed(
                self.Uncal(name, parStatus, pos_uncal, cal)
            )
        else:
            raise RuntimeError("Invalid parameter status")

    def GetOption(self, name):
        """
        Return an appropriate HDTV.Fit.Option object for the specified parameter
        """
        status = self.fOptStatus[name]
        return ROOT.HDTV.Fit.Option(type(status))(status)
