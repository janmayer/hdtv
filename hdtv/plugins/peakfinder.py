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

"""
Peak finding and fitting plugin for HDTV
"""

import copy

import ROOT

import hdtv.cmdline
import hdtv.options
import hdtv.plugins
import hdtv.ui


class PeakFinder:
    """
    Automatic peak finder - using ROOTS peak search function
    """

    def __init__(self, spectra):
        self.spectra = spectra
        hdtv.ui.debug("Loaded PeakFinder plugin")

    def __call__(
        self, sid, sigma, threshold, start=None, end=None, autofit=False, reject=False
    ):
        self.spec = self.spectra.dict[sid]
        self.sigma_E = sigma
        peaks = self.PeakSearch(sigma, threshold, start, end)
        num = self.StoreFits(peaks, autofit, reject)
        hdtv.ui.msg("Found " + str(num) + " peaks")
        # remove reference to spec otherwise we get trouble with garbage
        # collection
        self.spec = None

    def PeakSearch(self, sigma, threshold, start=None, end=None):
        """
        Search for peaks
        """
        sigma_E = sigma

        tSpec = ROOT.TSpectrum()

        # Copy underlying ROOT hist here so we can safely modify ranges, etc.
        # below
        hist = copy.copy(self.spec.hist).hist

        # Init start and end region
        if start is None:
            start_E = 0.0
        else:
            start_E = start
        start_Ch = self.spec.cal.E2Ch(start_E)
        if end is None:
            end_Ch = hist.GetNbinsX()
            end_E = self.spec.cal.Ch2E(end_Ch)
        else:
            end_E = end
            end_Ch = self.spec.cal.E2Ch(end_E)

        # good approximation of sigma_Ch
        sigma_Ch = self.spec.cal.E2Ch(sigma) - self.spec.cal.E2Ch(0.0)
        assert sigma_Ch > 0, "Sigma must be > 0"

        text = "Search Peaks in region "
        text += str(start_E) + "--" + str(end_E)
        text += " (sigma=" + str(sigma_E)
        text += " threshold=" + str(threshold * 100) + "%)"
        hdtv.ui.msg(text)

        # Invoke ROOT's peak finder
        hist.SetAxisRange(start_Ch, end_Ch)
        num_peaks = tSpec.Search(hist, sigma_Ch, "goff", threshold)
        foundpeaks = tSpec.GetPositionX()

        # Sort by position
        tmp = []
        for i in range(num_peaks):
            tmp.append(foundpeaks[i])  # convert from array to list
        tmp.sort()
        foundpeaks = tmp

        return foundpeaks

    def StoreFits(self, foundpeaks, autofit=False, reject=False):
        """
        Create fit objects from peak positions and add them to the fitlist
        If autofit is set to True fitting is done,
        if reject is set to True all badFits will be remove.
        """
        peak_count = 0
        while len(foundpeaks) > 0:
            p = foundpeaks.pop(0)
            fitter = copy.copy(self.spectra.workFit.fitter)
            fit = hdtv.fit.Fit(fitter, cal=self.spec.cal)
            pos_E = self.spec.cal.Ch2E(p)
            fit.ChangeMarker("peak", pos_E, action="set")
            if autofit:
                region_width = self.sigma_E * 5.0  # TODO: something sensible here
                # left region marker
                fit.ChangeMarker("region", pos_E - region_width / 2.0, action="set")
                limit = pos_E + region_width
                # collect multipletts
                while (
                    len(foundpeaks) > 0 and self.spec.cal.Ch2E(foundpeaks[0]) <= limit
                ):
                    next = foundpeaks.pop(0)
                    pos_E = self.spec.cal.Ch2E(next)
                    limit = pos_E + region_width
                    fit.ChangeMarker("peak", pos_E, "set")
                # right region marker
                fit.ChangeMarker("region", pos_E + region_width / 2.0, "set")
                fit.FitPeakFunc(self.spec)  # , silent = True
                # check fits
                result = self.BadFit(fit)
                if reject:
                    if result:
                        text = "Rejecting invalid fit:" + result
                        hdtv.ui.msg(text)
                        continue
                else:
                    if result:
                        text = "Adding invalid fit:" + result
                        hdtv.ui.warning(text)
            # Integrate. TODO: Might use this for additional checks
            if fit.regionMarkers.IsFull():
                region = [
                    fit.regionMarkers[0].p1.pos_uncal,
                    fit.regionMarkers[0].p2.pos_uncal,
                ]
                fit.integral = hdtv.integral.Integrate(
                    self.spec, fit.fitter.bgFitter, region
                )
            # add fits to spectrum
            self.spec.Insert(fit)
            # FIXME: no fit title
            # fit.title = fit.title + "(*)"
            # bookkeeping
            if len(fit.peaks) > 0:
                peak_count = peak_count + len(fit.peaks)
            else:
                peak_count = peak_count + 1

        return peak_count

    def BadFit(self, fit):
        """
        Check if the fit is sensible
        """
        bad = False
        text = ""
        for peak in fit.peaks:
            reason = None
            if peak.vol.nominal_value <= 0.0:
                bad = True
                reason = "vol = %s" % peak.vol
            elif (
                not fit.regionMarkers[0].p1.pos_cal
                < peak.pos_cal.nominal_value
                < fit.regionMarkers[0].p2.pos_cal
            ):
                bad = True
                reason = "peak position outside of region"
            # TODO: check for NaNs in errors
            elif fit.fitter.peakModel.name == "theuerkauf":
                if (
                    peak.width.nominal_value <= 0.0
                    or peak.width.nominal_value > 5 * self.sigma_E
                ):
                    bad = True
                    reason = "width = %s" % peak.width
            elif fit.fitter.peakModel.name == "ee":
                # FIXME: what are frequent bad things that can happen here???
                pass
            if reason:
                text += "\n" + str(peak).strip("\n") + " (reason: " + reason + ")"
            else:
                text += "\n" + str(peak).strip("\n")
        if bad:
            return text


