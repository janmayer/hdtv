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


class BackgroundModelPolynomial(BackgroundModel):
    """
    Polynomial background model
    """

    def __init__(self):
        super().__init__()
        self.fParStatus = {"nparams": 2}
        self.fValidParStatus = {"nparams": [int, "free"]}

        self.ResetParamStatus()
        self.name = "polynomial"
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
            if nparams == "free":
                if nbg is None:
                    raise ValueError(
                        "Free number of background parameters specified, but no number of background regions given."
                    )
                self.fFitter = ROOT.HDTV.Fit.PolyBg(nbg, integrate, likelihood)
                self.fParStatus["nparams"] = nbg
            else:
                self.fFitter = ROOT.HDTV.Fit.PolyBg(nparams, integrate, likelihood)
                self.fParStatus["nparams"] = nparams
        elif isinstance(self.fParStatus["nparams"], int):
            self.fFitter = ROOT.HDTV.Fit.PolyBg(
                self.fParStatus["nparams"], integrate, likelihood
            )
        elif self.fParStatus["nparams"] == "free":
            if nbg is None:
                raise ValueError(
                    "Free number of background parameters specified, but no number of background regions given."
                )
            self.fFitter = ROOT.HDTV.Fit.PolyBg(nbg, integrate, likelihood)
        else:
            msg = (
                "Status specifier %s of background fitter is invalid."
                % self.fParStatus["nparams"]
            )
            raise ValueError(msg)

        self.ResetGlobalParams()

        return self.fFitter
