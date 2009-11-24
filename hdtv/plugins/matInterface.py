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

#-------------------------------------------------------------------------------
# Matrix interface for hdtv
#-------------------------------------------------------------------------------
import ROOT

import hdtv.ui

from hdtv.matrix import Matrix

class MatInterface:
    def __init__(self, spectra):
        hdtv.ui.msg("Loaded user interface for working with 2-d spectra")
        self.spectra= spectra
        self.window = spectra.window
        self.oldcut = None
        
        # tv commands
        self.tv = TvMatInterface(self)

        # Register hotkeys
        self.window.AddHotkey(ROOT.kKey_g, lambda: self.spectra.SetMarker("cut"))
        self.window.AddHotkey([ROOT.kKey_c,ROOT.kKey_g],
                                lambda: self.spectra.SetMarker("cutregion"))
        self.window.AddHotkey([ROOT.kKey_c,ROOT.kKey_b],
                                lambda: self.spectra.SetMarker("cutbg"))
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_c, ROOT.kKey_g], 
                                lambda: self.spectra.RemoveMarker("cutregion"))
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_c, ROOT.kKey_b],
                                lambda: self.spectra.RemoveMarker("cutbg"))
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_C], self.spectra.ClearCut)
        self.window.AddHotkey([ROOT.kKey_Plus, ROOT.kKey_C], self.spectra.StoreCut)
        self.window.AddHotkey(ROOT.kKey_C, self.spectra.ExecuteCut)
        self.window.AddHotkey([ROOT.kKey_c, ROOT.kKey_s],
                        lambda: self.window.EnterEditMode(prompt = "Show Cut: ",
                        handler = self._HotkeyShow))
        self.window.AddHotkey([ROOT.kKey_c, ROOT.kKey_a],
                        lambda: self.window.EnterEditMode(prompt = "Activate Cut: ",
                        handler = self._HotkeyActivate))
        self.window.AddHotkey([ROOT.kKey_c, ROOT.kKey_p], lambda: self._HotkeyShow("PREV"))
        self.window.AddHotkey([ROOT.kKey_c, ROOT.kKey_n], lambda: self._HotkeyShow("NEXT"))
        self.window.AddHotkey(ROOT.kKey_Tab, self._HotkeySwitch)
        
        
    def _HotkeyShow(self, args):
        """
        Show wrapper for use with a Hotkey (internal use)
        """
        spec = self.spectra.GetActiveObject()
        if spec is None:
            self.window.viewport.SetStatusText("No active spectrum")
            return
        if not hasattr(spec, "matrix") or spec.matrix is None:
            self.window.viewport.SetStatusText("No matrix")
            return
        try:
            ids = hdtv.cmdhelper.ParseIds(args, spec.matrix)
        except ValueError:
            self.window.viewport.SetStatusText("Invalid cut identifier: %s" % args)
            return
        spec.ShowObjects(ids)
  

    def _HotkeyActivate(self, args):
        """
        ActivateObject wrapper for use with a Hotkey (internal use)
        """
        spec = self.spectra.GetActiveObject()
        if spec is None:
            self.window.viewport.SetStatusText("No active spectrum")
            return
        if not hasattr(spec, "matrix") or spec.matrix is None:
            self.window.viewport.SetStatusText("No matrix")
            return
        try:
            ids = hdtv.cmdhelper.ParseIds(args, spec.matrix)
        except ValueError:
            self.window.viewport.SetStatusText("Invalid cut identifier: %s" % args)
            return
        if len(ids) == 1:
            self.window.viewport.SetStatusText("Activating cut %s" %ids[0])
            self.spectra.ActivateCut(ids[0])
        elif len(ids) == 0:
            self.window.viewport.SetStatusText("Deactivating cut")
            self.spectra.ActivateCut(None)
        else:
            self.window.viewport.SetStatusText("Can only activate one cut")
        

    def _HotkeySwitch(self):
        #FIXME
        spec = self.spectra.GetActiveObject()
        if spec is None:
            hdtv.ui.error("There is no active spectrum")
            return 
        if not hasattr(spec, "matrix") or spec.matrix is None:
            hdtv.ui.error("Active spectrum does not belong to a matrix")
            return 
        mat = spec.matrix
        # for a cut, switch to projection
        if spec in mat.specs:
            if spec.axis == "y":
                # show x proj
                ID = self.spectra.Index(mat.xproj)
            else:
                # show y proj
                ID = self.spectra.Index(mat.yproj)
            if ID is None:
                hdtv.ui.warn("Projection is not loaded.")
                return
        # for a projection, cut to last shown cut
        else:
            ID = self.oldcut
            if ID is None:
                # FIXME
                hdtv.ui.warn("No old cut")
                return
        self.spectra.ShowObjects(ID)
    
        
    def LoadMatrix(self, fname, sym, ID=None):
        # FIXME: just for testing!
        histo = Histo2D()
        matrix = Matrix(histo, sym, self.spectra.viewport)
        proj = matrix.xproj
        ID = self.spectra.GetFreeID()
        matrix.ID = ID
        matrix.color = hdtv.color.ColorForID(ID)
        ID = self.spectra.Insert(proj, ID=ID+".x")
        self.spectra.ActivateObject(ID)

        
