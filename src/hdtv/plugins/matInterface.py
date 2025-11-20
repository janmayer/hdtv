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
Matrix interface for hdtv
"""


import ROOT

import hdtv.cmdline
import hdtv.rootext.display
import hdtv.ui
import hdtv.util
from hdtv.histogram import MHisto2D
from hdtv.matrix import Matrix
from hdtv.specreader import SpecReader, SpecReaderError


class MatInterface:
    def __init__(self, spectra):
        hdtv.ui.debug("Loaded user interface for working with 2-d spectra")

        self.spectra = spectra
        self.window = spectra.window
        self.oldcut = None

        # tv commands
        self.tv = TvMatInterface(self)

        # Register hotkeys
        if self.window:
            self.window.AddHotkey(ROOT.kKey_g, lambda: self.spectra.SetMarker("cut"))
            self.window.AddHotkey(
                [ROOT.kKey_c, ROOT.kKey_g], lambda: self.spectra.SetMarker("cutregion")
            )
            self.window.AddHotkey(
                [ROOT.kKey_c, ROOT.kKey_b], lambda: self.spectra.SetMarker("cutbg")
            )
            self.window.AddHotkey(
                [ROOT.kKey_Minus, ROOT.kKey_c, ROOT.kKey_g],
                lambda: self.spectra.RemoveMarker("cutregion"),
            )
            self.window.AddHotkey(
                [ROOT.kKey_Minus, ROOT.kKey_c, ROOT.kKey_b],
                lambda: self.spectra.RemoveMarker("cutbg"),
            )
            self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_C], self.spectra.ClearCut)
            self.window.AddHotkey([ROOT.kKey_Plus, ROOT.kKey_C], self.spectra.StoreCut)
            self.window.AddHotkey(ROOT.kKey_C, self.spectra.ExecuteCut)
            self.window.AddHotkey(
                [ROOT.kKey_c, ROOT.kKey_s],
                lambda: self.window.EnterEditMode(
                    prompt="Show Cut: ", handler=self._HotkeyShow
                ),
            )
            self.window.AddHotkey(
                [ROOT.kKey_c, ROOT.kKey_a],
                lambda: self.window.EnterEditMode(
                    prompt="Activate Cut: ", handler=self._HotkeyActivate
                ),
            )
            self.window.AddHotkey(
                [ROOT.kKey_c, ROOT.kKey_p], lambda: self._HotkeyShow("PREV")
            )
            self.window.AddHotkey(
                [ROOT.kKey_c, ROOT.kKey_n], lambda: self._HotkeyShow("NEXT")
            )
            self.window.AddHotkey(ROOT.kKey_Tab, self._HotkeySwitch)

    def _HotkeyShow(self, args):
        """
        Show wrapper for use with a Hotkey (internal use)
        """
        spec = self.spectra.GetActiveObject()
        if spec is None and self.window:
            self.window.viewport.SetStatusText("No active spectrum")
            return
        if (not hasattr(spec, "matrix") or spec.matrix is None) and self.window:
            self.window.viewport.SetStatusText("No matrix")
            return
        try:
            ids = hdtv.util.ID.ParseIds(args, spec.matrix)
        except ValueError:
            if self.window:
                self.window.viewport.SetStatusText("Invalid cut identifier: %s" % args)
            return
        spec.ShowObjects(ids)

    def _HotkeyActivate(self, args):
        """
        ActivateObject wrapper for use with a Hotkey (internal use)
        """
        spec = self.spectra.GetActiveObject()
        if spec is None and self.window:
            self.window.viewport.SetStatusText("No active spectrum")
            return
        if (not hasattr(spec, "matrix") or spec.matrix is None) and self.window:
            self.window.viewport.SetStatusText("No matrix")
            return
        try:
            ids = hdtv.util.ID.ParseIds(args, spec.matrix)
        except ValueError:
            if self.window:
                self.window.viewport.SetStatusText("Invalid cut identifier: %s" % args)
            return
        if len(ids) == 1:
            if self.window:
                self.window.viewport.SetStatusText("Activating cut %s" % ids[0])
            self.spectra.ActivateCut(ids[0])
        elif len(ids) == 0:
            if self.window:
                self.window.viewport.SetStatusText("Deactivating cut")
            self.spectra.ActivateCut(None)
        else:
            if self.window:
                self.window.viewport.SetStatusText("Can only activate one cut")

    def _HotkeySwitch(self):
        # FIXME
        spec = self.spectra.GetActiveObject()
        if spec is None:
            raise hdtv.cmdline.HDTVCommandError("There is no active spectrum")
        if not hasattr(spec, "matrix") or spec.matrix is None:
            raise hdtv.cmdline.HDTVCommandError(
                "Active spectrum does not belong to a matrix"
            )
        mat = spec.matrix
        # for a cut, switch to projection
        if spec in mat.specs:
            if spec.axis == "y":
                # show x proj
                ID = self.spectra.Index(mat.xproj)
            else:
                # show y proj
                ID = self.spectra.Index(mat.yproj)
            if ID is None:
                hdtv.ui.warning("Projection is not loaded.")
                return
        # for a projection, cut to last shown cut
        else:
            ID = self.oldcut
            if ID is None:
                # FIXME
                hdtv.ui.warning("No old cut")
                return
        self.spectra.ShowObjects(ID)

    def LoadMatrix(self, fname, sym, ID=None):
        # FIXME: just for testing!
        try:
            histo = MHisto2D(fname, sym)
        except (OSError, SpecReaderError):
            hdtv.ui.warning("Could not load %s" % fname)
            return

        matrix = Matrix(histo, sym, self.spectra.viewport)
        proj = matrix.xproj
        ID = self.spectra.GetFreeID()
        matrix.ID = ID
        matrix.color = hdtv.color.ColorForID(ID.major)
        # load x projection
        sid = self.spectra.Insert(proj, ID=hdtv.util.ID(ID.major, 1000))
        self.spectra.ActivateObject(sid)
        if sym is False:
            # also load y projection
            proj = matrix.yproj
            self.spectra.Insert(proj, ID=hdtv.util.ID(ID.major, 1001))

    def ListMatrix(self, matrix):
        params = ["ID", "stat", "axis", "gates", "bg", "specID"]
        cuts = []
        count = 0

        for ID, obj in matrix.dict.items():
            this = {}

            stat = ""
            if matrix.activeID == ID:
                stat += "A"
            if ID in matrix.visible:
                stat += "V"

            this["ID"] = ID
            this["stat"] = stat
            this["axis"] = obj.axis

            gates = ""
            for gate in obj.regionMarkers:
                p = sorted([gate.p1.pos_cal, gate.p2.pos_cal])
                gates += " %d - %d " % (p[0], p[1])
            this["gates"] = gates

            bgs = ""
            for bg in obj.bgMarkers:
                bg = sorted([bg.p1.pos_cal, bg.p2.pos_cal])
                bgs += " %d - %d " % (bg[0], bg[1])
            this["bg"] = bgs

            if obj.spec is not None:
                count += 1
                sid = self.spectra.Index(obj.spec)
                stat = ""
                if sid == self.spectra.activeID:
                    stat += "A"
                if sid in self.spectra.visible:
                    stat += "V"
                if len(stat) > 0:
                    spec = sid + " (" + stat + ")"
                else:
                    spec = sid
            else:
                spec = "not loaded"
            this["specID"] = spec

            cuts.append(this)
        table = hdtv.util.Table(cuts, params, sortBy="ID")

        if matrix.sym:
            sym = "symmetric"
        else:
            sym = "asymmetric"
        header = "\nmatrix ID = " + matrix.ID + ' "' + matrix.name + '" (' + sym + ")\n"
        footer = (
            "\n"
            + str(len(matrix.ids))
            + " cuts, "
            + str(count)
            + " loaded cut spectra."
        )

        table = hdtv.util.Table(
            cuts, params, sortBy="ID", extra_header=header, extra_footer=footer
        )
        return str(table)


class TvMatInterface:
    def __init__(self, matInterface):
        self.matIf = matInterface
        self.spectra = self.matIf.spectra

        prog = "matrix get"
        description = "load a matrix, i.e. the projections"
        description += "if the matrix is symmetric it only loads one projection"
        description += "if it is asymmetric both projections will be loaded."
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default=None,
            help="base id for loaded projections",
        )
        parser.add_argument("matrix_type", metavar="matrix-type", help="{asym,sym}")
        parser.add_argument(
            "filename", metavar="matrix-file", help="file with matrix to load"
        )
        hdtv.cmdline.AddCommand(
            prog, self.MatrixGet, level=0, fileargs=True, parser=parser
        )

        # FIXME
        prog = "matrix list"
        description = "list all loaded matrices and the belonging cuts and cut spectra."
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        # TODO: sort for gates
        # parser.add_argument("-k", "--key-sort", action = "store", default = hdtv.options.Get("fit.list.sort_key"),
        #     help = "sort by key")
        # parser.add_argument("-r", "--reverse-sort", action = "store_true", default = False,
        #     help = "reverse the sort")
        parser.add_argument(
            "-m",
            "--matrix",
            action="store",
            default="all",
            help="select matrix to work on",
        )
        hdtv.cmdline.AddCommand(prog, self.MatrixList, parser=parser)

        # FIXME
        prog = "matrix project"
        description = "reload projection of matrix"

        prog = "matrix view"
        description = "show 2D view of the matrix"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "filename", metavar="matrix-file", help="file with matrix to load"
        )
        parser.add_argument("format", nargs="?", default=None, help="format of matrix")
        hdtv.cmdline.AddCommand(
            prog, self.MatrixView, level=0, fileargs=True, parser=parser
        )

        # FIXME
        prog = "matrix delete"
        description = "delete the matrix, with all cuts and cut spectra"

        prog = "cut marker"
        description = "set/delete a marker for cutting"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument("type", help="{background,region}")
        parser.add_argument("action", help="{delete,set}")
        parser.add_argument("position", type=float, help="position of marker")
        hdtv.cmdline.AddCommand(
            prog, self.CutMarkerChange, parser=parser, completer=self.MarkerCompleter
        )

        # FIXME: this should accept --cut to reload cut spectra for a cut
        prog = "cut execute"
        description = "execute cut"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        hdtv.cmdline.AddCommand(prog, self.CutExecute, level=0, parser=parser)

        prog = "cut clear"
        description = "clear cut marker and remove last cut if it was not stored"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        hdtv.cmdline.AddCommand(prog, self.CutClear, parser=parser)

        prog = "cut store"
        description = "deactivates last cut (overwrite protection)"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        hdtv.cmdline.AddCommand(prog, self.CutStore, parser=parser)

        prog = "cut activate"
        description = "reactivates a cut from the cutlist"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument("cutid", nargs="+", help="id of cut")
        hdtv.cmdline.AddCommand(prog, self.CutActivate, parser=parser)

        prog = "cut delete"
        description = "delete a cut (marker and spectrum)"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument("cutid", nargs="+", help="id of cut")
        hdtv.cmdline.AddCommand(prog, self.CutDelete, minargs=1, parser=parser)

        # FIXME
        prog = "cut show"
        description = "show a cut"

        # FIXME
        prog = "cut hide"
        description = "hide a cut"

        # List of MTViewers (2d matrix views)
        self.matviews = []

    def MatrixView(self, args):
        """
        Load a matrix from file, then display it in 2d
        """
        hist = SpecReader.GetMatrix(args.filename, args.format)

        title = hist.GetTitle()
        viewer = ROOT.HDTV.Display.MTViewer(400, 400, hist, title)
        self.matviews.append(viewer)

    def MatrixGet(self, args):
        """
        Load a matrix from file
        """
        if args.spectrum is not None:
            ID = args.spectrum
        else:
            ID = None
        if args.matrix_type == "sym":
            sym = True
        elif args.matrix_type == "asym":
            sym = False
        else:
            # FIXME: is there really no way to test that automatically????
            raise hdtv.cmdline.HDTVCommandError(
                "Please specify if matrix is of type asym or sym"
            )
        self.matIf.LoadMatrix(args.filename, sym, ID=ID)

    def MatrixList(self, args):
        """
        Show a overview of matrices with all cuts and cut spectra
        """
        # TODO: Parse ids
        ids = "ALL"
        matrices = set()

        for spec in self.spectra.dict.values():
            if hasattr(spec, "matrix") and spec.matrix is not None:
                if ids == "ALL" or spec.matrix.ID in ids:
                    matrices.add(spec.matrix)

        result = ""
        for mat in matrices:
            result += self.matIf.ListMatrix(mat)
        hdtv.ui.msg(html=result)

    def CutMarkerChange(self, args):
        """
        Set or delete a marker from command line
        """
        # complete markertype if needed
        mtype = self.MarkerCompleter(args.type)
        if len(mtype) == 0:
            raise hdtv.cmdline.HDTVCommandError(
                "Marker type %s is not valid" % args.type
            )
        action = self.MarkerCompleter(
            args.action,
            args=[
                args.action,
            ],
        )
        if len(action) == 0:
            raise hdtv.cmdline.HDTVCommandError("Invalid action: %s" % args.action)

        mtype = mtype[0].strip()
        # replace "background" with "cutbg" which is internally used
        if mtype == "background":
            mtype = "cutbg"
        # replace "region" with "cutregion" which is internally used
        if mtype == "region":
            mtype = "cutregion"
        action = action[0].strip()
        if action == "set":
            self.spectra.SetMarker(mtype, args.position)
        if action == "delete":
            self.spectra.RemoveMarker(mtype, args.position)

    def MarkerCompleter(self, text, args=None):
        """
        Helper function for CutMarkerChange
        """
        if args is None or not args:
            mtypes = ["background", "region"]
            return hdtv.util.GetCompleteOptions(text, mtypes)
        elif len(args) == 1:
            actions = ["set", "delete"]
            return hdtv.util.GetCompleteOptions(text, actions)
        return []

    def CutExecute(self, args):
        return self.spectra.ExecuteCut()

    def CutClear(self, args):
        return self.spectra.ClearCut()

    def CutStore(self, args):
        return self.spectra.StoreCut()

    def CutActivate(self, args):
        """
        Activate a cut

        This marks a stored cut as active and copies its markers to the work cut
        """
        spec = self.spectra.GetActiveObject()
        if spec is None:
            hdtv.ui.warning("No active spectrum")
            return
        if not hasattr(spec, "matrix") or spec.matrix is None:
            hdtv.ui.warning("Active spectrum does not belong to a matrix")
            return
        ids = hdtv.util.ID.ParseIds(args.cutid, spec.matrix)
        if len(ids) == 1:
            hdtv.ui.msg("Activating cut %s" % ids[0])
            self.spectra.ActivateCut(ids[0])
        elif len(ids) == 0:
            hdtv.ui.msg("Deactivating cut")
            self.spectra.ActivateCut(None)
        else:
            raise hdtv.cmdline.HDTVCommandError("Can only activate one cut")

    def CutDelete(self, args):
        """
        Delete a cut and its cut spectrum
        """
        spec = self.spectra.GetActiveObject()
        if spec is None:
            hdtv.ui.warning("No active spectrum")
            return
        if not hasattr(spec, "matrix") or spec.matrix is None:
            hdtv.ui.warning("Active spectrum does not belong to a matrix")
            return
        ids = hdtv.util.ID.ParseIds(args.cutid, spec.matrix)
        for ID in ids:
            cut = spec.matrix.Pop(ID)
            # delete also cut spectrum
            if cut.spec is not None:
                sid = self.spectra.Index(cut.spec)
                hdtv.ui.msg("Remove spec %s" % sid)
                self.spectra.Pop(sid)


# plugin initialisation
import __main__

matrix_interface = MatInterface(__main__.spectra)
hdtv.cmdline.RegisterInteractive("mat", matrix_interface)
