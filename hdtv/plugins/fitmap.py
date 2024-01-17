# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2010  The HDTV development team (see file AUTHORS)
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

import argparse

from uncertainties import ufloat_fromstr

import hdtv.cmdline
import hdtv.ui
import hdtv.util


class FitMap:
    def __init__(self, spectra, ecal):
        hdtv.ui.debug("Loaded plugin for setting nominal positions to peaks")

        self.spectra = spectra
        self.ecal = ecal

        prog = "fit position assign"
        description = "assign energy value as nominal position for peak"
        usage = "%(prog)s peakid energy [peakid energy ...] "
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description, usage=usage
        )
        parser.add_argument(
            "args",
            metavar="peakid energy",
            help="peak energy pairs",
            nargs=argparse.REMAINDER,
        )
        hdtv.cmdline.AddCommand(prog, self.FitPosAssign, parser=parser)

        prog = "fit position erase"
        description = "erase nominal position for peaks"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument("peakid", nargs="+", help="peak id")
        hdtv.cmdline.AddCommand(prog, self.FitPosErase, parser=parser)

        prog = "fit position map"
        description = "read nominal position from file"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument("filename")
        parser.add_argument(
            "-o",
            "--overwrite",
            action="store_true",
            default=False,
            help="Overwrite existing nominal peak positions",
        )
        parser.add_argument(
            "-t",
            "--tolerance",
            default=12,
            type=float,
            help="Tolerance for associating peaks to positions [default:%(default)s]",
        )
        hdtv.cmdline.AddCommand(prog, self.FitPosMap, fileargs=True, parser=parser)

        prog = "calibration position recalibrate"
        description = (
            "use stored nominal positions of peaks to (re)calibrate the spectrum"
        )
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default="active",
            help="spectrum ids to apply calibration to",
        )
        parser.add_argument(
            "-d",
            "--degree",
            action="store",
            default="1",
            help="degree of calibration polynomial fitted [default: %(default)s]",
        )
        parser.add_argument(
            "-f",
            "--show-fit",
            action="store_true",
            default=False,
            help="show fit used to obtain calibration",
        )
        parser.add_argument(
            "-r",
            "--show-residual",
            action="store_true",
            default=False,
            help="show residual of calibration fit",
        )
        parser.add_argument(
            "-t",
            "--show-table",
            action="store_true",
            default=False,
            help="print table of energies given and energies obtained from fit",
        )
        parser.add_argument(
            "-i",
            "--ignore-errors",
            action="store_true",
            default=False,
            help="set all weights to 1 in fit (ignore error bars even if given)",
        )
        parser.add_argument(
            "fitids",
            nargs="*",
            default=["all"],
            help="ids of the fits/peaks to use for the calibration (default=all)",
        )
        hdtv.cmdline.AddCommand(prog, self.CalPosRecalibrate, parser=parser)

    def FitPosAssign(self, args):
        """
        Assign a nominal value for the positon of peaks

        Peaks are specified by their id and the peak number within the fit.
        Syntax: id.number
        If no number is given, the first peak in the fit is used.
        """
        if self.spectra.activeID is None:
            hdtv.ui.warning("No active spectrum, no action taken.")
            return False
        spec = self.spectra.GetActiveObject()
        if len(args.args) % 2 != 0:
            raise hdtv.cmdline.HDTVCommandError("Number of arguments must be even")
        else:
            for i in range(0, len(args.args), 2):
                en = ufloat_fromstr(args.args[i + 1])
                try:
                    ids = hdtv.util.ID.ParseIds(args.args[i], spec, only_existent=False)
                    pid = ids[0].minor
                    if pid is None:
                        pid = 0
                    fid = ids[0]
                    fid.minor = None
                    spec.dict[fid].peaks[pid].extras["pos_lit"] = en
                except ValueError:
                    continue
                except (KeyError, IndexError):
                    hdtv.ui.warning("no peak with id %s" % args.args[i])

    def FitPosErase(self, args):
        """
        Erase nominal values for the position of peaks

        Peaks are specified by their id and the peak number within the fit.
        Syntax: id.number
        If no number is given, the all peaks in that fit are used.
        """
        if self.spectra.activeID is None:
            hdtv.ui.warning("No active spectrum, no action taken.")
            return False
        spec = self.spectra.GetActiveObject()
        # use set, to prevent duplicates
        pids = set()
        fids = hdtv.util.ID.ParseIds(args.peakid, spec, only_existent=False)
        for i in fids:
            if i.minor is not None:
                pids.add(i)
            else:
                try:
                    # collect all peaks in this fit
                    pids.update(set(hdtv.util.ID.ParseIds("all", spec.dict[i])))
                except KeyError:
                    hdtv.ui.warning("no peak with id %s" % i.major)
                    continue
        for i in pids:
            pid = i.minor
            i.minor = None
            try:
                peak = spec.dict[i].peaks[pid]
            except (KeyError, IndexError):
                # ignore invalid peaks, but give a warning
                hdtv.ui.warning(f"no peak with id {i.major}.{pid}")
                continue
            try:
                peak.extras.pop("pos_lit")
            except KeyError:
                # ignore peaks where "pos_lit" is unset
                continue

    def FitPosMap(self, args):
        """
        Read a list of energies from file and map to the fitted peaks.

        The spectrum must be roughly calibrated for this to work.
        """
        f = hdtv.util.TxtFile(args.filename)
        f.read()
        energies = []
        for line in f.lines:
            energies.append(ufloat_fromstr(line.split(",")[0]))
        if self.spectra.activeID is None:
            hdtv.ui.warning("No active spectrum, no action taken.")
            return False
        if len(energies) == 0:
            hdtv.ui.warning(f"No energies found in file {args.filename}.")
            return False
        spec = self.spectra.GetActiveObject()
        count = 0
        for fit in spec.dict.values():
            for peak in fit.peaks:
                if args.overwrite:
                    peak.extras.pop("pos_lit", None)
                # pick best match within a certain tolerance (if it exists)
                tol = args.tolerance
                enlit = [e for e in energies if abs(peak.pos_cal.std_score(e)) < tol]
                if len(enlit) > 0:
                    peak.extras["pos_lit"] = min(
                        enlit, key=lambda e: abs(peak.pos_cal.std_score(e))
                    )
                    count += 1
        # give a feetback to the user
        hdtv.ui.msg("Mapped %s energies to peaks" % count)

    def CalPosRecalibrate(self, args):
        if self.spectra.activeID is None:
            hdtv.ui.warning("No active spectrum, no action taken.")
            return False
        spec = self.spectra.GetActiveObject()
        # parsing of command line
        sids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        if len(sids) == 0:
            sids = [self.spectra.activeID]
        degree = int(args.degree)
        fitIDs = hdtv.util.ID.ParseIds(args.fitids, spec, only_existent=False)
        peakDict = {}
        for fitID in fitIDs:
            try:
                if fitID.minor is None:
                    for minor, peak in enumerate(spec.dict[fitID].peaks):
                        peakDict[hdtv.util.ID(fitID.major, minor)] = peak
                else:
                    peakDict[fitID] = spec.dict[hdtv.util.ID(fitID.major)].peaks[
                        fitID.minor
                    ]
            except (IndexError, KeyError):
                hdtv.ui.warning(f"Ignoring invalid fit/peak id {fitID}")
        pairs = hdtv.util.Pairs()
        for peakId, peak in peakDict.items():
            if "pos_lit" in peak.extras:
                enlit = peak.extras["pos_lit"]
                pairs.add(peak.pos, enlit)
            elif args.fitids != ["all"]:
                hdtv.ui.warning(
                    f"Ignoring fit/peak id {peakId} without assigned nominal position"
                )
        cal = self.ecal.CalFromPairs(
            pairs,
            degree,
            table=args.show_table,
            fit=args.show_fit,
            residual=args.show_residual,
            ignore_errors=args.ignore_errors,
        )
        self.spectra.ApplyCalibration(sids, cal)
        return True


# plugin initialisation
import __main__
from hdtv.plugins.calInterface import energy_cal_interface

hdtv.cmdline.RegisterInteractive(
    "fitmap", FitMap(__main__.spectra, energy_cal_interface)
)
