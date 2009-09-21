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

#-------------------------------------------------------------------------------
# Functions for efficiency, energy calibration
# 
#-------------------------------------------------------------------------------
import os

import hdtv.spectrum
import hdtv.efficiency
import hdtv.cmdline
import hdtv.cmdhelper
import hdtv.options
import hdtv.ui
import hdtv.cal
import hdtv.util

class EffCalIf(object):
    
    def __init__(self, spectra):
        
        self.spectra = spectra
        
    def SetFun(self, spectrumID, name, parameter=None):
        """
        Set efficiency function to use
        
        
        Allowed names:  * "wunder" for "Wunder"-Efficiency
                        * "wiedenhoever" for Wiedenhoever-Efficiency
                        * "poly" for polynomial efficiency
        """ 
        
        if parameter is None:
            parameter = list()
            
        try:
            name = name.lower()
            if name == "wunder":
                self.spectra[spectrumID].fEffCal = hdtv.efficiency.WunderEff(pars=parameter)
            elif name == "wiedenhoever":
                self.spectra[spectrumID].fEffCal = hdtv.efficiency.WiedenhoeverEff(pars=parameter)
            elif name == "poly":
                self.spectra[spectrumID].fEffCal = hdtv.efficiency.PolyEff(pars=parameter)
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
            self.spectra[spectrumID].fEffCal.parameter = parameter
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
            self.spectra[spectrumID].fEffCal.loadPar(filename)
        except RuntimeError, msg:
            hdtv.ui.error(str(msg))
        except IOError, msg:
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
            self.spectra[spectrumID].fEffCal.loadCov(filename)
        except RuntimeError, msg:
            hdtv.ui.error(str(msg))
        except IOError, msg:
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
            self.spectra[spectrumID].fEffCal.savePar(filename)
        except IOError, msg:
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
            self.spectra[spectrumID].fEffCal.saveCov(filename)
        except IOError, msg:
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
            ids = self.spectra.keys()
            
        tabledata = list()
        for ID in ids:
            tableline = dict()
            tableline["ID"] = ID
            try:
                tableline["Name"] = self.spectra[ID].fEffCal.name
                # TODO: Decent formatting
                tableline["Parameter"] = str(self.spectra[ID].fEffCal.parameter)
            except AttributeError:
                tableline["Name"] = "-"
                tableline["Parameter"] = "-"
            tabledata.append(tableline)
            
        table = hdtv.util.Table(data=tabledata, keys=["ID", "Name", "Parameter"], sortBy="ID", ignoreEmptyCols=False)
        hdtv.ui.msg(str(table))
    
    def Plot(self, spectrumID):
        """
        Plot efficiency
        """
        try:
            self.spectra[spectrumID].fEffCal.TF1.Draw()
        except AttributeError:
            hdtv.ui.error("No efficiency for spectrum ID %d set", spectrumID)
            
    def Fit(self, spectrumID, filename, show_graph=False, fit_panel=False):
        """
        Plot efficiency
        """
        
        fitValues = hdtv.util.Pairs(hdtv.util.ErrValue)
         
        try:
            fitValues.fromFile(filename, sep=" ") # TODO: separator
        except IOError, msg:
            hdtv.ui.error(str(msg))
            return
        
        try:
            self.spectra[spectrumID].fEffCal.fit(fitValues, quiet=False)
            if show_graph:
                self.spectra[spectrumID].fEffCal.TGraph.Draw("a*")
                self.spectra[spectrumID].fEffCal.TF1.Draw("same")
            if fit_panel:
                self.spectra[spectrumID].fEffCal.TF1.FitPanel()
        except AttributeError:
            hdtv.ui.error("No efficiency for spectrum ID %d set", spectrumID)
        
   
