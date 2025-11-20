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
import glob
import os

import ROOT

import hdtv.cal
import hdtv.cmdline
import hdtv.color
import hdtv.options
import hdtv.ui
import hdtv.util
from hdtv.histogram import FileHistogram
from hdtv.specreader import SpecReaderError
from hdtv.spectrum import Spectrum
from hdtv.util import LockViewport


class SpecInterface:
    """
    User interface to work with 1-d spectra
    """

    def __init__(self, spectra):
        hdtv.ui.debug("Loaded user interface for working with 1-d spectra")

        self.spectra = spectra
        self.window = spectra.window
        self.caldict = spectra.caldict

        # tv commands
        self.tv = TvSpecInterface(self)

        # good to have as well...
        if self.window:
            self.window.AddHotkey(ROOT.kKey_PageUp, self.spectra.ShowPrev)
            self.window.AddHotkey(ROOT.kKey_PageDown, self.spectra.ShowNext)

            # register common tv hotkeys
            self.window.AddHotkey([ROOT.kKey_N, ROOT.kKey_p], self.spectra.ShowPrev)
            self.window.AddHotkey([ROOT.kKey_N, ROOT.kKey_n], self.spectra.ShowNext)
            self.window.AddHotkey(ROOT.kKey_Equal, self.spectra.RefreshAll)
            self.window.AddHotkey(ROOT.kKey_t, self.spectra.RefreshVisible)
            self.window.AddHotkey(
                ROOT.kKey_n,
                lambda: self.window.EnterEditMode(
                    prompt="Show spectrum: ", handler=self._HotkeyShow
                ),
            )
            self.window.AddHotkey(
                ROOT.kKey_a,
                lambda: self.window.EnterEditMode(
                    prompt="Activate spectrum: ", handler=self._HotkeyActivate
                ),
            )

        # Register configuration variables
        self.LoadSpectraNaturalSort = hdtv.options.Option(
            default=True,
            parse=hdtv.options.parse_bool,
        )
        hdtv.options.RegisterOption(
            "spec.get.sort_natural", self.LoadSpectraNaturalSort
        )

    def _HotkeyShow(self, arg):
        """
        ShowObjects wrapper for use with Hotkey
        """
        try:
            ids = hdtv.util.ID.ParseIds(arg, self.spectra)
            if len(ids) == 0:
                self.spectra.HideAll()
            else:
                self.spectra.ShowObjects(ids)
        except ValueError:
            if self.window:
                self.window.viewport.SetStatusText(
                    "Invalid spectrum identifier: %s" % arg
                )

    def _HotkeyActivate(self, arg):
        """
        ActivateObject wrapper for use with Hotkey
        """
        try:
            ids = hdtv.util.ID.ParseIds(arg, self.spectra)
            if len(ids) > 1:
                if self.window:
                    self.window.viewport.SetStatusText(
                        "Cannot activate more than one spectrum"
                    )
            elif len(ids) == 0:  # Deactivate
                oldactive = self.spectra.activeID
                self.spectra.ActivateObject(None)
                if self.window:
                    self.window.viewport.SetStatusText(
                        "Deactivated spectrum %s" % oldactive
                    )
            else:
                ID = ids[0]
                self.spectra.ActivateObject(ID)
                if self.window:
                    self.window.viewport.SetStatusText(
                        "Activated spectrum %s" % self.spectra.activeID
                    )
        except ValueError:
            if self.window:
                self.window.viewport.SetStatusText("Invalid id: %s" % arg)

    def LoadSpectra(self, patterns, ID=None):
        """
        Load spectra from files matching patterns.

        If ID is specified, the spectrum is stored with id ID, possibly
        replacing a spectrum that was there before.

        Returns:
            A list of the loaded spectra
        """
        with LockViewport(self.window.viewport if self.window else None):
            # only one filename is given
            if isinstance(patterns, str):
                patterns = [patterns]

            if ID is not None and len(patterns) > 1:
                raise hdtv.cmdline.HDTVCommandError(
                    "If you specify an ID, you can only give one pattern"
                )

            loaded = []
            for p in patterns:
                # put fmt if available
                p = p.rsplit("'", 1)
                if len(p) == 1 or not p[1]:
                    (fpat, fmt) = (p[0], None)
                else:
                    (fpat, fmt) = p

                files = glob.glob(os.path.expanduser(fpat))

                if len(files) == 0:
                    hdtv.ui.warning("%s: no such file" % fpat)
                elif ID is not None and len(files) > 1:
                    raise hdtv.cmdline.HDTVCommandAbort(
                        "pattern %s is ambiguous and you specified an ID" % fpat
                    )
                    break

                if self.LoadSpectraNaturalSort.Get():
                    files.sort(key=hdtv.util.natural_sort_key)
                else:
                    files.sort()

                for fname in files:
                    try:
                        # Create spectrum object
                        spec = Spectrum(FileHistogram(fname, fmt))
                    except (OSError, SpecReaderError):
                        hdtv.ui.warning(f"Could not load {fname}'{fmt}")
                    else:
                        sid = self.spectra.Insert(spec, ID)
                        spec.color = hdtv.color.ColorForID(sid.major)
                        try:
                            spec.cal = self.spectra.caldict[spec.name]
                        except KeyError:
                            pass
                        loaded.append(spec)
                        if fmt is None:
                            hdtv.ui.msg(f"Loaded {fname} into {sid}")
                        else:
                            hdtv.ui.msg(f"Loaded {fname}'{fmt} into {sid}")

            if loaded:
                # activate last loaded spectrum
                self.spectra.ActivateObject(loaded[-1].ID)
            # Expand window if it is the only spectrum
            if len(self.spectra) == 1:
                if self.window:
                    self.window.Expand()
            return loaded

    def ListSpectra(self, visible=False):
        """
        Create a list of all spectra (for printing)
        """
        spectra = []
        params = ["ID", "stat", "name", "fits"]

        for ID in self.spectra.dict.keys():
            if visible and (ID not in self.spectra.visible):
                continue

            thisspec = {}

            status = ""
            if self.spectra.activeID == ID:
                status += "A"
            if ID in self.spectra.visible:
                status += "V"

            if self.spectra.activeID == ID:
                color = self.spectra.dict[ID]._activeColor
            else:
                color = self.spectra.dict[ID]._passiveColor
            r, g, b = hdtv.color.GetRGB(color)
            r, g, b = int(255 * r), int(255 * g), int(255 * b)
            thisspec["ID"] = f'<style fg="#{r:02x}{g:02x}{b:02x}">{ID}</style>'
            thisspec["stat"] = status
            thisspec["name"] = self.spectra.dict[ID].name
            thisspec["fits"] = len(self.spectra.dict[ID].dict)
            spectra.append(thisspec)

        table = hdtv.util.Table(spectra, params, sortBy="ID", raw_columns=["ID"])
        hdtv.ui.msg(html=str(table), end="")

    def CopySpectrum(self, ID, copyTo=None):
        """
        Copy spectrum

        Return ID of new spectrum
        """
        if copyTo is None:
            copyTo = self.spectra.GetFreeID()
        # get copy of underlying histogramm
        hist = copy.copy(self.spectra.dict[ID].hist)
        # create new spectrum object
        spec = Spectrum(hist)
        spec.color = hdtv.color.ColorForID(copyTo.major)
        spec.typeStr = "spectrum, copy"
        spec.name = "%s (copy)" % spec.name
        if hist.cal:
            cal = copy.copy(hist.cal)
            self.caldict[spec.name] = cal
            spec.cal = cal
        sid = self.spectra.Insert(spec, copyTo)
        hdtv.ui.msg("Copied spectrum " + str(ID) + " to " + str(sid))


