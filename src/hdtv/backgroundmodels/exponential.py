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

import ROOT

from .background import BackgroundModel


class BackgroundModelExponential(BackgroundModel):
    """
    Exponential background model
    """

    def __init__(self):
        super().__init__()
        self.fParStatus = {"nparams": 2}
        self.fValidParStatus = {"nparams": [int, "free"]}

        self.ResetParamStatus()
        self.name = "exponential"
        self.requiredBgRegions = 1

    def ResetParamStatus(self):
        """
        Reset parameter status to defaults
        """
        self.fParStatus["nparams"] = 2

    def GetFitter(self, integrate, likelihood, nparams=None, nbg=None):
        """
        Creates a C++ Fitter object, which can then do the real work
        """
        if nparams is not None:
            self.fFitter = ROOT.HDTV.Fit.ExpBg(nparams, integrate, likelihood)
            self.fParStatus["nparams"] = nparams
        elif isinstance(self.fParStatus["nparams"], int):
            self.fFitter = ROOT.HDTV.Fit.ExpBg(
                self.fParStatus["nparams"], integrate, likelihood
            )
        else:
            msg = (
                "Status specifier %s of background fitter is invalid."
                % self.fParStatus["nparams"]
            )
            raise ValueError(msg)

        self.ResetGlobalParams()

        return self.fFitter
