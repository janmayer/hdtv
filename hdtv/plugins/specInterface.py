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

import ROOT
import os
import glob
import copy

import hdtv.cmdline
import hdtv.color
import hdtv.cal
import hdtv.util
import hdtv.ui

from hdtv.spectrum import Spectrum
from hdtv.histogram import FileHistogram
from hdtv.specreader import SpecReaderError


class SpecInterface(object):
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
        self.window.AddHotkey(ROOT.kKey_PageUp, self.spectra.ShowPrev)
        self.window.AddHotkey(ROOT.kKey_PageDown, self.spectra.ShowNext)

        # register common tv hotkeys
        self.window.AddHotkey([ROOT.kKey_N, ROOT.kKey_p],
                              self.spectra.ShowPrev)
        self.window.AddHotkey([ROOT.kKey_N, ROOT.kKey_n],
                              self.spectra.ShowNext)
        self.window.AddHotkey(ROOT.kKey_Equal, self.spectra.RefreshAll)
        self.window.AddHotkey(ROOT.kKey_t, self.spectra.RefreshVisible)
        self.window.AddHotkey(
            ROOT.kKey_n,
            lambda: self.window.EnterEditMode(
                prompt="Show spectrum: ",
                handler=self._HotkeyShow))
        self.window.AddHotkey(
            ROOT.kKey_a,
            lambda: self.window.EnterEditMode(
                prompt="Activate spectrum: ",
                handler=self._HotkeyActivate))

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
            self.window.viewport.SetStatusText(
                "Invalid spectrum identifier: %s" % arg)

    def _HotkeyActivate(self, arg):
        """
        ActivateObject wrapper for use with Hotkey
        """
        try:
            ids = hdtv.util.ID.ParseIds(arg, self.spectra)
            if len(ids) > 1:
                self.window.viewport.SetStatusText(
                    "Cannot activate more than one spectrum")
            elif len(ids) == 0:  # Deactivate
                oldactive = self.spectra.activeID
                self.spectra.ActivateObject(None)
                self.window.viewport.SetStatusText(
                    "Deactivated spectrum %s" % oldactive)
            else:
                ID = ids[0]
                self.spectra.ActivateObject(ID)
                self.window.viewport.SetStatusText(
                    "Activated spectrum %s" % self.spectra.activeID)
        except ValueError:
            self.window.viewport.SetStatusText("Invalid id: %s" % arg)

    def LoadSpectra(self, patterns, ID=None):
        """
        Load spectra from files matching patterns.

        If ID is specified, the spectrum is stored with id ID, possibly
        replacing a spectrum that was there before.
        """
        # Avoid multiple updates
        self.window.viewport.LockUpdate()
        # only one filename is given
        if isinstance(patterns, str) or isinstance(patterns, str):
            patterns = [patterns]

        if ID is not None and len(patterns) > 1:
            self.window.viewport.UnlockUpdate()
            raise hdtv.cmdline.HDTVCommandError(
                "If you specify an ID, you can only give one pattern")

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
                hdtv.ui.warn("%s: no such file" % fpat)
            elif ID is not None and len(files) > 1:
                hdtv.ui.error(
                    "pattern %s is ambiguous and you specified an ID" % fpat)
                break

            files.sort()

            for fname in files:
                try:
                    # Create spectrum object
                    spec = Spectrum(FileHistogram(fname, fmt))
                except (OSError, SpecReaderError):
                    hdtv.ui.warn("Could not load %s'%s" % (fname, fmt))
                else:
                    sid = self.spectra.Insert(spec, ID)
                    spec.color = hdtv.color.ColorForID(sid.major)
                    if spec.name in list(self.spectra.caldict.keys()):
                        spec.cal = self.spectra.caldict[spec.name]
                    loaded.append(sid)
                    if fmt is None:
                        hdtv.ui.msg("Loaded %s into %s" % (fname, sid))
                    else:
                        hdtv.ui.msg("Loaded %s'%s into %s" % (fname, fmt, sid))

        if len(loaded) > 0:
            # activate last loaded spectrum
            self.spectra.ActivateObject(loaded[-1])
        # Expand window if it is the only spectrum
        if len(self.spectra) == 1:
            self.window.Expand()
        self.window.viewport.UnlockUpdate()
        return loaded

    def ListSpectra(self, visible=False):
        """
        Create a list of all spectra (for printing)
        """
        spectra = list()
        params = ["ID", "stat", "name", "fits"]

        for (ID, obj) in self.spectra.dict.items():
            if visible and (ID not in self.spectra.visible):
                continue

            thisspec = dict()

            status = str()
            if ID == self.spectra.activeID:
                status += "A"
            if ID in self.spectra.visible:
                status += "V"

            thisspec["ID"] = ID
            thisspec["stat"] = status
            thisspec["name"] = self.spectra.dict[ID].name
            thisspec["fits"] = len(self.spectra.dict[ID].dict)
            spectra.append(thisspec)

        table = hdtv.util.Table(spectra, params, sortBy="ID")
        hdtv.ui.msg(str(table), newline=False)

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


