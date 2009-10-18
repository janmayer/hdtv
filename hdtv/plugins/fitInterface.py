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
import hdtv.cmdline
import hdtv.cmdhelper
import hdtv.options
import hdtv.util
import hdtv.ui

from hdtv.marker import MarkerCollection
from hdtv.fitter import Fitter
from hdtv.fit import Fit


import sys

class FitInterface:
    """
    User interface for fitting 1-d spectra
    """
    def __init__(self, spectra):
        hdtv.ui.msg("Loaded user interface for fitting of 1-d spectra")

        self.spectra = spectra
        self.window = self.spectra.window

        # tv commands
        self.tv = TvFitInterface(self)

        # Register configuration variables for fit interface
        opt = hdtv.options.Option(default = 20.0)
        hdtv.options.RegisterOption("fit.quickfit.region", opt) # default region width for quickfit
        opt = hdtv.options.Option(default = False, parse = hdtv.options.ParseBool)
        hdtv.options.RegisterOption("__debug__.fit.show_inipar", opt)
        
        # Register hotkeys
        self.window.AddHotkey(ROOT.kKey_b, 
                                lambda: self.spectra.SetFitMarker("bg"))
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_b],
                                lambda: self.spectra.RemoveFitMarker("bg"))
        self.window.AddHotkey(ROOT.kKey_r, 
                                lambda: self.spectra.SetFitMarker("region"))
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_r],
                                lambda: self.spectra.RemoveFitMarker("region"))
        self.window.AddHotkey(ROOT.kKey_p, 
                                lambda: self.spectra.SetFitMarker("peak"))
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_p],
                                lambda: self.spectra.RemoveFitMarker("peak"))
        self.window.AddHotkey(ROOT.kKey_B, 
                                lambda: self.spectra.ExecuteFit(peaks = False))
        self.window.AddHotkey(ROOT.kKey_F, 
                                lambda: self.spectra.ExecuteFit(peaks = True))
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_B], 
                                lambda: self.spectra.ClearFit(bg_only=True))
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_F], 
                                lambda: self.spectra.ClearFit(bg_only=False))
        self.window.AddHotkey(ROOT.kKey_Q, self.QuickFit)
#        self.window.AddHotkey([ROOT.kKey_Plus, ROOT.kKey_F], self.StoreFit)
#        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_F], self.ClearFit)
##       self.window.AddHotkey(ROOT.kKey_I, self.Integrate)
#        self.window.AddHotkey(ROOT.kKey_D, lambda: self.SetDecomp(True))
#        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_D],
#                                lambda: self.SetDecomp(False))
#        self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_s],
#                        lambda: self.window.EnterEditMode(prompt = "Show Fit: ",
#                                           handler = self._HotkeyShow))
#        self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_a],
#                        lambda: self.window.EnterEditMode(prompt = "Activate Fit: ",
#                                           handler = self._HotkeyActivate))
#        self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_p], self._HotkeyShowPrev)
#        self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_n], self._HotkeyShowNext)
        
       
    def ExecuteRefit(self, specID, fitID, peaks=True):
        """
        Execute Fit on non-active Fits
        """
        print "trying to refit Fit %s of spectrum %s" %(fitID, specID)


    def QuickFit(self, pos=None):
        print pos
        if pos is None:
            pos = self.window.viewport.GetCursorX()
        self.spectra.ClearFit()
        region_width = hdtv.options.Get("fit.quickfit.region")
        self.spectra.SetFitMarker("region", pos - region_width / 2.)
        self.spectra.SetFitMarker("region", pos + region_width / 2.)
        self.spectra.SetFitMarker("peak", pos)
        self.spectra.ExecuteFit()


class TvFitInterface:
    """
    TV style interface for fitting
    """
    def __init__(self, fitInterface):
        self.fitIf = fitInterface
        self.spectra = self.fitIf.spectra  
        
        prog = "fit execute"
        description = "(re)fit a fit"
        usage = "%prog [OPTIONS] <fit-ids>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-s", "--spectrum", action = "store", default = "active",
                            help = "Spectra to work on")
        parser.add_option("-b", "--background", action = "store_true", default = False,
                            help = "fit only the background")
        parser.add_option("-q","--quick", action="store", default=None,
                            help = "set position for doing a quick fit")
        hdtv.cmdline.AddCommand(prog, self.FitExecute, level=0, parser = parser)
        # the "fit execute" command is registered with level=0, 
        # this allows "fit execute" to be abbreviated as "fit", 
        # register all other commands starting with fit with default or higher priority
        
        prog = "fit marker"
        description = "set/delete a marker"
        description +="(possible types are background, region, peak)"
        usage = "%prog type action position"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.FitMarkerChange, nargs=3,
                                parser = parser, completer=self.MarkerCompleter)
        
        prog = "fit clear"
        description = "clear the active work fit"
        usage = "%prog"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-b", "--background_only", action="store_true", default = False,
                            help = "clear only background fit, refit peak fit with internal background")
        hdtv.cmdline.AddCommand(prog, self.FitClear, nargs=0, parser = parser)
        

    def FitMarkerChange(self, args, options):
        """
        Set or delete a marker from command line
        """
        # first argument is marker type name
        mtype = args[0]
        # complete markertype if needed
        mtype = self.MarkerCompleter(mtype)
        if len(mtype)==0:
            hdtv.ui.error("Markertype %s is not valid" %args[0])
            return
        # second argument is action
        action = args[1]
        action = self.MarkerCompleter(action, args=args[0:1])
        if len(action)==0:
            hdtv.ui.error("Invalid action: %s" %args[1])
        # parse position
        try:
            pos = float(args[2])
        except ValueError:
            hdtv.ui.error("Invalid position argument")
            return
        mtype = mtype[0].strip()
        # replace "background" with "bg" which is internally used
        if mtype == "background": mtype="bg"
        action = action[0].strip()
        if action == "set":
            self.spectra.SetFitMarker(mtype, pos)
        if action == "delete":
            self.spectra.RemoveFitMarker(mtype, pos)


    def MarkerCompleter(self, text, args=[]):
        if not args:
            mtypes = ["background","region", "peak"]
            return hdtv.cmdhelper.GetCompleteOptions(text, mtypes)
        elif len(args)==1:
            actions = ["set", "delete"]
            return hdtv.cmdhelper.GetCompleteOptions(text, actions)
        
            
    def FitExecute(self, args, options):
        """
        Execute a fit
        """
        specIDs = hdtv.cmdhelper.ParseIds(options.spectrum, self.spectra)
        if len(specIDs) == 0:
            hdtv.ui.warn("No spectrum to work on")
            return
        if options.background:
            doPeaks = False
        else:
            doPeaks = True
        for specID in specIDs:
            fitIDs = hdtv.cmdhelper.ParseIds(args, self.spectra.dict[specID])
            if len(fitIDs) == 0:
                if specID==self.spectra.activeID:
                    if options.quick is not None:
                        try:
                            pos = float(options.quick)
                        except:
                            hdtv.ui.error("Invalid position for quick fit.")
                            return
                        self.fitIf.QuickFit(pos)
                    else:
                        self.spectra.ExecuteFit(peaks=doPeaks) 
                else:
                    hdtv.ui.warn("No fit for spectrum %s to work on." %specID)
            for fitID in fitIDs:    
                self.fitIf.ExecuteRefit(specID=specID, fitID=fitID, peaks=doPeaks)
                
    def FitClear(self, args, options):
        """
        Clears work fit
        """
        self.spectra.ClearFit(options.background_only)

# plugin initialisation
import __main__
__main__.f = FitInterface(__main__.spectra)


