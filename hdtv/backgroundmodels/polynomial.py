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

import ROOT
from .background import BackgroundModel

class BackgroundModelPolynomial(BackgroundModel):
    """
    Polynomial background model
    """

    def __init__(self):
        super(BackgroundModelPolynomial, self).__init__()
        self.fOrderedParamKeys = ["bgdeg"]
        self.fParStatus = {"bgdeg": 1}
        self.fValidParStatus = {"bgdeg": [int, "free"]}

        self.ResetParamStatus()
        self.name = "polynomial"
        self.requiredBgRegions = 1

    def ResetParamStatus(self):
        """
        Reset parameter status to defaults
        """
        self.fParStatus["bgdeg"] = 1

    def GetFitter(self, bgdeg=1):
        """
        Creates a C++ Fitter object, which can then do the real work
        """
        if isinstance(self.fParStatus['bgdeg'], int):
            self.fFitter = ROOT.HDTV.Fit.PolyBg(self.fParStatus['bgdeg'])
            self.bgdeg = self.fParStatus['bgdeg']
        elif self.fParStatus['bgdeg'] == "free":
            self.fFitter = ROOT.HDTV.Fit.PolyBg(bgdeg)
            self.bgdeg = bgdeg
        else:
            msg = "Status specifier %s of background fitter is invalid." % fParStatus['bgdeg']
            raise ValueError(msg)

        self.ResetGlobalParams()

        return self.fFitter