class EffCalHDTVInterface(object):
    
    def __init__(self, spectra):
        
        self.effIf = EffCalIf(spectra)
        self.spectra = spectra
        self.opt = dict()
        
        self.opt["eff_fun"] = hdtv.options.Option(default = "wunder")
        hdtv.options.RegisterOption("calibration.efficiency.function", self.opt["eff_fun"])
        
        prog = "calibration efficiency set"
        description = "Set efficiency function"
        usage = "%prog [wunder|wiedenhoever|poly]"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-s", "--spectrum", help = "Spectrum ID to set efficiency for", action = "store",
                          default = "active")
        parser.add_option("-p", "--parameter", help = "Parameters for efficiency function", action = "store",
                          default = None)
        parser.add_option("-f", "--file", help = "Read efficiency from file", action = "store",
                          default = None)
        
        hdtv.cmdline.AddCommand(prog, self.SetFun, parser = parser, nargs = 1)
        
        prog = "calibration efficiency read parameter"
        description = "Read parameter for efficiency function from file"
        usage = "%prog <parameter-file>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-s", "--spectrum", help = "Spectrum IDs to read parameters for", action = "store",
                          default = "active")
        hdtv.cmdline.AddCommand(prog, self.ReadPar, parser = parser, fileArgs = True, nargs = 1)
        
        prog = "calibration efficiency read covariance"
        description = "Read covariance matrix of efficiency function from file"
        usage = "%prog <covariance-file>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-s", "--spectrum", help = "Spectrum IDs to read covariance for", action = "store",
                          default = "active")
        hdtv.cmdline.AddCommand(prog, self.ReadCov, parser = parser, fileArgs = True, nargs = 1)
        
        prog = "calibration efficiency write parameter"
        description = "Write paremeters of efficiency function from file"
        usage = "%prog <covariance-file>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-s", "--spectrum", help = "Spectrum ID from which to save parameters", action = "store",
                          default = "active")
        hdtv.cmdline.AddCommand(prog, self.WritePar, parser = parser, fileArgs = True, nargs = 1)
        
        
        prog = "calibration efficiency write covariance"
        description = "Write covariance matrix of efficiency function from file"
        usage = "%prog <covariance-file>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-s", "--spectrum", help = "Spectrum ID from which to save covariance", action = "store",
                          default = "active")
        hdtv.cmdline.AddCommand(prog, self.WriteCov, parser = parser, fileArgs = True, nargs = 1)
        
        prog = "calibration efficiency plot"
        description = "Plot efficiency of spectrum"
        usage = "%prog <spectrum-id>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.PlotEff, parser = parser, fileArgs = False, nargs = 1)
        
        prog = "calibration efficiency fit"
        description = "Fit efficiency"
        usage = "%prog <spectrum-id>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-f", "--file", help = "File with energy<->efficiency pairs", action = "store", default = None)
        parser.add_option("-p", "--fit-panel", help = "Show fit panel", action = "store_true", default = False)
        parser.add_option("-g", "--show-graph", help = "Show fitted graph", action = "store_true", default = False)
        
        hdtv.cmdline.AddCommand(prog, self.FitEff, parser = parser, fileArgs = False, nargs = 1)
        
        prog = "calibration efficiency list"
        description = "List efficiencies"
        usage = "%prog [spectrum-ids]"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.ListEff, parser = parser, fileArgs = False)
        
    def SetFun(self, args, options):
        """
        set efficiency function
        """
        if len(args) != 1:
            return "USAGE"

        eff_fun = args[0]
        
        if options.parameter is not None:
            pars = options.parameter.split(",")
            pars = map(lambda x: float(x), pars)
        else:
            pars = None
            
        if options.file is None:
            parFileName = None
            covFileName = None
        else:
            parFileName = options.file + ".par"
            covFileName = options.file + ".cov"
        
        try:
            ids = hdtv.cmdhelper.ParseIds(options.spectrum, self.spectra)
        except ValueError:
            hdtv.ui.error("Invalid ID %s" % options.spectrum)
            return
        
        for ID in ids:
            self.effIf.SetFun(ID, eff_fun, parameter=pars)
            if parFileName is not None:
                self.effIf.ReadPar(ID, parFileName)
            if covFileName is not None:
                self.effIf.ReadCov(ID, covFileName)

    def ReadPar(self, args, options):
        """
        Read efficiency parameter
        """
        if len(args) != 1:
            return "USAGE"

        filename = args[0]
        
        try:
            ids = hdtv.cmdhelper.ParseIds(options.spectrum, self.spectra)
        except ValueError:
            hdtv.ui.error("Invalid ID %s" % options.spectrum)
            return
        
        for ID in ids:
            self.effIf.ReadPar(ID, filename)

        
    def ReadCov(self, args, options):
        """
        Read efficiency covariance
        """
        if len(args) != 1:
            return "USAGE"
        
        filename = args[0]
        
        try:
            ids = hdtv.cmdhelper.ParseIds(options.spectrum, self.spectra)
        except ValueError:
            hdtv.ui.error("Invalid ID %s" % options.spectrum)
            return

        for ID in ids:
            self.effIf.ReadCov(ID, filename)

    def WritePar(self, args, options):
        """
        Save efficiency parameter
        """
        if len(args) != 1:
            return "USAGE"

        filename = args[0]
        
        try:
            ids = hdtv.cmdhelper.ParseIds(options.spectrum, self.spectra)
        except ValueError:
            hdtv.ui.error("Invalid ID %s" % options.spectrum)
            return
        
        if len(ids) > 1:
            hdtv.ui.error("Can only write efficiency parameter of one spectrum")
            return
        
        for ID in ids:
            self.effIf.WritePar(ID, filename)

        
    def WriteCov(self, args, options):
        """
        Write efficiency covariance
        """
        if len(args) != 1:
            return "USAGE"

        filename = args[0]
        
        try:
            ids = hdtv.cmdhelper.ParseIds(options.spectrum, self.spectra)
        except ValueError:
            hdtv.ui.error("Invalid ID %s" % options.spectrum)
            return
        
        if len(ids) > 1:
            hdtv.ui.error("Can only write efficiency covariance of one spectrum")
            return
        
        for ID in ids:
            self.effIf.WriteCov(ID, filename)
            
    
    def PlotEff(self, args, options):
        """
        Plot efficiency
        """
        try:
            ids = hdtv.cmdhelper.ParseIds(args, self.spectra)
        except ValueError:
            hdtv.ui.error("Invalid ID %s" % args)
            return
        
        if len(ids) > 1:
            hdtv.ui.error("Can only plot efficiency covariance of one spectrum")
            return
        
        for ID in ids:
            self.effIf.Plot(ID)
            
    def FitEff(self, args, options):
        """
        Fit efficiency
        """
        try:
            ids = hdtv.cmdhelper.ParseIds(args, self.spectra)
        except ValueError:
            hdtv.ui.error("Invalid ID %s" % args)
            return
            
        if len(ids) > 1:
            hdtv.ui.error("More than one spectrum given")

        for ID in ids:
            self.effIf.Fit(ID, options.file, options.show_graph, options.fit_panel)
            
            
    def ListEff(self, args, options):
        """
        List efficiencies
        """
        try:
            ids = hdtv.cmdhelper.ParseIds(args, self.spectra)
        except ValueError:
            hdtv.ui.error("Invalid ID %s" % args)
            return
        
        self.effIf.List(ids)

            

