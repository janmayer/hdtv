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
from hdtv.fitpanel import FitPanel

class FitInterface:
    """
    User interface for fitting 1-d spectra
    """
    def __init__(self, window, spectra, show_panel=True):
        hdtv.ui.msg("Loaded user interface for fitting of 1-d spectra")

        self.window = window
        self.spectra = spectra

        self.defaultFitter = Fitter(peakModel = "theuerkauf", bgdeg = 1)
        self.activeFit = Fit(self.defaultFitter.Copy())
        self.activeFit.Draw(self.window.viewport)

        # tv commands
        self.tv = TvFitInterface(self)

        # Register configuration variables for fit interface
        opt = hdtv.options.Option(default = 20.0)
        hdtv.options.RegisterOption("fit.quickfit.region", opt) # default region width for quickfit      
        

        # fit panel
        self.fitPanel = FitPanel()
        self.fitPanel.fFitHandler = self.Fit
        self.fitPanel.fClearHandler = self.ClearFit
        self.fitPanel.fResetHandler = self.ResetParameters
        self.fitPanel.fDecompHandler = lambda(stat): self.SetDecomp(stat)
        if show_panel:
            self.fitPanel.Show()

        # Register hotkeys
        self.window.AddHotkey(ROOT.kKey_Q, self.Quickfit)
        self.window.AddHotkey(ROOT.kKey_b, lambda: self._PutMarker("bg"))
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_b],
                                lambda: self._DeleteMarker("bg"))
        self.window.AddHotkey(ROOT.kKey_r, lambda: self._PutMarker("region"))
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_r],
                                lambda: self._DeleteMarker("region"))
        self.window.AddHotkey(ROOT.kKey_p, lambda: self._PutMarker("peak"))
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_p],
                                lambda: self._DeleteMarker("peak"))
        self.window.AddHotkey(ROOT.kKey_B, lambda: self.Fit(peaks = False))
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_B], self.ClearBackground)
        self.window.AddHotkey(ROOT.kKey_F, lambda: self.Fit(peaks = True))
        self.window.AddHotkey([ROOT.kKey_Plus, ROOT.kKey_F], self.KeepFit)
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_F], self.ClearFit)
#       self.window.AddHotkey(ROOT.kKey_I, self.Integrate)
        self.window.AddHotkey(ROOT.kKey_D, lambda: self.SetDecomp(True))
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_D],
                                lambda: self.SetDecomp(False))
        self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_s],
                        lambda: self.window.EnterEditMode(prompt = "Show Fit: ",
                                           handler = self._HotkeyShow))
        self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_a],
                        lambda: self.window.EnterEditMode(prompt = "Activate Fit: ",
                                           handler = self._HotkeyActivate))
        self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_p], self._HotkeyShowPrev)
        self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_n], self._HotkeyShowNext)


    def Quickfit(self):
        self.ClearFit()
        fit = self.GetActiveFit()
        pos = self.window.viewport.GetCursorX()
        region_width = hdtv.options.Get("fit.quickfit.region")
        fit.PutRegionMarker(pos - region_width / 2.)
        fit.PutRegionMarker(pos + region_width / 2.)
        fit.PutPeakMarker(pos)
        self.Fit()
        
    
    def _HotkeyShowPrev(self):
        """
        ShowPrev wrapper for use with a Hotkey (internal use)
        """
        if self.spectra.activeID == None:
            self.window.viewport.SetStatusText("No active spectrum")
            return
        try:
            self.spectra[self.spectra.activeID].ShowPrev()
        except AttributeError:
            self.window.viewport.SetStatusText("No fits available")
            
            
    def _HotkeyShowNext(self):
        """
        ShowNext wrapper for use with a Hotkey (internal use)
        """
        if self.spectra.activeID == None:
            self.window.viewport.SetStatusText("No active spectrum")
            return
        try:
            self.spectra[self.spectra.activeID].ShowNext()
        except AttributeError:
            self.window.viewport.SetStatusText("No fits available")
            
            
    def _HotkeyShow(self, args):
        """
        Show wrapper for use with a Hotkey (internal use)
        """
        if self.spectra.activeID == None:
            self.window.viewport.SetStatusText("No active spectrum")
            return
        try:
            ids = hdtv.cmdhelper.ParseRange(args)
            if ids == "NONE":
                self.spectra[self.spectra.activeID].HideAll()
            elif ids == "ALL":
                self.spectra[self.spectra.activeID].ShowAll()
            else:
                self.spectra[self.spectra.activeID].ShowObjects(ids)
        except AttributeError:
            self.window.viewport.SetStatusText("No fits available for active spectrum")
        except ValueError:
            self.window.viewport.SetStatusText("Invalid fit identifier: %s" % args)

    def _HotkeyActivate(self, arg):
        """
        ActivateObject wrapper for use with a Hotkey (internal use)
        """
        if self.spectra.activeID == None:
            self.window.viewport.SetStatusText("No active spectrum")
            return
        try:
            ID = int(arg)
            self.ActivateFit(ID)
        except ValueError:
            self.window.viewport.SetStatusText("Invalid fit identifier: %s" % arg)
        except KeyError:
            self.window.viewport.SetStatusText("No such id: %d" % ID)

    def _PutMarker(self, mtype):
        """
        Put marker of type region, peak or bg to the current position of cursor 
        (internal use)
        """
        fit = self.GetActiveFit()
        pos = self.window.viewport.GetCursorX()
        getattr(fit, "Put%sMarker" % mtype.title())(pos)


    def _DeleteMarker(self, mtype):
        """
        Delete the marker of type region, peak or bg, that is nearest to cursor 
        (internal use)
        """
        fit = self.GetActiveFit()
        pos = self.window.viewport.GetCursorX()
        markers = getattr(fit, "%sMarkers" % mtype.lower())
        markers.RemoveNearest(pos)


    def GetActiveFit(self):
        """
        Returns the currently active fit
        """
        if not self.spectra.activeID == None:
            spec = self.spectra[self.spectra.activeID]
            if hasattr(spec, "activeID") and not spec.activeID == None:
                return spec[spec.activeID]
        if not self.activeFit:
            self.activeFit = Fit(self.defaultFitter.Copy())
            self.activeFit.Draw(self.window.viewport)
        return self.activeFit
        

    def Fit(self, peaks = True):
        """
        Fit the peak
        
        If there are background markers, a background fit it included.
        """
        if self.spectra.activeID==None:
            hdtv.ui.error("There is no active spectrum")
            return 
        if self.fitPanel:
            self.fitPanel.Show()
        spec = self.spectra[self.spectra.activeID]
        if spec.activeID == None:
            ID = spec.Add(self.GetActiveFit())
            self.activeFit = None
            spec.ActivateObject(ID)
        fit = spec[spec.activeID]
        if not peaks and len(fit.bgMarkers) > 0:
            fit.FitBgFunc(spec)
        if peaks:
            fit.FitPeakFunc(spec)
        fit.Draw(self.window.viewport)
        # update fitPanel
        self.UpdateFitPanel()


    def ActivateFit(self, ID):
        """
        Activate one fit
        """
        hdtv.ui.msg("ActivateFit ID", ID)
        if self.spectra.activeID==None:
            hdtv.ui.error("There is no active spectrum")
            return 
        spec = self.spectra[self.spectra.activeID]
        if not hasattr(spec, "activeID"):
            hdtv.ui.error("There are no fits for this spectrum")
            return
        if not self.spectra.activeID in self.spectra.visible:
            hdtv.ui.warn("Active spectrum (id=%s) is not visible" %self.spectra.activeID)
        if not spec.activeID==None:
            # keep current status of old fit
            self.KeepFit()
        elif self.activeFit:
            self.activeFit.Remove()
            self.activeFit = None
        # activate another fit
        spec.ActivateObject(ID)
        if self.spectra.activeID in self.spectra.visible and spec.activeID:
            spec[spec.activeID].Show()
        # update fitPanel
        self.UpdateFitPanel()

    
    def FocusFit(self, ID):
        """
        Focus one fit
        """
        if self.spectra.activeID==None:
            hdtv.ui.error("There is no active spectrum")
            return 
        spec = self.spectra[self.spectra.activeID]
        
        if not hasattr(spec, "activeID"):
            hdtv.ui.error("There are no fits for this spectrum")
            return
        if not self.spectra.activeID in self.spectra.visible:
            hdtv.ui.warn("Active spectrum (id=%s) is not visible" %self.spectra.activeID)
        spec.FocusObject(ID)
        if self.spectra.activeID in self.spectra.visible and spec.activeID:
            spec[spec.activeID].Show()

    def KeepFit(self):
        """
        Keep this fit, 
        """
        # get active spectrum
        if self.spectra.activeID==None:
            hdtv.ui.error("There is no active spectrum")
            return 
        spec = self.spectra[self.spectra.activeID]
        if not hasattr(spec, "activeID") or spec.activeID == None:
            # do the fit
            self.Fit(peaks = True)
        spec[spec.activeID].SetTitle(str(spec.activeID))
        spec[spec.activeID].SetColor(spec.color)
        # remove the fit, if it is empty (=nothing fitted)
        if len(spec[spec.activeID].peaks) == 0:
            spec.pop(spec.activeID)
        # deactivate all objects
        spec.ActivateObject(None)
        

    def ClearFit(self):
        """
        Clear all fit markers and the pending fit, if there is one
        """
        fit = self.GetActiveFit()
        fit.Remove()
        # update fitPanel
        self.UpdateFitPanel()

    
    def ClearBackground(self):
        """
        Clear Background markers and refresh fit without background
        """
        fit = self.GetActiveFit()
        # remove background markers
        while len(fit.bgMarkers) > 0:
            fit.bgMarkers.pop().Remove()
        # redo Fit without Background
            fit.Refresh()
        # update fitPanel
        self.UpdateFitPanel()
        
    
