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
import hdtv.color
import hdtv.cal
import hdtv.util
from hdtv.drawable import Drawable

hdtv.dlmgr.LoadLibrary("display")

class FitValue(hdtv.util.ErrValue):
    def __init__(self, value, error, free):
        hdtv.util.ErrValue.__init__(self, value, error)
        self.free = free
        
    def fmt(self):
        if self.free:
            return hdtv.util.ErrValue.fmt(self)
        else:
            return hdtv.util.ErrValue.fmt_no_error(self) + " (HOLD)"

class EEPeak(Drawable):
    """
    Peak object for the ee fitter
    """
    def __init__(self, pos, amp, sigma1, sigma2, eta, gamma, vol, color=None, cal=None):
        Drawable.__init__(self, color, cal)
        self.pos = pos
        self.amp = amp
        self.sigma1 = sigma1
        self.sigma2 = sigma2
        self.eta = eta
        self.gamma = gamma
        # vol is not a fit parameter, but rather the result of the fit
        self.vol = vol
        
    def __getattr__(self, name):
        if name=="pos_cal":
            if self.cal is None:
                return self.pos
            pos_uncal = self.pos.value
            pos_err_uncal = self.pos.error
            pos_cal = self.cal.Ch2E(pos_uncal)
            pos_err_cal = abs(self.cal.dEdCh(pos_uncal) * pos_err_uncal)
            # FitValue is not supported because of missing code in C++
            return hdtv.util.ErrValue(pos_cal, pos_err_cal)
        elif name=="sigma1_cal":
            if self.cal is None:
                return self.sigma1
            pos_uncal = self.pos.value
            sigma1_uncal = self.sigma1.value
            sigma1_err_uncal = self.sigma1.error
            sigma1_cal = self.cal.Ch2E(pos_uncal) - self.cal.Ch2E(pos_uncal - sigma1_uncal)
            # This is only an approximation, valid as d(fwhm_cal)/d(pos_uncal) \approx 0
            #  (which is true for Ch2E \approx linear)
            sigma1_err_cal = abs( self.cal.dEdCh(pos_uncal - sigma1_uncal) * sigma1_err_uncal)
            # FitValue is not supported because of missing code in C++
            return hdtv.util.ErrValue(sigma1_cal, sigma1_err_cal)
        elif name=="sigma2_cal":
            if self.cal is None:
                return self.sigma2
            pos_uncal = self.pos.value
            sigma2_uncal = self.sigma2.value
            sigma2_err_uncal = self.sigma2.error
            sigma2_cal = self.cal.Ch2E(pos_uncal) - self.cal.Ch2E(pos_uncal - sigma2_uncal)
            # This is only an approximation, valid as d(fwhm_cal)/d(pos_uncal) \approx 0
            #  (which is true for Ch2E \approx linear)
            sigma2_err_cal = abs( self.cal.dEdCh(pos_uncal - sigma2_uncal) * sigma2_err_uncal)
            # FitValue is not supported because of missing code in C++
            return hdtv.util.ErrValue(sigma2_cal, sigma2_err_cal)
        elif name in ["amp_cal","eta_cal","gamma_cal","vol_cal"]:
            name = name[0:name.rfind("_cal")]
            return getattr(self, name)
        else:
            # DON'T FORGET THIS LINE! see http://code.activestate.com/recipes/52238/ 
            raise AttributeError, name 

    def __str__(self):
        text = str()
        text += "Pos:    " + self.pos.fmt() + "\n"
        text += "Amp:    " + self.amp.fmt() + "\n"
        text += "Sigma1: " + self.sigma1.fmt() + "\n"
        text += "Sigma2: " + self.sigma2.fmt() + "\n"
        text += "Eta:    " + self.eta.fmt() + "\n"
        text += "Gamma:  " + self.gamma.fmt() + "\n"
        text += "Volume: " + self.vol.fmt() + "\n"
        return text
    
    
    def __cmp__(self, other):    
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


# For each model implemented on the C++ side, we have a corresponding Python
# class to handle fitter setup and data transfer to the Python side

