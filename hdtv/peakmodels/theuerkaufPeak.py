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
import math
import ROOT
from peak import PeakModel, FitValue
from hdtv.drawable import Drawable

class TheuerkaufPeak(Drawable):
    """
    Peak object for the Theuerkauf (classic TV) fitter
    """
    def __init__(self, pos, vol, width, tl, tr, sh, sw, color=None, cal=None):
        Drawable.__init__(self, color, cal)
        # values are uncalibrated!
        self.pos = pos
        self.vol = vol
        # width==fwhm (internally the C++ fitter uses sigma)
        self.width = width    
        self.tl = tl
        self.tr = tr
        self.sh = sh
        self.sw = sw
        
    def __getattr__(self, name):
        """
        calculate calibrated values on the fly for pos and width
        """
        if name=="pos_cal":
            if self.cal is None:
                return self.pos
            pos_uncal = self.pos.value
            pos_err_uncal = self.pos.error
            pos_cal = self.cal.Ch2E(pos_uncal)
            pos_err_cal = abs(self.cal.dEdCh(pos_uncal) * pos_err_uncal)
            return FitValue(pos_cal, pos_err_cal, self.pos.free)
        elif name=="width_cal":
            if self.cal is None:
                return self.width
            pos_uncal = self.pos.value
            hwhm_uncal = self.width.value/2
            width_err_uncal = self.width.error
            width_cal = self.cal.Ch2E(pos_uncal + hwhm_uncal) - self.cal.Ch2E(pos_uncal - hwhm_uncal)
            # This is only an approximation, valid as d(width_cal)/d(pos_uncal) \approx 0
            #  (which is true for Ch2E \approx linear)
            width_err_cal = abs( (self.cal.dEdCh(pos_uncal + hwhm_uncal) / 2. + 
                                  self.cal.dEdCh(pos_uncal - hwhm_uncal) / 2.   ) * width_err_uncal)
            return FitValue(width_cal, width_err_cal, self.width.free)
        elif name in ["vol_cal","tl_cal","tr_cal","sh_cal","sw_cal"]:
            name = name[0:name.rfind("_cal")]
            return getattr(self, name)
        else:
            # DON'T FORGET THIS LINE! see http://code.activestate.com/recipes/52238/ 
            raise AttributeError, name 

    def __str__(self):
        """
        print the properties of this peak in a nicely formated way
        """
        text = str()
        text += "Pos:         " + self.pos_cal.fmt() + "\n"
        text += "Volume:      " + self.vol.fmt() + "\n"
        text += "FWHM:        " + self.width_cal.fmt() + "\n"
        # Note: do not use == or != when testing for None
        # those operators use cmp, which is not garanteed to handle None
        if not self.tl is None:
            text += "Left Tail:   " + self.tl.fmt() + "\n"
        else:
            text += "Left Tail:   None\n"
        if not self.tr is None:
            text += "Right Tail:  " + self.tr.fmt() + "\n"
        else:
            text += "Right Tail:  None\n"
        if not self.sh is None:
            text += "Step height: " + self.sh.fmt() + "\n"
            text += "Step width:  " + self.sw.fmt() + "\n"
        else:
            text += "Step:        None\n"
        return text

    def __cmp__(self, other):
        """
        compare peaks according to their position (uncalibrated)
        """    
        return cmp(self.pos, other.pos)
    
    
    def Draw(self, viewport):
        """
        Draw the function of this peak
        """
        if self.viewport:
            if self.viewport == viewport:
                # this has already been drawn
                self.Refresh()
                return
            else:
                # Unlike the Display object of the underlying implementation,
                # python objects can only be drawn on a single viewport
                raise RuntimeError, "Peak cannot be drawn on multiple viewports"
        self.viewport = viewport
        if self.displayObj:
            self.displayObj.Draw(self.viewport)


