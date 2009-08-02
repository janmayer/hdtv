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

from hdtv.spectrum import SpectrumCompound
from hdtv.marker import MarkerCollection
from hdtv.fitter import Fitter
from hdtv.fit import Fit
from hdtv.fitpanel import FitPanel

class FitInterface:
    """
    User interface for fitting 1-d spectra
    """
    def __init__(self, window, spectra, show_panel=True):
        print "Loaded user interface for fitting of 1-d spectra"
        self.window = window
        self.spectra = spectra

        self.defaultFitter = Fitter(peakModel="theuerkauf",bgdeg=1)
        self.activeFit = Fit(self.defaultFitter.Copy())
        self.activeFit.Draw(self.window.viewport)

        # tv commands
        self.tv = TvFitInterface(self)

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
        self.window.AddHotkey(ROOT.kKey_B, lambda: self.Fit(peaks=False))
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_B], self.ClearBackground)
        self.window.AddHotkey(ROOT.kKey_F, lambda: self.Fit(peaks=True))
        self.window.AddHotkey([ROOT.kKey_Plus, ROOT.kKey_F], self.KeepFit)
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_F], self.ClearFit)
#       self.window.AddHotkey(ROOT.kKey_I, self.Integrate)
        self.window.AddHotkey(ROOT.kKey_D, lambda: self.SetDecomp(True))
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_D], 
                                lambda: self.SetDecomp(False))
        self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_s],
                        lambda: self.window.EnterEditMode(prompt="Show Fit: ",
                                           handler=self._HotkeyShow))
        self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_a],
                        lambda: self.window.EnterEditMode(prompt="Activate Fit: ",
                                           handler=self._HotkeyActivate))
        self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_p], self._HotkeyShowPrev)
        self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_n], self._HotkeyShowNext)


    def Quickfit(self):
        self.ClearFit()
        fit = self.GetActiveFit()
        pos = self.window.viewport.GetCursorX()
        fit.PutRegionMarker(pos - 10.)
        fit.PutRegionMarker(pos + 10.)
        fit.PutPeakMarker(pos)
        self.Fit()
        
    
    def _HotkeyShowPrev(self):
        """
        ShowPrev wrapper for use with a Hotkey (internal use)
        """
        if self.spectra.activeID==None:
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
        if self.spectra.activeID==None:
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
        if self.spectra.activeID==None:
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
        if self.spectra.activeID==None:
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
        getattr(fit,"Put%sMarker" %mtype.title())(pos)


    def _DeleteMarker(self, mtype):
        """
        Delete the marker of type region, peak or bg, that is nearest to cursor 
        (internal use)
        """
        fit = self.GetActiveFit()
        pos = self.window.viewport.GetCursorX()
        markers = getattr(fit, "%sMarkers" %mtype.lower())
        markers.RemoveNearest(pos)


    def GetActiveFit(self):
        """
        Returns the currently active fit
        """
        if not self.spectra.activeID==None:
            spec = self.spectra[self.spectra.activeID]
            if hasattr(spec, "activeID") and not spec.activeID==None:
                return spec[spec.activeID]
        if not self.activeFit:
            self.activeFit = Fit(self.defaultFitter.Copy())
            self.activeFit.Draw(self.window.viewport)
        return self.activeFit
        

    def Fit(self, peaks=True):
        """
        Fit the peak
        
        If there are background markers, a background fit it included.
        """
        if self.spectra.activeID==None:
            print "There is no active spectrum"
            return 
        if self.fitPanel:
            self.fitPanel.Show()
        spec = self.spectra[self.spectra.activeID]
        if not hasattr(spec, "activeID"):
            # create SpectrumCompound object 
            spec = SpectrumCompound(self.window.viewport, spec)
            # replace the simple spectrum object by the SpectrumCompound
            self.spectra[self.spectra.activeID]=spec
        if spec.activeID==None:
            ID = spec.Add(self.GetActiveFit())
            self.activeFit = None
            spec.ActivateObject(ID)
        fit = spec[spec.activeID]
        if not peaks and len(fit.bgMarkers)>0:
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
        if self.spectra.activeID==None:
            print "There is no active spectrum"
            return 
        spec = self.spectra[self.spectra.activeID]
        if not hasattr(spec, "activeID"):
            print 'There are no fits for this spectrum'
            return
        if not self.spectra.activeID in self.spectra.visible:
            print 'Warning: active spectrum (id=%s) is not visible' %self.spectra.activeID
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

    
    def KeepFit(self):
        """
        Keep this fit, 
        """
        # get active spectrum
        if self.spectra.activeID==None:
            print "There is no active spectrum"
            return 
        spec = self.spectra[self.spectra.activeID]
        if not hasattr(spec, "activeID") or spec.activeID==None:
            # do the fit
            self.Fit(peaks=True)
        spec[spec.activeID].SetColor(spec.color)
        # remove the fit, if it is empty (=nothing fitted)
        if len(spec[spec.activeID].peaks)==0:
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
        fit  = self.GetActiveFit()
        # remove background markers
        while len(fit.bgMarkers)>0:
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
#                    # create SpectrumCompound object 
#                    spec = SpectrumCompound(self.window.viewport, spec)
#                    # replace the simple spectrum object by the SpectrumCompound
#                    self.spectra[ID]=spec
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


    def SetDecomp(self, stat=True):
        """
        Show peak decomposition
        """
        fit = self.GetActiveFit()
        fit.SetDecomp(stat)
        if self.fitPanel:
            self.fitPanel.SetDecomp(stat)
        

    def ShowFitStatus(self, default=False):
        if default:
            fitter = self.defaultFitter
        else:
            fitter = self.GetActiveFit().fitter
        statstr = str()
        statstr += "Background model: polynomial, deg=%d\n" % fitter.bgdeg
        statstr += "Peak model: %s\n" % fitter.peakModel.name
        statstr += "\n"
        statstr += fitter.OptionsStr()
        print statstr


    def SetParameter(self, parname, status, default=False):
        if default:
            self.defaultFitter.SetParameter(parname, status)
        fit = self.GetActiveFit()
        try:
            fit.fitter.SetParameter(parname, status)
            fit.Refresh()
            # Update fitPanel
            self.UpdateFitPanel()
        except ValueError:
            pass


    def ResetParameters(self, default=False):
        if default:
            self.defaultFitter.ResetParamStatus()
        fit = self.GetActiveFit()
        fit.fitter.ResetParamStatus()
        fit.Refresh()
        # Update fitPanel
        self.UpdateFitPanel()


    def SetPeakModel(self, peakmodel, default=False):
        """
        Set the peak model (function used for fitting peaks)
        """
        # Set new peak model
        if default:
            self.defaultFitter.SetPeakModel(peakmodel)
        fit = self.GetActiveFit()
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
            for i in range(0,deg+1):
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
        
        hdtv.cmdline.AddCommand("fit list", self.FitList, nargs=0, usage="fit list")
        hdtv.cmdline.AddCommand("fit show", self.FitShow, minargs=1)
        hdtv.cmdline.AddCommand("fit print", self.FitPrint, minargs=1, level=2)
        hdtv.cmdline.AddCommand("fit delete", self.FitDelete, minargs=1)
        hdtv.cmdline.AddCommand("fit activate", self.FitActivate, nargs=1)
