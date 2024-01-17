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

import array
import os

import ROOT

import hdtv.rootext.mfile
import hdtv.ui


class SpecReaderError(Exception):
    pass


class TextSpecReader:
    """
    Configurable formatted text file import
    The format string specifies the meaning of the columns in the file.
     x: x  (position)
     y: y  (counts)
     e: dy (error of counts)
     i: ignore this column

    If no column for x is specified, the bin number (beginning at zero) is
    taken for the bin center (just as the old tv program does it). If no
    column for e is specified, square root errors are assumed. It is an error
    if no column for y is specified.

    If no format string is given, the format is inferred from the number of
    columns in the file:
     1: y
     2: xy
     3: xye

    The cmts parameter is a tuple of possible strings that start a comment.
    cmts=None switches comment processing off. Comments extend to the end of the
    line. If unspecified, cmt defaults to ("#", "!", "//").
    """

    def __init__(self, fmt=None, cmts=("#", "!", "//")):
        self.xcol = self.ycol = self.ecol = None
        self.ncols = None
        self.cmts = cmts

        # Parse the format specifier string, if one has been specified
        if fmt:
            self.ncols = len(fmt)

            for col in range(len(fmt)):
                c = fmt[col]

                if c in ("x", "y", "e"):
                    if self.__dict__[c + "col"] is None:
                        self.__dict__[c + "col"] = col
                    else:
                        raise SpecReaderError(
                            "Invalid format string: %s appears more than once" % c
                        )
                elif c == "i":
                    pass
                else:
                    raise SpecReaderError("Invalid character %s in format string" % c)

            if self.ycol is None:
                raise SpecReaderError("You must specify a column for y")

    def GetBinLowEdges(self, centers):
        """
        Generate an array of (n+1) bin lower edges from an array of n bin
        centers. The result is returned as an array object so that is can be
        passed directly to the ROOT.TH1 constructor.
        """
        # This function generates n+1 lower bin edges l_0,...,l_n from n bin
        # centers c_0,...,c_{n-1}, such that the n equations
        #  c_i = (l_i + l_{i+1})/2 , i = 0,...,n-1
        # are fulfilled. Note that the problem is underdefined (n equations for
        # n+1 unknowns), so that there is a somewhat arbitrary choice being
        # made.
        xbins = array.array("d")
        w = (centers[1] - centers[0]) / 2.0
        xbins.append(centers[0] - w)
        for i in range(1, len(centers)):
            w = centers[i] - centers[i - 1] - w
            xbins.append(centers[i] - w)
        xbins.append(centers[-1] + w)

        return xbins

    def StripComments(self, line):
        end = len(line)

        if self.cmts:
            for cmt in self.cmts:
                pos = line.find(cmt)
                if pos >= 0:
                    end = min(end, pos)

        return line[:end]

    def GetSpectrum(self, fname, histname, histtitle):
        """
        Process a text file into a ROOT histogram object, using the format
        specified in the constructor.
        """
        data = []
        f = open(fname)
        linenum = 1

        try:
            for line in f:
                # Strip comments
                line = self.StripComments(line)

                # Split line into columns
                cols = line.split()

                # Ignore empty lines
                if len(cols) == 0:
                    linenum += 1
                    continue

                # If the format string was set to autodetect, we use the number
                # of columns in the first non-empty line to determine the
                # format.
                if self.ncols is None:
                    self.ncols = len(cols)
                    if self.ncols == 1:
                        self.xcol = None
                        self.ycol = 0
                        self.ecol = None
                    elif self.ncols == 2:
                        self.xcol = 0
                        self.ycol = 1
                        self.ecol = None
                    elif self.ncols == 3:
                        self.xcol = 0
                        self.ycol = 1
                        self.ecol = 2
                    else:
                        raise SpecReaderError(
                            "%s: %d: Failed to autodetect file format: found %d columns"
                            % (fname, linenum, self.ncols)
                        )

                # Check if number of columns is consistent
                elif len(cols) != self.ncols:
                    raise SpecReaderError(
                        "%s: %d: Invalid number of columns (found=%d, expected=%d)"
                        % (fname, linenum, len(cols), self.ncols)
                    )

                # Parse specified columns into float values
                linedata = []
                for col in (self.xcol, self.ycol, self.ecol):
                    if col is not None:
                        try:
                            linedata.append(float(cols[col]))
                        except ValueError:
                            raise SpecReaderError(
                                '%s: %d: Failed to parse value "%s" into float'
                                % (fname, linenum, cols[col])
                            )
                    else:
                        linedata.append(None)

                data.append(linedata)

                linenum += 1

        finally:
            f.close()

        nbins = len(data)

        if self.xcol is not None:
            # Sort by increasing x value
            data.sort(key=lambda a: a[0])

            xbins = self.GetBinLowEdges([d[0] for d in data])
            hist = ROOT.TH1D(histname, histtitle, nbins, xbins)
        else:
            hist = ROOT.TH1D(histname, histtitle, nbins, -0.5, nbins - 0.5)

        # Fill ROOT histogram object
        for b in range(nbins):
            hist.SetBinContent(b + 1, data[b][1])
            if self.ecol is not None:
                hist.SetBinError(b + 1, data[b][2])

        return hist


