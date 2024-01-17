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
Preliminary ROOT file interface for hdtv
"""

import fnmatch
import os

import ROOT

import hdtv.cmdline
import hdtv.rfile_utils
import hdtv.rootext.display
import hdtv.tabformat
import hdtv.ui
import hdtv.util
from hdtv.histogram import Histogram, RHisto2D, THnSparseWrapper
from hdtv.matrix import Matrix
from hdtv.spectrum import Spectrum


class RootFileInterface:
    def __init__(self, spectra):
        hdtv.ui.debug("Loaded user interface for working with root files")

        self.spectra = spectra
        self.window = spectra.window
        self.caldict = spectra.caldict
        self.rootfile = None
        self.browser = None
        self.matviews = []

        hdtv.cmdline.AddCommand("root ls", self.RootLs, maxargs=1)
        hdtv.cmdline.AddCommand("root ll", self.RootLL, maxargs=1, level=0)
        hdtv.cmdline.AddCommand("root pwd", self.RootPwd, nargs=0)
        hdtv.cmdline.AddCommand("root browse", self.RootBrowse, nargs=0)
        hdtv.cmdline.AddCommand("root open", self.RootOpen, nargs=1, fileargs=True)
        hdtv.cmdline.AddCommand("root close", self.RootClose, nargs=0)
        hdtv.cmdline.AddCommand(
            "root cd",
            self.RootCd,
            nargs=1,
            completer=hdtv.rfile_utils.RootCdCompleter(),
        )

        prog = "root get"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            "-r",
            "--replace",
            action="store_true",
            default=False,
            help="replace existing histogram list",
        )
        parser.add_argument(
            "-c",
            "--load-cal",
            action="store_true",
            default=False,
            help="load calibration from calibration dictionary",
        )
        parser.add_argument(
            "-v",
            "--invisible",
            action="store_true",
            default=False,
            help="do not make histograms visible, only add to display list",
        )
        parser.add_argument("pattern", nargs="+")
        hdtv.cmdline.AddCommand(
            "root get",
            self.RootGet,
            completer=hdtv.rfile_utils.RootCompleter(),
            parser=parser,
        )

        # FIXME: make use of matrix ID possible for already loaded matrix
        prog = "root matrix view"
        description = "show a 2D view of the matrix"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument("matname", nargs="+")
        hdtv.cmdline.AddCommand(
            prog,
            self.RootMatrixView,
            completer=hdtv.rfile_utils.RootCompleter(),
            parser=parser,
        )

        prog = "root matrix get"
        description = "load a matrix, i.e. the projections, from a ROOT file.\n"
        description += "If the matrix is symmetric it only loads one projection.\n"
        description += "If it is asymmetric both projections will be loaded."
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
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
            prog,
            self.RootMatrixGet,
            completer=hdtv.rfile_utils.RootCompleter(),
            parser=parser,
        )

        prog = "root cut view"
        description = "load a cut (TCutG) from a ROOT file and display it"
        description += "overlaid on the current matrix view"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-i",
            "--invert-axes",
            action="store_true",
            default=False,
            help="Exchange coordinate axes of cut (x <-> y)",
        )
        parser.add_argument("path", nargs="+", help="path of root cut")
        hdtv.cmdline.AddCommand(
            prog,
            self.RootCutView,
            completer=hdtv.rfile_utils.RootCompleter(),
            parser=parser,
        )

        prog = "root cut delete"
        description = "delete all cuts currently shown"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        hdtv.cmdline.AddCommand(prog, self.RootCutDelete, parser=parser)

        hdtv.cmdline.RegisterInteractive("gRootFile", self.rootfile)

    def RootBrowse(self, args):
        self.browser = ROOT.TBrowser()
        if self.rootfile is not None and not self.rootfile.IsZombie():
            self.rootfile.Browse(self.browser)

    def RootLs(self, args):
        keys = ROOT.gDirectory.GetListOfKeys()
        if not keys:
            return

        names = [k.GetName() for k in keys]

        if len(args) > 0:
            names = fnmatch.filter(names, args[0])

        names.sort()
        hdtv.tabformat.tabformat(names)

    def RootLL(self, args):
        if len(args) == 0:
            ROOT.gDirectory.ls()
        else:
            ROOT.gDirectory.ls(args[0])

    def RootCd(self, args):
        try:
            target = args[0]
        except IndexError:
            target = ""
        if self.rootfile:
            cur_root_dir = ROOT.gDirectory
        else:
            cur_root_dir = None

        (posix_path, rfile, root_dir) = hdtv.rfile_utils.GetRelDirectory(
            os.getcwd(), cur_root_dir, target
        )
        if (posix_path, rfile, root_dir) == (None, None, None):
            hdtv.ui.error("Invalid path specified.")
            return

        os.environ["OLDPWD"] = os.getcwd()
        os.chdir(posix_path)

        # If root_dir is None, we moved outside the ROOT file and are now in
        # a POSIX directory. If rfile is not None, we *changed* the ROOT file.
        if root_dir is None or rfile is not None:
            if self.rootfile is not None:
                hdtv.ui.info("Closing old root file %s" % self.rootfile.GetName())
                self.rootfile.Close()
            self.rootfile = rfile
            if self.rootfile is not None:
                hdtv.ui.info("Opened new root file %s" % self.rootfile.GetName())

        if root_dir is not None:
            root_dir.cd()

    def RootPwd(self, args):
        if self.rootfile is not None:
            ROOT.gDirectory.pwd()
        else:
            hdtv.ui.msg(os.getcwd())

    def RootOpen(self, args):
        return self.RootCd(args)

    def RootClose(self, args):
        if self.rootfile is None:
            hdtv.ui.info("No root file open, no action taken")
        else:
            self.rootfile.Close()
            self.rootfile = None

    def GetObj(self, path):
        """
        Load an object from a ROOT file
        """

        dirs = path.rsplit("/", 1)
        if len(dirs) == 1:
            # Load object from current directory
            obj = ROOT.gDirectory.Get(dirs[0])
        else:
            if self.rootfile:
                cur_root_dir = ROOT.gDirectory
            else:
                cur_root_dir = None

            (posix_path, rfile, root_dir) = hdtv.rfile_utils.GetRelDirectory(
                os.getcwd(), cur_root_dir, dirs[0]
            )

            if root_dir:
                obj = root_dir.Get(dirs[1])
            else:
                obj = None

            if rfile:
                rfile.Close()

        return obj

    def GetCut(self, path):
        """
        Load a cut (TCutG) from a ROOT file.
        """
        cut = self.GetObj(path)

        if cut is None or not isinstance(cut, ROOT.TCutG):
            hdtv.ui.error("%s is not a ROOT cut (TCutG)" % path)
            return None

        return cut

    def GetTH2(self, path):
        """
        Load a 2D histogram (``matrix'') from a ROOT file. This can be either
        a ``true'' TH2 histogram or a THnSparse of dimension 2.

        Note: Unlike RootGet(), this function does not support shell-style
        pattern expansion, as this make it too easy to undeliberately load
        too many histograms. As they use a lot of memory, this would likely
        lead to a crash of the program.
        """
        hist = self.GetObj(path)

        if hist is None or not (
            isinstance(hist, ROOT.TH2)
            or (isinstance(hist, ROOT.THnSparse) and hist.GetNdimensions() == 2)
        ):
            hdtv.ui.error("%s is not a 2d histogram" % path)
            return None

        return hist

    def RootCutView(self, args):
        """
        Load a ROOT cut (TCutG) from a ROOT file and display it.
        """
        if len(self.matviews) == 0:
            raise hdtv.cmdline.HDTVCommandError(
                "Cannot display cut: no matrix view open"
            )
        for path in args.path:
            cut = self.GetCut(path)
            if cut:
                self.matviews[-1].AddCut(cut, args.invert_axes)

    def RootCutDelete(self, args):
        """
        Delete all cuts shown in the current matrix view.
        """
        if len(self.matviews) == 0:
            raise hdtv.cmdline.HDTVCommandError("No matrix view open")
        self.matviews[-1].DeleteAllCuts()

    def RootMatrixView(self, args):
        """
        Load a 2D histogram (``matrix'') from a ROOT file and display it.
        """
        for path in args.matname:
            hist = self.GetTH2(path)
            if hist:
                title = hist.GetTitle()
                viewer = ROOT.HDTV.Display.MTViewer(400, 400, hist, title)
                self.matviews.append(viewer)

    def RootMatrixGet(self, args):
        """
        Load a 2D histogram (``matrix'') from a ROOT file in projection mode.
        """
        # FIXME: Copy and paste from matInterface.py -> unify?
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
        rhist = self.GetTH2(args.filename)
        if rhist is None:
            raise hdtv.cmdline.HDTVCommandError("Failed to open 2D histogram")

        if isinstance(rhist, ROOT.TH2):
            hist = RHisto2D(rhist)
        elif isinstance(rhist, ROOT.THnSparse):
            hist = RHisto2D(THnSparseWrapper(rhist))
        else:
            raise RuntimeError

        matrix = Matrix(hist, sym, self.spectra.viewport)
        ID = self.spectra.GetFreeID()
        matrix.ID = ID
        matrix.color = hdtv.color.ColorForID(ID.major)
        # load x projection
        proj = matrix.xproj
        sid = self.spectra.Insert(proj, ID=hdtv.util.ID(ID.major, 0))
        self.spectra.ActivateObject(sid)
        # for asym matrix load also y projection
        if sym is False:
            proj = matrix.yproj
            self.spectra.Insert(proj, ID=hdtv.util.ID(ID.major, 1))

    def RootGet(self, args):
        """
        Load spectra from Rootfile
        """
        if self.rootfile:
            cur_root_dir = ROOT.gDirectory
        else:
            cur_root_dir = None

        objs = []
        for pat in args.pattern:
            objs += hdtv.rfile_utils.Get(".", cur_root_dir, pat)

        if args.replace:
            self.spectra.Clear()

        loaded = []
        if self.window.viewport:
            self.window.viewport.LockUpdate()
        try:  # We should really use a context manager here...
            for obj in objs:
                if isinstance(obj, ROOT.TH1):
                    spec = Spectrum(Histogram(obj))
                    sid = self.spectra.Insert(spec)
                    spec.color = hdtv.color.ColorForID(sid.major)
                    loaded.append(sid)
                    if spec.cal:
                        self.caldict[spec.name] = spec.cal
                    else:
                        if args.load_cal:
                            try:
                                spec.cal = self.caldict[spec.name]
                            except KeyError:
                                hdtv.ui.warning(
                                    "No calibration found for %s" % spec.name
                                )
                else:
                    hdtv.ui.warning("%s is not a 1D histogram object" % obj.GetName())
            hdtv.ui.msg("%d spectra loaded" % len(loaded))
            if args.invisible:
                self.spectra.HideObjects(loaded)
            elif len(loaded) > 0:
                # activate last loaded spectrum
                self.spectra.ActivateObject(loaded[-1])
            # Expand window if it is the only spectrum
            if len(self.spectra) == 1:
                self.window.Expand()
        finally:
            if self.window.viewport:
                self.window.viewport.UnlockUpdate()


# plugin initialisation
import __main__

r = RootFileInterface(__main__.spectra)