#    def FitMultiSpectra(self, ids):
#        """
#        Use the fit markers of the active fit to fit multiple spectra.
#        The spectra that should be fitted are given by the parameter ids.
#        """
#        if isinstance(ids, int):
#            ids = [ids]
#        self.window.viewport.LockUpdate()
#        self.CopyActiveFit(ids)
#        for ID in ids:
#            spec = self.spectra[ID]
#            fit = spec[spec.activeID]
#            if len(fit.bgMarkers)>0:
#                fit.FitBgFunc(spec)
#            fit.FitPeakFunc(spec)
#            fit.Draw(self.window.viewport)
#            if not ID in self.spectra.visible:
#                fit.Hide()
#        self.window.viewport.UnlockUpdate()


#    def CopyActiveFit(self, ids):
#        """
#        Copy active fit to other spectra which are defined by the parameter ids
#        """
#        if isinstance(ids, int):
#            ids = [ids]
#        self.window.viewport.LockUpdate()
#        # get active fit to make the copies
#        fit = self.GetActiveFit()
#        for ID in ids:
#            try:
#                spec = self.spectra[ID]
#            except KeyError:
#                print "Warning: ID %s not found" % ID
#                continue
#            # do not copy, if active fit belongs already to this spectrum
#            if not fit.fitter.spec == spec:
#                try:
#                    # deactive all objects
#                    spec.ActivateObject(None)
#                except AttributeError:
#                     #TODO
#                fitID=spec.Add(fit.Copy(cal=spec.cal, color=spec.color))
#                if not ID in self.spectra.visible:
#                    spec[fitID].Hide()
#                spec.ActivateObject(fitID)
#        # clear pending Fit, if there is one
#        # Note: we have to keep this until now, 
#        # as it may be the template for all the copies 
#        if self.activeFit:
#            self.activeFit.Remove()
#            self.activeFit= None
#        self.window.viewport.UnlockUpdate()    


    def SetDecomp(self, stat = True):
        """
        Show peak decomposition
        """
        fit = self.GetActiveFit()
        fit.SetDecomp(stat)
        if self.fitPanel:
            self.fitPanel.SetDecomp(stat)
        

    def ShowFitStatus(self, default = False, ids = []):
        if default:
            ids.extend("d")
        else:
            ids.extend("a")
        statstr = str()
        for ID in ids:
            if ID == "a":
                fitter = self.GetActiveFit().fitter
                statstr += "active fitter: \n"
            elif ID == "d":
                fitter = self.defaultFitter
                statstr += "default fitter: \n"
            else:
                fitter = self.spectra[self.spectra.activeID][ID].fitter
                statstr += "fitter status of fit id %d: \n" % ID
            statstr += "Background model: polynomial, deg=%d\n" % fitter.bgdeg
            statstr += "Peak model: %s\n" % fitter.peakModel.name
            statstr += "\n"
            statstr += fitter.OptionsStr()
            statstr += "\n\n"
        hdtv.ui.msg(statstr)


    def SetParameter(self, parname, status, default = False, ids = []):
        """
        Sets status of fit parameter
        If not specified otherwise only the active fiter will be changed,
        if default=True, also the default fitter will be changed,
        if a list of fits is given, we try to set the parameter status also 
        for this fits. Be aware that failures for the fits from the list will
        be silently ignored.
        """
        # default fit
        if default:
            try:
                self.defaultFitter.SetParameter(parname, status)
            except ValueError, msg:
                hdtv.ui.error("while editing default Fit: %s" % msg)
        # active fit
        fit = self.GetActiveFit()
        try:
            fit.fitter.SetParameter(parname, status)
            fit.Refresh()
        except ValueError, msg:
            hdtv.ui.error("while editing active Fit: %s" % msg)
        # fit list
        for ID in ids:
            try:
                fit = self.spectra[self.spectra.activeID][ID]
                fit.fitter.SetParameter(parname, status)
                fit.Refresh()
            except ValueError:
                pass
        # Update fitPanel
        self.UpdateFitPanel()
 

    def ResetParameters(self, default = False, ids = []):
        if default:
            self.defaultFitter.ResetParamStatus()
        # active Fit
        fit = self.GetActiveFit()
        fit.fitter.ResetParamStatus()
        fit.Refresh()
        # fit list
        for ID in ids:
            fit = self.spectra[self.spectra.activeID][ID]
            fit.fitter.ResetParamStatus()
            fit.Refresh()
        # Update fitPanel
        self.UpdateFitPanel()


    def SetPeakModel(self, peakmodel, default = False, ids = []):
        """
        Set the peak model (function used for fitting peaks)
        """
        # default
        if default:
            self.defaultFitter.SetPeakModel(peakmodel)
        # active fit
        fit = self.GetActiveFit()
        fit.fitter.SetPeakModel(peakmodel)
        fit.Refresh()
        for ID in ids:
            fit = self.spectra[self.spectra.activeID][ID]
            fit.fitter.SetPeakModel(peakmodel)
            fit.Refresh()
        # Update fit panel
        self.UpdateFitPanel()
            

    def UpdateFitPanel(self):
        if not self.fitPanel:
            return
        fit = self.GetActiveFit()
        # options
        text = str()
        text += "Background model: polynomial, deg=%d\n" % fit.fitter.bgdeg
        text += "Peak model: %s\n" % fit.fitter.peakModel.name
        text += "\n"
        text += fit.fitter.peakModel.OptionsStr()
        self.fitPanel.SetOptions(text)
        # data
        text = str()
        if fit.fitter.bgFitter:
            deg = fit.fitter.bgFitter.GetDegree()
            chisquare = fit.fitter.bgFitter.GetChisquare()
            text += "Background (seperate fit): degree = %d   chi^2 = %.2f\n" % (deg, chisquare)
            for i in range(0, deg + 1):
                value = hdtv.util.ErrValue(fit.fitter.bgFitter.GetCoeff(i),
                                           fit.fitter.bgFitter.GetCoeffError(i))
                text += "bg[%d]: %s   " % (i, value.fmt())
            text += "\n\n"
        i = 0
        if fit.fitter.peakFitter:
            text += "Peak fit: chi^2 = %.2f\n" % fit.fitter.peakFitter.GetChisquare()
            for peak in fit.peaks:
                text += "Peak %d:\n%s\n" % (i, str(peak))
                i += 1
        self.fitPanel.SetData(text)
        