class SpecReader:
    @staticmethod
    def GetSpectrum(fname, fmt=None, histname=None, histtitle=None):
        """
        Reads a histogram from a non-ROOT file. fmt specifies the format.
        The following formats are recognized:
          * cracow  (Cracow from GSI)
          * mfile   (use libmfile and attempt autodetection)
          * any format specifier understood by libmfile
        """
        default_format = "mfile"

        if not fmt:
            fmt = default_format
        if histname is None:
            histname = os.path.basename(fname)
        if histtitle is None:
            histtitle = os.path.basename(fname)

        if fmt.lower() == "cracow":
            # hdtv.dlmgr.LoadLibrary("cracowio")
            # cio = ROOT.CracowIO()
            # hist = cio.GetCracowSpectrum(fname, histname, histtitle)
            # if not hist:
            #     raise SpecReaderError(cio.GetErrorMsg())
            # return hist
            raise SpecReaderError("Format not longer supported")
        elif fmt.split(":")[0].lower() == "col":
            # Extract subformat specifier to pass on to TextSpecReader
            pos = fmt.find(":")
            if pos > 0:
                subfmt = fmt[pos + 1 :]
            else:
                subfmt = None

            # The following lines may raise a SpecReaderError exception
            txtio = TextSpecReader(subfmt)
            return txtio.GetSpectrum(fname, histname, histtitle)
        else:
            mhist = ROOT.MFileHist()

            if not fmt or fmt.lower() == "mfile":
                result = mhist.Open(fname)
            else:
                result = mhist.Open(fname, fmt)

            if result != ROOT.MFileHist.ERR_SUCCESS:
                raise SpecReaderError(mhist.GetErrorMsg())

            # Get spectra out of Mfile Mat structure
            # Use the spectra given by line
            level = 0
            line = 0
            if len(fmt.split(".")) == 3:
                line = int(fmt.split(".")[0]) - 1
                level = 0
                hdtv.ui.msg("Using spectra in line " + str(line))

            hist = mhist.ToTH1D(histname, histtitle, level, line)
            if not hist:
                raise SpecReaderError(mhist.GetErrorMsg())
            return hist

    @staticmethod
    def GetMatrix(fname, fmt=None, histname=None, histtitle=None):
        if histname is None:
            histname = os.path.basename(fname)
        if histtitle is None:
            histtitle = os.path.basename(fname)

        mhist = ROOT.MFileHist()

        # FIXME: error handling
        if not fmt or fmt.lower() == "mfile":
            mhist.Open(fname)
        else:
            mhist.Open(fname, fmt)

        # FIXME: this ignores possibly specified bin errors
        hist = mhist.ToTH2D(histname, histtitle, 0)
        if not hist:
            raise SpecReaderError(mhist.GetErrorMsg())
        return hist

    @staticmethod
    def GetVMatrix(fname, fmt=None, histname=None, histtitle=None):
        """
        Load a ``virtual'' matrix, i.e. a matrix that is not completely loaded
        into memory.
        """
        if histname is None:
            histname = os.path.basename(fname)
        if histtitle is None:
            histtitle = os.path.basename(fname)

        mhist = ROOT.MFileHist()

        # FIXME: error handling
        if not fmt or fmt.lower() == "mfile":
            mhist.Open(fname)
        else:
            mhist.Open(fname, fmt)

        # FIXME: this ignores possibly specified bin errors
        return ROOT.MFMatrix(mhist, 0)

    @staticmethod
    def WriteSpectrum(hist, fname, fmt):
        result = ROOT.MFileHist.WriteTH1(hist, fname, fmt)
        if result != ROOT.MFileHist.ERR_SUCCESS:
            raise SpecReaderError(ROOT.MFileHist.GetErrorMsg(result))