class TvMatInterface:
    def __init__(self, matInterface):
        self.matIf = matInterface
        self.spectra = self.matIf.spectra

        prog = "matrix get"
        description = "load a matrix, i.e. the projections"
        description+= "if the matrix is symmetric it only loads one projection"
        description+= "if it is asymmetric both projections will be loaded."
        usage="%prog [OPTIONS] asym|sym filename"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog,usage=usage)
        parser.add_option("-s", "--spectrum", action="store",default=None, 
                          help="base id for loaded projections")
        hdtv.cmdline.AddCommand(prog, self.MatrixGet, level=0, 
                                nargs=2,fileargs=True, parser=parser)
        
        # FIXME
        prog = "matrix list"
        description = "list all loaded matrices and the belonging cuts and cut spectra."
        
        # FIXME
        prog = "matrix project"
        description = "reload projection of matrix"
        
        # FIXME
        prog = "matrix view"
        description = "show 2D view of the matrix"
                                       
        prog = "cut marker"
        description = "set/delete a marker for cutting"
        description +="(possible types are background, region, peak)"
        usage = "%prog type action position"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.CutMarkerChange, nargs=3,
                                parser = parser, completer=self.MarkerCompleter)
        
        # FIXME: this should accept --cut to reload cut spectra for a cut
        prog = "cut execute"
        description = "execute cut"
        usage = "%prog"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.CutExecute, level=0, nargs=0, parser = parser)
        
        prog = "cut clear"
        description = "clear cut marker and remove last cut if it was not stored"
        usage = "%prog"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.CutClear, nargs=0, parser = parser)
        
        prog = "cut store"
        description = "deactivates last cut (overwrite protection)"
        usage = "%prog"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.CutStore, nargs=0, parser = parser)
                                
                                
        prog = "cut activate"
        description = "re-activates a cut from the cutlist"
        usage = "%prog ID"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.CutActivate, nargs=1, parser = parser)
        
        # FIXME
        prog = "cut delete"
        description = "delete a cut"
        
        # FIXME
        prog = "cut show"
        description = "show a cut"
        
        # FIXME
        prog = "cut hide"
        description = "hide a cut"
        
                                
    def MatrixGet(self, args, options):
        if options.spectrum is not None:
            ID = options.spectrum
        else:
            ID = None
        if args[0] not in ["asym", "sym"]:
            # FIXME: is there really no way to test that automatically????
            hdtv.ui.error("Please specify if matrix is of type asym or sym")
            return "USAGE"
        self.matIf.LoadMatrix(args[1], args[0], ID = ID)
        
    def CutMarkerChange(self, args, options):
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
        # replace "background" with "cutbg" which is internally used
        if mtype == "background": mtype="cutbg"
        # replace "region" with "cutregion" which is internally used
        if mtype == "region": mtype="cutregion"
        action = action[0].strip()
        if action == "set":
            self.spectra.SetMarker(mtype, pos)
        if action == "delete":
            self.spectra.RemoveMarker(mtype, pos)

    def MarkerCompleter(self, text, args=[]):
        """
        Helper function for CutMarkerChange
        """
        if not args:
            mtypes = ["background","region"]
            return hdtv.cmdhelper.GetCompleteOptions(text, mtypes)
        elif len(args)==1:
            actions = ["set", "delete"]
            return hdtv.cmdhelper.GetCompleteOptions(text, actions)
            
    def CutExecute(self, args, options):
        return self.spectra.ExecuteCut()
        
    def CutClear(self, args, options):
        return self.spectra.ClearCut()
        
    def CutStore(self, args, options):
        return self.spectra.StoreCut()
        
    def CutActivate(self, args, options):
        """
        Activate a cut
        
        This marks a stored cut as active and copies its markers to the work cut
        """
        sid = self.spectra.activeID
        if sid is None:
            hdtv.ui.warn("No active spectrum")
            return
        spec = self.spectra.dict[sid]
        if not hasattr(spec, "matrix") or spec.matrix is None:
            hdtv.ui.warn("Active spectrum does not belong to a matrix")
            return
        try:
            ids = hdtv.cmdhelper.ParseIds(args, spec.matrix)
        except ValueError:
            return "USAGE"
        if len(ids) == 1:
            hdtv.ui.msg("Activating cut %s" %ids[0])
            self.spectra.ActivateCut(ids[0])
        elif len(ids) == 0:
            hdtv.ui.msg("Deactivating cut")
            self.spectra.ActivateCut(None)
        else:
            hdtv.ui.error("Can only activate one cut")
        
# plugin initialisation
import __main__
__main__.mat = MatInterface(__main__.spectra)