class EnergyCalIf(object):
    
    
    def __init__(self, spectra, specIf):
        
        self.spectra = spectra
        self.specIf = specIf
        
    def ApplyCalibration(self, specIDs, cal):
        """
        Apply calibration cal to spectra with ids
        """
        
        # Check if ids is list/iterable or just single id 
        try: iter(specIDs)
        except TypeError:
            specIDs = [specIDs]

        for ID in specIDs:
            try:
                self.spectra[ID].cal = cal
                hdtv.ui.msg("Calibrated spectrum with id %d" % ID)
            except KeyError:
                hdtv.ui.warn("There is no spectrum with id: %s" % ID)
                

    def GetCalsFromList(self, fname):
        """
        Reads calibrations from a calibration list file. The file has the format
        <specname>: <cal0> <cal1> ...
        The calibrations are written into the calibration dictionary.
        """
        fname = os.path.expanduser(fname)
        try:
            f = open(fname, "r")
        except IOError, msg:
            hdtv.ui.error("Error opening file: %s" % msg)
            return False
        linenum = 0
        for l in f:
            linenum += 1
            # Remove comments and whitespace; ignore empty lines
            l = l.split('#', 1)[0].strip()
            if l == "":
                continue
            try:
                (k, v) = l.split(':', 1)
                name = k.strip()
                coeff = [ float(s) for s in v.split() ]
                self.specIf.caldict[name] = coeff
            except ValueError:
                hdtv.ui.warn("Could not parse line %d of file %s: ignored." % (linenum, fname))
            else:
                spec = self.specIf.FindSpectrumByName(name)
                if not spec is None:
                    spec.cal = self.specIf.caldict[name]
        f.close()
        return True


    def CalPosRead(self, specIDs, filename):
        """
        Read calibration from file
        """
        # Load calibration
        cal = hdtv.cal.CalFromFile(filename)
        self.ApplyCalibration(specIDs, cal)        
        return True