class PeakModelTheuerkauf(PeakModel):
    """ 
    Theuerkauf peak model - "classical" model used by tv
    """
    def __init__(self):
        PeakModel.__init__(self)
        self.fOrderedParamKeys = ["pos", "vol", "width", "tl", "tr", "sh", "sw"]
        self.fParStatus = { "pos": None, "vol": None, "width": None,
                            "tl": None, "tr": None, "sh": None, "sw": None }
        self.fValidParStatus = { "pos":   [ float, "free", "hold" ],
                                 "vol":   [ float, "free", "hold" ],
                                 "width": [ float, "free", "equal" ],
                                 "tl":    [ float, "free", "equal", "none" ],
                                 "tr":    [ float, "free", "equal", "none" ],
                                 "sh":    [ float, "free", "equal", "none" ],
                                 "sw":    [ float, "free", "equal", "hold" ] }
                                 
        self.ResetParamStatus()
        self.Peak = TheuerkaufPeak
        self.name = "theuerkauf"
        

    def CopyPeak(self, cpeak, color=None, cal=None):
        """
        create a python peak object from C++ peak object
        """ 
        # get values from C++ object (uncalibrated)
        pos_uncal = cpeak.GetPos()
        pos_err_uncal = cpeak.GetPosError()
        # width==fwhm (internally the C++ fitter uses sigma)
        width_uncal = cpeak.GetSigma() * 2. * math.sqrt(2. * math.log(2.))
        width_err_uncal = cpeak.GetSigmaError() * 2. * math.sqrt(2. * math.log(2.))
        # create FitValues objets from this
        pos = FitValue(pos_uncal, pos_err_uncal, cpeak.PosIsFree())
        vol = FitValue(cpeak.GetVol(), cpeak.GetVolError(), cpeak.VolIsFree())
        width = FitValue(width_uncal, width_err_uncal, cpeak.SigmaIsFree())
        # optional parameters
        if cpeak.HasLeftTail():
            tl = FitValue(cpeak.GetLeftTail(), cpeak.GetLeftTailError(), 
                          cpeak.LeftTailIsFree())
        else:
            tl = None
        if cpeak.HasRightTail():
            tr = FitValue(cpeak.GetRightTail(), cpeak.GetRightTailError(),
                          cpeak.RightTailIsFree())
        else:
            tr = None
        if cpeak.HasStep():
            sh = FitValue(cpeak.GetStepHeight(), cpeak.GetStepHeightError(),
                          cpeak.StepHeightIsFree())
            sw = FitValue(cpeak.GetStepWidth(), cpeak.GetStepWidthError(),
                          cpeak.StepWidthIsFree())
        else:
            sh = sw = None
        # create peak object
        peak = self.Peak(pos, vol, width, tl, tr, sh, sw, color, cal)
        func = cpeak.GetPeakFunc()
        peak.displayObj = ROOT.HDTV.Display.DisplayFunc(func, color)
        peak.displayObj.SetCal(cal)
        return peak
        
    def RestoreParams(self, peak, cpeak):
        """
        Restore the params of a C++ peak object using a python peak object
        """
        cpeak.RestorePos(peak.pos.value, peak.pos.error)
        cpeak.RestoreVol(peak.vol.value,peak.vol.error)
        # internally the C++ fitter uses sigma
        sigma = peak.width.value/(2. * math.sqrt(2. * math.log(2.)))
        sigma_err = peak.width.error/(2. * math.sqrt(2. * math.log(2.)))
        cpeak.RestoreSigma(sigma, sigma_err)
        if peak.tl:
            cpeak.RestoreLeftTail(peak.tl.value, peak.tl.error)
        if peak.tr:
            cpeak.RestoreRightTail(peak.tr.value, peak.tr.error)
        if peak.sh:
            cpeak.RestoreStepHeight(peak.sh.value, peak.sh.error)
            cpeak.RestoreStepWidth(peak.sw.value, peak.sw.error)
            

    def ResetParamStatus(self):
        """
        Reset parameter status to defaults
        """
        self.fParStatus["pos"] = "free"
        self.fParStatus["vol"] = "free"
        self.fParStatus["width"] = "equal"
        self.fParStatus["tl"] = "none"
        self.fParStatus["tr"] = "none"
        self.fParStatus["sh"] = "none"
        self.fParStatus["sw"] = "hold"


    def Uncal(self, parname, value, pos_uncal, cal):
        """
        Convert a value from calibrated (spectrum) to uncalibrated (fitter) units
        This is needed, when a value is hold to a specific calibrated value.
        """
        if parname == "pos":
            return cal.E2Ch(value)
        elif parname == "width":
            pos_cal = cal.Ch2E(pos_uncal)
            width_uncal = cal.E2Ch(pos_cal + value/2.) - cal.E2Ch(pos_cal - value/2.)
            # Note that the underlying fitter uses ``sigma'' as a parameter
            #  (see HDTV technical documentation in the wiki)
            return width_uncal / (2. * math.sqrt(2. * math.log(2.)))
        elif parname in ("vol", "tl", "tr", "sh", "sw"):
            return value
        else:
            raise RuntimeError, "Unexpected parameter name"
            

    def GetFitter(self, region, peaklist, cal):
        """
        Creates a C++ Fitter object, which can then do the real work
        """
        # Define a fitter and a region
        self.fFitter = ROOT.HDTV.Fit.TheuerkaufFitter(region[0],region[1])
        self.ResetGlobalParams()
        # Check if enough values are provided in case of per-peak parameters
        #  (the function raises a RuntimeError if the check fails)
        self.CheckParStatusLen(len(peaklist))
                
        # Copy peaks to the fitter
        for pid in range(0, len(peaklist)):
            pos_uncal = peaklist[pid]
            
            pos = self.GetParam("pos", pid, pos_uncal, cal, pos_uncal)
            vol = self.GetParam("vol", pid, pos_uncal, cal)
            sigma = self.GetParam("width", pid, pos_uncal, cal)
            tl = self.GetParam("tl", pid, pos_uncal, cal)
            tr = self.GetParam("tr", pid, pos_uncal, cal)
            sh = self.GetParam("sh", pid, pos_uncal, cal)
            sw = self.GetParam("sw", pid, pos_uncal, cal)
            
            cpeak = ROOT.HDTV.Fit.TheuerkaufPeak(pos, vol, sigma, tl, tr, sh, sw)
            self.fFitter.AddPeak(cpeak)

        return self.fFitter
