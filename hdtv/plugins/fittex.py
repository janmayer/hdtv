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
import os
import hdtv.ui

from hdtv.util import Table
    
preamble="""\makeatletter
\@ifundefined{standalonetrue}{\\newif\ifstandalone}{}
\@ifundefined{section}{\standalonetrue}{\standalonefalse}
\makeatother
\ifstandalone

\documentclass[12pt,twoside,a4paper]{report}
\usepackage[ngerman]{babel}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{a4}
\usepackage[T1]{fontenc}
\usepackage{ae,aecompl}
\usepackage[utf8]{inputenc}
\usepackage[font=small,labelfont=bf,textfont=it]{caption}
\usepackage{longtable}


\\begin{document}
\\fi
\\begin{center}
\\begin{longtable}"""

enddok="""\end{longtable}
\end{center}

\ifstandalone
\end{document}
"""

class TexTable(Table):
    def __init__(self, data, keys, header = None, sortBy = None, reverseSort = False, ha="c"):
        Table.__init__(self, data, keys, header , ignoreEmptyCols = False, sortBy=sortBy, 
                       reverseSort = reverseSort, extra_header=preamble, extra_footer=enddok)
        self.col_sep_char = "&"
        self.empty_field = " "
        self.ha = ha
                 
    
    def build_header(self):
        header = "\hline" + os.linesep
        for key in self.header:
            header +="\multicolumn{1}{%s}{\\textbf{%s}}" %(self.ha,key)
            if key is not self.header[-1]:
                header +="&"
            else:
                header += "\\\ \hline" + os.linesep
        header += "\endfirsthead" + os.linesep + os.linesep
        header += "\hline"+ os.linesep
        for key in self.header:
            header +="\multicolumn{1}{%s}{\\textbf{%s}}" %(self.ha,key)
            if key is not self.header[-1]:
                header +="&"
            else:
                header += "\\\ \hline" + os.linesep+ os.linesep
        header += "\endhead" + os.linesep + os.linesep
        
        header +="\hline" + os.linesep
        header +="\multicolumn{%d}{r}{{wird fortgesetzt...}} \\\ " %len(self.header) + os.linesep 
        header +="\endfoot" + os.linesep + os.linesep

        header +="\hline \hline" + os.linesep
        header +="\endlastfoot" + os.linesep + os.linesep

        return header

                 
    def __str__(self):
        text = str()
        if not self.extra_header is None:
            text += str(self.extra_header)+"{"+len(self.keys)*self.ha+"}" + os.linesep
            
        lines = self.build_lines()
        
        header_line = self.build_header()
        text += header_line +os.linesep
       
        # Build lines
        for line in lines:
            line_str = ""
            for col in range(0, len(line)):
                if not self._ignore_col[col]:
                    line_str += str(" " + line[col] + " ").rjust(self._col_width[col]) 
                if col!=len(line)-1:
                    line_str += self.col_sep_char

            text += line_str  +"\\\ "+os.linesep
   
        if not self.extra_footer is None:
            text += str(self.extra_footer)
            
        return text

class fitTex:
    """
    Create a table for use with latex.
    
    The resulting file can be compiled standalone or included in another latex
    document. It uses the longtable package.
    """
    def __init__(self, spectra, fitInterface):
        hdtv.ui.msg("loading plugin for exporting fitlist to tex")
    
        self.spectra = spectra
        self.f = fitInterface
    
        prog = "fit tex"
        description = "create a table in latex format"
        usage="%prog outfile"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description, usage=usage)
        parser.add_option("-c", "--columns", action="store",default=None, 
                          help="values to include as columns of the table")
        parser.add_option("-H","--header", action="store", default=None,
                          help="header of columns")
        parser.add_option("-k", "--key-sort", action = "store", default = None,
                          help = "sort by key")
        parser.add_option("-r", "--reverse-sort", action = "store_true", default = False,
                        help = "reverse the sort")
        parser.add_option("-a","--alignment",action="store", default="c",
                        help="horizontal alignment (c=center, l=left or r=right)")
        parser.add_option("-f","--fit", action="store", default="all",
                          help="specify fits to include in table")
        parser.add_option("-s","--spectrum", action="store", default="active",
                          help="specify spectra")
        hdtv.cmdline.AddCommand(prog, self.WriteTex, nargs=1,parser=parser)
        
    def WriteTex(self, args, options):
        filename = args[0]
        
        # get list of fits
        fits = list()
        try:
            sids = hdtv.cmdhelper.ParseIds(options.spectrum, self.spectra)
        except ValueError:
            return "USAGE"
        if len(sids)==0:
            hdtv.ui.warn("No spectra chosen or active")
            return
        for sid in sids:
            spec = self.spectra.dict[sid]
            try:
                ids = hdtv.cmdhelper.ParseIds(options.fit, spec)
            except ValueError:
                return "USAGE"
            fits.extend([spec.dict[ID] for ID in ids])
        (peaklist, params) = self.f.ExtractFits(fits)
        
        # keys
        if options.columns is not None:
            keys = options.columns.split(",")
        else:
            keys = params
           
        # header 
        if options.header is not None:
            header= options.header.split(",")
        else:
            header = None
        
        # sort key
        if options.key_sort:
            sortBy = options.key_sort.lower()
        else:
            sortBy = keys[0]
        
        # alignment
        if options.alignment.lower() in ["c","l","r"]:
            ha = options.alignment.lower()
        else:
            msg="Invalid specifier for horizontal alignment. "
            msg+="Valid values are c,l,r. "
            hdtv.ui.warn(msg)
            ha = "c"
        
        # do the work
        table = TexTable(peaklist, keys, header, sortBy, options.reverse_sort, ha)
        out = file(filename,"w")
        out.write(str(table))
        
        
# plugin initialisation
import __main__
if not __main__.f:
    import FitInterface
    __main__.f = FitInterface(__main__.spectra)
__main__.f = fitTex(__main__.spectra, __main__.f)       

