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

import hdtv.ui
import hdtv.cmdline
import hdtv.cmdhelper
import hdtv.fitxml


class fitTex:
    """
    """
    def __init__(self):
        hdtv.ui.msg("loading export fitlist to tex plugin")
    
        self.spectra = specta
    
        prog = "fit tex"
        description = "create a table in latex format"
        usage="%prog outfile"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description, usage=usage)
        parser.add_option("-c", "--columns", action="store",default="none", 
                          help="values to include as columns of the table")
        parser.add_option("-h","--header", action="store", default="none",
                          help="header of columns")
        parser.add_option("","--calc",action="store",default="none",
                          help="special calulations for some values")
        parser.add_option("-x","--xml",action="store", default="none",
                          help="use xml file instead of fits belonging to the active fit")
        parser.add_option("-f","--fits", action="store", default="all",
                          help="specify fits to include in table")
        parser.add_option("-s","--specs", action="store", default="none",
                          help="specify spectra")
        hdtv.cmdline.AddCommand(prog, self.CreateTable, nargs=0,parser=parser)
    
    
    def CreateTable(self, args, options):
        if not options.xml:
            peaks = self.CollectPeaks(options.specs, options.fits)
        else:
            peaks = self.ReadXML(options.xml)
    
    
    def CollectPeaks(self,specs=None,fits=None):
        peaks = list()
        # spectra that should be considered
        if specs:
            specIDs = hdtv.cmdhelper.ParseIds(specs, self.spectra)
        elif not self.spectra.activeID is None:
            # default is to use active spectrum
            specIDs = [self.spectra.activeID]
        else:
            msg = "Please active a spectrum or "
            msg+= "specify which spectrum to use by --specs option"
            hdtv.error(msg)
            return
        for specID in specIDs:
            spec = self.spectra[specID]
            if fits:
                fitIDs = hdtv.cmdhelper.ParseFitID(fits, spec)
            else:
                # default is to print all fits
                fitIDs = spec.keys()
            for fitID in fitIDs:
                fit = spec[fitID]
                peaks.extend(fit.peaks)
        return peaks
                
                
            
    def ReadXML(self, xmlname):
        pass
        
    
    
    


#preamble=
#"""
#makeatletter
#\@ifundefined{standalonetrue}{\newif\ifstandalone}{}
#\@ifundefined{section}{\standalonetrue}{\standalonefalse}
#\makeatother
#\ifstandalone

#\documentclass[12pt,twoside,a4paper]{report}
#\usepackage[ngerman]{babel}
#\usepackage{amsmath}
#\usepackage{amssymb}
#\usepackage{graphicx}
#\usepackage{a4}
#\usepackage[T1]{fontenc}
#\usepackage{ae,aecompl}
#\usepackage[utf8]{inputenc}
#\usepackage[font=small,labelfont=bf,textfont=it]{caption}
#\usepackage{longtable}


#\begin{document}
#\fi
#\begin{center}
#\begin{longtable}{|l|l|l|}
#"""

#headerlines = 
#"""
#\hline 
#\multicolumn{1}{|c|}{\textbf{Eins}} & 
#\multicolumn{1}{c|}{\textbf{Zwei}} & 
#\multicolumn{1}{c|}{\textbf{Drei}} \\ \hline 
#\endfirsthead

#\hline
#\multicolumn{1}{|c|}{\textbf{Eins}} &
#\multicolumn{1}{c|}{\textbf{Zwei}} &
#\multicolumn{1}{c|}{\textbf{Drei}} \\ \hline 
#\endhead
#"""

#footerlines = 
#"""
#\hline 
#\multicolumn{3}{r}{{wird fortgesetzt...}} \\ 
#\endfoot

#\hline \hline
#\endlastfoot
#"""

if not hasattr(__main__, "spectra"):
    import hdtv.drawable
    __main__.spectra = hdtv.drawable.DrawableCompound(__main__.window.viewport)
FitTex(__main__.spectra)