class TvFitInterface:
    """
    TV style interface for fitting
    """
    def __init__(self, fitInterface):
        self.fitIf = fitInterface
        self.spectra = self.fitIf.spectra
        
        # Register configuration variables for fit list
        opt = hdtv.options.Option(default = "ID")
        hdtv.options.RegisterOption("fit.list.sort_key", opt)      
        
        prog = "fit list"
        description = "show a list of all fits belonging to the active spectrum"
        usage = "%prog"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-l", "--long", action = "store_true", default = False,
                        help = "show more details")
        parser.add_option("-v", "--visible", action = "store_true", default = False,
                        help = "only list visible fit")
        parser.add_option("-k", "--key-sort", action = "store", default = "",
                        help = "sort by key")
        parser.add_option("-r", "--reverse-sort", action = "store_true", default = False,
                        help = "reverse the sort")
        hdtv.cmdline.AddCommand(prog, self.FitList, nargs = 0, parser = parser)
        
        prog = "fit show"
        description = "display fits"
        usage = "%prog none|all|<ids>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        # TODO: add option to show the fit, that is closest to a certain value
        hdtv.cmdline.AddCommand(prog, self.FitShow, minargs = 1, parser = parser)
        
        prog = "fit hide"
        description = "hide fits"
        usage = "%prog all|<ids>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        # TODO: add option to show the fit, that is closest to a certain value
        hdtv.cmdline.AddCommand(prog, self.FitHide, parser = parser)
        
        
        prog = "fit focus"
        description = "focus on fit with id"
        usage = "fit focus [<id>]"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.FitFocus, minargs = 0, parser = parser)
        
        prog = "fit print"
        description = "print fit results"
        usage = "%prog all|<ids>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.FitPrint, minargs = 1, parser = parser, level = 2)
        
        prog = "fit delete"
        description = "delete fits"
        usage = "%prog all|<ids>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.FitDelete, minargs = 1, parser = parser)
        
        prog = "fit activate"
        description = "activate fit for further work"
        usage = "%prog <id>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        # TODO: add option to re-activate newest fit
        # TODO: add option to activate the fit, that is closest to a certain value
        hdtv.cmdline.AddCommand(prog, self.FitActivate, nargs = 1, parser = parser)
        
