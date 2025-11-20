# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2011-2013  The HDTV development team (see file AUTHORS)
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

import matplotlib
import numpy
import scipy

matplotlib.use("agg")  # Must be before import pylab!
import pylab
from matplotlib import transforms

import hdtv.cal
import hdtv.cmdline
import hdtv.color
import hdtv.ui

# TODO: add cut marker


class PrintOut:
    def __init__(self, spectra, energies=False):
        self.spectra = spectra
        self.labels = energies

    def Execute(self):
        """
        creates a plot with all currently visible objects
        """
        # extract visible spectrum objects
        ids = list(self.spectra.visible)
        specs = [self.spectra.dict[i] for i in ids]

        # create matplotlib plot
        pylab.rc("font", size=16)
        pylab.rc("lines", linewidth=1)
        pylab.rc("svg", fonttype="path")

        pylab.figure(figsize=(8.5, 4.2))

        # add spectra, fits, marker etc.
        for spec in specs:
            self.PrintHistogram(spec)
            # extract visible fits for this spectrum
            fids = list(spec.visible)
            fits = [spec.dict[i] for i in fids]
            # add workFit
            fits.append(self.spectra.workFit)
            for fit in fits:
                if self.spectra.window.IsInVisibleRegion(fit, part=True):
                    self.PrintFit(fit)

        # viewport limits
        x1 = self.spectra.viewport.GetXOffset()
        x2 = x1 + self.spectra.viewport.GetXVisibleRegion()
        y1 = self.spectra.viewport.GetYOffset()
        y2 = y1 + self.spectra.viewport.GetYVisibleRegion()

        # apply limits to plot
        pylab.xlim(x1, x2)
        pylab.ylim(y1, y2)

    def PrintHistogram(self, spec):
        """
        print histogramm
        """
        nbins = spec.hist.hist.GetNbinsX()
        # create values for x axis
        en = numpy.arange(nbins)
        # shift in order to get values at bin center
        en = en - 0.5
        # calibrate
        en = self.ApplyCalibration(en, spec.cal)
        # extract bin contents to numpy array
        data = numpy.zeros(nbins)
        for i in range(nbins):
            data[i] = spec.hist.hist.GetBinContent(i)
        # create spectrum plot
        (r, g, b) = hdtv.color.GetRGB(spec.color)
        pylab.step(en, data, color=(r, g, b), label=spec.name)

    def PrintFit(self, fit):
        """
        print fit including peak marker and functions
        """
        # peak marker
        for p in fit.peakMarkers:
            self.PrintMarker(p)
        # print all marker for a workFit
        if fit.active:
            for m in fit.bgMarkers:
                self.PrintMarker(m)
            for m in fit.regionMarkers:
                self.PrintMarker(m)
        # peak function
        func = fit.dispPeakFunc
        if fit.active:
            color = hdtv.color.region
        else:
            color = fit.color
        if func:
            self.PrintFunc(func, fit.cal, color)
        # background function
        bgfunc = fit.dispBgFunc
        if fit.active:
            color = hdtv.color.bg
        else:
            color = fit.color
        if bgfunc:
            self.PrintFunc(bgfunc, fit.cal, fit.color)
        i = 0
        for p in fit.peaks:
            # maybe energy labels for each peak
            if self.labels:
                self.PrintLabel(p, i)
                i = i + 1
            # maybe functions for each peak
            if fit._showDecomp:
                peakfunc = p.displayObj
                self.PrintFunc(peakfunc, p.cal, p.color)

    def PrintMarker(self, marker):
        """
        print marker
        """
        if marker.active:
            color = marker._activeColor
        else:
            color = marker.color
        (r, g, b) = hdtv.color.GetRGB(color)
        pos = marker.p1.pos_cal
        pylab.axvline(pos, color=(r, g, b))
        if marker.p2 is not None:
            pos = marker.p2.pos_cal
            pylab.axvline(pos, color=(r, g, b))

    def PrintLabel(self, peak, i):
        """
        print energy labels for peaks
        """
        x = peak.pos_cal.value
        ax = pylab.gca()
        trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)
        pylab.text(
            x,
            0.94 - 0.06 * i,
            f"{peak.pos_cal:S}",
            transform=trans,
            size="small",
        )

    def PrintFunc(self, func, cal, color):
        """
        print function by evaluation it at several points
        """
        x1 = func.GetMinCh()
        x2 = func.GetMaxCh()
        nbins = int(x2 - x1) * 20
        en = numpy.linspace(x1, x2, nbins)
        data = numpy.zeros(nbins)
        for i in range(nbins):
            data[i] = func.Eval(en[i])
        en = self.ApplyCalibration(en, cal)
        # create function plot
        (r, g, b) = hdtv.color.GetRGB(color)
        pylab.plot(en, data, color=(r, g, b))

    def ApplyCalibration(self, en, cal):
        """
        return calibrated values
        """
        if cal and not cal.IsTrivial():
            calpolynom = hdtv.cal.GetCoeffs(cal)
            # scipy needs highes order first
            calpolynom.reverse()
            en = scipy.polyval(calpolynom, en)
        return en


class PrintInterface:
    def __init__(self, spectra):
        self.spectra = spectra

        # command line interface
        prog = "print"
        description = "Prints all visible items to file. The file format is specified by the filename extension."
        description += (
            "Supported formats are: emf, eps, pdf, png, ps, raw, rgba, svg, svgz. "
        )
        description += "If no filename is given, an interactive mode is entered and the plot can be manipulated using pylab."
        description += (
            "Change to the python prompt and import the pylab module for that to work."
        )
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-F",
            "--force",
            action="store_true",
            default=False,
            help="overwrite existing files without asking",
        )
        parser.add_argument(
            "-y", "--ylabel", action="store", default=None, help="add label for y-axis"
        )
        parser.add_argument(
            "-x", "--xlabel", action="store", default=None, help="add label for x-axis"
        )
        parser.add_argument(
            "-t", "--title", action="store", default=None, help="add title for plot"
        )
        parser.add_argument(
            "-l", "--legend", action="store_true", default=False, help="add legend"
        )
        parser.add_argument(
            "-e",
            "--energies",
            action="store_true",
            default=False,
            help="add energy labels to each fitted peak",
        )
        parser.add_argument(
            "filename",
            metavar="output-file",
            nargs="?",
            default=None,
            help="file to print to",
        )
        hdtv.cmdline.AddCommand(prog, self.Print, fileargs=True, parser=parser)

    def Print(self, args):
        pylab.ioff()

        p = PrintOut(self.spectra, args.energies)
        p.Execute()

        # add some decorations
        if args.title:
            pylab.title(args.title)
        if args.ylabel:
            pylab.ylabel(args.ylabel)
        if args.xlabel:
            pylab.xlabel(args.xlabel)
        if args.legend and len(self.spectra) > 0:
            legend = pylab.legend(prop={"size": "x-small"})
            legend.draw_frame(False)

        # save finished plot to file
        if args.filename:
            fname = hdtv.util.user_save_file(args.filename, args.force)
            if not fname:
                return
            pylab.ioff()
            pylab.savefig(fname, bbox_inches="tight")
        else:
            # else go to interactive mode
            pylab.ion()
            # hack to open the plot window
            pylab.text(0, 0, "")


# plugin initialisation
import __main__

print_interface = PrintInterface(__main__.spectra)
hdtv.cmdline.RegisterInteractive("p", print_interface)
hdtv.ui.debug("Loaded user interface for printing")
