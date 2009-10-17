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
import os
import glob
import copy

import hdtv.cmdline
import hdtv.cmdhelper
import hdtv.color
import hdtv.cal
import hdtv.util
import hdtv.ui
 
from hdtv.spectrum import Spectrum, Histogram, FileHistogram
from hdtv.specreader import SpecReaderError

class SpecInterface:
    """
    User interface to work with 1-d spectra
    """
    def __init__(self, spectra):
        hdtv.ui.msg("Loaded user interface for working with 1-d spectra")
        self.spectra= spectra
        self.window = spectra.window
        self.caldict = spectra.caldict
        
        # tv commands
        self.tv = TvSpecInterface(self)
        
        # good to have as well...
        self.window.AddHotkey(ROOT.kKey_PageUp, self.spectra.ShowPrev)
        self.window.AddHotkey(ROOT.kKey_PageDown, self.spectra.ShowNext)
        
        # register common tv hotkeys
        self.window.AddHotkey([ROOT.kKey_N, ROOT.kKey_p], self.spectra.ShowPrev)
        self.window.AddHotkey([ROOT.kKey_N, ROOT.kKey_n], self.spectra.ShowNext)
        self.window.AddHotkey(ROOT.kKey_Equal, self.spectra.RefreshAll)
        self.window.AddHotkey(ROOT.kKey_t, self.spectra.RefreshVisible)
        self.window.AddHotkey(ROOT.kKey_n,
                lambda: self.window.EnterEditMode(prompt="Show spectrum: ",
                                           handler=self._HotkeyShow))
        self.window.AddHotkey(ROOT.kKey_a,
                lambda: self.window.EnterEditMode(prompt="Activate spectrum: ",
                                           handler=self._HotkeyActivate))
    
    def _HotkeyShow(self, arg):
        """ 
        ShowObjects wrapper for use with Hotkey
        """
        try:
            ids = hdtv.cmdhelper.ParseIds(arg, self.spectra)
            if len(ids) == 0:
                self.spectra.HideAll()
            else:
                self.spectra.ShowObjects(ids)
        except ValueError:
            self.window.viewport.SetStatusText("Invalid spectrum identifier: %s" % arg)

        
    def _HotkeyActivate(self, arg):
        """
        ActivateObject wrapper for use with Hotkey
        """
        try:
            ids = hdtv.cmdhelper.ParseIds(arg, self.spectra)
            if len(ids) > 1:
                self.window.viewport.SetStatusText("Cannot activate more than one spectrum")
            elif len(ids) == 0: # Deactivate
                oldactive = self.spectra.activeID
                self.spectra.ActivateObject(None)
                self.window.viewport.SetStatusText("Deactivated spectrum %d" % oldactive)
            else:
                ID = ids[0]
                self.spectra.ActivateObject(ID)
                self.window.viewport.SetStatusText("Activated spectrum %d" % self.spectra.activeID)
        except ValueError:
            self.window.viewport.SetStatusText("Invalid id: %s" % arg)


    def LoadSpectra(self, patterns, ID=None):
        """
        Load spectra from files matching patterns.
        
        If ID is specified, the spectrum is stored with id ID, possibly
        replacing a spectrum that was there before.
        """
        # Avoid multiple updates
        self.window.viewport.LockUpdate()
        # only one filename is given
        if type(patterns) == str or type(patterns) == unicode:
            patterns = [patterns]

        if ID is not None and len(patterns) > 1:
            hdtv.ui.error("If you specify an ID, you can only give one pattern")
            self.window.viewport.UnlockUpdate()
            return
        
        loaded = [] 
        for p in patterns:
            # put fmt if available
            p = p.rsplit("'", 1)
            if len(p) == 1 or not p[1]:
                (fpat, fmt) = (p[0], None)
            else:
                (fpat, fmt) = p

            files = glob.glob(os.path.expanduser(fpat))
            
            if len(files) == 0:
                hdtv.ui.warn("Warning: %s: no such file" % fpat)
            elif ID is not None and len(files) > 1:
                hdtv.ui.error("Error: pattern %s is ambiguous and you specified an ID" % fpat)
                break
                
            files.sort()
            
            for fname in files:
                try:
                    # Create spectrum object
                    spec = Spectrum(FileHistogram(fname, fmt))
                except (OSError, SpecReaderError):
                    hdtv.ui.warn("Could not load %s'%s" % (fname, fmt))
                else:
                    sid = self.spectra.Insert(spec, ID)
                    spec.color = hdtv.color.ColorForID(sid)
                    if spec.name in self.spectra.caldict.keys():
                        spec.cal = self.spectra.caldict[spec.name]
                    loaded.append(sid)
                    
                    if fmt == None:
                        hdtv.ui.msg("Loaded %s into %d" % (fname, sid))
                    else:
                        hdtv.ui.msg("Loaded %s'%s into %d" % (fname, fmt, sid))
        
        if len(loaded)>0:
            # activate last loaded spectrum
            self.spectra.ActivateObject(loaded[-1])
        # Expand window if it is the only spectrum
        if len(self.spectra) == 1: 
            self.window.Expand()
        self.window.viewport.UnlockUpdate()
        return loaded

    def ListSpectra(self, visible=False):
        """
        Create a list of all spectra (for printing)
        """
        spectra = list()
        params = ["ID", "stat", "name"]
        
        for (ID, obj) in self.spectra.dict.iteritems():
            if visible and (ID not in self.spectra.visible):
                continue
            
            thisspec = dict()
            
            status = str()
            if ID == self.spectra.activeID:
                status += "A"
            if ID in self.spectra.visible:
                status += "V"
            
            thisspec["ID"] = ID
            thisspec["stat"] = status
            thisspec["name"] = self.spectra.dict[ID].name
            spectra.append(thisspec)
        
        return str(hdtv.util.Table(spectra, params, sortBy="ID"))
 
    def CopySpectrum(self, ID, copyTo=None):
        """
        Copy spectrum
        
        Return ID of new spectrum
        """
        if copyTo is None:
            copyTo = self.spectra.GetFreeID()
        # get copy of underlying histogramm
        hist = copy.copy(self.spectra.dict[ID].hist)
        # create new spectrum object
        spec = Spectrum(hist)
        spec.color = hdtv.color.ColorForID(copyTo)
        spec.typeStr = "spectrum, copy"
        sid = self.spectra.Insert(spec, copyTo)
        hdtv.ui.msg("Copied spectrum " + str(ID) + " to " + str(sid))