# FIXME or remove
#    def BGFit(self):
#        """
#        Do a background fit
#        """
#        # Background fit
#        sid = self.spectra.activeID
#        tSpec = ROOT.TSpectrum()
#
#        spec = self.spectra[self.spectra.activeID]

#        hist = spec.fHist.__class__(spec.fHist) # Copy hist here
#        # TODO: draw background
#        hbg = hist.ShowBackground(20, "goff")
#        print "hbg", hbg
#        bgspec = hdtv.spectrum.Spectrum(hbg, cal=spec.cal)
#
#        bspec = hdtv.spectrum.SpectrumCompound(spec.viewport, bgspec)
#        sid = self.spectra.Add(bgspec)
#        bgspec.SetColor(hdtv.color.ColorForID(sid))
#        print "BGSPec", sid


# plugin initialisation
import __main__

peakfinder = PeakFinder(__main__.spectra)
hdtv.cmdline.RegisterInteractive("peakfinder", peakfinder)


# wrapper function


def PeakSearch(args):
    try:
        if __main__.spectra.activeID not in __main__.spectra.visible:
            hdtv.ui.warning("Active spectrum is not visible, no action taken")
            return True
    except KeyError:
        raise hdtv.cmdline.HDTVCommandAbort("No active spectrum")
        return False

    sid = __main__.spectra.activeID

    if args.sigma is None:
        args.sigma = hdtv.options.Get("fit.peakfind.sigma")
    if args.threshold is None:
        args.threshold = hdtv.options.Get("fit.peakfind.threshold")
    if args.autofit is None:
        args.autofit = hdtv.options.Get("fit.peakfind.auto_fit")

    # TODO: Access session peakfinder
    peakfinder(
        sid, args.sigma, args.threshold, args.start, args.end, args.autofit, args.reject
    )


# Register configuration variables for "fit peakfind"
opt = hdtv.options.Option(default=2.5, parse=lambda x: float(x))
hdtv.options.RegisterOption("fit.peakfind.sigma", opt)
opt = hdtv.options.Option(default=0.05, parse=lambda x: float(x))
hdtv.options.RegisterOption("fit.peakfind.threshold", opt)
opt = hdtv.options.Option(default=False, parse=hdtv.options.parse_bool)
hdtv.options.RegisterOption("fit.peakfind.auto_fit", opt)

# Register command "fit peakfind"
prog = "fit peakfind"
description = "Search for peaks in active spectrum in given range"
parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
parser.add_argument(
    "-s", "--sigma", type=float, action="store", default=None, help="FWHM of peaks"
)
parser.add_argument(
    "-t",
    "--threshold",
    type=float,
    action="store",
    default=None,
    help="Threshold of peaks to accept in fraction of the amplitude of highest peak (0. < threshold < 1.)",
)
parser.add_argument(
    "-a",
    "--autofit",
    action="store_true",
    default=None,
    help="automatically fit found peaks",
)
parser.add_argument(
    "-r",
    "--reject",
    action="store_true",
    default=False,
    help="reject fits with unreasonable values",
)
parser.add_argument("start", nargs="?", type=float, default=None, help="start of range")
parser.add_argument("end", nargs="?", type=float, default=None, help="end of range")
hdtv.cmdline.AddCommand(prog, PeakSearch, level=4, parser=parser, fileargs=False)
