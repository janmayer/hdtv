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

#-------------------------------------------------------------------------
# Functions for efficiency, energy calibration
#
#-------------------------------------------------------------------------

from __future__ import print_function

import os
import json
import argparse
import math

import hdtv.efficiency
import hdtv.cmdline
import hdtv.options
import hdtv.ui
import hdtv.cal
import hdtv.util
import hdtv.errvalue
from hdtv.fitxml import FitXml
from . import EnergyCalibration


class EffCalIf(object):

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
            parameter = list()

        try:
            name = name.lower()
            if name == "wunder":
                self.spectra.dict[spectrumID].effCal = hdtv.efficiency.WunderEff(
                    pars=parameter)
            elif name == "wiedenhoever":
                self.spectra.dict[spectrumID].effCal = hdtv.efficiency.WiedenhoeverEff(
                    pars=parameter)
            elif name == "poly":
                self.spectra.dict[spectrumID].effCal = hdtv.efficiency.PolyEff(
                    pars=parameter)
            elif name == "exp":
                self.spectra.dict[spectrumID].effCal = hdtv.efficiency.ExpEff(
                    pars=parameter)
            elif name == "pow":
                self.spectra.dict[spectrumID].effCal = hdtv.efficiency.PowEff(
                    pars=parameter)
            # elif name == "orthogonal": #to calibrate with Exp
            #    self.spectra.dict[spectrumID].effCal = hdtv.efficiency.ExpEff(pars=parameter)
            #    self.fit = True
            # elif name == "orthogonal_fit": #to fit with othogonal
            #    self.spectra.dict[spectrumID].effCal = hdtv.efficiency.OrthogonalEff(pars=parameter)
            #    self.fit = True
            else:
                hdtv.ui.error("No such efficiency function %s", name)
                return
        except IndexError:
            hdtv.ui.error("Invalid spectrum ID %d", spectrumID)

    def SetPar(self, spectrumID, parameter):
        """
        Set parameter for efficiency function
        """
        try:
            self.spectra.dict[spectrumID].effCal.parameter = parameter
        except IndexError:
            hdtv.ui.error("Invalid spectrum ID %d", spectrumID)
        except AttributeError:
            hdtv.ui.error("No efficiency for spectrum ID %d set", spectrumID)

    def Assign(self, todo):
        """
        Assign efficiency for fit
        """
        pass

    def ReadPar(self, spectrumID, filename):
        """
        Load efficiency parameter and covariance from file
        """
        try:
            self.spectra.dict[spectrumID].effCal.loadPar(filename)
        except RuntimeError as msg:
            hdtv.ui.error(str(msg))
        except IOError as msg:
            hdtv.ui.error(str(msg))
        except IndexError:
            hdtv.ui.error("Invalid spectrum ID %d", spectrumID)
        except AttributeError:
            hdtv.ui.error("No efficiency for spectrum ID %d set", spectrumID)

    def ReadCov(self, spectrumID, filename):
        """
        Load efficiency parameter and covariance from file
        """
        try:
            self.spectra.dict[spectrumID].effCal.loadCov(filename)
        except RuntimeError as msg:
            hdtv.ui.error(str(msg))
        except IOError as msg:
            hdtv.ui.error(str(msg))
        except IndexError:
            hdtv.ui.error("Invalid spectrum ID %d", spectrumID)
        except AttributeError:
            hdtv.ui.error("No efficiency for spectrum ID %d set", spectrumID)

    def WritePar(self, spectrumID, filename):
        """
        Save efficiency parameter
        """
        try:
            self.spectra.dict[spectrumID].effCal.savePar(filename)
        except IOError as msg:
            hdtv.ui.error(str(msg))
        except IndexError:
            hdtv.ui.error("Invalid spectrum ID %d", spectrumID)
        except AttributeError:
            hdtv.ui.error("No efficiency for spectrum ID %d set", spectrumID)

    def WriteCov(self, spectrumID, filename):
        """
        Save efficiency parameter
        """
        try:
            self.spectra.dict[spectrumID].effCal.saveCov(filename)
        except IOError as msg:
            hdtv.ui.error(str(msg))
        except IndexError:
            hdtv.ui.error("Invalid spectrum ID %d", spectrumID)
        except AttributeError:
            hdtv.ui.error("No efficiency for spectrum ID %d set", spectrumID)

    def List(self, ids=None):
        """
        List currently used efficiencies
        """
        if ids is None:
            ids = self.spectra.ids

        tabledata = list()
        for ID in ids:
            tableline = dict()
            tableline["ID"] = ID
            try:
                tableline["Name"] = self.spectra.dict[ID].effCal.name
                # TODO: Decent formatting
                tableline["Parameter"] = str(
                    self.spectra.dict[ID].effCal.parameter)
            except AttributeError:
                tableline["Name"] = "-"
                tableline["Parameter"] = "-"
            tabledata.append(tableline)

        table = hdtv.util.Table(
            data=tabledata,
            keys=[
                "ID",
                "Name",
                "Parameter"],
            sortBy="ID",
            ignoreEmptyCols=False)
        hdtv.ui.msg(str(table))

    def Plot(self, spectrumID):
        """
        Plot efficiency
        """
        try:
            self.spectra.dict[spectrumID].effCal.TF1.Draw()
        except AttributeError:
            hdtv.ui.error("No efficiency for spectrum ID %d set", spectrumID)

    def Fit(self, spectrumIDs, filename, nuclides, coefficients, sigma,
            show_graph=False, fit_panel=False, show_table=False, source=None):
        """
        Plot efficiency
        """

        for spectrumID in spectrumIDs:
            if not self.spectra.dict[spectrumID].effCal:
                hdtv.ui.error(
                    "Efficiency function not set for spectrum %d, use calibration efficiency set" %
                    spectrumID)
                return

        fitValues = hdtv.util.Pairs(lambda x: hdtv.errvalue.ErrValue(x, 0))
        tabledata = list()

        if filename is not None:  # at the moment you can only fit from one file
            # TODO: maybe it makes more sense to write another method for this
            try:
                fitValues.fromFile(filename, sep=" ")  # TODO: separator
                print(spectrumIDs)
                spectrumID = spectrumIDs[0]
            except IOError as msg:
                hdtv.ui.error(str(msg))
                return
        else:  # the spectrum has to be calibrated
            # try:
            if coefficients[0] is None:
                coefficients[0] = 1
                #raise hdtv.cmdline.HDTVCommandError("You have to give a coefficient for the first spectrum.")

            # the first spectrum/nuclide is used to calculate the factor of the
            # other ones
            spectrumID = spectrumIDs[0]
            nuclide = nuclides[0]
            coefficient = coefficients[0]

            Efficiency = self.CalculateEff(
                spectrumID, nuclide, coefficient, source, sigma)

            # for table option values are saved
            for peak, efficiency, intensity, volume in zip(*Efficiency):
                tabledata.append({
                    "Peak": peak,
                    "Efficiency": efficiency,
                    "ID": spectrumID,
                    "Nuclide": nuclide,
                    "Intensity": intensity,
                    "Vol": volume})

            fitValues.fromLists(Efficiency[0], Efficiency[1])
            # except: #TODO: errormessage
            # raise hdtv.cmdline.HDTVCommandError#("Spectrum with ID
            # "+str(ID)+" is not visible, no action taken")

            # in the region [0;maxEnergy] the relative efficiency will be
            # corrected to the fit
            maxEnergy = Efficiency[0][len(Efficiency[0]) - 1]

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
                            sigma)
                    # if it has its own coefficient only the efficiency has to
                    # be calculated
                    else:
                        NewEff = self.CalculateEff(
                            spectrumIDs[j], nuclides[j], coefficients[j], source, sigma)

                    # all new efficiencies are added to the first ones
                    for peak, efficiency, intensity, volume in zip(NewEff):
                        Efficiency[0].append(peak)
                        Efficiency[1].append(efficiency)

                        # for table option values are saved
                        tabledata.append({
                            "Peak": peak,
                            "Efficiency": efficiency,
                            "ID": spectrumIDs[j],
                            "Nuclide": nuclides[j],
                            "Intensity": intensity,
                            "Vol": volume})

                        fitValues = hdtv.util.Pairs(
                            lambda x: hdtv.errvalue.ErrValue(x, 0))
                fitValues.fromLists(Efficiency[0], Efficiency[1])
        # Call function to do the fit
        if self.fit:
            self.SetFun(spectrumID, "orthogonal_fit")
            self.spectra.dict[spectrumID].effCal.fit(
                Efficiency[0], Efficiency[1])
            # go back to the start condition
            self.SetFun(spectrumID, "orthogonal")
        else:
            try:
                self.spectra.dict[spectrumID].effCal.fit(
                    fitValues, quiet=False)
            except AttributeError:
                hdtv.ui.error(
                    "No efficiency for spectrum ID %d set", spectrumID)
            if show_graph:
                self.spectra.dict[spectrumID].effCal.TGraph.Draw("a*")
                self.spectra.dict[spectrumID].effCal.TF1.Draw("same")

            if fit_panel:
                self.spectra.dict[spectrumID].effCal.TGraph.FitPanel()

        # if table option is called a table will be created
        if show_table:
            print()
            table = hdtv.util.Table(
                data=tabledata,
                keys=[
                    "ID",
                    "Nuclide",
                    "Peak",
                    "Efficiency",
                    "Intensity",
                    "Vol"],
                sortBy="ID",
                ignoreEmptyCols=False)
            hdtv.ui.msg(str(table))

    def CalculateEff(self, spectrumID, nuclide, coefficient, source, sigma):
        """
        Calculates efficiency from a given spectrum and given nuclide.
        """

        Efficiency = []
        peakID = []
        # energy (calibrated) and volume of a peak are saved in this lists
        Peak = []
        PeakError = []
        Vol = []
        VolError = []
        PeakFinal = []
        IntensityErrorFinal = []

        # Peaks from the given spectrum are saved in Peak
        peaks = self.spectra.dict[hdtv.util.ID(spectrumID)].dict
        for i, peak in enumerate(list(peaks.values())):
            peakID.append(i)
            Peak.append(peak.ExtractParams()[0][0]['pos'].nominal_value)

        if Peak == []:
            raise hdtv.cmdline.HDTVCommandError(
                "You must fit at least one peak.")

        # It searches the right energy and intensity both with errors
        data = EnergyCalibration.SearchNuclide(str(nuclide), source)

        Energy = data[0]
        EnergyError = data[1]
        Intensity = data[2]
        IntensityError = data[3]

        # It matches the Peaks and the given energies
        Match = EnergyCalibration.MatchPeaksAndIntensities(
            Peak, peakID, Energy, Intensity, IntensityError, sigma)
        Peak = [hdtv.errvalue.ErrValue(peak, 0) for peak in Match[0]]
        Intensity = Match[1]
        peakID = Match[2]

        if Peak == []:
            raise hdtv.cmdline.HDTVCommandError(
                "There is no match between the fitted peaks and the energies of the nuclide.")

        # saves the right intensities for the peaks
        for i, ID in enumerate(peakID):
            Vol.append(hdtv.errvalue.ErrValue(
                list(peaks.values())[ID].ExtractParams()[0][0]['vol'].nominal_value,
                list(peaks.values())[ID].ExtractParams()[0][0]['vol'].std_dev))

            # Calculates the efficiency and its error and saves all peaks with
            # errors
            Efficiency.append(hdtv.errvalue.ErrValue(
                Vol[i].nominal_value / (coefficient * Intensity[i].nominal_value),
                # TODO: error of the coefficient is not included
                math.sqrt(
                    (1 / (coefficient * Intensity[i].nominal_value) * Vol[i].std_dev)**2
                    + (Vol[i].nominal_value / (coefficient * Intensity[i].nominal_value**2) *
                       Intensity[i].std_dev)**2)))
            PeakFinal.append(
                hdtv.errvalue.ErrValue(
                    Peak[i].nominal_value,
                    list(peaks.values())[ID].ExtractParams()[0][0]['pos'].std_dev))

        return(PeakFinal, Efficiency, Intensity, Vol)

    def EffCorrection(self, referenceID, maxEnergy, spectrumID,
                      fitValues, nuclide, source, sigma):
        """
        If there is one spectrum given without coefficient, you have to correct
        it by calculation the missing factor that it fits to the other one.
        """

        # fit the efficiency of the reference spectrum
        self.spectra.dict[referenceID].effCal.fit(fitValues, False)

        # calculate efficiency values for peaks
        Efficiency = self.CalculateEff(spectrumID, nuclide, 1, source, sigma)

        division = 0.0
        amountDivisionError = 0.0
        amountError = 0.0

        # calculates the factor of the nuclide
        # TODO: maybe a iterative function works better
        try:
            for i in range(0, len(Efficiency[0])):
                energy = Efficiency[0][i].nominal_value
                if energy <= maxEnergy:
                    functionValue = self.spectra.dict[referenceID].effCal.value(
                        energy)

                    division = Efficiency[1][i].nominal_value / functionValue
                    amountDivisionError = amountDivisionError + \
                        division * (Efficiency[1][i].std_dev)**(-2)
                    amountError = amountError + (Efficiency[1][i].std_dev)**(-2)

        except BaseException:
            division = 0.0
            amountDivisionError = 0.0
            amountError = 0.0

            for i in range(0, len(Efficiency[0])):
                energy = Efficiency[0][i].nominal_value
                if energy <= maxEnergy:
                    functionValue = self.spectra.dict[referenceID].effCal.value(
                        energy)

                    division = Efficiency[1][i].nominal_value / functionValue
                    amountDivisionError = amountDivisionError + division
                    amountError = amountError + 1

        if amountError == 0:
            division = 0.0
            amountDivisionError = 0.0
            amountError = 0.0

            for i in range(0, len(Efficiency[0])):
                energy = Efficiency[0][i].nominal_value
                functionValue = self.spectra.dict[referenceID].effCal.nominal_value(
                    energy)

                division = Efficiency[1][i].nominal_value / functionValue
                amountDivisionError = amountDivisionError + division
                amountError = amountError + 1

        # the mean value of the divisions is calculated
        factor = amountDivisionError / amountError

        # the corrected efficiency is calculated
        # Efficiency[1] = list(map(lambda x: x / factor, Efficiency[1]))
        for i in range(0, len(Efficiency[1])):
            Efficiency[1][i].nominal_value = Efficiency[1][i].nominal_value / factor
            Efficiency[1][i].std_dev = Efficiency[1][i].std_dev / factor

        return Efficiency


