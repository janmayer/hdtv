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

import copy
import os

import numpy as np
import ROOT
from scipy.interpolate import InterpolatedUnivariateSpline

import hdtv.cal
import hdtv.color
import hdtv.rootext.calibration
import hdtv.rootext.display
import hdtv.rootext.fit
import hdtv.rootext.mfile
from hdtv.drawable import Drawable
from hdtv.specreader import SpecReader, SpecReaderError
from hdtv.util import LockViewport

# Don't add created spectra to the ROOT directory
ROOT.TH1.AddDirectory(ROOT.kFALSE)


def HasPrimitiveBinning(hist):
    if hist.GetNbinsX() != (hist.GetXaxis().GetXmax() - hist.GetXaxis().GetXmin()):
        return False
    for bin in range(hist.GetNbinsX()):
        if hist.GetBinWidth(bin) != 1.0:
            return False
    return True


class Histogram(Drawable):
    """
    Histogram object

    This class is hdtvs wrapper around a ROOT histogram. It adds a calibration,
    plus some internal management for drawing the histogram to the hdtv spectrum
    viewer.
    """

    def __init__(self, hist, color=hdtv.color.default, cal=None):
        Drawable.__init__(self, color, cal)
        self._norm = 1.0
        self._ID = None
        self.effCal = None
        self.typeStr = "spectrum"
        self.cal = cal

        if cal is None:
            self.SetHistWithPrimitiveBinning(hist)
        else:
            self._hist = hist

    def __str__(self):
        return self.name

    def __copy__(self):
        # call C++ copy constructor
        hist = self._hist.__class__(self._hist)
        # create new spectrum object
        return Histogram(hist, color=self.color, cal=self.cal)

    # hist property
    def _set_hist(self, hist):
        self._hist = hist
        if self.displayObj:
            self.displayObj.SetHist(self._hist)

    def _get_hist(self):
        return self._hist

    hist = property(_get_hist, _set_hist)

    # name property
    def _get_name(self):
        if self._hist:
            return self._hist.GetName()

    def _set_name(self, name):
        self._hist.SetName(name)

    name = property(_get_name, _set_name)

    # norm property
    def _set_norm(self, norm):
        self._norm = norm
        if self.displayObj:
            self.displayObj.SetNorm(norm)

    def _get_norm(self):
        return self._norm

    norm = property(_get_norm, _set_norm)

    @property
    def info(self):
        """
        Return a string describing this spectrum
        """
        s = "Spectrum type: %s\n" % self.typeStr
        if not self._hist:
            return s
        s += "Name: %s\n" % str(self)
        s += "Nbins: %d\n" % self._hist.GetNbinsX()
        xmin = self._hist.GetXaxis().GetXmin()
        xmax = self._hist.GetXaxis().GetXmax()
        if self.cal and not self.cal.IsTrivial():
            s += f"Xmin: {self.cal.Ch2E(xmin):.2f} (cal)  {xmin:.2f} (uncal)\n"
            s += f"Xmax: {self.cal.Ch2E(xmax):.2f} (cal)  {xmax:.2f} (uncal)\n"
        else:
            s += "Xmin: %.2f\n" % xmin
            s += "Xmax: %.2f\n" % xmax

        if not self.cal or self.cal.IsTrivial():
            s += "Calibration: none\n"
        elif isinstance(self.cal, ROOT.HDTV.Calibration):
            s += "Calibration: Polynomial, degree %d\n" % self.cal.GetDegree()
            s += f"Calibration coefficients: {hdtv.cal.PrintCal(self.cal)}\n"
        else:
            s += "Calibration: unknown\n"
        return s

    # TODO: sumw2 function should be called at some point for correct error
    # handling
    def Plus(self, spec):
        """
        Add other spectrum to this one
        """
        # If the spectra have the same calibration (~= have the same binning),
        # and if they have the same number of bins
        # the root build-in add can be used
        if (
            self.cal == spec.cal or (self.cal.IsTrivial() and spec.cal.IsTrivial())
        ) and self._hist.GetNbinsX() == spec._hist.GetNbinsX():
            hdtv.ui.info("Adding binwise")
            self._hist.Add(spec._hist, 1.0)
        # If the binning is different, determine the amount to add to each bin
        # by integrating the other spectrum
        else:
            hdtv.ui.info("Adding calibrated")
            nbins = self._hist.GetNbinsX()
            for n in range(nbins):
                integral = ROOT.HDTV.TH1IntegrateWithPartialBins(
                    spec._hist,
                    spec.cal.E2Ch(self.cal.Ch2E(n - 0.5)),
                    spec.cal.E2Ch(self.cal.Ch2E(n + 0.5)),
                )
                # Note: Can't use Fill due to bin errors?
                self._hist.SetBinContent(
                    n + 1, self._hist.GetBinContent(n + 1) + integral
                )

        # update display
        if self.displayObj:
            self.displayObj.SetHist(self._hist)
        self.typeStr = "spectrum, modified (sum)"

    def Minus(self, spec):
        """
        Subtract other spectrum from this one
        """
        # If the spectra have the same calibration (~= have the same binning),
        # and if they have the same number of bins
        # the root build-in add can be used
        if (
            self.cal == spec.cal or (self.cal.IsTrivial() and spec.cal.IsTrivial())
        ) and self._hist.GetNbinsX() == spec._hist.GetNbinsX():
            hdtv.ui.info("Subtracting binwise")
            self._hist.Add(spec._hist, -1.0)
        # If the binning is different, determine the amount to add to each bin
        # by integrating the other spectrum
        else:
            hdtv.ui.info("Subtracting calibrated")
            nbins = self._hist.GetNbinsX()
            for n in range(nbins):
                integral = ROOT.HDTV.TH1IntegrateWithPartialBins(
                    spec._hist,
                    spec.cal.E2Ch(self.cal.Ch2E(n - 0.5)),
                    spec.cal.E2Ch(self.cal.Ch2E(n + 0.5)),
                )
                # Note: Can't use Fill due to bin errors?
                self._hist.SetBinContent(
                    n + 1, self._hist.GetBinContent(n + 1) - integral
                )

        # update display
        if self.displayObj:
            self.displayObj.SetHist(self._hist)
        self.typeStr = "spectrum, modified (difference)"

    def Multiply(self, factor):
        """
        Multiply spectrum with factor
        """
        self._hist.Scale(factor)
        # update display
        if self.displayObj:
            self.displayObj.SetHist(self._hist)
        self.typeStr = "spectrum, modified (multiplied)"

    def Rebin(self, ngroup, calibrate=True):
        """
        Rebin spectrum by adding ngroup bins into one
        """
        bins = self._hist.GetNbinsX()
        self._hist.RebinX(ngroup)
        self._hist.GetXaxis().SetLimits(0, bins / ngroup)
        # update display
        if self.displayObj:
            self.displayObj.SetHist(self._hist)
        # update calibration
        if calibrate:
            if self.cal:
                # Copy to not modify the cal in the position calibration cal dict
                self.cal = copy.copy(self.cal)
            else:
                self.cal = hdtv.cal.MakeCalibration((0, 1))
            self.cal.Rebin(ngroup)
            self.displayObj.SetCal(self.cal)
            hdtv.ui.info("Calibration updated for rebinned spectrum")
        self.typeStr = f"spectrum, modified (rebinned, ngroup={ngroup})"

    def Calbin(
        self, binsize: float = 1.0, spline_order: int = 3, use_tv_binning: bool = True
    ):
        """
        Rebin spectrum to match calibration unit

        Args:
            binsize: Size of calibrated bins
            spline_order: Order of the spline interpolation (default: 3)
            use_tv_binning: Center first bin on 0. (True) or
                lower edge of first bin on 0. (False).
        """

        nbins_old = self._hist.GetNbinsX()
        lower_old = self.cal.Ch2E(0)
        upper_old = self.cal.Ch2E(nbins_old - 1)

        nbins = int(np.ceil(upper_old / binsize)) + 1
        if use_tv_binning:
            lower = -0.5 * binsize
            # upper = 0.5 * binsize + (upper_old // nbins) * (nbins - 1)
        else:
            lower = 0.0
            # upper = binsize + (upper_old // nbins) * (nbins - 1)

        # Create new histogram with number of bins equal
        # to the calibrated range of the old histogram
        # Always subtract -0.5 from the integer bin centers to create standard tv-type histogram
        newhist = ROOT.TH1D(
            self._hist.GetName(), self._hist.GetTitle(), nbins, -0.5, nbins - 0.5
        )

        input_bins_center, input_hist = np.transpose(
            [
                [
                    self.cal.Ch2E(n - 1),
                    self._hist.GetBinContent(n)
                    / (self.cal.Ch2E(n) - self.cal.Ch2E(n - 1)),
                ]
                for n in range(1, self._hist.GetNbinsX() + 1)
            ]
        )

        output_bins_low = np.arange(nbins) * binsize + lower
        output_bins_high = output_bins_low + binsize

        inter = InterpolatedUnivariateSpline(
            input_bins_center, input_hist, k=spline_order
        )

        inter_integral_v = np.vectorize(inter.integral)
        output_hist = np.maximum(
            inter_integral_v(output_bins_low, output_bins_high), 0.0
        )

        # Suppress bins outside of original histogram range
        min_bin = int((lower_old - lower) / binsize)
        if min_bin >= 0:
            output_hist[:min_bin] = np.zeros(min_bin)
        else:
            # If 'lower_old' is already lower than 'lower', nothing needs to be done.
            # In both binning types, this would mean that 'lower_old' is outside of the
            # range of the new bins.
            hdtv.ui.warning(
                "Bins with negative energies in original spectrum were discarded."
            )

        for i in range(nbins):
            newhist.SetBinContent(i + 1, output_hist[i])

        self._hist = newhist
        if use_tv_binning:
            if binsize == 1.0:
                self.cal = None
            else:
                self.cal = hdtv.cal.MakeCalibration((0, binsize))
        else:
            self.cal = hdtv.cal.MakeCalibration((binsize / 2, binsize))
        # update display
        if self.displayObj:
            self.displayObj.SetHist(self._hist)
        # update calibration
        self.displayObj.SetCal(self.cal)
        hdtv.ui.info(f"Rebinned to calibration unit (binsize={binsize}).")

    def Poisson(self):
        """
        Randomize each bin content assuming a Poissonian distribution.
        """
        for i in range(self._hist.GetNbinsX() + 1):
            counts = self._hist.GetBinContent(i)
            # error = self._hist.GetBinError(i)
            varied = np.random.poisson(counts)
            self._hist.SetBinContent(i, varied)
        if self.displayObj:
            self.displayObj.SetHist(self._hist)

    def Draw(self, viewport):
        """
        Draw this spectrum to the viewport
        """

        if self.viewport is not None and not self.viewport == viewport:
            # Unlike the DisplaySpec object of the underlying implementation,
            # Spectrum() objects can only be drawn on a single viewport
            raise RuntimeError("Spectrum can only be drawn on a single viewport")
        self.viewport = viewport
        # Lock updates
        with LockViewport(self.viewport):
            # Show spectrum
            if self.displayObj is None and self._hist is not None:
                if self.active:
                    color = self._activeColor
                else:
                    color = self._passiveColor
                self.displayObj = ROOT.HDTV.Display.DisplaySpec(self._hist, color)
                self.displayObj.SetNorm(self.norm)
                self.displayObj.Draw(self.viewport)
                # add calibration
                if self.cal:
                    self.displayObj.SetCal(self.cal)
                # and ID
                if self.ID is not None:
                    ID = str(self.ID).strip(".")
                    self.displayObj.SetID(ID)

    def WriteSpectrum(self, fname, fmt):
        """
        Write the spectrum to file
        """
        fname = os.path.expanduser(fname)
        try:
            SpecReader.WriteSpectrum(self._hist, fname, fmt)
        except SpecReaderError as msg:
            hdtv.ui.error(f"Failed to write spectrum: {msg} (file: {fname})")
            return False
        return True

    def SetHistWithPrimitiveBinning(self, hist, caldegree=4, silent=False):
        log = hdtv.ui.debug if silent else hdtv.ui.info
        if HasPrimitiveBinning(hist):
            self._hist = hist
        else:
            log(
                hist.GetName()
                + " unconventional binning detected. Converting and trying to create calibration using a polynomial of order "
                + str(caldegree)
                + " ..."
            )
            self._hist = ROOT.TH1D(
                hist.GetName(), hist.GetTitle(), hist.GetNbinsX(), 0, hist.GetNbinsX()
            )
            if caldegree:
                cf = hdtv.cal.CalibrationFitter()
            # TODO: Slow
            for bin in range(hist.GetNbinsX()):
                if caldegree:
                    cf.AddPair(bin, hist.GetXaxis().GetBinUpEdge(bin))
                self._hist.SetBinContent(bin, hist.GetBinContent(bin))
                # Original comment by JM in commit #dd438b7c44265072bf8b0528170cecc95780e38c:
                # "TODO: Copy Errors?"
                #
                # Edit by UG: It makes sense to simply copy the uncertainties. There are two
                # possible cases:
                # 1. The ROOT histogram contains user-defined uncertainties per bin that can
                #    be retrieved by calling hist.GetBinError(). In this case, it can be
                #    assumed that the user knew what he was doing when the uncertainties
                #    were assigned.
                # 2. The ROOT histogram contains no user-defined uncertainties. In this case,
                #    a call of hist.GetBinError() will return the square root of the bin
                #    content, which is a sensible assumption.
                #
                # Since text spectra are loaded in a completely analogous way, implicitly
                # assuming that the uncertainties are Poissonian, there is no need to issue
                # an additional warning.
                self._hist.SetBinError(bin, hist.GetBinError(bin))
            if caldegree:
                cf.FitCal(caldegree)
                self.cal = cf.calib


