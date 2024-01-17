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

from html import escape

import ROOT

import hdtv.cmdline
import hdtv.fit
import hdtv.options
import hdtv.ui
import hdtv.util


class FitInterface:
    """
    User interface for fitting 1-d spectra
    """

    def __init__(self, spectra):
        hdtv.ui.debug("Loaded user interface for fitting of 1-d spectra")

        self.spectra = spectra
        self.window = self.spectra.window

        # tv commands
        self.tv = TvFitInterface(self)

        # Register configuration variables for fit interface
        # default region width for quickfit

        self.opt = {}
        self.opt["quickfit.region"] = hdtv.options.Option(
            default=20.0, parse=lambda x: float(x)
        )
        hdtv.options.RegisterOption("fit.quickfit.region", self.opt["quickfit.region"])

        self.opt["display.decomp"] = hdtv.options.Option(
            default=False,
            parse=hdtv.options.parse_bool,
            changeCallback=lambda x: self.SetDecomposition(x),
        )
        hdtv.options.RegisterOption("fit.display.decomp", self.opt["display.decomp"])

        self.opt["list.show_pos_lit_residuals"] = hdtv.options.Option(
            default=False, parse=hdtv.options.parse_bool
        )
        hdtv.options.RegisterOption(
            "fit.list.show_pos_lit_residuals", self.opt["list.show_pos_lit_residuals"]
        )

        if self.window:
            self._register_hotkeys()

    def _register_hotkeys(self):
        self.window.AddHotkey(ROOT.kKey_b, lambda: self.spectra.SetMarker("bg"))
        self.window.AddHotkey(
            [ROOT.kKey_Minus, ROOT.kKey_b], lambda: self.spectra.RemoveMarker("bg")
        )
        self.window.AddHotkey(ROOT.kKey_r, lambda: self.spectra.SetMarker("region"))
        self.window.AddHotkey(
            [ROOT.kKey_Minus, ROOT.kKey_r], lambda: self.spectra.RemoveMarker("region")
        )
        self.window.AddHotkey(ROOT.kKey_p, lambda: self.spectra.SetMarker("peak"))
        self.window.AddHotkey(
            [ROOT.kKey_Minus, ROOT.kKey_p], lambda: self.spectra.RemoveMarker("peak")
        )
        self.window.AddHotkey(ROOT.kKey_B, lambda: self.spectra.ExecuteFit(peaks=False))
        self.window.AddHotkey(ROOT.kKey_F, lambda: self.spectra.ExecuteFit(peaks=True))
        self.window.AddHotkey(
            [ROOT.kKey_Minus, ROOT.kKey_B], lambda: self.spectra.ClearFit(bg_only=True)
        )
        self.window.AddHotkey(
            [ROOT.kKey_Minus, ROOT.kKey_F], lambda: self.spectra.ClearFit(bg_only=False)
        )
        self.window.AddHotkey(ROOT.kKey_Q, self.QuickFit)
        self.window.AddHotkey([ROOT.kKey_Plus, ROOT.kKey_F], self.spectra.StoreFit)
        self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_F], self.spectra.ClearFit)
        self.window.AddHotkey(ROOT.kKey_D, lambda: self.ShowDecomposition(True))
        self.window.AddHotkey(
            [ROOT.kKey_Minus, ROOT.kKey_D], lambda: self.ShowDecomposition(False)
        )
        self.window.AddHotkey(
            [ROOT.kKey_f, ROOT.kKey_s],
            lambda: self.window.EnterEditMode(
                prompt="Show Fit: ", handler=self._HotkeyShow
            ),
        )
        self.window.AddHotkey(
            [ROOT.kKey_f, ROOT.kKey_a],
            lambda: self.window.EnterEditMode(
                prompt="Activate Fit: ", handler=self._HotkeyActivate
            ),
        )
        self.window.AddHotkey(
            [ROOT.kKey_f, ROOT.kKey_p], lambda: self._HotkeyShow("PREV")
        )
        self.window.AddHotkey(
            [ROOT.kKey_f, ROOT.kKey_n], lambda: self._HotkeyShow("NEXT")
        )
        self.window.AddHotkey(ROOT.kKey_I, self.spectra.ExecuteIntegral)

    def _HotkeyShow(self, args):
        """
        Show wrapper for use with a Hotkey (internal use)
        """
        spec = self.spectra.GetActiveObject()
        if spec is None:
            self.window.viewport.SetStatusText("No active spectrum")
            return
        try:
            ids = hdtv.util.ID.ParseIds(args, spec)
        except ValueError:
            self.window.viewport.SetStatusText("Invalid fit identifier: %s" % args)
            return
        spec.ShowObjects(ids)

    def _HotkeyActivate(self, args):
        """
        ActivateObject wrapper for use with a Hotkey (internal use)
        """
        spec = self.spectra.GetActiveObject()
        if spec is None:
            self.window.viewport.SetStatusText("No active spectrum")
            return
        try:
            ids = hdtv.util.ID.ParseIds(args, spec)
        except ValueError:
            self.window.viewport.SetStatusText("Invalid fit identifier: %s" % args)
            return
        if len(ids) == 1:
            self.window.viewport.SetStatusText("Activating fit %s" % ids[0])
            self.spectra.ActivateFit(ids[0])
        elif not ids:
            self.window.viewport.SetStatusText("Deactivating fit")
            self.spectra.ActivateFit(None)
        else:
            self.window.viewport.SetStatusText("Can only activate one fit")

    def ExecuteRefit(self, specID, fitID, peaks=True):
        """
        Re-Execute Fit on store fits
        """
        try:
            spec = self.spectra.dict[specID]
        except KeyError:
            raise KeyError("invalid spectrum ID")
        try:
            fit = spec.dict[fitID]
        except KeyError:
            raise KeyError("invalid fit ID")
        if peaks:
            fit.FitPeakFunc(spec)
        else:
            if fit.fitter.backgroundModel.fParStatus["nparams"] == -1:
                raise RuntimeError("background degree of -1")
            fit.FitBgFunc(spec)
        hdtv.ui.msg(html=str(fit))
        fit.Draw(self.window.viewport)

    def ExecuteReintegrate(self, specID, fitID, print_result=True):
        """
        Re-Execute Fit on store fits
        """
        print("Reintegrating")
        try:
            spec = self.spectra.dict[specID]
        except KeyError:
            raise KeyError("invalid spectrum ID")
        try:
            fit = spec.dict[fitID]
        except KeyError:
            raise KeyError("invalid fit ID")
        if not fit.regionMarkers.IsFull():
            raise hdtv.cmdline.HDTVCommandAbort("Region not set.")
            return

        if fit.bgMarkers:
            if fit.fitter.backgroundModel.fParStatus["nparams"] == -1:
                raise hdtv.cmdline.HDTVCommandAbort(
                    "Background degree of -1 contradicts background fit."
                )
                return
            # pure background fit
            fit.FitBgFunc(spec)

        region = [fit.regionMarkers[0].p1.pos_uncal, fit.regionMarkers[0].p2.pos_uncal]
        bg = fit.fitter.bgFitter

        fit.integral = hdtv.integral.Integrate(spec, bg, region)
        if print_result:
            hdtv.ui.msg(html=fit.print_integral())
        fit.Draw(self.window.viewport)
        print("Successfully reintegrated")

    def QuickFit(self, pos=None):
        """
        Set region and peak markers automatically and do a quick fit as position "pos".

        If pos is not given, use cursor position
        """
        if pos is None:
            pos = self.window.viewport.GetCursorX()
        self.spectra.ClearFit()
        region_width = hdtv.options.Get("fit.quickfit.region")
        self.spectra.SetMarker("region", pos - region_width / 2.0)
        self.spectra.SetMarker("region", pos + region_width / 2.0)
        self.spectra.SetMarker("peak", pos)
        self.spectra.ExecuteFit()

    def ListFits(self, sid=None, ids=None, sortBy=None, reverseSort=False):
        """
        List results of stored fits as nice table
        """
        if sid is None:
            sid = self.spectra.activeID
        spec = self.spectra.dict[sid]
        # if there are not fits for this spectrum, there is not much to do
        if not spec.ids:
            hdtv.ui.msg("Spectrum " + str(sid) + " (" + spec.name + "): No fits")
            return
        # create result header
        result_header = "Fits in Spectrum " + str(sid) + " (" + spec.name + ")" + "\n"
        if ids is None:
            ids = spec.ids
        fits = [spec.dict[ID] for ID in ids]
        count_fits = len(fits)
        (objects, params) = self.ExtractFits(fits)

        # create result footer
        result_footer = (
            "\n" + str(len(objects)) + " peaks in " + str(count_fits) + " fits."
        )
        # create the table
        try:
            table = hdtv.util.Table(
                objects,
                params,
                sortBy=sortBy,
                reverseSort=reverseSort,
                extra_header=result_header,
                extra_footer=result_footer,
            )
            hdtv.ui.msg(html=str(table), end="")
        except KeyError as e:
            raise hdtv.cmdline.HDTVCommandError(
                "Spectrum " + str(sid) + ": No such attribute: " + str(e) + "\n"
                "Spectrum " + str(sid) + ": Valid attributes are: " + str(params)
            )

    def ListIntegrals(
        self, sid=None, ids=None, sortBy=None, reverseSort=False, integral_type="auto"
    ):
        """
        List integrals of fit regions as nice table
        """
        if sid is None:
            sid = self.spectra.activeID
        spec = self.spectra.dict[sid]
        # if there are not fits for this spectrum, there is not much to do
        if not spec.ids:
            hdtv.ui.msg("Spectrum " + str(sid) + " (" + spec.name + "): No fits")
            return
        # create result header
        result_header = (
            "Integrals of fit regions in Spectrum "
            + str(sid)
            + " ("
            + spec.name
            + ")"
            + "\n"
        )
        if ids is None:
            ids = spec.ids
        fits = [spec.dict[ID] for ID in ids]
        (objects, params) = self.ExtractIntegrals(fits, integral_type)

        # create the table
        try:
            table = hdtv.util.Table(
                objects,
                params,
                sortBy=sortBy,
                reverseSort=reverseSort,
                extra_header=result_header,
            )
            hdtv.ui.msg(html=str(table), end="")
        except KeyError as e:
            raise hdtv.cmdline.HDTVCommandError(
                "Spectrum " + str(sid) + ": No such attribute: " + str(e) + "\n"
                "Spectrum " + str(sid) + ": Valid attributes are: " + str(params)
            )

    def PrintWorkFit(self):
        """
        Print results of workFit as nice table
        """
        fit = self.spectra.workFit
        if fit.spec is not None:
            hdtv.ui.msg(html=str(fit))

    def PrintWorkFitIntegral(self):
        """
        Print integral of workFit range as nice table
        """
        # TODO
        fit = self.spectra.workFit
        if fit.spec is not None:
            hdtv.ui.msg(html=fit.print_integral())

    def ExtractFits(self, fits):
        """
        Helper function for use with ListFits and PrintWorkFit functions.

        Return values:
            fitlist    : a list of dicts for each peak in the fits
            params     : a ordered list of valid parameter names
        """
        fitlist = []
        params = []
        # loop through fits
        for fit in fits:
            # Get peaks
            (peaklist, fitparams) = fit.ExtractParams()
            if not peaklist:
                # If fit does not contain any peaks, fake an
                # entry to show that the fit ID is taken
                fakeID = hdtv.util.ID(fit.ID.major)
                # HACK: ID.minor is not allowed to contain strings,
                # but it will never be compared anyway and e.g. "0.-"
                # is nicer than just "0" in the table
                fakeID.minor = "-"
                fakeStat = "I"  # no peaks -> basically an integral only
                if fit.ID in fit.spec.visible:
                    fakeStat = fakeStat + "V"
                if fit.active:
                    fakeStat = "A" + fakeStat
                peaklist = [{"id": fakeID, "stat": fakeStat}]
                fitparams = ["id", "stat"]
            # update list of valid params
            for p in fitparams:
                # do not use set operations here to keep order of params
                if p not in params:
                    params.append(p)
                    if self.opt["list.show_pos_lit_residuals"].Get() and p == "pos_lit":
                        params.append("Δpos_lit")
            # add peaks to the list
            if self.opt["list.show_pos_lit_residuals"].Get() and "Δpos_lit" in params:
                for peak in peaklist:
                    if "pos_lit" in peak:
                        peak["Δpos_lit"] = peak["pos_lit"] - peak["pos"]
            fitlist.extend(peaklist)
        return (fitlist, params)

    def ExtractIntegrals(self, fits, integral_type="auto"):
        """
        Helper function for functions ListIntegrals, PrintWorkFitIntegral.

        Return values:
            integrallist : a list of dicts for each integral in the fits
            params       : a ordered list of valid parameter names
        """
        integrallist = []
        params = []
        # loop through fits
        for fit in fits:
            (integrals, integralparams) = fit.ExtractIntegralParams(integral_type)

            # update list of valid params
            for p in integralparams:
                # do not use set operations here to keep order of params
                if p not in params:
                    params.append(p)
            # add peaks to the list
            integrallist.extend(integrals)
        return (integrallist, params)

    def ShowFitterStatus(self, ids=None):
        """
        Show status of the fit parameters of the work Fit.

        If default is true, the status of the default Fitter is shown in addition.
        If a list of ids is given, the status of the fitters belonging to that
        fits is also shown. Note, that the latter will silently fail for invalid
        IDs.
        """
        if ids is None:
            ids = []
        ids.extend("a")
        statstr = ""
        for ID in ids:
            if ID == "a":
                fitter = self.spectra.workFit.fitter
                statstr += "active fitter: \n"
            else:
                spec = self.spectra.GetActiveObject()
                if spec is None:
                    continue
                fitter = spec.dict[ID].fitter
                statstr += "fitter status of fit id %d: \n" % ID
            if fitter.backgroundModel.name == "polynomial":
                statstr += "<b>Background model:</b> %s" % escape(
                    fitter.backgroundModel.name
                )
                statstr += ", deg=%i" % fitter.backgroundModel.fParStatus["nparams"]
                statstr += "\n"
            else:
                statstr += "<b>Background model:</b> %s\n" % escape(
                    fitter.backgroundModel.name
                )
            statstr += "<b>Peak model:</b> %s\n" % fitter.peakModel.name
            statstr += fitter.OptionsStr()
        hdtv.ui.msg(html=statstr)

    def SetFitterParameter(self, parname, status, ids=None):
        """
        Sets status of fitter parameter

        If not specified otherwise only the fitter of the workFit will be changed.
        If a list of fits is given, we try to set the parameter status also
        for these fits. Be aware that failures for the fits from the list will
        be silently ignored.
        """
        # active fit
        fit = self.spectra.workFit
        status = status.split(",")  # Create list from multiple stati
        if len(status) == 1:
            # Only single status was given so SetParameter need single string
            status = status[0]
        try:
            fit.fitter.SetParameter(parname, status)
            fit.Refresh()
        except ValueError as msg:
            raise hdtv.cmdline.HDTVCommandError(
                "while editing active Fit: \n\t%s" % msg
            )
        # fit list
        if not ids:  # works for None and empty list
            return
        spec = self.spectra.GetActiveObject()
        if spec is None:
            hdtv.ui.warning("No active spectrum")
        try:
            iter(ids)
        except TypeError:
            ids = [ids]
        for ID in ids:
            try:
                fit = spec.dict[ID]
                fit.fitter.SetParameter(parname, status)
                fit.Refresh()
            except KeyError:
                pass

    def ResetFitterParameters(self, ids=None):
        """
        Reset Status of Fitter

        The fitter of the workFit is resetted to the internal default values .
        If a list with ids is given, they are treated in the same way as the workFit.
        """
        # active Fit
        fit = self.spectra.workFit
        fit.fitter.ResetParamStatus()
        fit.Refresh()
        # fit list
        if not ids:  # works for None and empty list
            return
        spec = self.spectra.GetActiveObject()
        if spec is None:
            hdtv.ui.warning("No active spectrum")
        try:
            iter(ids)
        except TypeError:
            ids = [ids]
        for ID in ids:
            fit = spec.dict[ID]
            fit.fitter.ResetParamStatus()
            fit.Refresh()

    def SetPeakModel(self, peakmodel, ids=None):
        """
        Set the peak model (function used for fitting peaks)

        If a list of ids is given, the peak model of the stored fits with that
        ids will be set. Note, that the latter will fail silently for invalid
        fit ids.
        """
        # active fit
        fit = self.spectra.workFit
        fit.fitter.SetPeakModel(peakmodel)
        fit.Refresh()
        # fit list
        if not ids:  # works for None and empty list
            return
        spec = self.spectra.GetActiveObject()
        if spec is None:
            hdtv.ui.warning("No active spectrum")
        try:
            iter(ids)
        except TypeError:
            ids = [ids]
        for ID in ids:
            fit = spec.dict[ID]
            fit.fitter.SetPeakModel(peakmodel)
            fit.Refresh()

    def SetBackgroundModel(self, backgroundModel, ids=None):
        """
        Set the background model (function used for fitting the quasi-continuous background)

        If a list of ids is given, the peak model of the stored fits with that
        ids will be set. Note, that the latter will fail silently for invalid
        fit ids.
        """
        # active fit
        fit = self.spectra.workFit
        fit.fitter.SetBackgroundModel(backgroundModel)
        fit.Refresh()
        # fit list
        if not ids:  # works for None and empty list
            return
        spec = self.spectra.GetActiveObject()
        if spec is None:
            hdtv.ui.warning("No active spectrum")
        try:
            iter(ids)
        except TypeError:
            ids = [ids]
        for ID in ids:
            fit = spec.dict[ID]
            fit.fitter.SetBackgroundModel(backgroundModel)
            fit.Refresh()

    def SetDecomposition(self, default_enable):
        """
        Set default decomposition display status
        """
        # default_enable may be an hdtv.options.opt instance, so we
        # excplicitely convert to bool here
        default_enable = bool(default_enable)
        hdtv.fit.Fit.showDecomp = default_enable
        # show these decompositions for workFit
        self.ShowDecomposition(default_enable)
        # show these decompositions for all other fits
        for specID in self.spectra.ids:
            fitIDs = self.spectra.dict[specID].ids
            self.ShowDecomposition(default_enable, sid=specID, ids=fitIDs)

    def ShowDecomposition(self, enable, sid=None, ids=None):
        """
        Show decomposition of fits
        """

        fits = []
        if sid is None:
            spec = self.spectra.GetActiveObject()
        else:
            spec = self.spectra.dict[sid]

        fits = []
        if ids is None:
            if self.spectra.workFit is not None:
                fits.append(self.spectra.workFit)
        else:
            fits = [spec.dict[ID] for ID in ids]

        for fit in fits:
            fit.SetDecomp(enable)