class TvSpecInterface:
    """
    TV style commands for the spectrum interface.
    """

    def __init__(self, specInterface):
        self.opt = {}
        self.specIf = specInterface
        self.spectra = self.specIf.spectra

        # spectrum commands
        prog = "spectrum get"
        description = "Load a spectrum from a file (using libmfile)"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default=None,
            help="id for loaded spectrum",
        )
        parser.add_argument("pattern", nargs="+")
        hdtv.cmdline.AddCommand(
            prog, self.SpectrumGet, level=0, fileargs=True, parser=parser
        )
        # the spectrum get command is registered with level=0,
        # this allows "spectrum get" to be abbreviated as "spectrum", register
        # all other commands starting with spectrum with default or higher
        # priority

        prog = "spectrum list"
        description = "List all spectra"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-v",
            "--visible",
            action="store_true",
            default=False,
            help="list only visible (and active) spectra",
        )
        hdtv.cmdline.AddCommand(prog, self.SpectrumList, parser=parser)

        prog = "spectrum delete"
        description = "Delete one or multiple spectra"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument("specid", nargs="*", help="id of spectrum to delete")
        hdtv.cmdline.AddCommand(prog, self.SpectrumDelete, parser=parser)

        prog = "spectrum activate"
        description = (
            "Activate a single spetrum. If hidden, the spectrum is set to visible."
        )
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument("specid", nargs="*", help="id of spectrum to activate")
        hdtv.cmdline.AddCommand(prog, self.SpectrumActivate, parser=parser)

        prog = "spectrum show"
        description = "Set one or multiple spectra to visible"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "specid", nargs="*", help="id (or all, shown) of spectrum to update"
        )
        hdtv.cmdline.AddCommand(prog, self.SpectrumShow, parser=parser)

        prog = "spectrum hide"
        description = "Set one or multiple spectra to hidden"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "specid", nargs="*", help="id (or all, shown) of spectrum to update"
        )
        hdtv.cmdline.AddCommand(prog, self.SpectrumHide, level=2, parser=parser)

        prog = "spectrum info"
        description = "Display information associated with one or multiple spectra"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument("specid", nargs="*", help="id of spectrum to update")
        hdtv.cmdline.AddCommand(prog, self.SpectrumInfo, parser=parser)

        prog = "spectrum update"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid", nargs="*", help="id (or all, shown) of spectrum to update"
        )
        hdtv.cmdline.AddCommand(prog, self.SpectrumUpdate, parser=parser)

        prog = "spectrum write"
        description = "Write a single spectrum to the filesystem (using libmfile)"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument("filename", help="filename of output file")
        parser.add_argument(
            "format", help="format of spectrum file (e.g. txt for simple text file)"
        )
        parser.add_argument(
            "specid", nargs="?", default=None, help="id of spectrum to write"
        )
        parser.add_argument(
            "-F",
            "--force",
            action="store_true",
            default=False,
            help="overwrite existing files without asking",
        )
        hdtv.cmdline.AddCommand(prog, self.SpectrumWrite, parser=parser)

        prog = "spectrum normalize"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid", nargs="*", default=None, help="id of spectrum to normalize"
        )
        parser.add_argument("norm", type=float, help="norm of spectrum")
        hdtv.cmdline.AddCommand(prog, self.SpectrumNormalization, parser=parser)

        prog = "spectrum rebin"
        description = "Rebin the spectrum by grouping neighboring bins. The calibration of the spectrum is updated accordingly."
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "specid", nargs="*", default=None, help="id of spectrum to rebin"
        )
        parser.add_argument("ngroup", type=int, help="group n bins for rebinning")
        parser.add_argument(
            "-c",
            "--calibrate",
            action="store_true",
            help="Calibrate the spectrum after rebinning. If this switch is not used, peak positions will be shifted from pos to 1/ngroup*pos.",
        )
        hdtv.cmdline.AddCommand(
            prog, self.SpectrumRebin, level=2, fileargs=False, parser=parser
        )

        self.opt["binning"] = hdtv.options.Option(
            default="tv", parse=hdtv.options.parse_choices(["root", "tv"])
        )
        hdtv.options.RegisterOption("spec.binning", self.opt["binning"])

        prog = "spectrum calbin"
        description = "Align binning to energy calibration of spectrum."
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "specid", nargs="*", default=None, help="id of spectrum to calbin"
        )
        parser.add_argument(
            "--spline-order",
            "-k",
            type=int,
            default=3,
            metavar="[1-5]",
            help="Order of the spline interpolation (default: %(default)s)",
        )
        parser.add_argument(
            "-d", "--deterministic", action="store_true", help="Rebin deterministically"
        )
        parser.add_argument("--seed", "-s", type=int, help="Set random number seed")
        parser.add_argument(
            "--binsize",
            "-b",
            type=float,
            default=1.0,
            help="Size of each bin after rebinning (default: %(default)s)",
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--root-binning",
            "-r",
            action="store_true",
            help="Lower edge of first bin is aligned to 0.",
        )
        group.add_argument(
            "--tv-binning",
            "-t",
            action="store_true",
            help="Center of first bin is aligned to 0.",
        )
        hdtv.cmdline.AddCommand(
            prog, self.SpectrumCalbin, level=2, fileargs=False, parser=parser
        )

        prog = "spectrum resample"
        description = "Vary the content of each bin within its uncertainty, creating a new random sample of the underlying probability distribution."
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "specid", nargs="*", default=None, help="id of spectrum to resample"
        )
        parser.add_argument(
            "--distribution",
            "-d",
            type=str,
            default="poisson",
            help="Specify a random distribution function (default: %(default)s)",
        )
        parser.add_argument("--seed", "-s", type=int, help="Set random number seed")
        hdtv.cmdline.AddCommand(
            prog,
            self.SpectrumResample,
            level=2,
            fileargs=False,
            completer=self.RandomModelCompleter,
            parser=parser,
        )

        prog = "spectrum add"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "-n",
            "--normalize",
            action="store_true",
            help="normalize <target-id> by dividing through number of added spectra afterwards",
        )
        parser.add_argument(
            "targetid",
            metavar="target-id",
            help="where to place the resulting spectrum",
        )
        parser.add_argument("specid", nargs="*", help="ids of spectra to add up")
        hdtv.cmdline.AddCommand(
            prog, self.SpectrumAdd, level=2, fileargs=False, parser=parser
        )

        prog = "spectrum subtract"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "targetid",
            metavar="target-id",
            help="where to place the resulting spectrum",
        )
        parser.add_argument("specid", nargs="*", help="ids of spectra to subtract")
        hdtv.cmdline.AddCommand(
            prog, self.SpectrumSub, level=2, fileargs=False, parser=parser
        )

        prog = "spectrum multiply"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid", nargs="*", default=None, help="id of spectrum to multiply"
        )
        parser.add_argument("factor", type=float, help="multiplication factor")
        hdtv.cmdline.AddCommand(
            prog, self.SpectrumMultiply, level=2, fileargs=False, parser=parser
        )

        prog = "spectrum copy"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid", nargs="*", default=None, help="id of spectrum to copy"
        )
        parser.add_argument(
            "-s", "--spectrum", action="store", default=None, help="Target spectrum id"
        )
        hdtv.cmdline.AddCommand(
            prog, self.SpectrumCopy, level=2, fileargs=False, parser=parser
        )

        prog = "spectrum name"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid", nargs="?", default=None, help="id of spectrum to name"
        )
        parser.add_argument("name", help="name of spectrum")
        hdtv.cmdline.AddCommand(
            prog, self.SpectrumName, level=2, fileargs=False, parser=parser
        )

    def SpectrumList(self, args):
        """
        Print a list of spectra
        """
        self.specIf.ListSpectra(visible=args.visible)

    def SpectrumGet(self, args):
        """
        Load Spectra from files
        """
        if args.spectrum is not None:
            try:
                ids = hdtv.util.ID.ParseIds(
                    args.spectrum, self.spectra, only_existent=False
                )
                if len(ids) > 1:
                    raise hdtv.cmdline.HDTVCommandError("More than one ID given")
                ID = ids[0]
            except ValueError as msg:
                raise hdtv.cmdline.HDTVCommandError("Invalid ID: %s" % msg)
        else:
            ID = None
        self.specIf.LoadSpectra(patterns=args.pattern, ID=ID)

    def SpectrumDelete(self, args):
        """
        Deletes spectra
        """
        ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)

        if len(ids) == 0:
            hdtv.ui.warning("Nothing to do")
            return
        for ID in ids:
            self.spectra.Pop(ID)

    def SpectrumActivate(self, args):
        """
        Activate one spectrum
        """
        ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)

        if len(ids) > 1:
            raise hdtv.cmdline.HDTVCommandError("Can only activate one spectrum")
        elif len(ids) == 0:
            self.spectra.ActivateObject(None)
        else:
            self.spectra.ActivateObject(min(ids))

    def SpectrumCopy(self, args):
        """
        Copy spectra
        """
        ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)

        if len(ids) == 0:
            hdtv.ui.warning("Nothing to do")
            return
        targetids = []
        if args.spectrum is not None:
            targetids = hdtv.util.ID.ParseIds(
                args.spectrum, self.spectra, only_existent=False
            )
            targetids.sort()
        if len(targetids) == 0:
            targetids = [None for i in range(len(ids))]
        elif len(targetids) == 1:  # Only start ID is given
            startID = targetids[0]
            targetids = [
                hdtv.util.ID(i) for i in range(startID.major, startID.major + len(ids))
            ]
            targetids.sort()
        elif len(targetids) != len(ids):
            raise hdtv.cmdline.HDTVCommandError(
                "Number of target ids does not match number of ids to copy"
            )
        for i in range(len(ids)):
            try:
                self.specIf.CopySpectrum(ids[i], copyTo=targetids[i])
            except KeyError:
                raise hdtv.cmdline.HDTVCommandError("No such spectrum: " + str(ids[i]))

    def SpectrumAdd(self, args):
        """
        Add spectra (spec1 + spec2, ...)
        """
        # FIXME: Properly separate targetid, specid
        ids = hdtv.util.ID.ParseIds(
            [args.targetid] + args.specid, self.spectra, only_existent=False
        )

        if len(ids) == 0:
            hdtv.ui.warning("Nothing to do")
            return

        addTo = ids[0]
        # if addTo is a new spectrum
        if addTo not in list(self.spectra.dict.keys()):
            # first copy last of the spectra that should be added
            self.specIf.CopySpectrum(ids.pop(), addTo)

        # add all other spectra to the last spectrum
        for i in ids[1:]:
            try:
                hdtv.ui.msg("Adding " + str(i) + " to " + str(addTo))
                self.spectra.dict[addTo].Plus(self.spectra.dict[i])
            except KeyError:
                raise hdtv.cmdline.HDTVCommandError("Could not add " + str(i))
        self.spectra.dict[addTo].name = "sum"

        if args.normalize:
            norm_fac = len(ids)
            hdtv.ui.msg("Normalizing spectrum %s by 1/%d" % (addTo, norm_fac))
            self.spectra.dict[addTo].Multiply(1.0 / norm_fac)

    def SpectrumSub(self, args):
        """
        Subtract spectra (spec1 - spec2, ...)
        """
        # FIXME: Properly separate targetid, specid
        ids = hdtv.util.ID.ParseIds(
            [args.targetid] + args.specid, self.spectra, only_existent=False
        )

        if len(ids) == 0:
            hdtv.ui.warning("Nothing to do")
            return

        subFrom = ids[0]
        if subFrom not in list(self.spectra.dict.keys()):
            self.specIf.CopySpectrum(ids.pop(), subFrom)

        for i in ids[1:]:
            try:
                hdtv.ui.msg("Subtracting " + str(i) + " from " + str(subFrom))
                self.spectra.dict[subFrom].Minus(self.spectra.dict[i])
            except KeyError:
                raise hdtv.cmdline.HDTVCommandError("Could not subtract " + str(i))
        self.spectra.dict[subFrom].name = "difference"

    def SpectrumMultiply(self, args):
        """
        Multiply spectrum
        """
        if args.specid is None:
            if self.spectra.activeID is not None:
                msg = (
                    "Using active spectrum %s for multiplication"
                    % self.spectra.activeID
                )
                hdtv.ui.msg(msg)
                ids = [self.spectra.activeID]
            else:
                hdtv.ui.msg("No active spectrum")
                ids = []
        else:
            ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)

        if len(ids) == 0:
            hdtv.ui.warning("Nothing to do")
            return

        for i in ids:
            if i in list(self.spectra.dict.keys()):
                hdtv.ui.msg("Multiplying " + str(i) + " with " + str(args.factor))
                self.spectra.dict[i].Multiply(args.factor)
            else:
                raise hdtv.cmdline.HDTVCommandError(
                    "Cannot multiply spectrum " + str(i) + " (Does not exist)"
                )

    def SpectrumRebin(self, args):
        """
        Rebin spectrum
        """
        if args.specid is None:
            if self.spectra.activeID is not None:
                msg = "Using active spectrum %s for rebinning" % self.spectra.activeID
                hdtv.ui.msg(msg)
                ids = [self.spectra.activeID]
            else:
                hdtv.ui.msg("No active spectrum")
                ids = []
        else:
            ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)

        if len(ids) == 0:
            hdtv.ui.warning("Nothing to do")
            return

        for i in ids:
            if i in list(self.spectra.dict.keys()):
                hdtv.ui.msg(
                    "Rebinning "
                    + str(i)
                    + " with "
                    + str(args.ngroup)
                    + " bins per new bin"
                )
                self.spectra.dict[i].Rebin(args.ngroup, calibrate=args.calibrate)
            else:
                raise hdtv.cmdline.HDTVCommandError(
                    "Cannot rebin spectrum " + str(i) + " (Does not exist)"
                )

    def SpectrumCalbin(self, args):
        """
        Calbin spectrum
        """
        if args.specid is None:
            if self.spectra.activeID is not None:
                msg = "Using active spectrum %s for rebinning" % self.spectra.activeID
                hdtv.ui.msg(msg)
                ids = [self.spectra.activeID]
            else:
                hdtv.ui.msg("No active spectrum")
                ids = []
        else:
            ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)

        use_tv_binning = hdtv.options.Get("spec.binning") == "tv"
        use_tv_binning |= args.tv_binning
        use_tv_binning ^= args.root_binning

        if use_tv_binning:
            hdtv.ui.debug("Calbinning using tv binning convention.")
        else:
            hdtv.ui.debug("Calbinning using ROOT binning convention.")

        if len(ids) == 0:
            hdtv.ui.warning("Nothing to do")
            return

        with hdtv.util.temp_seed(args.seed):
            for i in ids:
                if i in list(self.spectra.dict.keys()):
                    spec = self.spectra.dict[i]
                    sum_before = spec._hist.Integral()
                    spec.Calbin(
                        binsize=args.binsize,
                        spline_order=args.spline_order,
                        use_tv_binning=use_tv_binning,
                    )
                    if spec.cal:
                        self.spectra.caldict[spec.name] = spec.cal
                    if not args.deterministic:
                        spec.Poisson()
                    hdtv.ui.msg(f"Calbinning {i} with binsize={args.binsize}")
                    sum_after = spec._hist.Integral()
                    change = 100 * (1 - sum_after / sum_before)
                    hdtv.ui.debug(
                        "Calbin: "
                        f"Area before = {sum_before}. "
                        f"Area after = {sum_after}."
                    )
                    hdtv.ui.info(f"Total area changed by {change:f}%")
                else:
                    raise hdtv.cmdline.HDTVCommandError(
                        "Cannot rebin spectrum " + str(i) + " (Does not exist)"
                    )

    def SpectrumResample(self, args):
        """
        Rebin spectrum
        """
        if args.specid is None:
            if self.spectra.activeID is not None:
                msg = "Using active spectrum %s for resampling" % self.spectra.activeID
                hdtv.ui.msg(msg)
                ids = [self.spectra.activeID]
            else:
                hdtv.ui.msg("No active spectrum")
                ids = []
        else:
            ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)

        if len(ids) == 0:
            hdtv.ui.warning("Nothing to do")
            return

        with hdtv.util.temp_seed(args.seed):
            for i in ids:
                if i in list(self.spectra.dict.keys()):
                    spec = self.spectra.dict[i]
                    sum_before = spec._hist.Integral()
                    if args.distribution == "poisson":
                        spec.Poisson()
                    else:
                        raise hdtv.cmdline.HDTVCommandError(
                            f"Unknown probability distribution: {args.distribution}"
                        )
                    sum_after = spec._hist.Integral()
                    change = 100 * (1 - sum_after / sum_before)
                    hdtv.ui.debug(
                        f"Resample ({args.distribution}): "
                        f"Area before = {sum_before}. "
                        f"Area after = {sum_after}."
                    )
                    hdtv.ui.info(f"Total area changed by {change:f}%")
                else:
                    raise hdtv.cmdline.HDTVCommandError(
                        f"Cannot resample spectrum {i} (Does not exist)"
                    )

    def SpectrumHide(self, args):
        """
        Hides spectra
        """
        if len(args.specid) == 0:
            ids = list(self.spectra.dict.keys())
        else:
            ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)

        self.spectra.HideObjects(ids)

    def SpectrumShow(self, args):
        """
        Shows spectra

        When inverse == True SpectrumShow behaves like SpectrumHide
        """
        if len(args.specid) == 0:
            ids = list(self.spectra.dict.keys())
        else:
            ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)

        self.spectra.ShowObjects(ids)

    def SpectrumInfo(self, args):
        """
        Print info on spectrum objects
        """
        if len(args.specid) == 0:
            specids = ["active"]
        else:
            specids = args.specid
        ids = hdtv.util.ID.ParseIds(specids, self.spectra)
        s = ""
        for ID in ids:
            try:
                spec = self.spectra.dict[ID]
            except KeyError:
                s += "Spectrum %s: ID not found\n" % ID
                continue
            s += "Spectrum %s:\n" % ID
            s += hdtv.util.Indent(spec.info, "  ")
        hdtv.ui.msg(s, end="")

    def SpectrumUpdate(self, args):
        """
        Refresh spectra
        """
        if len(args.specid) == 0:
            specids = ["active"]
        else:
            specids = args.specid
        ids = hdtv.util.ID.ParseIds(specids, self.spectra)
        if len(ids) == 0:
            hdtv.ui.warning("Nothing to do")
            return
        self.spectra.RefreshObjects(ids)

    def SpectrumWrite(self, args):
        """
        Write Spectrum to File
        """
        # TODO: should accept somthing like "spec write all"
        filename = args.filename
        fmt = args.format
        if args.specid is None:
            ID = self.spectra.activeID
        else:
            ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)
            if len(ids) != 1:
                raise ValueError("There is just one index possible here.")
            ID = ids[0]
        try:
            fname = hdtv.util.user_save_file(args.filename, args.force)
            if not fname:
                return
            self.spectra.dict[ID].WriteSpectrum(filename, fmt)
            hdtv.ui.msg(f"Wrote spectrum with id {ID} to file {filename}")
        except KeyError:
            hdtv.ui.warning("There is no spectrum with id: %s" % ID)

    def SpectrumName(self, args):
        """
        Give spectrum a name
        """
        if args.specid is None:
            ID = self.spectra.activeID
        else:
            ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)

            if len(ids) == 0:
                hdtv.ui.warning("Nothing to do")
                return
            elif len(ids) > 1:
                hdtv.ui.warning("Can only rename one spectrum at a time")
                return

            ID = ids[0]

        spec = self.spectra.dict[ID]
        spec.name = args.name
        if spec.cal and not spec.cal.IsTrivial():
            self.spectra.caldict[args.name] = spec.cal
        hdtv.ui.msg(f"Renamed spectrum {ID} to '{args.name}'")

    def SpectrumNormalization(self, args):
        "Set normalization for spectrum"
        if args.specid is None:
            ids = [self.spectra.activeID]
        else:
            ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)
            if len(ids) == 0:
                hdtv.ui.warning("Nothing to do")
                return

        for ID in ids:
            try:
                self.spectra.dict[ID].norm = args.norm
            except KeyError:
                raise hdtv.cmdline.HDTVCommandError(
                    "There is no spectrum with id: %s" % ID
                )

    def RandomModelCompleter(self, text, args=None):
        """
        Helper function for SpectrumResample
        """
        return hdtv.util.GetCompleteOptions(text, iter(["poisson"]))


# plugin initialisation
import __main__

spec_interface = SpecInterface(__main__.spectra)
hdtv.cmdline.RegisterInteractive("s", spec_interface)