#        hdtv.cmdline.AddCommand("fit copy", self.FitCopy, minargs=1)
#        hdtv.cmdline.AddCommand("fit multi", self.FitMulti, minargs=1)

        prog = "fit parameter"
        description = "show status of fit parameter, reset or set parameter"
        usage = "%prog [OPTIONS] status | reset | parname status"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-d", "--default", action = "store_true", default = False,
                            help = "act on default fitter")
        parser.add_option("-f", "--fit", action = "store", default = "none",
                            help = "change parameter of selected fit and refit")
        hdtv.cmdline.AddCommand(prog, self.FitParam, level = 0,
                                completer = self.ParamCompleter,
                                parser = parser, minargs = 1)
        
        prog = "fit function peak activate"
        description = "selects which peak model to use"
        usage = "%prog [OPTIONS] name"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-d", "--default", action = "store_true", default = False,
                            help = "change default fitter")
        parser.add_option("-f", "--fit", action = "store", default = "none",
                            help = "change selected fits and refit")
        hdtv.cmdline.AddCommand(prog, self.FitSetPeakModel,
                                completer = self.PeakModelCompleter,
                                parser = parser, minargs = 1)

        # calibration command
        prog = "calibration position assign"
        description = "Calibrate the active spectrum by asigning energies to fitted peaks. "
        description += "peaks are specified by their index and the peak number within the peak "
        description += "(if number is ommitted the first (and only?) peak is taken)."
        usage = "%prog [OPTIONS] <id0> <E0> [<od1> <E1> ...]"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-s", "--spec", action = "store", default = "all",
                        help = "spectrum ids to apply calibration to")
        parser.add_option("-d", "--degree", action = "store", default = "1",
                        help = "degree of calibration polynomial fitted [default: %default]")
        parser.add_option("-f", "--show-fit", action = "store_true", default = False,
                        help = "show fit used to obtain calibration")
        parser.add_option("-r", "--show-residual", action = "store_true", default = False,
                        help = "show residual of calibration fit")
        parser.add_option("-t", "--show-table", action = "store_true", default = False,
                        help = "print table of energies given and energies obtained from fit")
        hdtv.cmdline.AddCommand("calibration position assign", self.CalPosAssign,
                                parser = parser, minargs = 2, level=0)

    def FitList(self, args, options):
        """
        Print a list of all fits belonging to the active spectrum 
        """
        try:
            spec = self.spectra[self.spectra.activeID]
        except KeyError:
            hdtv.ui.error("No active spectrum")
            return False
        except AttributeError:
            hdtv.ui.error("There are no fits for this spectrum")
            return False
        if self.spectra.activeID in self.spectra.visible:
            visible = True
        else:
            visible = False
        hdtv.ui.msg('Fits belonging to %s (visible=%s):' %(str(spec), visible))

         # Sort key
        if options.key_sort != "":
            key = options.key_sort
        else:
            key = hdtv.options.Get("fit.list.sort_key")
        
        # Build table
        params = ["id"]
        key = key.lower()

        objects = list()
        
        if not hasattr(spec, "objects"):
            hdtv.ui.newline()
            hdtv.ui.msg("[None]")
            hdtv.ui.newline()
            return
        
        # Get fits
        for (ID, obj) in spec.objects.iteritems():
            
            if options.visible: # Don't print on visible fits
                if not ID in spec.visible:
                    continue
                
            # Get peaks
            for peak in obj.peaks:
                
                thispeak = dict()
                thispeak["id"] = ID
            
                for p in obj.fitter.peakModel.fOrderedParamKeys:
        
                    if p == "pos": # Store channel additionally to position
                        thispeak["channel"] = getattr(peak, "pos")
                        if "channel" not in params:
                            params.append("channel")
                    
                    p_cal = p + "_cal" # Use calibrated values if available
                    if hasattr(peak, p_cal):
                        thispeak[p] = getattr(peak, p_cal)
                    else:
                        thispeak[p] = getattr(peak, p_cal)
                
                    if p not in params:
                        params.append(p)
                        
                objects.append(thispeak)
        try:
            table = hdtv.util.Table(objects, params, sortBy=key, reverseSort=options.reverse_sort)
            hdtv.ui.msg(str(table))
        except KeyError:
            
            hdtv.ui.error("No such attribute: " + str(key))
            hdtv.ui.error("Valid attributes are: " + str(params))
            return False
            
    def FitDelete(self, args, options):
        """ 
        Delete fits
        """
        if self.spectra.activeID is None:
            hdtv.ui.warn("No active spectrum, no action taken.")
            return
        if not self.spectra.activeID in self.spectra.visible:
            hdtv.ui.warn("Active spectrum is not visible, no action taken")
            return
        spec = self.spectra[self.spectra.activeID]
        ids = hdtv.cmdhelper.ParseFitIds(args, spec)
        if len(ids)>0:
            spec.RemoveObjects(ids)

    def FitHide(self, args, options):
        """
        Hide Fits
        """
        if self.spectra.activeID is None:
            hdtv.ui.warn("No active spectrum, no action taken.")
            return
        if not self.spectra.activeID in self.spectra.visible:
            hdtv.ui.warn("Active spectrum is not visible, no action taken")
            return
        spec = self.spectra[self.spectra.activeID]
        ids = hdtv.cmdhelper.ParseFitIds(args,spec)
        if len(ids)>0:
            spec.HideObjects(ids)
        else:
            spec.HideAll()

    
    def FitShow(self, args, options):
        """
        Show Fits
        """
        if self.spectra.activeID is None:
            hdtv.ui.warn("No active spectrum, no action taken.")
            return
        if not self.spectra.activeID in self.spectra.visible:
            hdtv.ui.warn("Active spectrum is not visible, no action taken")
            return
        spec = self.spectra[self.spectra.activeID]
        ids = hdtv.cmdhelper.ParseFitIds(args,spec)
        if len(ids)>0:
            spec.ShowObjects(ids)
            for ID in ids:
                hdtv.ui.msg("Fit %d:" %ID, spec[ID].formated_str(verbose=True))
        else:
            spec.HideAll()

    def FitPrint(self, args, options):
        """
        Print fit results
        """
        if self.spectra.activeID is None:
            hdtv.ui.warn("No active spectrum, no action taken.")
            return
        spec = self.spectra[self.spectra.activeID]
        ids = hdtv.cmdhelper.ParseFitIds(args, spec)
        for ID in ids:
            hdtv.ui.msg("Fit %d:" %ID, spec[ID].formated_str(verbose=True))


    def FitActivate(self, args, options):
        """
        Activate one fit
        """
        try:
            ID = hdtv.cmdhelper.ParseRange(args, special = ["NONE"])
            if ID == "NONE":
                ID = None
            else:
                ID = int(args[0])
            self.fitIf.ActivateFit(ID)
        except ValueError:
            hdtv.ui.error("Invalid id %s" %ID)

    def FitFocus(self, args, options):
        """
        Focus a fit. If no fit is given focus the active fit
        """
        try:
            if len(args) == 0:
                ID = None
            else:
                ID = int(args[0])
            self.fitIf.FocusFit(ID)
        except ValueError:
            hdtv.ui.error("Invalid id %s" %ID)