class FileHistogram(Histogram):
    """
    File spectrum object

    A spectrum that comes from a file in any of the formats supported by hdtv.
    """

    def __init__(self, fname, fmt=None, color=hdtv.color.default, cal=None):
        """
        Read a spectrum from file
        """
        # check if file exists
        try:
            os.path.exists(fname)
        except OSError:
            hdtv.ui.error("File %s not found" % fname)
            raise
        # call to SpecReader to get the hist
        try:
            hist = SpecReader.GetSpectrum(fname, fmt)
        except SpecReaderError as msg:
            hdtv.ui.error(str(msg))
            raise
        self.fmt = fmt
        self.filename = fname
        Histogram.__init__(self, hist, color, cal)
        self.typeStr = "spectrum, read from file"

    @property
    def info(self):
        # get the info property of the baseclass
        s = super().info
        s += "Filename: %s\n" % self.filename
        if self.fmt:
            s += "File format: %s\n" % self.fmt
        else:
            s += "File format: autodetected\n"
        return s

    def Refresh(self):
        """
        Reload the spectrum from disk
        """
        try:
            os.path.exists(self.filename)
        except OSError:
            hdtv.ui.warning("File %s not found, keeping previous data" % self.filename)
            return
        # call to SpecReader to get the hist
        try:
            hist = SpecReader.GetSpectrum(self.filename, self.fmt)
        except SpecReaderError as msg:
            hdtv.ui.warning(
                f"Failed to load spectrum: {msg} (file: {self.filename}), keeping previous data"
            )
            return
        self.hist = hist