class EffCalHDTVInterface(object):

    def __init__(self, EffCalIf):

        self.effIf = EffCalIf
        self.spectra = EffCalIf.spectra

        self.opt = dict()

        self.opt["eff_fun"] = hdtv.options.Option(default="wunder")
        hdtv.options.RegisterOption(
            "calibration.efficiency.function", self.opt["eff_fun"])

        prog = "calibration efficiency set"
        description = "Set efficiency function"
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            help="Spectrum ID to set efficiency for",
            action="store",
            default="active")
        parser.add_argument(
            "-p",
            "--parameter",
            help="Parameters for efficiency function",
            action="store",
            default=None)
        parser.add_argument(
            "-f",
            "--file",
            help="Read efficiency from file",
            action="store",
            default=None)
        parser.add_argument("function",
            help='efficiency function for calibration',
            choices=['wunder', 'wiedenhoever', 'poly', 'exp', 'pow']) # +orthogonal
        hdtv.cmdline.AddCommand(prog, self.SetFun, parser=parser)

        prog = "calibration efficiency read parameter"
        description = "Read parameter for efficiency function from file"
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            help="Spectrum IDs to read parameters for",
            action="store",
            default="active")
        parser.add_argument(
            'filename',
            metavar='parameter-file',
            help="file with efficiency function parameters")
        hdtv.cmdline.AddCommand(
            prog, self.ReadPar, parser=parser, fileArgs=True)

        prog = "calibration efficiency read covariance"
        description = "Read covariance matrix of efficiency function from file"
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            help="Spectrum IDs to read covariance for",
            action="store",
            default="active")
        parser.add_argument(
            'filename',
            metavar='covariance-file',
            help="file with efficiency covariance matrix")
        hdtv.cmdline.AddCommand(
            prog, self.ReadCov, parser=parser, fileArgs=True)

        prog = "calibration efficiency write parameter"
        description = "Write parameters of efficiency function from file"
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            help="Spectrum ID from which to save parameters",
            action="store",
            default="active")
        parser.add_argument(
            'filename',
            metavar='parameter-file',
            help="output file for efficiency function parameters")
        hdtv.cmdline.AddCommand(prog, self.WritePar,
                                parser=parser, fileArgs=True)

        prog = "calibration efficiency write covariance"
        description = "Write covariance matrix of efficiency function from file"
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            help="Spectrum ID from which to save covariance",
            action="store",
            default="active")
        parser.add_argument(
            'filename',
            metavar='covariance-file',
            help="output file for efficiency covariance matrix")
        hdtv.cmdline.AddCommand(prog, self.WriteCov,
                                parser=parser, fileArgs=True)

        prog = "calibration efficiency plot"
        description = "Plot efficiency of spectrum"
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description)
        parser.add_argument(
            "spectrum",
            metavar="spectrum-id",
            help="Spectrum ID to plot efficiency from",
            default="active")
        hdtv.cmdline.AddCommand(
            prog, self.PlotEff, parser=parser, fileArgs=False)

        prog = "calibration efficiency fit"
        # TODO:better description
        description = "Fit efficiency. For each spectrum a nuclide is necessary and for the first a coefficient or a file."
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description,
            epilog="Example: %(prog)s 4,Ra-226,1e7 3,Eu-152 1,Ba-133 -gpt")
        parser.add_argument(
            "-f",
            "--file",
            help="File with energy-efficiency pairs",
            action="store",
            default=None)  # does not really make sense, see method "Fit"
        parser.add_argument("-p", "--fit-panel", help="Show fit panel",
            action="store_true", default=False)
        parser.add_argument("-g", "--show-graph", help="Show fitted graph",
            action="store_true", default=False)
        parser.add_argument(
            "-t",
            "--show-table",
            help="Show table of fitted peaks",
            action="store_true",
            default=False)
        parser.add_argument(
            "-d",
            "--database",
            action="store",
            default="active",
            help="Database from witch the data should be imported.")
        parser.add_argument(
            "-s",
            "--sigma",
            action="store",
            type=float,
            default=0.5,
            help="allowed error of energy-position")
        parser.add_argument(
            'args',
            metavar='spectrumID,nuclide[,factor]',
            help='Spectrum with nuclide and optional factor',
            nargs='*')
        hdtv.cmdline.AddCommand(
            prog, self.FitEff, parser=parser, fileArgs=False)

        prog = "calibration efficiency list"
        description = "List efficiencies"
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description)
        parser.add_argument(
            "spectrum",
            metavar="spectrum-ids",
            help="Spectrum IDs to list",
            default="active")
        hdtv.cmdline.AddCommand(
            prog, self.ListEff, parser=parser, fileArgs=False)

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
            hdtv.ui.error("Invalid ID %s" % args.spectrum)
            return

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
            hdtv.ui.error("Invalid ID %s" % args.spectrum)
            return

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
            hdtv.ui.error("Invalid ID %s" % args.spectrum)
            return

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
            hdtv.ui.error("Invalid ID %s" % args.spectrum)
            return

        if len(ids) > 1:
            hdtv.ui.error(
                "Can only write efficiency parameter of one spectrum")
            return

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
            hdtv.ui.error("Invalid ID %s" % args.spectrum)
            return

        if len(ids) > 1:
            hdtv.ui.error(
                "Can only write efficiency covariance of one spectrum")
            return

        for ID in ids:
            self.effIf.WriteCov(ID, filename)

    def PlotEff(self, args):
        """
        Plot efficiency
        """
        try:
            ids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        except ValueError:
            hdtv.ui.error("Invalid ID %s" % args.spectrum)
            return

        if len(ids) > 1:
            hdtv.ui.error(
                "Can only plot efficiency covariance of one spectrum")
            return

        for ID in ids:
            self.effIf.Plot(ID)

    def FitEff(self, args):
        """
        Fit efficiency
        """
        if len(args.args) == 0:
            return "USAGE"

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
                    argument = argument.split(',')
                    ID.append(argument[0])
                    nuclides.append(argument[1])
                except BaseException:
                    raise hdtv.cmdline.HDTVCommandError(
                        "You have to give at least a 'spectrumID,nuclide'.")

                if len(argument) > 2:
                    try:
                        coefficients.append(float(argument[2]))
                    except BaseException:
                        raise hdtv.cmdline.HDTVCommandError(
                            "Invalid coefficient %s." % str(argument[2]))
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
            args.database)

    def ListEff(self, args):
        """
        List efficiencies
        """
        try:
            ids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        except ValueError:
            hdtv.ui.error("Invalid ID %s" % args.spectrum)
            return

        self.effIf.List(ids)