#    def FitCopy(self, args):
#        try:
#            ids = hdtv.cmdhelper.ParseRange(args)
#            if ids == "NONE":
#                return
#            if ids == "ALL":
#                ids = self.spectra.keys()
#            self.fitIf.CopyActiveFit(ids)
#        except: 
#            print "Usage: fit copy <ids>|all"
#            return False

#    def FitMulti(self, args):
#        try:
#            ids = hdtv.cmdhelper.ParseRange(args, ["all", "shown"])
#        except ValueError:
#            print "Usage: fit multi <ids>|all|shown"
#            return False
#        if ids == "ALL":
#            ids = self.spectra.keys()
#        elif ids =="SHOWN":
#            ids = list(self.spectra.visible)
#        self.fitIf.FitMultiSpectra(ids)


    def FitSetPeakModel(self, args, options):
        name = args[0].lower()
        # complete the model name if needed
        models = self.PeakModelCompleter(name)
        # check for unambiguity
        if len(models)>1:
            hdtv.ui.error("Peak model name %s is ambiguous" %name)
        else:
            name = models[0]
            name = name.strip()
            ids = list()
            if options.fit:
                spec = self.spectra[self.spectra.activeID]
                ids = hdtv.cmdhelper.ParseFitIds(options.fit, spec)
            self.fitIf.SetPeakModel(name, options.default, ids)

    def PeakModelCompleter(self, text):
        """
        Creates a completer for all possible peak models
        """
        return hdtv.cmdhelper.GetCompleteOptions(text, hdtv.fitter.gPeakModels.iterkeys())

    def FitParam(self, args, options):
        # first argument is parameter name
        param = args.pop(0)
        # complete the parameter name if needed
        parameter = self.ParamCompleter(param)
        # check for unambiguity
        if len(parameter)>1:
            hdtv.ui.error("Parameter name %s is ambiguous" %param)
            return
        if len(parameter)==0:
            hdtv.ui.error("Parameter name %s is not valid" %param)
            return
        param = parameter[0]
        param = param.strip()
        ids =list()
        if options.fit:
            spec = self.spectra[self.spectra.activeID]
            ids = hdtv.cmdhelper.ParseFitIds(options.fit, spec)
        if param=="status":
            self.fitIf.ShowFitStatus(options.default, ids)
        elif param == "reset":
            self.fitIf.ResetParameters(options.default, ids)
        else:
            try:
                self.fitIf.SetParameter(param, " ".join(args), options.default, ids)
            except ValueError, msg:
                hdtv.ui.error(msg)
        
    def ParamCompleter(self, text):
        """
        Creates a completer for all possible parameter names
        If the different peak models are used for active fitter and default fitter,
        options for both peak models are presented to the user.
        """
        params = set(["status", "reset"])
        defaultParams = set(self.fitIf.defaultFitter.params)
        activeParams  = set(self.fitIf.GetActiveFit().fitter.params)
        # create a list of all possible parameter names
        params = params.union(defaultParams).union(activeParams)
        return hdtv.cmdhelper.GetCompleteOptions(text, params)
        
        
    def CalPosAssign(self, args, options):
        """ 
        Calibrate the active spectrum by assigning energies to fitted peaks

        Peaks are specified by their id and the peak number within the peak.
        Syntax: id.number
        If no number is given, the first peak in the fit is used.
        """
        if self.spectra.activeID == None:
            hdtv.ui.warn("No active spectrum, no action taken.")
            return False
        spec = self.spectra[self.spectra.activeID] 
        try:
            if len(args) % 2 != 0:
                hdtv.ui.error("Number of parameters must be even")
                return "USAGE"
            ids = hdtv.cmdhelper.ParseSpecIDs(options.spec, self.spectra)
            if ids == False:
                return
            degree = int(options.degree)
        except ValueError:
            return "USAGE"
        try:
            channels = list()
            energies = list()
            while len(args) > 0:
                # parse fit ids 
                fitID = args.pop(0).split('.')
                if len(fitID) > 2:
                    raise ValueError
                elif len(fitID) == 2:
                    channel = spec[int(fitID[0])].peakMarkers[int(fitID[1])].p1
                else:
                    channel = spec[int(fitID[0])].peakMarkers[0].p1
                channel = spec.cal.E2Ch(channel)
                channels.append(channel)
                # parse energy
                energies.append(float(args.pop(0)))
            pairs = zip(channels, energies)
            cal = hdtv.cal.CalFromPairs(pairs, degree, options.show_table,
                                        options.show_fit, options.show_residual)
        except (ValueError, RuntimeError), msg:
            hdtv.ui.error(msg)
            return False
        else:
            for ID in ids:
                try:
                    self.spectra[ID].SetCal(cal)
                    hdtv.ui.msg("Calibrated spectrum with id %d" %ID)
                except KeyError:
                    hdtv.ui.warn("There is no spectrum with id: %s" %ID)
            self.fitIf.window.Expand()        
            return True


# plugin initialisation
import __main__
if not hasattr(__main__, "window"):
    import hdtv.window
    __main__.window = hdtv.window.Window()
if not hasattr(__main__, "spectra"):
    import hdtv.drawable
    __main__.spectra = hdtv.drawable.DrawableCompound(__main__.window.viewport)
__main__.f = FitInterface(__main__.window, __main__.spectra, show_panel = False)