class CutHistogram(Histogram):
    def __init__(self, hist, axis, gates, color=hdtv.color.default, cal=None):
        Histogram.__init__(self, hist, color, cal)
        self.gates = gates
        self.axis = axis

    @property
    def info(self):
        s = super().info
        s += "cut "
        s += "on %s axis gate: " % self.axis
        for i in range(len(self.gates)):
            g = self.gates[i]
            s += "%d - %d " % (g.p1.pos_cal, g.p2.pos_cal)
            if i != len(self.gates):
                "and"
        return s


class THnSparseWrapper:
    """
    Wrapper around a 2d THnSparse object, providing ProjectionX and
    ProjectionY.
    """

    def __init__(self, hist):
        if not (isinstance(hist, ROOT.THnSparse) and hist.GetNdimensions() == 2):
            raise RuntimeError("Class needs a THnSparse histogram of dimension 2")
        self.__dict__["_hist"] = hist

    def __setattr__(self, name, value):
        self.__dict__["_hist"].__setattr__(name, value)

    def __getattr__(self, name):
        return getattr(self.__dict__["_hist"], name)

    def GetXaxis(self):
        return self._hist.GetAxis(0)

    def GetYaxis(self):
        return self._hist.GetAxis(1)

    def ProjectionX(self, name, b1, b2, opt):
        a = self._hist.GetAxis(1)
        if b1 > b2:
            a.SetRange(0, a.GetNbins())
        else:
            a.SetRange(b1, b2)

        proj = self._hist.Projection(0, opt)
        a.SetRange(0, a.GetNbins())

        proj.SetName(name)
        return proj

    def ProjectionY(self, name, b1, b2, opt):
        a = self._hist.GetAxis(0)
        if b1 > b2:
            a.SetRange(0, a.GetNbins())
        else:
            a.SetRange(b1, b2)

        proj = self._hist.Projection(1, opt)
        a.SetRange(0, a.GetNbins())

        proj.SetName(name)
        return proj