class EnergyCalIf(object):
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

    def CalFromPairs(self, pairs, degree=1, table=False,
                     fit=False, residual=False, ignore_errors=False):
        """
        Create calibration from pairs of channel and energy
        """
        fitter = hdtv.cal.CalibrationFitter()
        for p in pairs:
            fitter.AddPair(p[0], p[1])
        fitter.FitCal(degree, ignore_errors=ignore_errors)
        print(fitter.ResultStr())
        if table:
            print("")
            print(fitter.ResultTable())
        if fit:
            fitter.DrawCalFit()
        if residual:
            fitter.DrawCalResidual()
        return fitter.calib

    def CalFromFits(self, fits, pairs, degree=1, table=False, fit=False,
                    residual=False, ignore_errors=False):
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
                hdtv.ui.warn("Ignoring invalid peak id %s" % fid)
                continue
            peak.extras["pos_lit"] = p[1]
            valid_pairs.add(hdtv.errvalue.ErrValue(peak.pos.nominal_value), p[1])
        return self.CalFromPairs(valid_pairs, degree, table, fit, residual,
                                 ignore_errors=ignore_errors)

    def CalsFromList(self, fname):
        """
        Reads calibrations from a calibration list file. The file has the format
        <specname>: <cal0> <cal1> ...
        The calibrations are written into the calibration dictionary.
        """
        calDict = dict()
        f = hdtv.util.TxtFile(fname)
        f.read()
        for (l, n) in zip(f.lines, f.linos):
            try:
                (k, v) = l.split(':', 1)
                name = k.strip()
                coeff = [float(s) for s in v.split()]
                calDict[name] = hdtv.cal.MakeCalibration(coeff)
            except ValueError:
                hdtv.ui.warn(
                    "Could not parse line %d of file %s: ignored." %
                    (n, fname))
        return calDict

    def CreateCalList(self, calDict):
        """
        Creates a printable list of all calibrations in calDict
        <specname>: <cal0> <cal1> ...
        """
        lines = list()
        names = sorted(calDict.keys())
        for name in names:
            cal = calDict[name]
            lines.append(name + ": " + hdtv.cal.PrintCal(cal))
        text = "\n".join(lines)
        return text

    def CopyCal(self, source_id, ids):
        """
        Copy a calibration
        """
        cal = self.spectra.dict[source_id].cal
        coeffs = hdtv.cal.GetCoeffs(cal)
        cal = hdtv.cal.MakeCalibration(cal)
        self.spectra.ApplyCalibration(ids, cal)