class TvSpecInterface(object):
    """
    TV style commands for the spectrum interface.
    """

    def __init__(self, specInterface):
        self.specIf = specInterface
        self.spectra = self.specIf.spectra

        # spectrum commands
        prog = "spectrum get"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument("-s", "--spectrum", action="store", default=None,
            help="id for loaded spectrum")
        parser.add_argument(
            "pattern",
            nargs='+')
        hdtv.cmdline.AddCommand(prog, self.SpectrumGet, level=0,
            fileargs=True, parser=parser)
        # the spectrum get command is registered with level=0,
        # this allows "spectrum get" to be abbreviated as "spectrum", register
        # all other commands starting with spectrum with default or higher
        # priority

        prog = "spectrum list"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "-v",
            "--visible",
            action="store_true",
            default=False,
            help="list only visible (and active) spectra")
        hdtv.cmdline.AddCommand(prog, self.SpectrumList, parser=parser)

        prog = "spectrum delete"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid",
            nargs='*',
            help='id of spectrum to delete')
        hdtv.cmdline.AddCommand(
            prog, self.SpectrumDelete, parser=parser)

        prog = "spectrum activate"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid",
            nargs='*',
            help='id of spectrum to activate')
        hdtv.cmdline.AddCommand(
            prog, self.SpectrumActivate, parser=parser)

        prog = "spectrum show"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid",
            nargs='*',
            help='id (or all, shown) of spectrum to update')
        hdtv.cmdline.AddCommand(prog, self.SpectrumShow, parser=parser)

        prog = "spectrum hide"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid",
            nargs='*',
            help='id (or all, shown) of spectrum to update')
        hdtv.cmdline.AddCommand(prog, self.SpectrumHide,
                                level=2, parser=parser)

        prog = "spectrum info"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid",
            nargs='*',
            help='id of spectrum to update')
        hdtv.cmdline.AddCommand(prog, self.SpectrumInfo, parser=parser)

        prog = "spectrum update"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid",
            nargs='*',
            help='id (or all, shown) of spectrum to update')
        hdtv.cmdline.AddCommand(prog, self.SpectrumUpdate, parser=parser)

        prog = "spectrum write"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            'filename',
            help="filename of output file")
        parser.add_argument(
            'format',
            help="format of spectrum file")
        parser.add_argument(
            "specid",
            nargs='?',
            default=None,
            help='id of spectrum to write')
        hdtv.cmdline.AddCommand(prog, self.SpectrumWrite, parser=parser)

        prog = "spectrum normalize"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid",
            nargs='*',
            default=None,
            help='id of spectrum to normalize')
        parser.add_argument(
            "norm",
            type=float,
            help='norm of spectrum')
        hdtv.cmdline.AddCommand(
            prog, self.SpectrumNormalization, parser=parser)

        prog = "spectrum rebin"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid",
            nargs='*',
            default=None,
            help='id of spectrum to rebin')
        parser.add_argument(
            "ngroup",
            type=int,
            help='group n bins for rebinning')
        hdtv.cmdline.AddCommand(
            prog,
            self.SpectrumRebin,
            level=2,
            fileargs=False,
            parser=parser)

        prog = "spectrum calbin"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid",
            nargs='*',
            default=None,
            help='id of spectrum to rebin')
        hdtv.cmdline.AddCommand(
            prog,
            self.SpectrumCalbin,
            level=2,
            fileargs=False,
            parser=parser)

        prog = "spectrum add"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "-n",
            "--normalize",
            action="store_true",
            help="normalize <target-id> by dividing through number of added spectra afterwards")
        parser.add_argument(
            "targetid",
            metavar="target-id",
            help='where to place the resulting spectrum')
        parser.add_argument(
            "specid",
            nargs='*',
            help='ids of spectra to add up')
        hdtv.cmdline.AddCommand(
            prog,
            self.SpectrumAdd,
            level=2,
            fileargs=False,
            parser=parser)

        prog = "spectrum subtract"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "targetid",
            metavar="target-id",
            help='where to place the resulting spectrum')
        parser.add_argument(
            "specid",
            nargs='*',
            help='ids of spectra to subtract')
        hdtv.cmdline.AddCommand(prog, self.SpectrumSub, level=2,
                                fileargs=False, parser=parser)

        prog = "spectrum multiply"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid",
            nargs='*',
            default=None,
            help='id of spectrum to multiply')
        parser.add_argument(
            "factor",
            type=float,
            help='multiplication factor')
        hdtv.cmdline.AddCommand(
            prog,
            self.SpectrumMultiply,
            level=2,
            fileargs=False,
            parser=parser)

        prog = "spectrum copy"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid",
            nargs='*',
            default=None,
            help='id of spectrum to copy')
        parser.add_argument("-s", "--spectrum", action="store",
                          default=None, help="Target spectrum id")
        hdtv.cmdline.AddCommand(prog, self.SpectrumCopy, level=2,
                                fileargs=False, parser=parser)

        prog = "spectrum name"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "specid",
            nargs='?',
            default=None,
            help='id of spectrum to name')
        parser.add_argument(
            "name",
            help='name of spectrum')
        hdtv.cmdline.AddCommand(prog, self.SpectrumName, level=2,
                                fileargs=False, parser=parser)

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
                    args.spectrum, self.spectra, only_existent=False)
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
            hdtv.ui.warn("Nothing to do")
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
            hdtv.ui.warn("Nothing to do")
            return
        targetids = list()
        if args.spectrum is not None:
            targetids = hdtv.util.ID.ParseIds(
                args.spectrum, self.spectra, only_existent=False)
            targetids.sort()
        if len(targetids) == 0:
            targetids = [None for i in range(0, len(ids))]
        elif len(targetids) == 1:  # Only start ID is given
            startID = targetids[0]
            targetids = [hdtv.util.ID(i) for i in range(
                startID.major, startID.major + len(ids))]
            targetids.sort()
        elif len(targetids) != len(ids):
            raise hdtv.cmdline.HDTVCommandError(
                "Number of target ids does not match number of ids to copy")
        for i in range(0, len(ids)):
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
            [args.targetid] + args.specid, self.spectra, only_existent=False)

        if len(ids) == 0:
            hdtv.ui.warn("Nothing to do")
            return

        addTo = ids[0]
        # if addTo is a new spectrum
        if addTo not in list(self.spectra.dict.keys()):
            # first copy last of the spectra that should be added
            sid = self.specIf.CopySpectrum(ids.pop(), addTo)

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
            self.spectra.dict[addTo].Multiply(1. / norm_fac)

    def SpectrumSub(self, args):
        """
        Subtract spectra (spec1 - spec2, ...)
        """
        # FIXME: Properly separate targetid, specid
        ids = hdtv.util.ID.ParseIds(
            [args.targetid] + args.specid, self.spectra, only_existent=False)

        if len(ids) == 0:
            hdtv.ui.warn("Nothing to do")
            return

        subFrom = ids[0]
        if subFrom not in list(self.spectra.dict.keys()):
            sid = self.specIf.CopySpectrum(ids.pop(), subFrom)

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
                msg = "Using active spectrum %s for multiplication" % self.spectra.activeID
                hdtv.ui.msg(msg)
                ids = [self.spectra.activeID]
            else:
                hdtv.ui.msg("No active spectrum")
                ids = list()
        else:
            ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)

        if len(ids) == 0:
            hdtv.ui.warn("Nothing to do")
            return

        for i in ids:
            if i in list(self.spectra.dict.keys()):
                hdtv.ui.msg("Multiplying " + str(i) + " with " + str(args.factor))
                self.spectra.dict[i].Multiply(args.factor)
            else:
                raise hdtv.cmdline.HDTVCommandError(
                    "Cannot multiply spectrum " + str(i) + " (Does not exist)")

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
                ids = list()
        else:
            ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)

        if len(ids) == 0:
            hdtv.ui.warn("Nothing to do")
            return

        for i in ids:
            if i in list(self.spectra.dict.keys()):
                hdtv.ui.msg("Rebinning " + str(i) + " with " +
                            str(args.ngroup) + " bins per new bin")
                self.spectra.dict[i].Rebin(args.ngroup)
            else:
                raise hdtv.cmdline.HDTVCommandError(
                    "Cannot rebin spectrum " + str(i) + " (Does not exist)")

    def SpectrumCalbin(self, args):
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
                ids = list()
        else:
            ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)

        if len(ids) == 0:
            hdtv.ui.warn("Nothing to do")
            return

        for i in ids:
            if i in list(self.spectra.dict.keys()):
                self.spectra.dict[i].Calbin()
            else:
                raise hdtv.cmdline.HDTVCommandError(
                    "Cannot rebin spectrum " + str(i) + " (Does not exist)")

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
        s = str()
        for ID in ids:
            try:
                spec = self.spectra.dict[ID]
            except KeyError:
                s += "Spectrum %s: ID not found\n" % ID
                continue
            s += "Spectrum %s:\n" % ID
            s += hdtv.util.Indent(spec.info, "  ")
        hdtv.ui.msg(s, newline=False)

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
            hdtv.ui.warn("Nothing to do")
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
            self.spectra.dict[ID].WriteSpectrum(filename, fmt)
            hdtv.ui.msg("Wrote spectrum with id %s to file %s" %
                        (ID, filename))
        except KeyError:
            hdtv.ui.warn("There is no spectrum with id: %s" % ID)

    def SpectrumName(self, args):
        """
        Give spectrum a name
        """
        if args.specid is None:
            ID = self.spectra.activeID
        else:
            ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)

            if len(ids) == 0:
                hdtv.ui.warn("Nothing to do")
                return
            elif len(ids) > 1:
                hdtv.ui.warn("Can only rename one spectrum at a time")
                return

            ID = ids[0]

        spec = self.spectra.dict[ID]
        spec.name = args.name
        if spec.cal and not spec.cal.IsTrivial():
            self.spectra.caldict[args.name] = spec.cal
        hdtv.ui.msg("Renamed spectrum %s to \'%s\'" % (ID, args.name))

    def SpectrumNormalization(self, args):
        "Set normalization for spectrum"
        if args.specid is None:
            ids = [self.spectra.activeID]
        else:
            ids = hdtv.util.ID.ParseIds(args.specid, self.spectra)
            if len(ids) == 0:
                hdtv.ui.warn("Nothing to do")
                return

        for ID in ids:
            try:
                self.spectra.dict[ID].norm = args.norm
            except KeyError:
                raise hdtv.cmdline.HDTVCommandError("There is no spectrum with id: %s" % ID)


# plugin initialisation
import __main__
__main__.s = SpecInterface(__main__.spectra)