#        hdtv.cmdline.AddCommand("fit copy", self.FitCopy, minargs=1)
#        hdtv.cmdline.AddCommand("fit multi", self.FitMulti, minargs=1)

        prog = "fit status"
        description="Show status of fit parameter"
        usage = "%prog [OPTIONS]"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description, usage=usage)
        parser.add_option("-d", "--default", action="store_true", default=False, 
                            help="show status of default fitter")
        hdtv.cmdline.AddCommand(prog, self.FitStatus, nargs=0, parser=parser)
        
        prog = "fit reset"
        description="Reset status of fit parameter to hardcoded defaults"
        usage = "%prog [OPTIONS]"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description, usage=usage)
        parser.add_option("-d", "--default", action="store_true", default=False, 
                            help="reset default fitter")
        hdtv.cmdline.AddCommand(prog, self.FitReset, nargs=0, parser=parser)
        
        prog = "fit param"
        description="set fit parameter"
        usage = "%prog [OPTIONS] parname status"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description, usage=usage)
        parser.add_option("-d", "--default", action="store_true", default=False, 
                            help="edit default fitter")
        hdtv.cmdline.AddCommand(prog, self.FitParam, 
                                completer=self.ParamCompleter, 
                                parser=parser, minargs=1)
        
        prog = "fit function peak activate"
        description = "selects which peak model to use"
        usage = "%prog [OPTIONS] name"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description, usage=usage)
        parser.add_option("-d", "--default", action="store_true", default=False, 
                            help="change default fitter")
        hdtv.cmdline.AddCommand(prog, self.FitSetPeakModel, 
                                completer= self.PeakModelCompleter, 
                                parser=parser, minargs=1)
        
   
        # calibration command
        prog = "calibration position assign"
        description = "Calibrate the active spectrum by asigning energies to fitted peaks. "
        description+= "peaks are specified by their index and the peak number within the peak "
        description+= "(if number is ommitted the first (and only?) peak is taken)."
        usage = "%prog [OPTIONS] <id0> <E0> [<od1> <E1> ...]"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description, usage=usage)
        parser.add_option("-s", "--spec", action="store", default="all", 
                        help="spectrum ids to apply calibration to")
        parser.add_option("-d", "--degree", action="store", default="1", 
                        help="degree of calibration polynomial fitted [default: %default]")
        parser.add_option("-f", "--show-fit", action="store_true",default=False, 
                        help="show fit used to obtain calibration")
        parser.add_option("-r", "--show-residual", action="store_true",default=False, 
                        help="show residual of calibration fit")
        parser.add_option("-t", "--show-table", action="store_true", default=False, 
                        help="print table of energies given and energies obtained from fit")
        hdtv.cmdline.AddCommand("calibration position assign", self.CalPosAssign, 
                                parser=parser, minargs=2)

    
    def FitWrite(self, args):
        """
        Write a list of all fits belonging to the active spectrum to an XML file
        """
        try:
            spec = self.spectra[self.spectra.activeID]
            if self.spectra.activeID in self.spectra.visible:
                visible = True
            else:
                visible = False
        except KeyError:
            print "No active spectrum"
            return False
        except AttributeError:
            print "There are no fits for this spectrum"
            return False
        except:
            return "USAGE"
            
        print 'Dumping fits belonging to %s (visible=%s):' %(str(spec), visible)
        hdtv.fitio.FitIO().Write(spec)


    def FitList(self, args):
        """
        Print a list of all fits belonging to the active spectrum 
        """
        try:
            spec = self.spectra[self.spectra.activeID]
            if self.spectra.activeID in self.spectra.visible:
                visible = True
            else:
                visible = False
            print 'Fits belonging to %s (visible=%s):' %(str(spec), visible)
            spec.ListObjects()
        except KeyError:
            print "No active spectrum"
            return False
        except AttributeError:
            print "There are no fits for this spectrum"
            return False
        except:
            return "USAGE"
        
    def FitDelete(self, args):
        """ 
        Delete fits
        """
        try:
            ids = hdtv.cmdhelper.ParseRange(args)
            if ids == "NONE":
                return
            elif ids == "ALL":
                ids = self.spectra[self.spectra.activeID].keys()
            self.spectra[self.spectra.activeID].RemoveObjects(ids)
        except KeyError:
            print "No active spectrum"
            return False
        except AttributeError:
            print "There are no fits for this spectrum"
            return False
        except:
            print "Usage: fit delete <ids>|all"
            return False
    
    def FitShow(self, args):
        """
        Show Fits
        """
        try:
            ids = hdtv.cmdhelper.ParseRange(args)
            if not self.spectra.activeID in self.spectra.visible:
                print "Warning: active spectrum is not visible, no action taken"
                return True
            if ids == "NONE":
                self.spectra[self.spectra.activeID].HideAll()
            elif ids == "ALL":
                self.spectra[self.spectra.activeID].ShowAll()
            else:
                self.spectra[self.spectra.activeID].ShowObjects(ids)
        except KeyError:
            print "No active spectrum"
            return False
        except AttributeError:
            print "There are no fits for this spectrum"
            return False
        except: 
            print "Usage: fit show <ids>|all|none"
            return False
    
    def FitPrint(self, args):
        try:
            spec = self.spectra[self.spectra.activeID]
        except KeyError:
            print "No active spectrum"
            return False
        try:
            ids = hdtv.cmdhelper.ParseRange(args)
            if ids == "NONE":
                return
            if ids == "ALL":
                ids = spec.keys()
            for ID in ids:
                try:
                    print str(spec[ID])
                except KeyError:
                    print "Warning: No fit with id %s" %ID
                    continue
        except AttributeError:
            print "There are no fits for this spectrum"
            return False
        except: 
            print "Usage: fit print <ids>|all"
            return False

    def FitActivate(self, args):
        """
        Activate one spectrum
        """
        try:
            ID = hdtv.cmdhelper.ParseRange(args)
            if ID=="NONE":
                ID = None
            else:
                ID = int(args[0])
            self.fitIf.ActivateFit(ID)
        except ValueError:
            print "Usage: fit activate <id>|none"
            return False

    def ParseIDs(self, strings):
        """
        Parse IDs, raises a ValueError if parsing fails
        """
        ids = hdtv.cmdhelper.ParseRange(strings, ["ALL", "NONE", "ACTIVE"])
        if ids=="NONE":
            return []
        elif ids=="ACTIVE":
            if self.spectra.activeID==None:
                print "Error: no active spectrum"
                return False
            else:
                ids = [self.spectra.activeID]
        elif ids=="ALL":
            ids = self.spectra.keys()
        return ids

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


    def FitStatus(self, args, options):
        self.fitIf.ShowFitStatus(options.default)

    def FitReset(self, args, options):
        self.fitIf.ResetParameters(options.default)
    
    def FitSetPeakModel(self, args, options):
        name = args[0].lower()
        # complete the model name if needed
        models = self.PeakModelCompleter(name)
        # check for unambiguity
        if len(models)>1:
            print "Error: peak model name %s is ambiguous" %name
        else:
            name = models[0]
            name = name.strip()
            self.fitIf.SetPeakModel(name, options.default)

    def PeakModelCompleter(self, text):
        """
        Creates a completer for all possible peak models
        """
        return hdtv.util.GetCompleteOptions(text, hdtv.fitter.gPeakModels.iterkeys())

    def FitParam(self, args, options):
        # first argument is parameter name
        param = args.pop(0)
        # complete the parameter name if needed
        parameter= self.ParamCompleter(param)
        # check for unambiguity
        if len(parameter)>1:
            print "Error: parameter name %s is ambiguous" %param
        elif len(parameter)==0:
            print "Error: parameter name %s is not valid" %param
        else:
            param = parameter[0]
            param = param.strip()
            try:
                self.fitIf.SetParameter(param," ".join(args), options.default)
            except ValueError, msg:
                print "Error: %s" % msg
        
    def ParamCompleter(self, text):
        """
        Creates a completer for all possible parameter names
        If the different peak models are used for active fitter and default fitter,
        options for both peak models are presented to the user.
        """
        defaultParams = set(self.fitIf.defaultFitter.params)
        activeParams  = set(self.fitIf.GetActiveFit().fitter.params)
        params = set.union(defaultParams, activeParams)
        return hdtv.util.GetCompleteOptions(text, params)
        
        
    def CalPosAssign(self, args, options):
        """ 
        Calibrate the active spectrum by assigning energies to fitted peaks

        Peaks are specified by their id and the peak number within the peak.
        Syntax: id.number
        If no number is given, the first peak in the fit is used.
        """
        if self.spectra.activeID == None:
            print "Warning: No active spectrum, no action taken."
            return False
        spec = self.spectra[self.spectra.activeID]    
        try:
            if len(args) % 2 != 0:
                print "Error: number of parameters must be even"
                return "USAGE"
            ids = self.ParseIDs(options.spec)
            if ids == False:
                return
            degree = int(options.degree)
        except ValueError:
            return "USAGE"
        try:
            channels = list()
            energies = list()
            while len(args)>0:
                # parse fit ids 
                fitID = args.pop(0).split('.')
                if len(fitID)>2:
                    raise ValueError
                elif len(fitID)==2:
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
            print "Error: " + str(msg)
            return False
        else:
            for ID in ids:
                try:
                    self.spectra[ID].SetCal(cal)
                    print "calibrated spectrum with id %d" %ID
                except KeyError:
                    print "Warning: there is no spectrum with id: %s" %ID
            self.fitIf.window.Expand()        
            return True


# plugin initialisation
import __main__
if not hasattr(__main__,"window"):
    import hdtv.window
    __main__.window = hdtv.window.Window()
if not hasattr(__main__, "spectra"):
    import hdtv.drawable
    __main__.spectra = hdtv.drawable.DrawableCompound(__main__.window.viewport)
__main__.f = FitInterface(__main__.window, __main__.spectra, show_panel=False)