class EnergyCalHDTVInterface(object):

    def __init__(self, ECalIf):

        self.EnergyCalIf = ECalIf
        self.spectra = ECalIf.spectra

        # calibration commands
        prog = "calibration position set"
        description = "Create calibration from the coefficients p of a polynomial"
        usage = "%(prog)s [-h] [-s SPECTRUM] p0 p1 [p2 ...]"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, usage=usage)
        parser.add_argument("-s", "--spectrum", action="store", default="active",
                          help="spectrum ids to apply calibration to")
        parser.add_argument("p0", type=float,
            help=argparse.SUPPRESS)
        parser.add_argument("prest", metavar='p1, [p2 ...]', nargs='+', type=float,
            help=argparse.SUPPRESS)
        hdtv.cmdline.AddCommand(prog, self.CalPosSet, parser=parser)

        prog = "calibration position unset"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument("-s", "--spectrum", action="store", default="active",
                          help="spectrum ids to unset calibration")
        hdtv.cmdline.AddCommand(prog, self.CalPosUnset, parser=parser)

        prog = "calibration position copy"
        description = """apply the calibration that is used for the spectrum
                      selected by source-id to the spectra with dest-ids."""
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description)
        parser.add_argument(
            "sourceid", metavar='source-id', action="store",
            help="spectrum to copy calibration from")
        parser.add_argument(
            "destids", metavar='dest-id', action="store",
            help="spectrum to copy calibration to", nargs='+')
        hdtv.cmdline.AddCommand(prog, self.CalPosCopy, parser=parser)

        prog = "calibration position enter"
        description = "Fit a calibration polynomial to the energy/channel pairs given. "
        usage = "%(prog)s [OPTIONS] channel0 energy0 [channel1 energy1 ...]"
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description, usage=usage,
            epilog="""Hint: Specifying degree=0 will fix the linear term at 1.
                   Specify spec=None to only fit the calibration.""")
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default="active",
            help="spectrum ids to apply calibration to")
        parser.add_argument(
            "-d",
            "--degree",
            action="store",
            default=1,
            type=int,
            help="degree of calibration polynomial fitted [default: %(default)s]")
        parser.add_argument(
            "-D",
            "--draw-fit",
            action="store_true",
            default=False,
            help="draw fit used to obtain calibration")
        parser.add_argument(
            "-r",
            "--draw-residual",
            action="store_true",
            default=False,
            help="show residual of calibration fit")
        parser.add_argument(
            "-t",
            "--show-table",
            action="store_true",
            default=False,
            help="print table of energies given and energies obtained from fit")
        parser.add_argument(
            "-f",
            "--file",
            action="store",
            default=None,
            help="get channel-energy pairs from file")
        parser.add_argument(
            "-i",
            "--ignore-errors",
            action="store_true",
            default=False,
            help="set all weights to 1 in fit (ignore error bars even if given)")
        parser.add_argument(
            "args",
            metavar="channelN energyN",
            type=float,
            help="channel-energy pairs used for fit",
            nargs=argparse.REMAINDER)
        hdtv.cmdline.AddCommand(
            prog,
            self.CalPosEnter,
            level=0,
            parser=parser,
            fileargs=True)

        prog = "calibration position nuclide"
        description = "Fit a calibration polynomial to a given nuclide."
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description)
        parser.add_argument(
            "-S", "--sigma", action="store", default=0.0001, type=float,
            help="allowed error by variation of energy/channel")
        parser.add_argument("-s", "--spectrum", action="store", default=None,
                          help="spectrum ids to apply calibration to", nargs=1)
        parser.add_argument(
            "-d",
            "--database",
            action="store",
            default="active",
            help="Database from witch the data should be imported.")
        parser.add_argument(
            "nuclide",
            nargs='+',
            help="nuclide to use for calibration")
        hdtv.cmdline.AddCommand(prog, self.CalPosNuc, parser=parser)

        prog = "nuclide"
        description = "Prints out the Information of the nuclide."
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description)
        parser.add_argument(
            "-d",
            "--database",
            action="store",
            default="active",
            help="Database from witch the data should be imported.")
        parser.add_argument(
            "nuclide",
            nargs='+',
            help="nuclide to query")
        hdtv.cmdline.AddCommand(prog, self.Nuc, parser=parser)

        prog = "calibration position read"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument("-s", "--spectrum", action="store", default="active",
                          help="spectrum ids to apply calibration to")
        parser.add_argument(
            'filename',
            help="file with position calibration parameters")
        hdtv.cmdline.AddCommand(prog, self.CalPosRead, parser=parser,
                                fileargs=True)

        prog = "calibration position assign"
        description = "Calibrate the active spectrum by asigning energies to fitted peaks. "
        description += "peaks are specified by their index and the peak number within the peak "
        description += "(if number is ommitted the first (and only?) peak is taken)."
        usage = "%(prog)s [OPTIONS] id0 energy0 [id1 energy1 ...]"
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description, usage=usage)
        parser.add_argument("-s", "--spectrum", action="store", default="active",
                          help="spectrum ids to apply calibration to")
        parser.add_argument(
            "-d",
            "--degree",
            action="store",
            default="1",
            help="degree of calibration polynomial fitted [default: %(default)s]")
        parser.add_argument(
            "-f",
            "--show-fit",
            action="store_true",
            default=False,
            help="show fit used to obtain calibration")
        parser.add_argument(
            "-r",
            "--show-residual",
            action="store_true",
            default=False,
            help="show residual of calibration fit")
        parser.add_argument(
            "-t",
            "--show-table",
            action="store_true",
            default=False,
            help="print table of energies given and energies obtained from fit")
        parser.add_argument(
            "-i",
            "--ignore-errors",
            action="store_true",
            default=False,
            help="set all weights to 1 in fit (ignore error bars even if given)")
        parser.add_argument(
            "args",
            metavar="idN energyN",
            type=float,
            help="peak id-energy pair used for calibration",
            nargs=argparse.REMAINDER)
        hdtv.cmdline.AddCommand(
            "calibration position assign",
            self.CalPosAssign,
            parser=parser)

        prog = "calibration position list"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        hdtv.cmdline.AddCommand(prog, self.CalPosList, parser=parser)

        prog = "calibration position list write"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument("-F", "--force", action="store_true", default=False,
            help="overwrite existing files without asking")
        parser.add_argument(
            'filename',
            metavar='output-file',
            help="output file for position list")
        hdtv.cmdline.AddCommand(prog, self.CalPosListWrite, parser=parser,
                                fileargs=True)

        prog = "calibration position list read"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        parser.add_argument(
            'filename',
            metavar='input-file',
            help="input file for calibration position list")
        hdtv.cmdline.AddCommand(prog, self.CalPosListRead, parser=parser,
                                fileargs=True)

        prog = "calibration position list clear"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog)
        hdtv.cmdline.AddCommand(
            prog, self.CalPosListClear, parser=parser)

    def Nuc(self, args):
        """
        Returns a table of energies and intensities of the given nuclide.
        """
        for nuclide in args.nuclide:
            Data = EnergyCalibration.SearchNuclide(nuclide, args.database)
            try:
                EnergyCalibration.TabelOfNuclide(
                    nuclide,
                    Data[0],
                    Data[1],
                    Data[2],
                    Data[3],
                    Data[4],
                    Data[5],
                    Data[6])
            except TypeError:
                hdtv.ui.debug("Table of nuclide energies is empty")

    def CalPosSet(self, args):
        """
        Create calibration from the coefficients p of a polynomial
        """
        # parsing command
        try:
            cal = [args.p0] + args.prest
            ids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        except BaseException:
            return "USAGE"
        if len(ids) == 0:
            hdtv.ui.warn("Nothing to do")
            return
        # do the work
        self.spectra.ApplyCalibration(ids, cal)
        return True

    def CalPosUnset(self, args):
        """
        Unset calibration
        """
        # parsing command
        try:
            ids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        except BaseException:
            return "USAGE"
        if len(ids) == 0:
            hdtv.ui.warn("Nothing to do")
            return
        self.spectra.ApplyCalibration(ids, None)
        return True

    def CalPosCopy(self, args):
        """
        Copy calibration from one spectrum to others
        """
        self.EnergyCalIf.CopyCal(
            hdtv.util.ID.ParseIds(args.sourceid, self.spectra),
            hdtv.util.ID.ParseIds(args.destids, self.spectra))

    def CalPosEnter(self, args):
        """
        Create calibration from pairs of channel and energy
        """
        # parsing command
        try:
            pairs = hdtv.util.Pairs(hdtv.errvalue.ErrValue)
            degree = int(args.degree)
            if args.file is not None:  # Read from file
                pairs.fromFile(args.file)
            else:  # Read from command line
                if len(args.args) % 2 != 0:
                    hdtv.ui.error("Number of parameters must be even")
                    raise hdtv.cmdline.HDTVCommandError
                for channel, energy in zip(*[iter(args.args)]*2):
                    pairs.add(channel, energy)
            sids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
        except BaseException:
            return "USAGE"
        try:
            # do the work
            cal = self.EnergyCalIf.CalFromPairs(
                pairs,
                degree,
                args.show_table,
                args.draw_fit,
                args.draw_residual,
                ignore_errors=args.ignore_errors)
        except RuntimeError as msg:
            hdtv.ui.error(str(msg))
            return False

        if len(sids) == 0:
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
                    if spectrumIDList[i] != ',':
                        raise hdtv.cmdline.HDTVCommandError(
                            "Invalid spectrumID, it has to look like '0,1'")
            for i in range(0, len(spectrumIDList),
                           2):  # makes a list of all spectrum IDs
                try:
                    # check if spectrumIDs are integers and save them
                    spectrumID.append(int(spectrumIDList[i]))
                except BaseException:
                    raise hdtv.cmdline.HDTVCommandError(
                        "Invalid specrtumID, it has to look like '0,1'")
        else:
            if not __main__.spectra.activeID in __main__.spectra.visible:  # check if active spectrum is visible
                raise hdtv.cmdline.HDTVCommandError(
                    "Active spectrum is not visible, no action taken")
            # when no option is called the active spectrum is used
            spectrumID.append(int(self.spectra.activeID))

        Energies = []
        Peaks = []

        # position of the fitted peaks saved in peaks
        for ID in spectrumID:
            try:
                fits = self.spectra.dict[hdtv.util.ID(ID)].dict
                for fit in list(fits.values()):
                    Peaks.append(fit.ExtractParams()[0][0]['channel'].nominal_value)
            except BaseException:  # errormessage if there is no spectrum with the given ID
                raise hdtv.cmdline.HDTVCommandError(
                    "Spectrum with ID " + str(ID) + " is not visible, no action taken")

        # finds the right energies for the given nuclide(s) from table
        for nucl in args.nuclide:
            for Energy in EnergyCalibration.SearchNuclide(nucl, args.database)[
                    0]:
                Energies.append(Energy)

        database = str(EnergyCalibration.SearchNuclide(
            nucl, args.database)[6])

        # matches the right peaks with the right energy
        Match = EnergyCalibration.MatchPeaksAndEnergies(Peaks, Energies, args.sigma)

        # prints all important values
        nuclideStr = ''
        spectrumIDStr = ''
        for nucl in args.nuclide:
            nuclideStr = nuclideStr + ' ' + str(nucl)
        for spec in spectrumID:
            spectrumIDStr = spectrumIDStr + ' ' + str(spec)

        print("Create a calibration for nuclide " + nuclideStr +
             " (sigma: " + str(args.sigma) +
             ", spectrum" + spectrumIDStr +
             ", database " + database + ")")

        # calibration
        degree = 1
        fitter = hdtv.cal.CalibrationFitter()
        for p in Match:  # builds pairs
            fitter.AddPair(p[0], p[1])
        fitter.FitCal(degree, ignore_errors=True)
        print(fitter.ResultStr())
        cal = fitter.calib
        for ID in spectrumID:
            self.spectra.ApplyCalibration(ID, cal)  # do the calibration

    def CalPosRead(self, args):
        """
        Read calibration from file
        """
        # parsing command
        try:
            sids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
            filename = args.filename
        except BaseException:
            return "USAGE"

        if len(sids) == 0:
            hdtv.ui.warn("Nothing to do")
            return
        # do the work
        try:
            cal = self.EnergyCalIf.CalFromFile(filename)
            self.spectra.ApplyCalibration(sids, cal)
        except ValueError:
            hdtv.ui.error(
                "Malformed calibration parameter file \'%s\'." % filename)
            return False
        except IOError as msg:
            hdtv.ui.error(str(msg))
            return False
        return True

    def CalPosAssign(self, args):
        """
        Calibrate the active spectrum by assigning energies to fitted peaks

        Peaks are specified by their id and the peak number within the fit.
        Syntax: id.number
        If no number is given, the first peak in the fit is used.
        """
        if self.spectra.activeID is None:
            hdtv.ui.warn("No active spectrum, no action taken.")
            return False
        spec = self.spectra.GetActiveObject()
        # parsing of command
        try:
            if len(args.args) % 2 != 0:
                hdtv.ui.error("Number of arguments must be even")
                raise hdtv.cmdline.HDTVCommandError
            else:
                pairs = hdtv.util.Pairs()
                for peak_id, energy in zip(*[iter(args.args)]*2):
                    ID = hdtv.util.ID.ParseIds(
                        peak_id, spec, only_existent=False)[0]
                    value = hdtv.errvalue.ErrValue(energy)
                    pairs.add(ID, value)
            sids = hdtv.util.ID.ParseIds(args.spectrum, self.spectra)
            if len(sids) == 0:
                sids = [self.spectra.activeID]
            degree = int(args.degree)
        except BaseException:
            return "USAGE"
        # do the work
        try:
            cal = self.EnergyCalIf.CalFromFits(
                spec.dict,
                pairs,
                degree,
                table=args.show_table,
                fit=args.show_fit,
                residual=args.show_residual,
                ignore_errors=args.ignore_errors)
        except RuntimeError as msg:
            hdtv.ui.error(str(msg))
            return False
        self.spectra.ApplyCalibration(sids, cal)
        return True

    def CalPosList(self, args):
        """
        Print currently known calibration list
        """
        text = self.EnergyCalIf.CreateCalList(self.spectra.caldict)
        hdtv.ui.msg(text)

    def CalPosListWrite(self, args):
        """
        Write calibration list to file
        """
        text = self.EnergyCalIf.CreateCalList(self.spectra.caldict)
        fname = args.filename
        if not args.force and os.path.exists(fname):
            hdtv.ui.warn("This file already exists:")
            overwrite = None
            while overwrite not in ["Y", "y", "N", "n", "", "B", "b"]:
                question = "Do you want to replace it [y,n] or backup it [B]:"
                overwrite = input(question)
            if overwrite in ["b", "B", ""]:
                os.rename(fname, "%s.bak" % fname)
            elif overwrite in ["n", "N"]:
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
        for name in caldict.keys():
            for sid in self.spectra.dict.keys():
                if self.spectra.dict[sid].name == name:
                    cal = caldict[name]
                    self.spectra.ApplyCalibration([sid], cal)

    def CalPosListClear(self, args):
        """
        Clear list of name <-> calibration pairs
        """
        for name in self.spectra.caldict.keys():
            for sid in self.spectra.dict.keys():
                if self.spectra.dict[sid].name == name:
                    self.spectra.ApplyCalibration([sid], None)
        self.spectra.caldict.clear()


import __main__
__main__.eff = EffCalIf(__main__.spectra)
__main__.ecal = EnergyCalIf(__main__.spectra)