class TvFitInterface:
    """
    TV style interface for fitting
    """

    def __init__(self, fitInterface):
        self.fitIf = fitInterface
        self.spectra = self.fitIf.spectra

        # Register configuration variables for fit list
        opt = hdtv.options.Option(default="id")
        hdtv.options.RegisterOption("fit.list.sort_key", opt)

        prog = "fit execute"
        description = "(re)fit a fit"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default="active",
            help="Spectra to work on",
        )
        parser.add_argument(
            "-b",
            "--background",
            action="store_true",
            default=False,
            help="fit only the background",
        )
        parser.add_argument(
            "-q",
            "--quick",
            action="store",
            default=None,
            type=float,
            help="set position for doing a quick fit",
        )
        parser.add_argument(
            "-S",
            "--store",
            action="store_true",
            default=False,
            help="store fit after fitting",
        )
        parser.add_argument(
            "fitids",
            nargs="*",
            default=None,
            help="id(s) of the fit(s) to (re)fit. Use 'none' to execute the WorkFit (default)",
        )
        hdtv.cmdline.AddCommand(prog, self.FitExecute, level=0, parser=parser)
        # the "fit execute" command is registered with level=0,
        # this allows "fit execute" to be abbreviated as "fit",
        # register all other commands starting with fit with default or higher
        # priority

        prog = "fit integral execute"
        description = "integrate over the fit region"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default="active",
            help="Spectra to work on",
        )
        parser.add_argument(
            "-S",
            "--store",
            action="store_true",
            default=False,
            help="store integral (as fit without peaks) after integration",
        )
        parser.add_argument(
            "fitids",
            nargs="*",
            default=None,
            help="id(s) of the fit(s) to (re)integrate. Use 'none' to integrate the WorkFit (default)",
        )
        hdtv.cmdline.AddCommand(prog, self.FitIntegralExecute, parser=parser)

        prog = "fit marker"
        description = "set/delete a marker"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "type",
            # choices=['background', 'region', 'peak'], # no autocompletion
            help="type of marker to modify (background, region, peak)",
        )
        parser.add_argument(
            "action",
            # choices=['set', 'delete'], # no autocompletion
            help="set or delete marker",
        )
        parser.add_argument(
            "position", nargs="+", type=float, help="position of marker"
        )
        hdtv.cmdline.AddCommand(
            prog, self.FitMarkerChange, parser=parser, completer=self.MarkerCompleter
        )

        prog = "fit clear"
        description = "clear the active work fit"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-b",
            "--background_only",
            action="store_true",
            default=False,
            help="clear only background fit, refit peak fit with internal background",
        )
        hdtv.cmdline.AddCommand(prog, self.FitClear, parser=parser)

        prog = "fit store"
        description = "Store the current workFit"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "fitid", default=None, help="fitid to use for storage", nargs="?"
        )
        hdtv.cmdline.AddCommand(prog, self.FitStore, parser=parser)

        prog = "fit activate"
        description = "reactivates a fit from the fitlist"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "fitids",
            default=[],
            nargs="?",
            help="id of fit to reactivate. Use 'none' to activate the WorkFit, deactivating a fitlist fit, but keeping any fit markers (default)",
        )
        hdtv.cmdline.AddCommand(prog, self.FitActivate, parser=parser)

        prog = "fit delete"
        description = "delete fits"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default="active",
            help="spectrum ids to work on",
        )
        parser.add_argument(
            "fitids", default=None, help="id(s) of fit(s) to delete", nargs="+"
        )
        hdtv.cmdline.AddCommand(prog, self.FitDelete, parser=parser)

        prog = "fit show"
        description = "display fits"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default="active",
            help="select spectra to work on",
        )
        parser.add_argument(
            "-v",
            "--adjust-viewport",
            action="store_true",
            default=False,
            help="adjust viewport to include all fits",
        )
        parser.add_argument("fitids", default=None, help="id(s) of fit(s) to show")
        hdtv.cmdline.AddCommand(prog, self.FitShow, parser=parser)

        prog = "fit hide"
        description = "hide fits"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default="active",
            help="select spectra to work on",
        )
        parser.add_argument("fitids", default=None, help="id(s) of fit(s) to hide")
        hdtv.cmdline.AddCommand(prog, self.FitHide, parser=parser)

        prog = "fit show decomposition"
        description = "display decomposition of fits"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default="active",
            help="select spectra to work on",
        )
        parser.add_argument(
            "fitids",
            nargs="*",
            default=None,
            help="id(s) of fit(s) to show decomposition of. Use 'none' to show the decomposition of the WorkFit (default)",
        )
        hdtv.cmdline.AddCommand(prog, self.FitShowDecomp, parser=parser)

        prog = "fit hide decomposition"
        description = "display decomposition of fits"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default="active",
            help="select spectra to work on",
        )
        parser.add_argument(
            "fitids",
            nargs="*",
            default=None,
            help="id(s) of fit(s) to hide decomposition of. Use 'none' to hide the decomposition of the WorkFit (default)",
        )
        hdtv.cmdline.AddCommand(prog, self.FitHideDecomp, parser=parser)

        prog = "fit focus"
        description = "adjust viewport to include all fits with id(s)"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s", "--spectrum", action="store", default="active", help="select spectra"
        )
        parser.add_argument("fitid", default=None, help="id(s) of fit(s) focus on")
        hdtv.cmdline.AddCommand(prog, self.FitFocus, parser=parser)

        prog = "fit list"
        description = "list fit results"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-v",
            "--visible",
            action="store_true",
            default=False,
            help="only list visible fit",
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
            "-s",
            "--spectrum",
            action="store",
            default="active",
            help="select spectra to work on",
        )
        parser.add_argument(
            "-f",
            "--fit",
            action="store",
            default="all",
            help="specify which fits to list",
        )
        # FIXME: Why use a different syntax here? --fit vs fitids
        #       parser.add_argument(
        #           "fitids",
        #           default=None,
        #           help="id(s) of fit(s) to list",
        #           nargs='?')
        hdtv.cmdline.AddCommand(prog, self.FitList, parser=parser)

        prog = "fit integral list"
        description = "list integrals of fit ranges"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-v",
            "--visible",
            action="store_true",
            default=False,
            help="only list visible fit",
        )
        parser.add_argument(
            "-k",
            "--key-sort",
            action="store",
            default=hdtv.options.Get("fit.list.sort_key"),
            help="sort by key",
        )
        parser.add_argument(
            "-r",
            "--reverse-sort",
            action="store_true",
            default=False,
            help="reverse the sort",
        )
        parser.add_argument(
            "-i",
            "--integral-type",
            default="auto",
            help="Type of integral {auto,tot,bg,sub,all}. [Default=auto]",
        )
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default="active",
            help="select spectra to work on",
        )
        parser.add_argument(
            "-f",
            "--fit",
            action="store",
            default="all",
            help="specify which fits to list",
        )
        # FIXME: Why use a different syntax here? --fit vs fitids
        #       parser.add_argument(
        #           "fitids",
        #           default=None,
        #           help="id(s) of fit(s) to list",
        #           nargs='?')
        hdtv.cmdline.AddCommand(prog, self.FitIntegralList, parser=parser)

        prog = "fit parameter"
        description = "show status of fit parameter, reset or set parameter"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-f",
            "--fit",
            action="store",
            default=None,
            help="change parameter of selected fit and refit. 'none' refers to the WorkFit (default)",
        )
        parser.add_argument(
            "action", help="{status,reset,background,tl,vol,pos,sh,sw,tr,width}"
        )
        parser.add_argument(
            "value_peak",
            metavar="value",
            help="fixed value to use for the parameter or instruction how to fit it \
                (e.g. 'free', 'equal', 'hold', 'none',...). Comma separated values can \
                be used to set values for each peak marker individually.",
            nargs="*",
        )
        hdtv.cmdline.AddCommand(
            prog, self.FitParam, completer=self.ParamCompleter, parser=parser
        )

        prog = "fit function peak activate"
        description = "selects which peak model to use"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-f",
            "--fit",
            action="store",
            default=None,
            help="change selected fits and refit",
        )
        parser.add_argument("peakmodel", help="name of peak model")
        hdtv.cmdline.AddCommand(
            prog, self.FitSetPeakModel, completer=self.PeakModelCompleter, parser=parser
        )

        prog = "fit function background activate"
        description = "selects which background model to use"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-f",
            "--fit",
            action="store",
            default=None,
            help="change selected fits and refit",
        )
        parser.add_argument("backgroundmodel", help="name of background model")
        hdtv.cmdline.AddCommand(
            prog,
            self.FitSetBackgroundModel,
            completer=self.BackgroundModelCompleter,
            parser=parser,
        )

    def FitMarkerChange(self, args):
        """
        Set or delete a marker from command line
        """
        # first argument is marker type name
        mtype = args.type
        # complete markertype if needed
        mtype = self.MarkerCompleter(mtype)
        if len(mtype) == 0:
            raise hdtv.cmdline.HDTVCommandError(
                "Markertype %s is not valid" % args.type
            )
        # second argument is action
        action = self.MarkerCompleter(
            args.action,
            args=[
                args.action,
            ],
        )
        if len(action) == 0:
            raise hdtv.cmdline.HDTVCommandError("Invalid action: %s" % args.action)
        # replace "background" with "bg" which is internally used
        mtype = mtype[0].strip()
        if mtype == "background":
            mtype = "bg"
        action = action[0].strip()

        # parse position
        for pos in args.position:
            if action == "set":
                self.spectra.SetMarker(mtype, pos)
            elif action == "delete":
                self.spectra.RemoveMarker(mtype, pos)

    def MarkerCompleter(self, text, args=None):
        """
        Helper function for FitMarkerChange
        """
        if args is None or not args:
            mtypes = ["background", "region", "peak"]
            return hdtv.util.GetCompleteOptions(text, mtypes)
        elif len(args) == 1:
            actions = ["set", "delete"]
            return hdtv.util.GetCompleteOptions(text, actions)
        return []

    def FitExecute(self, args):
        """
        Execute a fit
        """
        specIDs = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        if len(specIDs) == 0:
            hdtv.ui.warning("No spectrum to work on")
            return
        if args.background:
            doPeaks = False
        else:
            doPeaks = True

        # Store active spec ID before activation of other spectra
        oldActiveID = self.spectra.activeID

        for specID in specIDs:
            self.spectra.ActivateObject(specID)
            fitIDs = hdtv.util.ID.ParseIds(args.fitids, self.spectra.dict[specID])
            if len(fitIDs) == 0:
                if args.quick is not None:
                    self.fitIf.QuickFit(args.quick)
                else:
                    self.spectra.ExecuteFit(peaks=doPeaks)

                # Needed when args.quick is set for multiple spectra, else fits will be lost
                if args.store is True:
                    self.spectra.StoreFit()  # Store current fit

            for fitID in fitIDs:
                try:
                    hdtv.ui.msg(f"Executing fit {fitID} in spectrum {specID}")
                    self.fitIf.ExecuteReintegrate(
                        specID=specID, fitID=fitID, print_result=False
                    )
                    self.fitIf.ExecuteRefit(specID=specID, fitID=fitID, peaks=doPeaks)
                except (KeyError, RuntimeError) as e:
                    hdtv.ui.warning(e)
                    continue

        if (
            oldActiveID is not None
        ):  # Reactivate spectrum that was active in the beginning
            self.spectra.ActivateObject(oldActiveID)
        return None

    def FitIntegralExecute(self, args):
        """
        Execute integral over fit region
        """
        specIDs = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        if not specIDs:
            hdtv.ui.warning("No spectrum to work on")
            return

        # Store active spec ID before activation of other spectra
        oldActiveID = self.spectra.activeID

        for specID in specIDs:
            self.spectra.ActivateObject(specID)
            fitIDs = hdtv.util.ID.ParseIds(args.fitids, self.spectra.dict[specID])
            if not fitIDs:
                self.spectra.ExecuteIntegral()

                if (
                    args.store is True
                ):  # Needed when args.quick is set for multiple spectra, else fits will be lost
                    self.spectra.StoreFit()  # Store current fit

            for fitID in fitIDs:
                try:
                    hdtv.ui.msg(
                        f"Executing integral for region of fit {fitID} in spectrum {specID}"
                    )
                    self.fitIf.ExecuteReintegrate(specID=specID, fitID=fitID)
                except (KeyError, RuntimeError) as e:
                    hdtv.ui.warning(e)
                    continue

        if (
            oldActiveID is not None
        ):  # Reactivate spectrum that was active in the beginning
            self.spectra.ActivateObject(oldActiveID)
        return None

    def FitClear(self, args):
        """
        Clear work fit
        """
        self.spectra.ClearFit(args.background_only)

    def FitStore(self, args):
        """
        Store work fit
        """
        try:
            self.spectra.StoreFit(args.fitid)
        except IndexError:
            return

    def FitActivate(self, args):
        """
        Activate a fit

        This marks a stored fit as active and copies its markers to the work Fit
        """
        sid = self.spectra.activeID
        if sid is None:
            hdtv.ui.warning("No active spectrum")
            return
        spec = self.spectra.dict[sid]
        ids = hdtv.util.ID.ParseIds(args.fitids, spec)
        if len(ids) == 1:
            hdtv.ui.msg("Activating fit %s" % ids[0])
            self.spectra.ActivateFit(ids[0], sid)
        elif not ids:
            hdtv.ui.msg("Deactivating fit")
            self.spectra.ActivateFit(None, sid)
        else:
            raise hdtv.cmdline.HDTVCommandError("Can only activate one fit")

    def FitDelete(self, args):
        """
        Delete fits
        """
        sids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        if not sids:
            hdtv.ui.warning("No spectra chosen or active")
            return
        else:
            for s in sids:
                spec = self.spectra.dict[s]
                fitids = hdtv.util.ID.ParseIds(args.fitids, spec, only_existent=False)
                already_removed = set()
                for fitid in fitids:
                    # only whole fits can be removed not single peaks
                    if fitid.minor is not None:
                        if fitid.major in already_removed:
                            continue
                        else:
                            msg = "It is not possible to remove single peaks, "
                            msg += (
                                "removing whole fit with id %s instead." % fitid.major
                            )
                            hdtv.ui.warning(msg)
                            fitid.minor = None
                            already_removed.add(fitid.major)
                    # do the work
                    spec.Pop(fitid)

    def FitHide(self, args):
        """
        Hide Fits
        """
        # FitHide is the same as FitShow, except that the spectrum selection is
        # inverted
        self.FitShow(args, inverse=True)

    def FitShow(self, args, inverse=False):
        """
        Show Fits

        inverse = True inverses the fit selection i.e. FitShow becomes FitHide
        """
        sids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        for sid in sids:
            spec = self.spectra.dict[sid]
            fitids = hdtv.util.ID.ParseIds(args.fitids, spec)
            if inverse:
                spec.HideObjects(fitids)
            else:
                spec.ShowObjects(fitids)
                if args.adjust_viewport:
                    fits = [spec.dict[fitid] for fitid in fitids]
                    self.spectra.window.FocusObjects(fits)

    def FitHideDecomp(self, args):
        """
        Hide decomposition of fits
        """
        self.FitShowDecomp(args, show=False)

    def FitShowDecomp(self, args, show=True):
        """
        Show decomposition of fits

        show = False hides decomposition
        """
        sids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        for sid in sids:
            spec = self.spectra.dict[sid]
            fitIDs = hdtv.util.ID.ParseIds(args.fitids, spec)

            if not fitIDs:
                fitIDs = None
            self.fitIf.ShowDecomposition(show, sid=sid, ids=fitIDs)

    def FitFocus(self, args):
        """
        Focus a fit.

        If no fit is given focus the active fit.
        """
        sids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)

        fits = []
        if not args.fitid:
            fits.append(self.spectra.workFit)
            spec = self.spectra.GetActiveObject()
            activeFit = spec.GetActiveObject()
            if activeFit is not None:
                fits.append(activeFit)
        else:
            for sid in sids:
                spec = self.spectra.dict[sid]
                ids = hdtv.util.ID.ParseIds(args.fitid, spec)
                fits.extend([spec.dict[ID] for ID in ids])
                spec.ShowObjects(ids, clear=False)
                if not fits:
                    hdtv.ui.warning("Nothing to focus in spectrum %s" % sid)
                    return
        self.spectra.window.FocusObjects(fits)

    def FitList(self, args):
        """
        Show a nice table with the results of fits

        By default the result of the work fit is shown.
        """
        self.fitIf.PrintWorkFit()
        sids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        if not sids:
            hdtv.ui.warning("No spectra chosen or active")
            return
        # parse sort_key
        if args.key_sort is None:
            args.key_sort = hdtv.options.Get("fit.list.sort_key")
        key_sort = args.key_sort
        for sid in sids:
            spec = self.spectra.dict[sid]
            ids = hdtv.util.ID.ParseIds(args.fit, spec)
            if args.visible:
                ids = list(spec.visible)
            if not ids:
                continue
            self.fitIf.ListFits(
                sid, ids, sortBy=key_sort, reverseSort=args.reverse_sort
            )

    def FitIntegralList(self, args):
        """
        Show a nice table with the results of fits

        By default the result of the work fit is shown.
        """
        self.fitIf.PrintWorkFitIntegral()
        sids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        if not sids:
            hdtv.ui.warning("No spectra chosen or active")
            return
        # parse sort_key
        key_sort = args.key_sort
        for sid in sids:
            spec = self.spectra.dict[sid]
            ids = hdtv.util.ID.ParseIds(args.fit, spec)
            if args.visible:
                ids = list(spec.visible)
            if not ids:
                continue
            self.fitIf.ListIntegrals(
                sid,
                ids,
                sortBy=key_sort,
                reverseSort=args.reverse_sort,
                integral_type=args.integral_type,
            )

    def FitSetPeakModel(self, args):
        """
        Defines peak model to use for fitting
        """
        name = args.peakmodel.lower()
        # complete the model name if needed
        models = self.PeakModelCompleter(name)
        # check for unambiguity
        if len(models) > 1:
            raise hdtv.cmdline.HDTVCommandError(
                "Peak model name '%s' is ambiguous" % name
            )
        if not models:
            raise hdtv.cmdline.HDTVCommandError("Invalid peak model '%s'" % name)
        else:
            name = models[0].strip()
            ids = []
            if args.fit:
                spec = self.spectra.GetActiveObject()
                if spec is None:
                    hdtv.ui.warning("No active spectrum, no action taken.")
                    return
                ids = hdtv.util.ID.ParseIds(args.fit, spec)
            self.fitIf.SetPeakModel(name, ids)

    def FitSetBackgroundModel(self, args):
        """
        Defines background model to use for fitting
        """
        name = args.backgroundmodel.lower()
        # complete the model name if needed
        models = self.BackgroundModelCompleter(name)
        # check for unambiguity
        if len(models) > 1:
            raise hdtv.cmdline.HDTVCommandError(
                "Background model name '%s' is ambiguous" % name
            )
        if not models:
            raise hdtv.cmdline.HDTVCommandError("Invalid background model '%s'" % name)
        else:
            name = models[0].strip()
            ids = []
            if args.fit:
                spec = self.spectra.GetActiveObject()
                if spec is None:
                    hdtv.ui.warning("No active spectrum, no action taken.")
                    return
                ids = hdtv.util.ID.ParseIds(args.fit, spec)
            self.fitIf.SetBackgroundModel(name, ids)

    def PeakModelCompleter(self, text, args=None):
        """
        Helper function for FitSetPeakModel
        """
        return hdtv.util.GetCompleteOptions(
            text, iter(hdtv.peakmodels.PeakModels.keys())
        )

    def BackgroundModelCompleter(self, text, args=None):
        """
        Helper function for FitSetBackgroundModel
        """
        return hdtv.util.GetCompleteOptions(
            text, iter(hdtv.backgroundmodels.BackgroundModels.keys())
        )

    def FitParam(self, args):
        """
        Manipulate the status of fitter parameter
        """
        # first argument is parameter name
        param = args.action
        # complete the parameter name if needed
        parameter = self.ParamCompleter(param)
        # check for unambiguity
        if len(parameter) > 1:
            raise hdtv.cmdline.HDTVCommandError(
                "Parameter name %s is ambiguous" % param
            )
        if not parameter:
            raise hdtv.cmdline.HDTVCommandError(
                "Parameter name %s is not valid" % param
            )
        param = parameter[0].strip()
        ids = []
        if args.fit:
            spec = self.spectra.GetActiveObject()
            if spec is None:
                hdtv.ui.warning("No active spectrum, no action taken.")
                return
            ids = hdtv.util.ID.ParseIds(args.fit, spec)
        if param == "status":
            self.fitIf.ShowFitterStatus(ids)
        elif param == "reset":
            self.fitIf.ResetFitterParameters(ids)
        else:
            try:
                self.fitIf.SetFitterParameter(param, " ".join(args.value_peak), ids)
            except ValueError as msg:
                raise hdtv.cmdline.HDTVCommandError(msg)

    def ParamCompleter(self, text, args=None):
        """
        Creates a completer for all possible parameter names
        or valid states for a parameter (args[0]: parameter name).
        """
        if not args:  # args is None or [] -> complete parameter names
            params = ["status", "reset"]
            # create a list of all possible parameter names
            params.extend(self.spectra.workFit.fitter.params)
            return hdtv.util.GetCompleteOptions(text, params)
        else:  # args[0] = parameter name -> complete its possible values
            states = []
            param = args[0]
            if param in ["status", "reset", "background"]:
                return []  # No further args to autocomplete
            else:
                activePM = self.spectra.workFit.fitter.peakModel
                try:
                    if param in activePM.fValidParStatus:
                        valid_status = activePM.fValidParStatus[param]
                    else:
                        valid_status = activePM.fValidOptStatus[param]
                    states = [
                        str(s).lower()
                        for s in valid_status
                        if isinstance(s, (str, bool))
                    ]
                except KeyError:
                    # param is not a parameter of the peak model of active
                    # fitter
                    return []
                return hdtv.util.GetCompleteOptions(text, states)

    def ResetFit(self, args):
        """
        Reset fitter of a fit to unfitted default.
        """
        specIDs = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        if not specIDs:
            raise hdtv.cmdline.HDTVCommandError("No spectrum to work on")
        for specID in specIDs:
            fitIDs = hdtv.util.ID.ParseIds(args.fitids, self.spectra.dict[specID])
            if not fitIDs:
                hdtv.ui.warning("No fit for spectrum %d to work on" % specID)
                continue
            for fitID in fitIDs:
                self.fitIf.FitReset(
                    specID=specID, fitID=fitID, resetFitter=not args.keep_fitter
                )


# plugin initialisation

import __main__

fit_interface = FitInterface(__main__.spectra)
hdtv.cmdline.RegisterInteractive("f", fit_interface)
