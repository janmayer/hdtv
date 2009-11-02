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

# Preliminary ROOT file interface for hdtv

import ROOT
import os
import hdtv.cmdline
import hdtv.tabformat
import hdtv.spectrum
import fnmatch
import readline
import hdtv.rfile_utils

from hdtv.spectrum import Spectrum, Histogram
#from hdtv.matrix import Matrix

#class RMatrix(Matrix):
#    """
#    ROOT TH2-backed matrix for projection
#    """
#    def __init__(self, hist, prj_x=True, color=None, cal=None):
#        hdtv.dlmgr.LoadLibrary("mfile-root")
#        self.hist = hist
#        prj = ROOT.RMatrix.PROJ_X if prj_x else ROOT.RMatrix.PROJ_Y
#        self.vmat = ROOT.RMatrix(self.hist, prj)
#        title = self.hist.GetTitle()
#        
#        # Load the projection on the cut axis
#        if prj_x:
#            phist = self.hist.ProjectionY(title + "_pry")
#        else:
#            phist = self.hist.ProjectionX(title + "_prx")
#                
#        Matrix.__init__(self, phist, title, color, cal)
#        
#    def __del__(self):
#        # Explicitly deconstruct C++ objects in the right order
#        self.vmat = None
#        ROOT.SetOwnership(self.hist, True)
#        self.hist = None
        

class RootFileInterface:
    def __init__(self, spectra):
        print "Loaded user interface for working with root files"
        self.spectra = spectra
        self.window = spectra.window
        self.caldict = spectra.caldict
        self.rootfile = None
        self.browser = None
        self.matviews = list()
        
        hdtv.cmdline.AddCommand("root browse", self.RootBrowse, nargs=0)
        hdtv.cmdline.AddCommand("root ls", self.RootLs, maxargs=1)
        hdtv.cmdline.AddCommand("root ll", self.RootLL, maxargs=1)
        hdtv.cmdline.AddCommand("root open", self.RootOpen, nargs=1, level=0, fileargs=True)
        hdtv.cmdline.AddCommand("root close", self.RootClose, nargs=0)
        hdtv.cmdline.AddCommand("root cd", self.RootCd, nargs=1,
                                completer=self.RootCd_Completer)
        hdtv.cmdline.AddCommand("root pwd", self.RootPwd, nargs=0)

        parser = hdtv.cmdline.HDTVOptionParser(prog="root get", usage="%prog [OPTIONS] <pattern>")
        parser.add_option("-r", "--replace", action="store_true",
                          default=False, help="replace existing histogram list")
        parser.add_option("-c", "--load-cal", action="store_true",
                          default=False, help="load calibration from calibration dictionary")
        parser.add_option("-v", "--invisible", action="store_true",
                          default=False, help="do not make histograms visible, only add to display list")
        hdtv.cmdline.AddCommand("root get", self.RootGet, minargs=1, completer=self.RootGet_Completer,
                                parser=parser)
        
        hdtv.cmdline.AddCommand("root matrix", self.RootMatrix, minargs=1,
                                completer=self.RootGet_Completer,
                                usage="root matrix <matname> [<matname> ...]")
        