class Histo2D:
    def __init__(self):
        pass

    @property
    def name(self):
        return "generic 2D histogram"

    @property
    def xproj(self):
        return None

    @property
    def yproj(self):
        return None

    def ExecuteCut(self, regionMarkers, bgMarkers, axis):
        return None


class RHisto2D(Histo2D):
    """
    ROOT TH2-backed matrix for projection
    """

    def __init__(self, rhist):
        self.rhist = rhist

        # Lazy generation of projections
        self._prx = None
        self._pry = None

    @property
    def name(self):
        return self.rhist.GetName()

    @property
    def xproj(self):
        if self._prx is None:
            name = self.rhist.GetName() + "_prx"
            self._prx = self.rhist.ProjectionX(name, 0, -1, "e")
            # do not store the Histogram object here because of garbage
            # collection
            prx = Histogram(self._prx)
            prx.typeStr = "x projection"
        return prx

    @property
    def yproj(self):
        if self._pry is None:
            name = self.rhist.GetName() + "_pry"
            self._pry = self.rhist.ProjectionY(name, 0, -1, "e")
            # do not store the Histogram object here because of garbage
            # collection
            pry = Histogram(self._pry)
            pry.typeStr = "y projection"
        return pry

    def ExecuteCut(self, regionMarkers, bgMarkers, axis):
        # _axis_ is the axis the markers refer to, so we project on the *other*
        # axis. We call _axis_ the cut axis and the other axis the projection
        # axis. If the matrix is symmetric, this does not matter, so _axis_ is
        # "0" and the implementation can choose.

        if len(regionMarkers) < 1:
            raise RuntimeError("Need at least one gate for cut")

        if axis == "0":
            axis = "x"

        if axis not in ("x", "y"):
            raise ValueError("Bad value for axis parameter")

        if axis == "x":
            cutAxis = self.rhist.GetXaxis()
            projector = self.rhist.ProjectionY
        else:
            cutAxis = self.rhist.GetYaxis()
            projector = self.rhist.ProjectionX

        b1 = cutAxis.FindBin(regionMarkers[0].p1.pos_uncal)
        b2 = cutAxis.FindBin(regionMarkers[0].p2.pos_uncal)

        name = self.rhist.GetName() + "_cut"
        rhist = projector(name, min(b1, b2), max(b1, b2), "e")
        # Ensure proper garbage collection for ROOT histogram objects
        ROOT.SetOwnership(rhist, True)

        numFgBins = abs(b2 - b1) + 1
        for r in regionMarkers[1:]:
            b1 = cutAxis.FindBin(r.p1.pos_uncal)
            b2 = cutAxis.FindBin(r.p2.pos_uncal)
            numFgBins += abs(b2 - b1) + 1

            tmp = projector("proj_tmp", min(b1, b2), max(b1, b2), "e")
            ROOT.SetOwnership(tmp, True)
            rhist.Add(tmp, 1.0)

        bgBins = []
        numBgBins = 0
        for b in bgMarkers:
            b1 = cutAxis.FindBin(b.p1.pos_uncal)
            b2 = cutAxis.FindBin(b.p2.pos_uncal)
            numBgBins += abs(b2 - b1) + 1
            bgBins.append((min(b1, b2), max(b1, b2)))

        if numBgBins > 0:
            bgFactor = -float(numFgBins) / float(numBgBins)

            for b in bgBins:
                tmp = projector("proj_tmp", b[0], b[1], "e")
                ROOT.SetOwnership(tmp, True)
                rhist.Add(tmp, bgFactor)

        hist = CutHistogram(rhist, axis, regionMarkers)
        hist.typeStr = "cut"
        return hist