# Base class for all peak models
class PeakModel:
    """
    A peak model is a function used to fit peaks. The user can choose how to fit
    its parameters (and whether to include them at all, i.e. for tails). After
    everything has been configured, the peak model produces a C++ fitter object.
    """
    def __init__(self):
        self.fGlobalParams = dict()

    def ResetGlobalParams(self):
        self.fGlobalParams.clear()
        
    def OrderedParamKeys(self):
        """
        Return the names of all peak parameters in the preferred ordering
        """
        return self.fOrderedParamKeys
        
    def OptionsStr(self):
        """
        Returns a string describing the currently set parameters of the model
        """
        statstr = ""
        
        for name in self.OrderedParamKeys():
            status = self.fParStatus[name]

            # Short format for multiple values...
            if type(status) == list:
                statstr += "%s: " % name
                sep = ""
                for stat in status:
                    statstr += sep
                    if stat in ("free", "equal", "hold", "none"):
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
                else:
                    statstr += "%s: fixed at %.3f\n" % (name, status)
                    
        return statstr
        
    def CheckParStatusLen(self, minlen):
        """
        Checks if each parameter status provided on a peak-by-peak basis
        has at least minlen entires. Raises a RuntimeError with an appropriate
        error message if the check fails.
        """
        for (parname, status) in self.fParStatus.iteritems():
            if type(status) == list and len(status) < minlen:
                raise RuntimeError, "Not enough values for status of %s" % parname
        
    def ParseParamStatus(self, parname, status):
        """
        Parse a parameter status specification string
        """
        # Case-insensitive matching
        status = status.strip().lower()
    
        # Check to see if status corresponds, possibly abbreviated,
        #  to a number of special keywords
        stat = None
        if len(status) < 1:
            raise ValueError
        elif "free"[0:len(status)] == status:
            stat = "free"
        elif "equal"[0:len(status)] == status:
            stat = "equal"
        elif "none"[0:len(status)] == status:
            stat = "none"
        elif "hold"[0:len(status)] == status:
            stat = "hold"
    
        # If status was a keyword, see if this setting is legal for the
        #  parameter in question
        if not stat is None:
            if stat in self.fValidParStatus[parname]:
                return stat
            else:
                raise RuntimeError, "Invalid status %s for parameter %s" % (stat, parname)
        # If status was not a keyword, try to parse it as a string
        else:
            return float(status)
        
        
    def SetParameter(self, parname, status):
        """
        Set status for a certain parameter
        """
        parname = parname.strip().lower()
        
        if not parname in self.fValidParStatus.keys():
            raise RuntimeError, "Invalid parameter name"
            
        if "," in status:
            self.fParStatus[parname] = map(lambda s: self.ParseParamStatus(parname, s),
                                           status.split(","))
        else:
            self.fParStatus[parname] = self.ParseParamStatus(parname, status)
        

    def GetParam(self, name, peak_id, pos_uncal, cal, ival=None):
        """
        Return an appropriate HDTV.Fit.Param object for the specified parameter
        """
        # See if the parameter status has been specified for each peak
        # individually, or for all peaks at once
        if type(self.fParStatus[name]) == list:
            parStatus = self.fParStatus[name][peak_id]
        else:
            parStatus = self.fParStatus[name]
        # Switch according to parameter status
        if parStatus == "equal":
            if not name in self.fGlobalParams:
                if ival == None:
                    self.fGlobalParams[name] = self.fFitter.AllocParam()
                else:
                    self.fGlobalParams[name] = self.fFitter.AllocParam(ival)
            return self.fGlobalParams[name]
        elif parStatus == "free":
            if ival == None:
                return self.fFitter.AllocParam()
            else:
                return self.fFitter.AllocParam(ival)
        elif parStatus == "hold":
            if ival == None:
                return ROOT.HDTV.Fit.Param.Fixed()
            else:
                return ROOT.HDTV.Fit.Param.Fixed(ival)
        elif parStatus == "none":
            return ROOT.HDTV.Fit.Param.None()
        elif type(parStatus) == float:
            return ROOT.HDTV.Fit.Param.Fixed(self.Uncal(name, parStatus, pos_uncal, cal))
        else:
            raise RuntimeError, "Invalid parameter status"
            
# TVs classic peak model
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
        hwhm_uncal = cpeak.GetSigma() * math.sqrt(2. * math.log(2.))
        width_uncal = 2* hwhm_uncal
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
        # Define a fitter and a region
        self.fFitter = ROOT.HDTV.Fit.TheuerkaufFitter(cal.E2Ch(region[0]),
                                                      cal.E2Ch(region[1]))
        self.ResetGlobalParams()
        # Check if enough values are provided in case of per-peak parameters
        #  (the function raises a RuntimeError if the check fails)
        self.CheckParStatusLen(len(peaklist))
        
        # transfer peaklist to uncalibrated values
        peaklist_uncal = [cal.E2Ch(x) for x in peaklist]
        
        # Copy peaks to the fitter
        for pid in range(0, len(peaklist_uncal)):
            pos_uncal = peaklist_uncal[pid]
            
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