#        parser = hdtv.cmdline.HDTVOptionParser(prog="root project", usage="%prog [OPTIONS] <TH2 histogram>")
#        parser.add_option("-p", "--project", default="x", help="projection axis",
#                          metavar="[x|y]")
#        hdtv.cmdline.AddCommand("root project", self.RootProject, nargs=1,
#                                completer=self.RootGet_Completer, parser=parser)
                                
        hdtv.cmdline.RegisterInteractive("gRootFile", self.rootfile)
    
    def RootBrowse(self, args):
        self.browser = ROOT.TBrowser()
        if self.rootfile != None and not self.rootfile.IsZombie():
            self.rootfile.Browse(self.browser)

    def RootLs(self, args):
        keys = ROOT.gDirectory.GetListOfKeys()
        if not keys:
            return
        
        names = [k.GetName() for k in keys]
    
        if len(args) > 0:
            names = fnmatch.filter(names, args[0])
        
        names.sort()
        hdtv.tabformat.tabformat(names)
    
    def RootLL(self, args):
        if len(args) == 0:
            ROOT.gDirectory.ls()
        else:
            ROOT.gDirectory.ls(args[0])
            
    def RootCd(self, args):
        if self.rootfile:
            cur_root_dir = ROOT.gDirectory
        else:
            cur_root_dir = None
    
        (posix_path, rfile, root_dir) = hdtv.rfile_utils.GetRelDirectory(os.getcwd(), cur_root_dir, args[0])
        if (posix_path, rfile, root_dir) == (None, None, None):
            print "Error: invalid path specified."
            return
            
        os.chdir(posix_path)
            
        # If root_dir is None, we moved outside the ROOT file and are now in
        # a POSIX directory. If rfile is not None, we *changed* the ROOT file.
        if root_dir == None or rfile != None:
            if self.rootfile != None:
                print "Info: closing old root file %s" % self.rootfile.GetName()
                self.rootfile.Close()
            self.rootfile = rfile
            if self.rootfile != None:
                print "Info: opened new root file %s" % self.rootfile.GetName()
            
        if root_dir != None:
            root_dir.cd()
        
    def RootPwd(self, args):
        if self.rootfile != None:
            ROOT.gDirectory.pwd()
        else:
            print os.getcwd()
            
    def RootOpen(self, args):
        return self.RootCd(args)
        
    def RootClose(self, args):
        if self.rootfile == None:
            print "Info: no root file open, no action taken"
        else:
            self.rootfile.Close()
            self.rootfile = None
            
    def RootGet_Completer(self, text, args=None):
        return self.Completer(text, dirs_only=False)
        
    def RootCd_Completer(self, text, args=None):
        return self.Completer(text, dirs_only=True)
        
    def Completer(self, text, dirs_only):
        buf = readline.get_line_buffer()
        if buf == "":
            # This should not happen...
            return []
            
        if self.rootfile:
            cur_root_dir = ROOT.gDirectory
        else:
            cur_root_dir = None
        
        if buf[-1] == " ":
            return hdtv.rfile_utils.PathComplete(".", cur_root_dir, "", text, dirs_only)
        else:
            path = buf.rsplit(None, 1)[-1]
            dirs = path.rsplit("/", 1)
            
            # Handle absolute paths
            if dirs[0] == "":
                dirs[0] = "/"
            
            if len(dirs) == 1:
                return hdtv.rfile_utils.PathComplete(".", cur_root_dir, "", text, dirs_only)
            else:
                return hdtv.rfile_utils.PathComplete(".", cur_root_dir, dirs[0], text, dirs_only)
                
    def GetTH2(self, path):
        """
        Load a 2D histogram (``matrix'') from a ROOT file.
        
        Note: Unlike RootGet(), this function does not support shell-style
        pattern expansion, as this make it too easy to undeliberately load
        too many histograms. As they use a lot of memory, this would likely
        lead to a crash of the program.
        """
        dirs = path.rsplit("/", 1)
        if len(dirs) == 1:
            # Load 2d histogram from current directory
            hist = ROOT.gDirectory.Get(dirs[0])
        else:
            if self.rootfile:
                cur_root_dir = ROOT.gDirectory
            else:
                cur_root_dir = None
        
            (posix_path, rfile, root_dir) = hdtv.rfile_utils.GetRelDirectory(os.getcwd(), cur_root_dir, dirs[0])
        
            if root_dir:
                hist = root_dir.Get(dirs[1])
            else:
                hist = None
            
            if rfile:
                rfile.Close()
    
        if hist == None or not isinstance(hist, ROOT.TH2):
            print "Error: %s is not a 2d histogram" % path
            return None

        return hist
        
    def RootMatrix(self, args):
        """
        Load a 2D histogram (``matrix'') from a ROOT file and display it.
        """
        for path in args:
            hist = self.GetTH2(path)
            if hist:
                title = hist.GetTitle()
                viewer = ROOT.HDTV.Display.MTViewer(400, 400, hist, title)
                self.matviews.append(viewer)
#            
#    def RootProject(self, args, options):
#        """
#        Load a 2D histogram (``matrix'') from a ROOT file in projection mode.
#        """
#        
#        axis = options.project.lower()
#        if axis == "x":
#            prj_x = True
#        elif axis == "y":
#            prj_x = False
#        else:
#            print "Error: projection axis must be x or y"
#            return None
#        
#        hist = self.GetTH2(args[0])
#        if hist:
#            spec = RMatrix(hist, prj_x)
#            sid = self.spectra.Insert(spec)
#            spec.color = hdtv.color.ColorForID(sid)
#            self.spectra.ActivateObject(sid)
#            self.window.Expand()        
    
    def RootGet(self, args, options):
        """
        Load spectra from Rootfile
        """
        if self.rootfile:
            cur_root_dir = ROOT.gDirectory
        else:
            cur_root_dir = None
            
        objs = []
        for pat in args:
            objs += hdtv.rfile_utils.Get(".", cur_root_dir, pat)
    
        if options.replace:
            self.spectra.Clear()
            
        loaded = list()
        self.window.viewport.LockUpdate()
        try:  # We should really use a context manager here...
            for obj in objs:
                if isinstance(obj, ROOT.TH1):
                    spec = Spectrum(Histogram(obj))
                    sid = self.spectra.Insert(spec)
                    spec.color = hdtv.color.ColorForID(sid)
                    loaded.append(sid)
                    if options.load_cal:
                        if spec.name in self.spectra.caldict:
                            spec.cal = self.caldict[spec.name]
                        else:
                            print "Warning: no calibration found for %s" % spec.name
                else:
                    hdtv.ui.warn("%s is not a 1D histogram object" % obj.GetName())
            hdtv.ui.msg("%d spectra loaded" % len(loaded))
            if options.invisible:
                self.spectra.HideObjects(loaded)
            elif len(loaded)>0:
                # activate last loaded spectrum
                self.spectra.ActivateObject(loaded[-1])
            # Expand window if it is the only spectrum
            if len(self.spectra) == 1: 
                self.window.Expand()
        finally:
            self.window.viewport.UnlockUpdate()

# plugin initialisation
import __main__
r = RootFileInterface(__main__.spectra)