class MHisto2D(Histo2D):
    """
    MFile-backed matrix for projection
    """

    def __init__(self, fname, sym):
        # check if file exists
        try:
            os.stat(fname)
        except OSError as error:
            hdtv.ui.error(str(error))
            raise

        self.GenerateFiles(fname, sym)

        basename = self.GetBasename(fname)

        # call to SpecReader to get the hist
        try:
            self.vmatrix = SpecReader.GetVMatrix(fname)
        except SpecReaderError as msg:
            hdtv.ui.error(str(msg))
            raise

        self._xproj = FileHistogram(basename + ".prx")
        self._xproj.typeStr = "Projection"

        if sym:
            self._yproj = None
            self.tvmatrix = self.vmatrix  # Fixme
        else:
            self._yproj = FileHistogram(basename + ".pry")
            self._yproj.typeStr = "Projection"

            try:
                self.tvmatrix = SpecReader.GetVMatrix(basename + ".tmtx")
            except SpecReaderError as msg:
                hdtv.ui.error(str(msg))
                raise

        self.filename = fname

    @property
    def xproj(self):
        return self._xproj

    @property
    def yproj(self):
        return self._yproj

    def ExecuteCut(self, regionMarkers, bgMarkers, axis):
        # _axis_ is the axis the markers refer to, so we project on the *other*
        # axis. We call _axis_ the cut axis and the other axis the projection
        # axis. If the matrix is symmetric, this does not matter, so _axis_ is
        # "0" and the implementation can choose.

        if len(regionMarkers) < 1:
            raise RuntimeError("Need at least one gate for cut")

        if axis == "0":
            axis = "x"

        if axis not in ("x", "y"):
            raise ValueError("Bad value for axis parameter")

        if axis == "x":
            # FIXME: Calibrations for gated spectra asym/sym
            thiscal = self._xproj.cal
            if self._yproj:
                othercal = self._yproj.cal
            else:
                othercal = self._xproj.cal
            matrix = self.tvmatrix
        else:
            thiscal = self._yproj.cal
            othercal = self._xproj.cal
            matrix = self.vmatrix

        matrix.ResetRegions()

        for r in regionMarkers:
            # FIXME: The region markers are not used correctly in many parts
            # of the code. Workaround by explicitly using the cal here
            b1 = matrix.FindCutBin(thiscal.E2Ch(r.p1.pos_cal))
            b2 = matrix.FindCutBin(thiscal.E2Ch(r.p2.pos_cal))
            matrix.AddCutRegion(b1, b2)

        for b in bgMarkers:
            b1 = matrix.FindCutBin(thiscal.E2Ch(b.p1.pos_cal))
            b2 = matrix.FindCutBin(thiscal.E2Ch(b.p2.pos_cal))
            matrix.AddBgRegion(b1, b2)

        name = self.filename + "_cut"
        rhist = matrix.Cut(name, name)
        # Ensure proper garbage collection for ROOT histogram objects
        ROOT.SetOwnership(rhist, True)

        hist = CutHistogram(rhist, axis, regionMarkers)
        hist.typeStr = "cut"
        hist._cal = othercal
        return hist

    def GetBasename(self, fname):
        if fname.endswith(".mtx"):
            return fname[:-4]
        else:
            return fname

    def GenerateFiles(self, fname, sym):
        """
        Generate projection(s) and possibly transpose (for asymmetric matrices),
        if they do not exist yet.
        """
        basename = self.GetBasename(fname)

        # Generate projection(s)
        prx_fname = basename + ".prx"
        pry_fname = ""
        if os.path.exists(prx_fname):
            hdtv.ui.info("Using %s for x projection" % prx_fname)
            prx_fname = ""

        if not sym:
            pry_fname = basename + ".pry"
            if os.path.exists(pry_fname):
                hdtv.ui.info("Using %s for y projection" % pry_fname)
                pry_fname = ""

        if prx_fname or pry_fname:
            errno = ROOT.MatOp.Project(fname, prx_fname, pry_fname)
            if errno != ROOT.MatOp.ERR_SUCCESS:
                raise RuntimeError("Project: " + ROOT.MatOp.GetErrorString(errno))

            if prx_fname:
                hdtv.ui.info("Generated x projection: %s" % prx_fname)
            if pry_fname:
                hdtv.ui.info("Generated y projection: %s" % pry_fname)

        # Generate transpose
        if not sym:
            trans_fname = basename + ".tmtx"
            if os.path.exists(trans_fname):
                hdtv.ui.info("Using %s for transpose" % trans_fname)
            else:
                errno = ROOT.MatOp.Transpose(fname, trans_fname)
                if errno != ROOT.MatOp.ERR_SUCCESS:
                    raise RuntimeError("Transpose: " + ROOT.MatOp.GetErrorString(errno))
                hdtv.ui.info("Generated transpose: %s" % trans_fname)
