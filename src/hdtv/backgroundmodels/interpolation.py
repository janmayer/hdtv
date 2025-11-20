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


class BackgroundModelInterpolation(BackgroundModel):
    """
    Interpolation background model
    """

    def __init__(self):
        super().__init__()
        self.fParStatus = {"nparams": 3}
        self.fValidParStatus = {"nparams": [int]}

        self.ResetParamStatus()
        self.name = "interpolation"
        self.requiredBgRegions = 3

    def ResetParamStatus(self):
        """
        Reset parameter status to defaults
        """
        self.fParStatus["nparams"] = 3

    def GetFitter(self, integrate, likelihood, nparams=None, nbg=None):
        """
        Creates a C++ Fitter object, which can then do the real work
        integrate and likelihood are ignored (do not make sense here)
        """

        if nbg is not None:
            if nbg < self.requiredBgRegions:
                return None
            self.fFitter = ROOT.HDTV.Fit.InterpolationBg(2 * nbg)
            self.fParStatus["nparams"] = 2 * nbg
        elif nparams is not None:
            self.fFitter = ROOT.HDTV.Fit.InterpolationBg(nparams)
            self.fParStatus["nparams"] = nparams
        else:
            msg = (
                "Status specifier %s of background fitter is invalid."
                % self.fParStatus["nparams"]
            )
            raise ValueError(msg)

        self.ResetGlobalParams()

        return self.fFitter
