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

import hdtv.cmdline
import hdtv.ui
import hdtv.util

preamble = r"""\makeatletter
\@ifundefined{standalonetrue}{\newif\ifstandalone}{\let\ifbackup=\ifstandalone}
\@ifundefined{section}{\standalonetrue}{\standalonefalse}
\makeatother
\ifstandalone

\documentclass[12pt,oneside,a4paper]{report}
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


\begin{document}
\fi
\begin{center}
\begin{longtable}"""

enddok = r"""\end{longtable}
\end{center}

\ifstandalone
\end{document}
\else
\let\ifstandalone=\ifbackup
\expandafter\endinput
\fi
"""


class TexTable(hdtv.util.Table):
    def __init__(self, data, keys, header=None, sortBy=None, reverseSort=False, ha="c"):
        hdtv.util.Table.__init__(
            self,
            data,
            keys,
            header,
            ignoreEmptyCols=False,
            sortBy=sortBy,
            reverseSort=reverseSort,
            extra_header=preamble,
            extra_footer=enddok,
        )
        self.col_sep_char = "&"
        self.empty_field = " "
        self.ha = ha

    def build_header(self):
        header = r"\hline" + os.linesep
        for i in range(2):
            for string in self.header:
                string = string.replace("_", "-")
                header += rf"\multicolumn{{1}}{{{self.ha}}}{{\textbf{{{string}}}}} &"
            header = header.rstrip("&")
            header += r"\\ \hline" + os.linesep
            if i == 0:
                header += r"\endfirsthead" + os.linesep + os.linesep
                header += r"\hline" + os.linesep
            else:
                header += r"\endhead" + os.linesep + os.linesep

        header += r"\hline" + os.linesep
        header += (
            r"\multicolumn{%d}{r}{{wird fortgesetzt...}} \\\ " % len(self.header)
            + os.linesep
        )
        header += r"\endfoot" + os.linesep + os.linesep

        header += r"\hline " + os.linesep
        header += r"\endlastfoot" + os.linesep + os.linesep

        return header

    def __str__(self):
        text = ""
        if self.extra_header is not None:
            text += (
                str(self.extra_header)
                + "{"
                + len(self.keys) * self.ha
                + "}"
                + os.linesep
            )

        lines = self.build_lines()

        header_line = self.build_header()
        text += header_line + os.linesep

        # Build lines
        for line in lines:
            line_str = ""
            for col in range(len(line)):
                if not self._ignore_col[col]:
                    line_str += str(" " + line[col] + " ").rjust(self._col_width[col])
                if col != len(line) - 1:
                    line_str += self.col_sep_char

            text += line_str + r"\\ " + os.linesep

        if self.extra_footer is not None:
            text += str(self.extra_footer)

        return text


class fitTex:
    """
    Create a table for use with latex.

    The resulting file can be compiled standalone or included in another latex
    document. It uses the longtable package.
    """

    def __init__(self, spectra, fitInterface):
        hdtv.ui.debug("Loaded plugin for exporting fitlist to tex")

        self.spectra = spectra
        self.f = fitInterface

        prog = "fit tex"
        description = "create a table in latex format"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-c",
            "--columns",
            action="store",
            default=None,
            help="values to include as columns of the table",
        )
        parser.add_argument(
            "-H", "--header", action="store", default=None, help="header of columns"
        )
        parser.add_argument(
            "-k", "--key-sort", action="store", default=None, help="sort by key"
        )
        parser.add_argument(
            "-r",
            "--reverse-sort",
            action="store_true",
            default=False,
            help="reverse the sort",
        )
        parser.add_argument(
            "-a",
            "--alignment",
            action="store",
            default="c",
            help="horizontal alignment (c=center, l=left or r=right)",
        )
        parser.add_argument(
            "-f",
            "--fit",
            action="store",
            default="all",
            help="specify fits to include in table",
        )
        parser.add_argument(
            "-s", "--spectrum", action="store", default="active", help="specify spectra"
        )
        parser.add_argument("filename", metavar="output-file", help="file to write to")
        hdtv.cmdline.AddCommand(prog, self.WriteTex, parser=parser)

    def WriteTex(self, args):
        filename = os.path.expanduser(args.filename)

        # get list of fits
        fits = []
        sids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        if len(sids) == 0:
            hdtv.ui.warning("No spectra chosen or active")
            return
        for sid in sids:
            spec = self.spectra.dict[sid]
            ids = hdtv.util.ID.ParseIds(args.fit, spec)
            fits.extend([spec.dict[ID] for ID in ids])
        (peaklist, params) = self.f.ExtractFits(fits)

        # keys
        if args.columns is not None:
            keys = args.columns.split(",")
        else:
            keys = params

        # header
        if args.header is not None:
            header = args.header.split(",")
        else:
            header = None

        # sort key
        if args.key_sort:
            sortBy = args.key_sort.lower()
        else:
            sortBy = keys[0]

        # alignment
        if args.alignment.lower() in ["c", "l", "r"]:
            ha = args.alignment.lower()
        else:
            msg = "Invalid specifier for horizontal alignment. "
            msg += "Valid values are c,l,r. "
            hdtv.ui.warning(msg)
            ha = "c"

        # do the work
        table = TexTable(peaklist, keys, header, sortBy, args.reverse_sort, ha)
        with open(filename, "w") as out:
            out.write(str(table))


# plugin initialisation
import __main__
from hdtv.plugins.fitInterface import fit_interface

hdtv.cmdline.RegisterInteractive("fittex", fitTex(__main__.spectra, fit_interface))