class TvSpecInterface:
    """
    TV style commands for the spectrum interface.
    """
    def __init__(self, specInterface):
        self.specIf = specInterface
        self.spectra = self.specIf.spectra
        
        # spectrum commands
        prog = "spectrum get"   
        usage="%prog [OPTIONS] <pattern> [<pattern> ...]"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog,usage=usage)
        parser.add_option("-s", "--spectrum", action="store",default=None, 
                          help="id for loaded spectrum")
        hdtv.cmdline.AddCommand("spectrum get", self.SpectrumGet, level=0, 
                                minargs=1,fileargs=True, parser=parser)
        # the spectrum get command is registered with level=0, 
        # this allows "spectrum get" to be abbreviated as "spectrum", register 
        # all other commands starting with spectrum with default or higher priority
        
        prog="spectrum list"
        usage="%prog [OPTIONS]"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, usage=usage)
        parser.add_option("-v", "--visible", action="store_true", default=False, 
                          help="list only visible (and active) spectra")
        hdtv.cmdline.AddCommand("spectrum list", self.SpectrumList, nargs=0, parser=parser)
        
        
        hdtv.cmdline.AddCommand("spectrum delete", self.SpectrumDelete, minargs=0,
                                usage="%prog <ids>")
        hdtv.cmdline.AddCommand("spectrum activate", self.SpectrumActivate, nargs=1,
                                usage="%prog <id>")
        hdtv.cmdline.AddCommand("spectrum show", self.SpectrumShow, minargs=0,
                                usage="%prog <ids>|all|none|...")
        hdtv.cmdline.AddCommand("spectrum hide", self.SpectrumHide, minargs=0,
                                usage="%prog <ids>|all|none|...", level = 2)
        hdtv.cmdline.AddCommand("spectrum info", self.SpectrumInfo, minargs=0,
                                usage="%prog [ids]")
        hdtv.cmdline.AddCommand("spectrum update", self.SpectrumUpdate, minargs=0,
                                usage="%prog <ids>|all|shown")
        hdtv.cmdline.AddCommand("spectrum write", self.SpectrumWrite, minargs=1, maxargs=2,
                                usage="%prog <filename>'<format> [id]")
        hdtv.cmdline.AddCommand("spectrum normalization", self.SpectrumNormalization,
                                minargs=1, usage="%prog [ids] <norm>")

        prog = "spectrum add"
        usage="%prog [OPTIONS] <target-id> <ids>|all"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, usage=usage)
        parser.add_option("-n", "--normalize", action="store_true", 
                          help="normalize <target-id> by dividing through number of added spectra afterwards")
        hdtv.cmdline.AddCommand(prog, self.SpectrumAdd, level = 2, minargs=1, fileargs=False, parser=parser)

        prog = "spectrum substract"
        usage="%prog [OPTIONS] <target-id> <ids>|all"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, usage=usage)
        hdtv.cmdline.AddCommand(prog, self.SpectrumSub, level = 2, minargs=1, 
                                fileargs=False, parser=parser)
        
        prog = "spectrum multiply"
        usage="%prog [OPTIONS]  [ids]|all|... <factor>"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, usage=usage)
        hdtv.cmdline.AddCommand(prog, self.SpectrumMultiply, level = 2, minargs=1, 
                                fileargs=False, parser=parser)
        
        prog = "spectrum copy"
        usage="%prog <ids>"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, usage=usage)
        parser.add_option("-s", "--spectrum", action="store", default=None, help="Target spectrum id")
        hdtv.cmdline.AddCommand(prog, self.SpectrumCopy, level = 2, 
                                fileargs=False, parser=parser)
        
        prog = "spectrum name"
        usage="%prog [id] <name>"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, usage=usage)
        hdtv.cmdline.AddCommand(prog, self.SpectrumName, level = 2, 
                                fileargs = False, parser=parser)

    
    def SpectrumList(self, args, options):
        """
        Print a list of spectra
        """
        speclist = self.specIf.ListSpectra(visible=options.visible)
        hdtv.ui.msg(speclist)


    def SpectrumGet(self, args, options):
        """
        Load Spectra from files
        """
        if options.spectrum is not None:
            ID = int(options.spectrum)
        else:
            ID = None
        self.specIf.LoadSpectra(patterns = args, ID = ID)


    def SpectrumDelete(self, args):
        """ 
        Deletes spectra 
        """
        try:
            ids = hdtv.cmdhelper.ParseIds(args, self.spectra)
        except ValueError:
            return "USAGE"
                    
        if len(ids) == 0:
            hdtv.ui.warn("Nothing to do")
            return
        for ID in ids:
            self.spectra.Pop(ID)

    def SpectrumActivate(self, args):
        """
        Activate one spectra
        """
        try:
            ids = hdtv.cmdhelper.ParseIds(args, self.spectra)
        except ValueError:
            return "USAGE"

        if len(ids) > 1:
            hdtv.ui.error("Can only activate one spectrum")
        elif len(ids) == 0:
            self.spectra.ActivateObject(None)
        else:
            self.spectra.ActivateObject(min(ids))


    def SpectrumCopy(self, args, options):
        """
        Copy spectra
        """
        hdtv.ui.debug("SpectrumCopy: args= " + str(args) + " options= " + str(options), level=6)
        try:
            ids = hdtv.cmdhelper.ParseIds(args, self.spectra)
            
            if len(ids) == 0:
                hdtv.ui.warn("Nothing to do")
                return
        except ValueError:
            return "USAGE"
            
        targetids = list()
        if options.spectrum is not None:
            targetids = hdtv.cmdhelper.ParseIds(options.spectrum, self.spectra, only_existent=False)
        if len(targetids) == 0:
            targetids = [None for i in range(0,len(ids))]
        elif len(targetids) == 1: # Only start ID is given
            startID = targetids[0]
            targetids = [i for i in range(startID, startID+len(ids))]
        elif len(targetids) != len(ids):
            hdtv.ui.error("Number of target ids does not match number of ids to copy")
            return
        
        # TODO: unfortunately ParseRange() in ParseIDs() uses unsorted sets
        ids.sort()
        targetids.sort()
        for i in range(0, len(ids)):
            try:                
                self.specIf.CopySpectrum(ids[i], copyTo=targetids[i])
            except KeyError:
                hdtv.ui.error("No such spectrum: " + str(ids[i]))
                
    
    def SpectrumAdd(self, args, options):
        """
        Add spectra (spec1 + spec2, ...)
        """
        try:
            addTo = int(args[0])
            try:
                ids = hdtv.cmdhelper.ParseIds(args[1:], self.spectra)
            except KeyError:
                hdtv.ui.msg("Adding active spectrum %d" % self.spectra.activeID)
                ids = [self.spectra.activeID]
        except ValueError:
            return "USAGE"
        
        if len(ids) == 0:
            hdtv.ui.warn("Nothing to do")
            return

        if not addTo in self.spectra.dict.keys():
            sid = self.specIf.CopySpectrum(ids.pop(), addTo)
        
        for i in ids:
            try:
                hdtv.ui.msg("Adding " + str(i) + " to " + str(addTo))
                self.spectra.dict[addTo].Plus(self.spectra.dict[i])
            except KeyError:
                hdtv.ui.error("Could not add " + str(i))
                
        if options.normalize:
            norm_fac = len(ids)
            hdtv.ui.msg("Normalizing spectrum %d by 1/%d" % (addTo, norm_fac))
            self.spectra.dict[addTo].Multiply(1./norm_fac)


    def SpectrumSub(self, args, options):
        """
        Substract spectra (spec1 - spec2, ...)
        """   
        subFrom = int(args[0])
        try:
            ids = hdtv.cmdhelper.ParseIds(args[1:], self.spectra)
        except KeyError:
            ids = [self.spectra.activeID]
            hdtv.ui.msg("Substracting active spectrum %d" % self.spectra.activeID)
        except ValueError:
            return "USAGE"
            
        if len(ids) == 0:
            hdtv.ui.warn("Nothing to do")
            return

        if not subFrom in self.spectra.dict.keys():
            sid = self.specIf.CopySpectrum(ids.pop(), subFrom)
        
        for i in ids:
            try:
                hdtv.ui.msg("Substracting " + str(i) + " from " + str(subFrom))
                self.spectra.dict[subFrom].Minus(self.spectra.dict[i])
            except KeyError:
                hdtv.ui.error("Could not substract " + str(i))

    
    def SpectrumMultiply(self, args, options):
        """
        Multiply spectrum
        """
        try:
            factor = float(eval(args[-1]))
            
            if len(args) == 1:
                if self.spectra.activeID is not None:
                    msg = "Using active spectrum %d for multiplication" % self.spectra.activeID
                    hdtv.ui.msg(msg)
                    ids = [self.spectra.activeID]
                else:
                    hdtv.ui.msg("No active spectrum")
                    ids = list()
            else:
                ids = hdtv.cmdhelper.ParseIds(args[:-1], self.spectra)

        except (IndexError, ValueError):
            return "USAGE"
            
        if len(ids) == 0:
            hdtv.ui.warn("Nothing to do")
            return

        for i in ids:
            if i in self.spectra.dict.keys():
                hdtv.ui.msg("Multiplying " + str(i) + " with " + str(factor))
                self.spectra.dict[i].Multiply(factor)
            else:
                hdtv.ui.error("Cannot multiply spectrum " + str(i) + " (Does not exist)")  
    
    
    def SpectrumHide(self, args):
        """
        Hides spectra
        """
        return self.SpectrumShow(args, inverse=True)
        
    
    def SpectrumShow(self, args, inverse=False):
        """
        Shows spectra
        
        When inverse == True SpectrumShow behaves like SpectrumHide
        """
        if len(args) == 0:
            ids = self.spectra.dict.keys()
        else:
            try:
                ids = hdtv.cmdhelper.ParseIds(args, self.spectra)
            except ValueError:
                return "USAGE"
        if inverse:
            self.spectra.HideObjects(ids)
        else:
            self.spectra.ShowObjects(ids)
     
            
    def SpectrumInfo(self, args):
        """
        Print info on spectrum objects
        """
        try:
            ids = hdtv.cmdhelper.ParseIds(args, self.spectra)
        except ValueError:
            return "USAGE"

        s = str()
        for ID in ids:
            try:
                spec = self.spectra.dict[ID]
            except KeyError:
                s += "Spectrum %d: ID not found\n" % ID
                continue
            s += "Spectrum %d:\n" % ID
            s += hdtv.cmdhelper.Indent(spec.info, "  ")
            s += "\n"
        hdtv.ui.msg(s, newline=False)


    def SpectrumUpdate(self, args):
        """
        Refresh spectra
        """
        try:
            ids = hdtv.cmdhelper.ParseIds(args, self.spectra)
        except ValueError:
            return "USAGE"
        if len(ids) == 0:
            hdtv.ui.warn("Nothing to do")
            return
        self.spectra.RefreshObjects(ids)

            
    def SpectrumWrite(self, args):
        """
        Write Spectrum to File
        """
        # TODO: should accept somthing like "spec write all" -> Utilize: hdtv.cmdhelper.ParseSpecIds
        try:
            (fname, fmt) = args[0].rsplit("'", 1)
            if len(args) == 1:
                ID = self.spectra.activeID
            elif len(args)==2:
                ID = int(args[1])
            else:
                hdtv.ui.error("There is just one index possible here.")
                raise ValueError
            try:
                self.spectra.dict[ID].WriteSpectrum(fname, fmt)
                hdtv.ui.msg("Wrote spectrum with id %d to file %s" %(ID, fname))
            except KeyError:
                 hdtv.ui.warn("There is no spectrum with id: %s" %ID)
        except ValueError:
            return "USAGE"
            
    def SpectrumName(self, args, options):
        """
        Give spectrum a name
        """
        if len(args) == 1:
            ID = self.spectra.activeID
            name = args[0]
        else:
            try:
                ids = hdtv.cmdhelper.ParseIds(args[0], self.spectra)
            except ValueError:
                return "USAGE"
            
            if len(ids) == 0:
                hdtv.ui.warn("Nothing to do")
                return
            elif len(ids) > 1:
                hdtv.ui.warn("Can only rename one spectrum at a time")
                return
            
            ID = ids[0]
            name = args[1]
        
        self.spectra.dict[ID].name = name
        hdtv.ui.msg("Renamed spectrum %d to \'%s\'" % (ID, name))
    
    def SpectrumNormalization(self, args):
        "Set normalization for spectrum"
        try:
            if len(args) == 1:
                ids = [ self.spectra.activeID ]
            else:
                ids = hdtv.cmdhelper.ParseIds(args[:-1], self.spectra)
                if len(ids) == 0:
                    hdtv.ui.warn("Nothing to do")
                    return

            norm = float(args[-1])
        except ValueError:
            return "USAGE"
            
        for ID in ids:
            try:
                self.spectra.dict[ID].norm = norm
            except KeyError:
                hdtv.ui.error("There is no spectrum with id: %s" % ID)


# plugin initialisation
import __main__
__main__.s = SpecInterface(__main__.spectra)

