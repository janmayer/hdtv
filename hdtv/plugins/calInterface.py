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
Functions for efficiency, energy calibration
"""

import argparse

from uncertainties import ufloat_fromstr

import hdtv.cal
import hdtv.cmdline
import hdtv.efficiency
import hdtv.options
import hdtv.ui
import hdtv.util

from . import EnergyCalibration


class EffCalIf:
    def __init__(self, spectra):
        self.spectra = spectra

        # tv commands
        self.tv = EffCalHDTVInterface(self)
        self.fit = False

    def SetFun(self, spectrumID, name, parameter=None):
        """
        Set efficiency function to use


        Allowed names:  * "wunder" for "Wunder"-Efficiency
                        * "wiedenhoever" for Wiedenhoever-Efficiency
                        * "poly" for polynomial efficiency
                        * "exp" for exponential efficiency
                        * "pow" for power function efficiency
        """
        if parameter is None:
            parameter = []

        try:
            name = name.lower()
            if name == "wunder":
                self.spectra.dict[spectrumID].effCal = hdtv.efficiency.WunderEff(
                    pars=parameter
                )
            elif name == "wiedenhoever":
                self.spectra.dict[spectrumID].effCal = hdtv.efficiency.WiedenhoeverEff(
                    pars=parameter
                )
            elif name == "poly":
                self.spectra.dict[spectrumID].effCal = hdtv.efficiency.PolyEff(
                    pars=parameter
                )
            elif name == "exp":
                self.spectra.dict[spectrumID].effCal = hdtv.efficiency.ExpEff(
                    pars=parameter
                )
            elif name == "pow":
                self.spectra.dict[spectrumID].effCal = hdtv.efficiency.PowEff(
                    pars=parameter
                )
            # elif name == "orthogonal": #to calibrate with Exp
            #    self.spectra.dict[spectrumID].effCal = hdtv.efficiency.ExpEff(pars=parameter)
            #    self.fit = True
            # elif name == "orthogonal_fit": #to fit with othogonal
            #    self.spectra.dict[spectrumID].effCal = hdtv.efficiency.OrthogonalEff(pars=parameter)
            #    self.fit = True
            else:
                raise hdtv.cmdline.HDTVCommandError(
                    "No such efficiency function %s" % name
                )
        except IndexError:
            raise hdtv.cmdline.HDTVCommandError("Invalid spectrum ID %d" % spectrumID)

    def SetPar(self, spectrumID, parameter):
        """
        Set parameter for efficiency function
        """
        try:
            self.spectra.dict[spectrumID].effCal.parameter = parameter
        except IndexError:
            raise hdtv.cmdline.HDTVCommandError("Invalid spectrum ID %d" % spectrumID)
        except AttributeError:
            raise hdtv.cmdline.HDTVCommandError(
                "No efficiency for spectrum ID %d set" % spectrumID
            )

    def Assign(self, todo):
        """
        Assign efficiency for fit
        """

    def ReadPar(self, spectrumID, filename):
        """
        Load efficiency parameter and covariance from file
        """
        try:
            self.spectra.dict[spectrumID].effCal.loadPar(filename)
        except IndexError:
            raise hdtv.cmdline.HDTVCommandError("Invalid spectrum ID %d" % spectrumID)
        except AttributeError:
            raise hdtv.cmdline.HDTVCommandError(
                "No efficiency for spectrum ID %d set" % spectrumID
            )

    def ReadCov(self, spectrumID, filename):
        """
        Load efficiency parameter and covariance from file
        """
        try:
            self.spectra.dict[spectrumID].effCal.loadCov(filename)
        except IndexError:
            raise hdtv.cmdline.HDTVCommandError("Invalid spectrum ID %d" % spectrumID)
        except AttributeError:
            raise hdtv.cmdline.HDTVCommandError(
                "No efficiency for spectrum ID %d set" % spectrumID
            )

    def WritePar(self, spectrumID, filename):
        """
        Save efficiency parameter
        """
        try:
            self.spectra.dict[spectrumID].effCal.savePar(filename)
        except IndexError:
            raise hdtv.cmdline.HDTVCommandError("Invalid spectrum ID %d" % spectrumID)
        except AttributeError:
            raise hdtv.cmdline.HDTVCommandError(
                "No efficiency for spectrum ID %d set" % spectrumID
            )

    def WriteCov(self, spectrumID, filename):
        """
        Save efficiency parameter
        """
        try:
            self.spectra.dict[spectrumID].effCal.saveCov(filename)
        except IndexError:
            raise hdtv.cmdline.HDTVCommandError("Invalid spectrum ID %d" % spectrumID)
        except AttributeError:
            raise hdtv.cmdline.HDTVCommandError(
                "No efficiency for spectrum ID %d set" % spectrumID
            )

    def List(self, ids=None):
        """
        List currently used efficiencies
        """
        if ids is None:
            ids = self.spectra.ids

        tabledata = []
        for ID in ids:
            tableline = {}
            tableline["ID"] = ID
            try:
                tableline["Name"] = self.spectra.dict[ID].effCal.name
                # TODO: Decent formatting
                tableline["Parameter"] = str(self.spectra.dict[ID].effCal.parameter)
            except AttributeError:
                tableline["Name"] = "-"
                tableline["Parameter"] = "-"
            tabledata.append(tableline)

        table = hdtv.util.Table(
            data=tabledata,
            keys=["ID", "Name", "Parameter"],
            sortBy="ID",
            ignoreEmptyCols=False,
        )
        hdtv.ui.msg(html=str(table))

    def Plot(self, spectrumID):
        """
        Plot efficiency
        """
        try:
            self.spectra.dict[spectrumID].effCal.TF1.Draw()
        except AttributeError:
            raise hdtv.cmdline.HDTVCommandError(
                "No efficiency for spectrum ID %d set" % spectrumID
            )

    def Fit(
        self,
        spectrumIDs,
        filename,
        nuclides,
        coefficients,
        sigma,
        show_graph=False,
        fit_panel=False,
        show_table=False,
        source=None,
    ):
        """
        Plot efficiency
        """

        for spectrumID in spectrumIDs:
            if not self.spectra.dict[spectrumID].effCal:
                raise hdtv.cmdline.HDTVCommandError(
                    "Efficiency function not set for spectrum %d, use calibration efficiency set"
                    % spectrumID
                )

        fitValues = hdtv.util.Pairs()
        tabledata = []

        if filename is not None:  # at the moment you can only fit from one file
            # TODO: maybe it makes more sense to write another method for this
            fitValues.fromFile(filename, sep=" ")  # TODO: separator
            hdtv.ui.msg(spectrumIDs)
            spectrumID = spectrumIDs[0]
        else:  # the spectrum has to be calibrated
            # try:
            if coefficients[0] is None:
                coefficients[0] = 1
                # raise hdtv.cmdline.HDTVCommandError("You have to give a coefficient for the first spectrum.")

            # the first spectrum/nuclide is used to calculate the factor of the
            # other ones
            spectrumID = spectrumIDs[0]
            nuclide = nuclides[0]
            coefficient = coefficients[0]

            matches = self.CalculateEff(spectrumID, nuclide, coefficient, source, sigma)

            # for table option values are saved
            for match in matches:
                tabledata.append(
                    {
                        "Peak": match["fit"].ExtractParams()[0][0]["pos"],
                        "Efficiency": match["efficiency"],
                        "ID": spectrumID,
                        "Nuclide": nuclide,
                        "Intensity": match["transition"]["intensity"],
                        "Vol": match["fit"].ExtractParams()[0][0]["vol"],
                    }
                )

            energies = [match["fit"].ExtractParams()[0][0]["pos"] for match in matches]
            efficiencies = [match["efficiency"] for match in matches]
            fitValues.fromLists(energies, efficiencies)

            # in the region [0;maxEnergy] the relative efficiency will be
            # corrected to the fit
            maxEnergy = energies[-1]

            if len(spectrumIDs) > 1:
                for j in range(1, len(spectrumIDs)):
                    # if the observed spectrum has no coefficient it has to be
                    # corrected
                    if coefficients[j] is None:
                        NewEff = self.EffCorrection(
                            spectrumIDs[0],
                            maxEnergy,
                            spectrumIDs[j],
                            fitValues,
                            nuclides[j],
                            source,
                            sigma,
                        )
                    # if it has its own coefficient only the efficiency has to
                    # be calculated
                    else:
                        NewEff = self.CalculateEff(
                            spectrumIDs[j], nuclides[j], coefficients[j], source, sigma
                        )

                    # all new efficiencies are added to the first ones
                    energies.extend(
                        [match["fit"].ExtractParams()[0][0]["pos"] for match in NewEff]
                    )
                    efficiencies.extend([match["efficiency"] for match in NewEff])
                    for match in NewEff:
                        tabledata.append(
                            {
                                "Peak": match["fit"].ExtractParams()[0][0]["pos"],
                                "Efficiency": match["efficiency"],
                                "ID": spectrumIDs[j],
                                "Nuclide": nuclides[j],
                                "Intensity": match["transition"]["intensity"],
                                "Vol": match["fit"].ExtractParams()[0][0]["vol"],
                            }
                        )

                    fitValues = hdtv.util.Pairs()

                fitValues.fromLists(energies, efficiencies)

        # Call function to do the fit
        if self.fit:
            self.SetFun(spectrumID, "orthogonal_fit")
            self.spectra.dict[spectrumID].effCal.fit(energies, efficiencies)
            # go back to the start condition
            self.SetFun(spectrumID, "orthogonal")
        else:
            try:
                self.spectra.dict[spectrumID].effCal.fit(fitValues, quiet=False)
            except AttributeError:
                raise hdtv.cmdline.HDTVCommandAbort(
                    "No efficiency for spectrum ID %d set", spectrumID
                )
            if show_graph:
                self.spectra.dict[spectrumID].effCal.TGraph.Draw("a*")
                self.spectra.dict[spectrumID].effCal.TF1.Draw("same")

            if fit_panel:
                self.spectra.dict[spectrumID].effCal.TGraph.FitPanel()

        # if table option is called a table will be created
        if show_table:
            table = hdtv.util.Table(
                data=tabledata,
                keys=["ID", "Nuclide", "Peak", "Efficiency", "Intensity", "Vol"],
                sortBy="ID",
                ignoreEmptyCols=False,
            )
            hdtv.ui.msg(html=str(table))

    def CalculateEff(self, spectrumID, nuclide, coefficient, source, sigma):
        """
        Calculates efficiency from a given spectrum and given nuclide.
        """
        fits = list(self.spectra.dict[hdtv.util.ID(spectrumID)].dict.values())
        data = EnergyCalibration.SearchNuclide(nuclide, source)

        # It matches the Peaks and the given energies
        matches = EnergyCalibration.MatchFitsAndTransitions(
            fits, data["transitions"], sigma=sigma
        )
        if not matches:
            raise hdtv.cmdline.HDTVCommandError(
                "There is no match between the fitted peaks and the energies of the nuclide."
            )

        # Calculate efficiency
        for match in matches:
            match["efficiency"] = match["fit"].ExtractParams()[0][0]["vol"] / (
                coefficient * match["transition"]["intensity"]
            )

        return matches

    def EffCorrection(
        self, referenceID, maxEnergy, spectrumID, fitValues, nuclide, source, sigma
    ):
        """
        If there is one spectrum given without coefficient, you have to correct
        it by calculation the missing factor that it fits to the other one.
        """

        # fit the efficiency of the reference spectrum
        self.spectra.dict[referenceID].effCal.fit(fitValues, False)

        # calculate efficiency values for peaks
        matches = self.CalculateEff(spectrumID, nuclide, 1, source, sigma)

        division = 0.0
        amountDivisionError = 0.0
        amountError = 0.0

        # calculates the factor of the nuclide
        # TODO: maybe a iterative function works better
        try:
            for match in matches:
                energy = match["fit"].ExtractParams()[0][0]["pos"]
                if energy <= maxEnergy:
                    functionValue = self.spectra.dict[referenceID].effCal.value(energy)

                    division = match["efficiency"].nominal_value / functionValue
                    amountDivisionError = amountDivisionError + division * (
                        match["efficiency"].std_dev
                    ) ** (-2)
                    amountError = amountError + (match["efficiency"].std_dev) ** (-2)

        except BaseException:
            division = 0.0
            amountDivisionError = 0.0
            amountError = 0.0

            for match in matches:
                energy = match["fit"].ExtractParams()[0][0]["pos"]
                if energy <= maxEnergy:
                    functionValue = self.spectra.dict[referenceID].effCal.value(energy)

                    division = match["efficiency"].nominal_value / functionValue
                    amountDivisionError = amountDivisionError + division
                    amountError = amountError + 1

        if amountError == 0:
            division = 0.0
            amountDivisionError = 0.0
            amountError = 0.0

            for match in matches:
                energy = match["fit"].ExtractParams()[0][0]["pos"]
                functionValue = self.spectra.dict[referenceID].effCal.nominal_value(
                    energy
                )

                division = match["efficiency"].nominal_value / functionValue
                amountDivisionError = amountDivisionError + division
                amountError = amountError + 1

        # the mean value of the divisions is calculated
        factor = amountDivisionError / amountError

        # the corrected efficiency is calculated
        # Efficiency[1] = list(map(lambda x: x / factor, Efficiency[1]))
        for match in matches:
            match["efficiency"] = match["efficiency"] / factor

        return matches


class EffCalHDTVInterface:
    def __init__(self, EffCalIf):
        self.effIf = EffCalIf
        self.spectra = EffCalIf.spectra

        self.opt = {}

        self.opt["eff_fun"] = hdtv.options.Option(
            default="wunder",
            parse=hdtv.options.parse_choices(
                ["wunder", "wiedenhoever", "poly", "exp", "pow"]
            ),
        )  # +orthogonal
        hdtv.options.RegisterOption(
            "calibration.efficiency.function", self.opt["eff_fun"]
        )

        prog = "calibration efficiency set"
        description = "Set efficiency function"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            help="Spectrum ID to set efficiency for",
            action="store",
            default="active",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            help="Parameters for efficiency function",
            action="store",
            default=None,
        )
        parser.add_argument(
            "-f",
            "--file",
            help="Read efficiency from file",
            action="store",
            default=None,
        )
        parser.add_argument(
            "function",
            help="efficiency function for calibration",
            choices=["wunder", "wiedenhoever", "poly", "exp", "pow"],
        )  # +orthogonal
        hdtv.cmdline.AddCommand(prog, self.SetFun, parser=parser)

        prog = "calibration efficiency read parameter"
        description = "Read parameter for efficiency function from file"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            help="Spectrum IDs to read parameters for",
            action="store",
            default="active",
        )
        parser.add_argument(
            "filename",
            metavar="parameter-file",
            help="file with efficiency function parameters",
        )
        hdtv.cmdline.AddCommand(prog, self.ReadPar, parser=parser, fileArgs=True)

        prog = "calibration efficiency read covariance"
        description = "Read covariance matrix of efficiency function from file"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            help="Spectrum IDs to read covariance for",
            action="store",
            default="active",
        )
        parser.add_argument(
            "filename",
            metavar="covariance-file",
            help="file with efficiency covariance matrix",
        )
        hdtv.cmdline.AddCommand(prog, self.ReadCov, parser=parser, fileArgs=True)

        prog = "calibration efficiency write parameter"
        description = "Write parameters of efficiency function from file"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            help="Spectrum ID from which to save parameters",
            action="store",
            default="active",
        )
        parser.add_argument(
            "filename",
            metavar="parameter-file",
            help="output file for efficiency function parameters",
        )
        hdtv.cmdline.AddCommand(prog, self.WritePar, parser=parser, fileArgs=True)

        prog = "calibration efficiency write covariance"
        description = "Write covariance matrix of efficiency function from file"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            help="Spectrum ID from which to save covariance",
            action="store",
            default="active",
        )
        parser.add_argument(
            "filename",
            metavar="covariance-file",
            help="output file for efficiency covariance matrix",
        )
        hdtv.cmdline.AddCommand(prog, self.WriteCov, parser=parser, fileArgs=True)

        prog = "calibration efficiency plot"
        description = "Plot efficiency of spectrum"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "spectrum",
            metavar="spectrum-id",
            help="Spectrum ID to plot efficiency from",
            default="active",
        )
        hdtv.cmdline.AddCommand(prog, self.PlotEff, parser=parser, fileArgs=False)

        prog = "calibration efficiency fit"
        # TODO:better description
        description = "Fit efficiency. For each spectrum a nuclide is necessary and for the first a coefficient or a file."
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog,
            description=description,
            epilog="Example: %(prog)s 4,Ra-226,1e7 3,Eu-152 1,Ba-133 -gpt",
        )
        parser.add_argument(
            "-f",
            "--file",
            help="File with energy-efficiency pairs",
            action="store",
            default=None,
        )  # does not really make sense, see method "Fit"
        parser.add_argument(
            "-p",
            "--fit-panel",
            help="Show fit panel",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-g",
            "--show-graph",
            help="Show fitted graph",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-t",
            "--show-table",
            help="Show table of fitted peaks",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-d",
            "--database",
            action="store",
            default="active",
            help="Database from witch the data should be imported.",
        )
        parser.add_argument(
            "-s",
            "--sigma",
            action="store",
            type=float,
            default=0.5,
            help="allowed error of energy-position",
        )
        parser.add_argument(
            "args",
            metavar="spectrumID,nuclide[,factor]",
            help="Spectrum with nuclide and optional factor",
            nargs="+",
        )
        hdtv.cmdline.AddCommand(prog, self.FitEff, parser=parser, fileArgs=False)

        prog = "calibration efficiency list"
        description = "List efficiencies"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "spectrum",
            metavar="spectrum-ids",
            nargs="*",
            help="Spectrum IDs to list",
            default="active",
        )
        hdtv.cmdline.AddCommand(prog, self.ListEff, parser=parser, fileArgs=False)

    def SetFun(self, args):
        """
        set efficiency function
        """

        eff_fun = args.function

        if args.parameter is not None:
            pars = args.parameter.split(",")
            pars = [float(x) for x in pars]
        else:
            pars = None

        if args.file is None:
            parFileName = None
            covFileName = None
        else:
            parFileName = args.file + ".par"
            covFileName = args.file + ".cov"

        try:
            ids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        except ValueError:
            raise hdtv.cmdline.HDTVCommandError("Invalid ID %s" % args.spectrum)

        for ID in ids:
            self.effIf.SetFun(ID, eff_fun, parameter=pars)
            if parFileName is not None:
                self.effIf.ReadPar(ID, parFileName)
            if covFileName is not None:
                self.effIf.ReadCov(ID, covFileName)

    def ReadPar(self, args):
        """
        Read efficiency parameter
        """
        filename = args.filename

        try:
            ids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        except ValueError:
            raise hdtv.cmdline.HDTVCommandError("Invalid ID %s" % args.spectrum)

        for ID in ids:
            self.effIf.ReadPar(ID, filename)

    def ReadCov(self, args):
        """
        Read efficiency covariance
        """
        filename = args.filename

        try:
            ids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        except ValueError:
            raise hdtv.cmdline.HDTVCommandError("Invalid ID %s" % args.spectrum)

        for ID in ids:
            self.effIf.ReadCov(ID, filename)

    def WritePar(self, args):
        """
        Save efficiency parameter
        """
        filename = args.filename

        try:
            ids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        except ValueError:
            raise hdtv.cmdline.HDTVCommandError("Invalid ID %s" % args.spectrum)

        if len(ids) > 1:
            raise hdtv.cmdline.HDTVCommandError(
                "Can only write efficiency parameter of one spectrum"
            )

        for ID in ids:
            self.effIf.WritePar(ID, filename)

    def WriteCov(self, args):
        """
        Write efficiency covariance
        """
        filename = args.filename

        try:
            ids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        except ValueError:
            raise hdtv.cmdline.HDTVCommandError("Invalid ID %s" % args.spectrum)

        if len(ids) > 1:
            raise hdtv.cmdline.HDTVCommandError(
                "Can only write efficiency covariance of one spectrum"
            )

        for ID in ids:
            self.effIf.WriteCov(ID, filename)

    def PlotEff(self, args):
        """
        Plot efficiency
        """
        try:
            ids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        except ValueError:
            raise hdtv.cmdline.HDTVCommandError("Invalid ID %s" % args.spectrum)

        if len(ids) > 1:
            raise hdtv.cmdline.HDTVCommandError(
                "Can only plot efficiency covariance of one spectrum"
            )

        for ID in ids:
            self.effIf.Plot(ID)

    def FitEff(self, args):
        """
        Fit efficiency
        """
        # TODO: error if spectrum is not visible
        ID = []
        nuclides = []
        coefficients = []
        try:
            ids = hdtv.util.ID.ParseIds(args.args, self.spectra)
        except BaseException:
            pass

        if args.file is None:
            for argument in args.args:
                try:
                    argument = argument.split(",")
                    ID.append(argument[0])
                    nuclides.append(argument[1])
                except BaseException:
                    raise hdtv.cmdline.HDTVCommandError(
                        "You have to give at least a 'spectrumID,nuclide'."
                    )

                if len(argument) > 2:
                    try:
                        coefficients.append(float(argument[2]))
                    except BaseException:
                        raise hdtv.cmdline.HDTVCommandError(
                            "Invalid coefficient %s." % str(argument[2])
                        )
                else:
                    coefficients.append(None)
            try:
                ids = hdtv.util.ID.ParseIds(ID, self.spectra)
            except ValueError:
                raise hdtv.cmdline.HDTVCommandError("Invalid ID %s" % ID)
                return

        self.effIf.Fit(
            ids,
            args.file,
            nuclides,
            coefficients,
            args.sigma,
            args.show_graph,
            args.fit_panel,
            args.show_table,
            args.database,
        )

    def ListEff(self, args):
        """
        List efficiencies
        """
        try:
            ids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        except ValueError:
            raise hdtv.cmdline.HDTVCommandError("Invalid ID %s" % args.spectrum)

        self.effIf.List(ids)


class EnergyCalIf:
    """
    Interface for energy calibrations
    """

    def __init__(self, spectra):
        self.spectra = spectra

        # tv commands
        self.tv = EnergyCalHDTVInterface(self)

    def CalFromFile(self, fname):
        """
        Read calibration polynom from file

        Allow formats are:
            * One coefficient in each line, starting with p0
            * Coefficients in one line, seperated by space, starting with p0
        """
        f = hdtv.util.TxtFile(fname)
        f.read()

        try:
            calpoly = []
            for line in f.lines:
                l = line.split()
                if len(l) > 1:  # One line cal file
                    for p in l:
                        calpoly.append(float(p))
                    raise StopIteration
                else:
                    if l[0] != "":
                        calpoly.append(float(l[0]))

        except StopIteration:  # end file reading
            pass

        return hdtv.cal.MakeCalibration(calpoly)

    def CalFromPairs(
        self,
        pairs,
        degree=1,
        table=False,
        fit=False,
        residual=False,
        ignore_errors=False,
    ):
        """
        Create calibration from pairs of channel and energy
        """
        fitter = hdtv.cal.CalibrationFitter()
        for p in pairs:
            fitter.AddPair(p[0], p[1])
        fitter.FitCal(degree, ignore_errors=ignore_errors)
        hdtv.ui.msg(html=fitter.ResultStr())
        if table:
            hdtv.ui.msg(html=str(fitter.ResultTable()))
        if fit:
            fitter.DrawCalFit()
        if residual:
            fitter.DrawCalResidual()
        return fitter.calib

    def CalFromFits(
        self,
        fits,
        pairs,
        degree=1,
        table=False,
        fit=False,
        residual=False,
        ignore_errors=False,
    ):
        """
        Create a calibration from pairs of fits and energies
        """
        valid_pairs = hdtv.util.Pairs()
        for p in pairs:
            pid = p[0].minor
            if pid is None:
                pid = 0
            fid = p[0]
            fid.minor = None
            try:
                peak = fits[fid].peaks[pid]
            except (IndexError, KeyError):
                fid.minor = pid
                hdtv.ui.warning("Ignoring invalid peak id %s" % fid)
                continue
            peak.extras["pos_lit"] = p[1]
            valid_pairs.add(peak.pos, p[1])
        return self.CalFromPairs(
            valid_pairs, degree, table, fit, residual, ignore_errors=ignore_errors
        )

    def CalsFromList(self, fname):
        """
        Reads calibrations from a calibration list file. The file has the format
        <specname>: <cal0> <cal1> ...
        The calibrations are written into the calibration dictionary.
        """
        calDict = {}
        f = hdtv.util.TxtFile(fname)
        f.read()
        for l, n in zip(f.lines, f.linos):
            try:
                (k, v) = l.split(":", 1)
                name = k.strip()
                coeff = [float(s) for s in v.split()]
                calDict[name] = hdtv.cal.MakeCalibration(coeff)
            except ValueError:
                hdtv.ui.warning(
                    "Could not parse line %d of file %s: ignored." % (n, fname)
                )
        return calDict

    def CreateCalList(self, calDict, sort: bool = True):
        """
        Creates a printable list of all calibrations in calDict
        <specname>: <cal0> <cal1> ...
        """
        lines = []
        names = calDict.keys()
        if sort:
            names = sorted(names, key=hdtv.util.natural_sort_key)
        for name in names:
            cal = calDict[name]
            lines.append(name + ": " + hdtv.cal.PrintCal(cal))
        return "\n".join(lines)

    def CopyCal(self, source_id, ids):
        """
        Copy a calibration
        """
        cal = self.spectra.dict[source_id].cal
        cal = hdtv.cal.MakeCalibration(cal)
        self.spectra.ApplyCalibration(ids, cal)


class EnergyCalHDTVInterface:
    def __init__(self, ECalIf):
        self.EnergyCalIf = ECalIf
        self.spectra = ECalIf.spectra

        self.calListSort = hdtv.options.Option(
            default=True, parse=hdtv.options.parse_bool
        )
        hdtv.options.RegisterOption("calibration.position.list.sort", self.calListSort)

        # calibration commands
        prog = "calibration position set"
        description = "Create calibration from the coefficients p of a polynomial"
        usage = "%(prog)s [-h] [-s SPECTRUM] p0 p1 [p2 ...]"
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description, usage=usage
        )
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default="active",
            help="spectrum ids to apply calibration to",
        )
        parser.add_argument("p0", type=float, help=argparse.SUPPRESS)
        parser.add_argument(
            "prest",
            metavar="p1, [p2 ...]",
            nargs="+",
            type=float,
            help=argparse.SUPPRESS,
        )
        hdtv.cmdline.AddCommand(prog, self.CalPosSet, parser=parser)

        prog = "calibration position unset"
        description = "Unset the calibration of spectra"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default="active",
            help="spectrum ids to unset calibration",
        )
        hdtv.cmdline.AddCommand(prog, self.CalPosUnset, parser=parser)

        prog = "calibration position copy"
        description = """apply the calibration that is used for the spectrum
                      selected by source-id to the spectra with dest-ids."""
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "sourceid",
            metavar="source-id",
            action="store",
            help="spectrum to copy calibration from",
        )
        parser.add_argument(
            "destids",
            metavar="dest-id",
            action="store",
            help="spectrum to copy calibration to",
            nargs="+",
        )
        hdtv.cmdline.AddCommand(prog, self.CalPosCopy, parser=parser)

        prog = "calibration position enter"
        description = "Fit a calibration polynomial to the energy/channel pairs given. "
        usage = "%(prog)s [OPTIONS] channel0 energy0 [channel1 energy1 ...]"
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog,
            description=description,
            usage=usage,
            epilog="""Hint: Specifying degree=0 will fix the linear term at 1.
                   Specify spec=None to only fit the calibration.""",
        )
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
            default=1,
            type=int,
            help="degree of calibration polynomial fitted [default: %(default)s]",
        )
        parser.add_argument(
            "-D",
            "--draw-fit",
            action="store_true",
            default=False,
            help="draw fit used to obtain calibration",
        )
        parser.add_argument(
            "-r",
            "--draw-residual",
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
            "-f",
            "--file",
            action="store",
            default=None,
            help="get channel-energy pairs from file",
        )
        parser.add_argument(
            "-i",
            "--ignore-errors",
            action="store_true",
            default=False,
            help="set all weights to 1 in fit (ignore error bars even if given)",
        )
        parser.add_argument(
            "args",
            metavar="channelN energyN",
            help="channel-energy pairs used for fit",
            nargs=argparse.REMAINDER,
        )
        hdtv.cmdline.AddCommand(
            prog, self.CalPosEnter, level=0, parser=parser, fileargs=True
        )

        prog = "calibration position nuclide"
        description = "Fit a calibration polynomial to a given nuclide."
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-S",
            "--sigma",
            action="store",
            default=0.0001,
            type=float,
            help="allowed error by variation of energy/channel",
        )
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default=None,
            help="spectrum ids to apply calibration to",
            nargs=1,
        )
        parser.add_argument(
            "-d",
            "--database",
            action="store",
            default="active",
            help="Database from witch the data should be imported.",
        )
        parser.add_argument("nuclide", nargs="+", help="nuclide to use for calibration")
        hdtv.cmdline.AddCommand(prog, self.CalPosNuc, parser=parser)

        prog = "nuclide"
        description = "Prints out the Information of the nuclide."
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-d",
            "--database",
            action="store",
            default="active",
            help="Database from witch the data should be imported.",
        )
        parser.add_argument("nuclide", nargs="+", help="nuclide to query")
        hdtv.cmdline.AddCommand(prog, self.Nuc, parser=parser)

        prog = "calibration position read"
        description = """Read the energy calibration from a file containing a single calibration.
        This corresponds to the energy calibration format used by tv:
        The calibration coefficients are all placed in separate lines."""
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default="active",
            help="spectrum ids to apply calibration to",
        )
        parser.add_argument(
            "filename", help="file with position calibration parameters"
        )
        hdtv.cmdline.AddCommand(prog, self.CalPosRead, parser=parser, fileargs=True)

        prog = "calibration position assign"
        description = """Calibrate the active spectrum by asigning energies to fitted peaks.
        peaks are specified by their index and the peak number within the peak
        (if number is ommitted the first (and only?) peak is taken)."""
        usage = "%(prog)s [OPTIONS] id0 energy0 [id1 energy1 ...]"
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description, usage=usage
        )
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
            "args",
            metavar="idN energyN",
            help="peak id-energy pair used for calibration",
            nargs=argparse.REMAINDER,
        )
        hdtv.cmdline.AddCommand(
            "calibration position assign", self.CalPosAssign, parser=parser
        )

        prog = "calibration position list"
        description = "List all energy calibrations that are currently loaded."
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--sort",
            "-s",
            action="store_true",
            help="sort calibration list",
        )
        group.add_argument(
            "--unsorted",
            "-u",
            action="store_true",
            help="leave calibration list unsorted",
        )
        hdtv.cmdline.AddCommand(prog, self.CalPosList, parser=parser)

        prog = "calibration position list write"
        description = "Write all loaded energy calibrations to a file."
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-F",
            "--force",
            action="store_true",
            default=False,
            help="overwrite existing files without asking",
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--sort",
            "-s",
            action="store_true",
            help="sort calibration list",
        )
        group.add_argument(
            "--unsorted",
            "-u",
            action="store_true",
            help="leave calibration list unsorted",
        )
        parser.add_argument(
            "filename", metavar="output-file", help="output file for position list"
        )
        hdtv.cmdline.AddCommand(
            prog, self.CalPosListWrite, parser=parser, fileargs=True
        )

        prog = "calibration position list read"
        description = "Read several energy calibrations from a file."
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "filename",
            metavar="input-file",
            help="input file for calibration position list",
        )
        hdtv.cmdline.AddCommand(prog, self.CalPosListRead, parser=parser, fileargs=True)

        prog = "calibration position list clear"
        description = "Clear all energy calibrations"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        hdtv.cmdline.AddCommand(prog, self.CalPosListClear, parser=parser)

    def Nuc(self, args):
        """
        Returns a table of energies and intensities of the given nuclide.
        """
        for nuclide in args.nuclide:
            data = EnergyCalibration.SearchNuclide(nuclide, args.database)
            EnergyCalibration.TableOfNuclide(data)

    def CalPosSet(self, args):
        """
        Create calibration from the coefficients p of a polynomial
        """
        # parsing command
        cal = [args.p0] + args.prest
        ids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        if not ids:
            hdtv.ui.warning("Nothing to do")
            return
        # do the work
        self.spectra.ApplyCalibration(ids, cal)
        return True

    def CalPosUnset(self, args):
        """
        Unset calibration
        """
        # parsing command
        ids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        if not ids:
            hdtv.ui.warning("Nothing to do")
            return
        self.spectra.ApplyCalibration(ids, None)
        return True

    def CalPosCopy(self, args):
        """
        Copy calibration from one spectrum to others
        """
        self.EnergyCalIf.CopyCal(
            hdtv.util.ID.ParseIds(args.sourceid, self.spectra)[0],
            hdtv.util.ID.ParseIds(args.destids, self.spectra),
        )

    def CalPosEnter(self, args):
        """
        Create calibration from pairs of channel and energy
        """
        # parsing command
        pairs = hdtv.util.Pairs(ufloat_fromstr)
        degree = int(args.degree)
        if args.file is not None:  # Read from file
            pairs.fromFile(args.file)
        else:  # Read from command line
            if len(args.args) % 2 != 0:
                raise hdtv.cmdline.HDTVCommandError("Number of parameters must be even")
            for channel, energy in zip(*[iter(args.args)] * 2):
                pairs.add(channel, energy)
        sids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        # do the work
        cal = self.EnergyCalIf.CalFromPairs(
            pairs,
            degree,
            args.show_table,
            args.draw_fit,
            args.draw_residual,
            ignore_errors=args.ignore_errors,
        )

        if not sids:
            hdtv.ui.msg("calibration: %s" % hdtv.cal.PrintCal(cal))
            return True
        self.spectra.ApplyCalibration(sids, cal)
        return True

    def CalPosNuc(self, args):
        """
        Create a calibration for given nuclide.
        """
        # option spectrum
        spectrumID = []
        try:
            spectrumIDList = list(args.spectrum)
            optionSpectrum = True  # check if option spectrum is called
        except BaseException:
            optionSpectrum = False

        if optionSpectrum:
            # TODO: Use build in -s parsing
            if len(spectrumIDList) > 1:
                # check if string is like '1,2,3 ...'
                for i in range(1, len(spectrumIDList) - 1, 2):
                    if spectrumIDList[i] != ",":
                        raise hdtv.cmdline.HDTVCommandError(
                            "Invalid spectrumID, it has to look like '0,1'"
                        )
            for i in range(
                0, len(spectrumIDList), 2
            ):  # makes a list of all spectrum IDs
                try:
                    # check if spectrumIDs are integers and save them
                    spectrumID.append(int(spectrumIDList[i]))
                except BaseException:
                    raise hdtv.cmdline.HDTVCommandError(
                        "Invalid spectrumID, it has to look like '0,1'"
                    )
        else:
            # check if active spectrum is visible
            if __main__.spectra.activeID not in __main__.spectra.visible:
                raise hdtv.cmdline.HDTVCommandError(
                    "Active spectrum is not visible, no action taken"
                )
            # when no option is called the active spectrum is used
            spectrumID.append(int(self.spectra.activeID))

        Peaks = []

        # position of the fitted peaks saved in peaks
        for ID in spectrumID:
            try:
                fits = self.spectra.dict[hdtv.util.ID(ID)].dict
                for fit in list(fits.values()):
                    Peaks.append(fit.ExtractParams()[0][0]["channel"])
            except (
                BaseException
            ):  # errormessage if there is no spectrum with the given ID
                raise hdtv.cmdline.HDTVCommandError(
                    "Spectrum with ID " + str(ID) + " is not visible, no action taken"
                )

        # finds the right transitions for the given nuclide(s) from table
        nuclei = [
            EnergyCalibration.SearchNuclide(nucl, args.database)
            for nucl in args.nuclide
        ]
        transitions = [transition for n in nuclei for transition in n["transitions"]]
        energies = [t["energy"] for t in transitions]

        # matches the right peaks with the right energy
        Match = EnergyCalibration.MatchPeaksAndEnergies(Peaks, energies, args.sigma)

        # prints all important values
        nuclideStr = " ".join(args.nuclide)
        spectrumIDStr = " ".join([str(i) for i in spectrumID])

        hdtv.ui.msg(
            "Create a calibration for nuclide "
            + nuclideStr
            + " (sigma: "
            + str(args.sigma)
            + ", spectrum"
            + spectrumIDStr
            + ", database "
            + nuclei[0]["reference"]
            + ")"
        )

        # calibration
        degree = 1
        fitter = hdtv.cal.CalibrationFitter()
        for p in Match:  # builds pairs
            fitter.AddPair(p[0], p[1])
        fitter.FitCal(degree, ignore_errors=True)
        hdtv.ui.msg(html=fitter.ResultStr())
        cal = fitter.calib
        for ID in spectrumID:
            self.spectra.ApplyCalibration(ID, cal)  # do the calibration

    def CalPosRead(self, args):
        """
        Read calibration from file
        """
        # parsing command
        sids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        filename = args.filename

        if not sids:
            hdtv.ui.warning("Nothing to do")
            return
        # do the work
        try:
            cal = self.EnergyCalIf.CalFromFile(filename)
            self.spectra.ApplyCalibration(sids, cal)
        except ValueError:
            raise hdtv.cmdline.HDTVCommandError(
                "Malformed calibration parameter file '%s'." % filename
            )
        return True

    def CalPosAssign(self, args):
        """
        Calibrate the active spectrum by assigning energies to fitted peaks

        Peaks are specified by their id and the peak number within the fit.
        Syntax: id.number
        If no number is given, the first peak in the fit is used.
        """
        if self.spectra.activeID is None:
            hdtv.ui.warning("No active spectrum, no action taken.")
            return False
        spec = self.spectra.GetActiveObject()
        # parsing of command
        if len(args.args) % 2 != 0:
            raise hdtv.cmdline.HDTVCommandError("Number of arguments must be even")
        else:
            pairs = hdtv.util.Pairs()
            for peak_id, energy in zip(*[iter(args.args)] * 2):
                ID = hdtv.util.ID.ParseIds(peak_id, spec, only_existent=False)[0]
                value = ufloat_fromstr(energy)
                pairs.add(ID, value)
        sids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        if not sids:
            sids = [self.spectra.activeID]
        degree = int(args.degree)
        # do the work
        cal = self.EnergyCalIf.CalFromFits(
            spec.dict,
            pairs,
            degree,
            table=args.show_table,
            fit=args.show_fit,
            residual=args.show_residual,
            ignore_errors=args.ignore_errors,
        )
        self.spectra.ApplyCalibration(sids, cal)
        return True

    def CalPosList(self, args):
        """
        Print currently known calibration list
        """
        sort = (args.sort or self.calListSort.Get()) and (not args.unsorted)
        text = self.EnergyCalIf.CreateCalList(self.spectra.caldict, sort=sort)
        hdtv.ui.msg(text)

    def CalPosListWrite(self, args):
        """
        Write calibration list to file
        """
        sort = (args.sort or self.calListSort.Get()) and (not args.unsorted)
        text = self.EnergyCalIf.CreateCalList(self.spectra.caldict, sort=sort)
        fname = hdtv.util.user_save_file(args.filename, args.force)
        if not fname:
            return
        with open(fname, "w") as calfile:
            calfile.write(text)

    def CalPosListRead(self, args):
        """
        Read calibrations for several spectra from file
        """
        caldict = self.EnergyCalIf.CalsFromList(args.filename)
        if caldict is None:
            return
        # update calcdict of main session
        self.spectra.caldict.update(caldict)
        for specId, spec in self.spectra.dict.items():
            try:
                cal = self.spectra.caldict[spec.name]
            except KeyError:
                pass
            else:
                self.spectra.ApplyCalibration([specId], cal, storeInCaldict=False)

    def CalPosListClear(self, args):
        """
        Clear list of name <-> calibration pairs
        """
        for specId, spec in self.spectra.dict.items():
            if (
                self.spectra.caldict.get(spec.name) is not None
            ):  # Use get() instead of "key in dict", as the latter only checks for literally matching keys, while get() also considers glob/regex matches
                self.spectra.ApplyCalibration([specId], None)
        self.spectra.caldict.clear()


import __main__

eff_cal_interface = EffCalIf(__main__.spectra)
energy_cal_interface = EnergyCalIf(__main__.spectra)
hdtv.cmdline.RegisterInteractive("eff", eff_cal_interface)
hdtv.cmdline.RegisterInteractive("ecal", energy_cal_interface)