# Peak model for electron-electron scattering
# Implementation requested by Oleksiy Burda <burda@ikp.tu-darmstadt.de>
class PeakModelEE(PeakModel):
    """
    ee scattering peak model
    """
    def __init__(self):
        PeakModel.__init__(self)
        self.fOrderedParamKeys = ["pos", "amp", "sigma1", "sigma2", "eta", "gamma", "vol"]
        self.fParStatus = { "pos": None, "amp": None, "sigma1": None, "sigma2": None,
                            "eta": None, "gamma": None, "vol":None }
        # volume is not a fit parameter, but is must be in this list
        # because it is a property of an EEPeak
        self.fValidParStatus = { "pos":    [ float, "free", "hold" ],
                                 "amp":    [ float, "free", "hold" ],
                                 "sigma1": [ float, "free", "equal" ],
                                 "sigma2": [ float, "free", "equal" ],
                                 "eta":    [ float, "free", "equal" ],
                                 "gamma":  [ float, "free", "equal" ],
                                 "vol":    ["free"] }
        self.ResetParamStatus()
        self.name = "ee"
        self.Peak = EEPeak
        
        
    def CopyPeak(self, cpeak, color=None, cal=None):
        """
        Copies peak data from a C++ peak class to a Python class
        """
        # create ErrValues (the use of FitValues is not implemented in C++)
        pos = hdtv.util.ErrValue(cpeak.GetPos(), cpeak.GetPosError())
        amp = hdtv.util.ErrValue(cpeak.GetAmp(), cpeak.GetAmpError())
        sigma1 = hdtv.util.ErrValue(cpeak.GetSigma1(), cpeak.GetSigma1Error())
        sigma2 = hdtv.util.ErrValue(cpeak.GetSigma2(), cpeak.GetSigma2Error())
        eta = hdtv.util.ErrValue(cpeak.GetEta(), cpeak.GetEtaError())
        gamma = hdtv.util.ErrValue(cpeak.GetGamma(), cpeak.GetGammaError())
        vol = hdtv.util.ErrValue(cpeak.GetVol(), cpeak.GetVolError())
        # create the peak object
        peak = self.Peak(pos, amp, sigma1, sigma2, eta, gamma, vol)
        func = cpeak.GetPeakFunc()
        peak.displayObj = ROOT.HDTV.Display.DisplayFunc(func, color)
        peak.displayObj.SetCal(cal)
        return peak
        
    
    def ResetParamStatus(self):
        """
        Reset parameter status to defaults
        """
        self.fParStatus["pos"] = "free"
        self.fParStatus["amp"] = "free"
        self.fParStatus["sigma1"] = "equal"
        self.fParStatus["sigma2"] = "equal"
        self.fParStatus["eta"] = "equal"
        self.fParStatus["gamma"] = "equal"
        self.fParStatus["vol"] = "free"
    
    def Uncal(self, parname, value, pos_uncal, cal):
        """
        Convert a value from calibrated to uncalibrated units
        """
        if parname == "pos":
            return cal.E2Ch(value)
        elif parname == "sigma1":
            pos_cal = cal.Ch2E(pos_uncal)
            left_hwhm_uncal = pos_uncal - cal.E2Ch(pos_cal - value)
            return left_hwhm_uncal
        elif parname == "sigma2":
            pos_cal = cal.Ch2E(pos_uncal)
            right_hwhm_uncal = cal.E2Ch(pos_cal + value) - pos_uncal
            return right_hwhm_uncal
        elif parname in ("amp", "eta", "gamma"):
            return value
        else:
            raise RuntimeError, "Unexpected parameter name"
        
        
    def GetFitter(self, region, peaklist, cal):
        self.fFitter = ROOT.HDTV.Fit.EEFitter(cal.E2Ch(region[0]),
                                              cal.E2Ch( region[1]))

        self.ResetGlobalParams()
        
        # Check if enough values are provided in case of per-peak parameters
        #  (the function raises a RuntimeError if the check fails)
        self.CheckParStatusLen(len(peaklist))
        
        peaklist_uncal = [cal.E2Ch(x) for x in peaklist]
            
        for pid in range(0, len(peaklist_uncal)):
            pos_uncal = peaklist_uncal[pid]
            
            pos = self.GetParam("pos", pid, pos_uncal, cal, pos_uncal)
            amp = self.GetParam("amp", pid, pos_uncal, cal)
            sigma1 = self.GetParam("sigma1", pid, pos_uncal, cal)
            sigma2 = self.GetParam("sigma2", pid, pos_uncal, cal)
            eta = self.GetParam("eta", pid, pos_uncal, cal)
            gamma = self.GetParam("gamma", pid, pos_uncal, cal)

            peak = ROOT.HDTV.Fit.EEPeak(pos, amp, sigma1, sigma2, eta, gamma)
            self.fFitter.AddPeak(peak)
            
        return self.fFitter