class EnergyCalHDTVInterface(object):
    
    def __init__(self, spectra, specInterface):
        
        self.EnergyCalIf = EnergyCalIf(spectra, specInterface)
        self.spectra = spectra
        
        # calibration commands
        parser = hdtv.cmdline.HDTVOptionParser(prog = "calibration position read",
                                               usage = "%prog [OPTIONS] <filename>")
        parser.add_option("-s", "--spec", action = "store",
                          default = "all", help = "spectrum ids to apply calibration to")
        hdtv.cmdline.AddCommand("calibration position read", self.CalPosRead, level = 0, nargs = 1,
                                fileargs = True, parser = parser)
        
        parser = hdtv.cmdline.HDTVOptionParser(prog = "calibration position enter",
                     description = 
"""Fit a calibration polynomial to the energy/channel pairs given.
Hint: specifying degree=0 will fix the linear term at 1. Specify spec=None
to only fit the calibration.""",
                     usage = "%prog [OPTIONS] <ch0> <E0> [<ch1> <E1> ...]")
        parser.add_option("-s", "--spec", action = "store",
                          default = "all", help = "spectrum ids to apply calibration to")
        parser.add_option("-d", "--degree", action = "store",
                          default = "1", help = "degree of calibration polynomial fitted [default: %default]")
        parser.add_option("-D", "--draw-fit", action = "store_true",
                          default = False, help = "draw fit used to obtain calibration")
        parser.add_option("-r", "--draw-residual", action = "store_true",
                          default = False, help = "show residual of calibration fit")
        parser.add_option("-t", "--show-table", action = "store_true",
                          default = False, help = "print table of energies given and energies obtained from fit")
        parser.add_option("-f", "--file", action = "store",
                          default = None, help = "get channel<->energy pairs from file")
        hdtv.cmdline.AddCommand("calibration position enter", self.CalPosEnter, level = 0,
                                minargs = 0, parser = parser, fileargs = True)
        
        parser = hdtv.cmdline.HDTVOptionParser(prog = "calibration position set",
                                               usage = "%prog [OPTIONS] <p0> <p1> [<p2> ...]")
        parser.add_option("-s", "--spec", action = "store",
                          default = "all", help = "spectrum ids to apply calibration to")
        hdtv.cmdline.AddCommand("calibration position set", self.CalPosSet, level = 0,
                                minargs = 2, parser = parser)
        
        
        hdtv.cmdline.AddCommand("calibration position getlist", self.CalPosGetlist, nargs = 1,
                                fileargs = True,
                                usage = "%prog <filename>", level = 0)

    
    def CalPosRead(self, args, options):
        """
        Read calibration from file
        """
        try:
            ids = hdtv.cmdhelper.ParseIds(options.spec, self.spectra)
            fname = args[0]
        except (ValueError, IndexError):
            return "USAGE"
            
        if len(ids) == 0:
            hdtv.ui.warn("Nothing to do")
            return

        self.EnergyCalIf.CalPosRead(ids, fname)        
        return True
            
        
    def CalPosEnter(self, args, options):
        """
        Create calibration from pairs of channel and energy
        """
        try:
            pairs = hdtv.util.Pairs(hdtv.util.ErrValue)
            if not options.file is None: # Read from file     
                pairs.fromFile(options.file)
            else:
                if len(args) % 2 != 0: # Read from command line
                    hdtv.ui.error("Number of parameters must be even")
                    return "USAGE"
                for p in range(0, len(args), 2):
                    pairs.add(args[p], args[p + 1])
            ids = hdtv.cmdhelper.ParseIds(options.spec, self.spectra)
            if len(ids) == 0:
                hdtv.ui.warn("Nothing to do")
                return
            degree = int(options.degree)
        except ValueError:
            return "USAGE"
        except IOError, msg:
            hdtv.ui.error(str(msg))
            return False
        
        try:
            cal = hdtv.cal.CalFromPairs(pairs, degree, options.show_table,
                                        options.draw_fit, options.draw_residual)
        except (ValueError, RuntimeError), msg:
            hdtv.ui.error(str(msg))
            return False
        else:
            self.EnergyCalIf.ApplyCalibration(ids, cal)            
            return True


    def CalPosSet(self, args, options):
        """
        Create calibration from the coefficients p of a polynomial
        n is the degree of the polynomial
        """
        try:
            cal = [float(i) for i in args]
            ids = hdtv.cmdhelper.ParseIds(options.spec, self.spectra)
        except ValueError:
            return "USAGE"
        
        if len(ids) == 0:
            hdtv.ui.warn("Nothing to do")
            return
        
        self.EnergyCalIf.ApplyCalibration(ids, cal)
        return True

        
    def CalPosGetlist(self, args):
        """
        Read calibrations for several spectra from file
        """
        self.EnergyCalIf.GetCalsFromList(args[0])
 
    

import __main__
__main__.eff = EffCalHDTVInterface(__main__.spectra)
__main__.ecal = EnergyCalHDTVInterface(__main__.spectra, __main__.s)
                
            
            

