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
import json

import hdtv.efficiency
import hdtv.cmdline
import hdtv.options
import hdtv.ui
import hdtv.cal
import hdtv.util
import hdtv.errvalue
from hdtv.fitxml import FitXml
import EnergyCalibration



class EffCalIf(object):
    
    def __init__(self, spectra):
        
        self.spectra = spectra
        
        # tv commands
        self.tv = EffCalHDTVInterface(self) 
        
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
                self.spectra.dict[spectrumID].effCal = hdtv.efficiency.WunderEff(pars=parameter)
            elif name == "wiedenhoever":
                self.spectra.dict[spectrumID].effCal = hdtv.efficiency.WiedenhoeverEff(pars=parameter)
            elif name == "poly":
                self.spectra.dict[spectrumID].effCal = hdtv.efficiency.PolyEff(pars=parameter)
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
            self.spectra.dict[spectrumID].effCal.loadCov(filename)
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
            self.spectra.dict[spectrumID].effCal.savePar(filename)
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
            self.spectra.dict[spectrumID].effCal.saveCov(filename)
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
            ids = self.spectra.ids
            
        tabledata = list()
        for ID in ids:
            tableline = dict()
            tableline["ID"] = ID
            try:
                tableline["Name"] = self.spectra.dict[ID].effCal.name
                # TODO: Decent formatting
                tableline["Parameter"] = str(self.spectra.dict[ID].effCal.parameter)
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
            self.spectra.dict[spectrumID].effCal.TF1.Draw()
        except AttributeError:
            hdtv.ui.error("No efficiency for spectrum ID %d set", spectrumID)
            
    def Fit(self, spectrumID, filename, show_graph=False, fit_panel=False):
        """
        Plot efficiency
        """
        
        fitValues = hdtv.util.Pairs(hdtv.errvalue.ErrValue)
         
        try:
            fitValues.fromFile(filename, sep=" ") # TODO: separator
        except IOError, msg:
            hdtv.ui.error(str(msg))
            return
        
        try:
            self.spectra.dict[spectrumID].effCal.fit(fitValues, quiet=False)
            if show_graph:
                self.spectra.dict[spectrumID].effCal.TGraph.Draw("a*")
                self.spectra.dict[spectrumID].effCal.TF1.Draw("same")

            if fit_panel:
                self.spectra.dict[spectrumID].effCal.TGraph.FitPanel()
        except AttributeError:
            hdtv.ui.error("No efficiency for spectrum ID %d set", spectrumID)

   
class EffCalHDTVInterface(object):
    
    def __init__(self, EffCalIf):
        
        self.effIf = EffCalIf
        self.spectra = EffCalIf.spectra

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
            ids = hdtv.util.ID.ParseIds(options.spectrum, self.spectra)
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
            ids = hdtv.util.ID.ParseIds(options.spectrum, self.spectra)
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
            ids = hdtv.util.ID.ParseIds(options.spectrum, self.spectra)
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
            ids = hdtv.util.ID.ParseIds(options.spectrum, self.spectra)
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
            ids = hdtv.util.ID.ParseIds(options.spectrum, self.spectra)
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
            ids = hdtv.util.ID.ParseIds(args, self.spectra)
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
            ids = hdtv.util.ID.ParseIds(args, self.spectra)
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
            ids = hdtv.util.ID.ParseIds(args, self.spectra)
        except ValueError:
            hdtv.ui.error("Invalid ID %s" % args)
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
                if len(l) > 1: # One line cal file
                    for p in l:
                        calpoly.append(float(p))
                    raise StopIteration
                else:
                    if l[0] != "":
                        calpoly.append(float(l[0]))

        except StopIteration: # end file reading
            pass

        return hdtv.cal.MakeCalibration(calpoly)
        
        
    def CalFromPairs(self, pairs, degree=1, table=False, fit=False, residual=False, ignoreErrors=False):
        """
        Create calibration from pairs of channel and energy
        """
        fitter = hdtv.cal.CalibrationFitter()
        for p in pairs:
            fitter.AddPair(p[0], p[1])
        fitter.FitCal(degree, ignoreErrors=ignoreErrors)
        print fitter.ResultStr()
        if table:
            print ""
            print fitter.ResultTable()
        if fit:
            fitter.DrawCalFit()
        if residual:
            fitter.DrawCalResidual()
        return fitter.calib
        
        
    def CalFromFits(self, fits, pairs, degree=1, table=False, fit=False, 
                                        residual=False, ignoreErrors=False):
        """
        Create a calibration from pairs of fits and energies
        """
        valid_pairs = hdtv.util.Pairs()
        for p in pairs:
            pid = p[0].minor
            if pid is None:  pid = 0
            fid = p[0]
            fid.minor=None
            try:
                peak = fits[fid].peaks[pid]
            except (IndexError,KeyError):
                fid.minor = pid
                hdtv.ui.warn("Ignoring invalid peak id %s" % fid)
                continue 
            peak.extras["pos_lit"] = p[1]
            valid_pairs.add(hdtv.errvalue.ErrValue(peak.pos.value),p[1])
        return self.CalFromPairs(valid_pairs, degree, table, fit, residual,
                                     ignoreErrors=ignoreErrors)


    def CalsFromList(self, fname):
        """
        Reads calibrations from a calibration list file. The file has the format
        <specname>: <cal0> <cal1> ...
        The calibrations are written into the calibration dictionary.
        """
        calDict = dict()
        f = hdtv.util.TxtFile(fname)
        f.read()
        for (l,n) in zip(f.lines,f.linos):
            try:
                (k, v) = l.split(':', 1)
                name = k.strip()
                coeff = [ float(s) for s in v.split() ]
                calDict[name]= hdtv.cal.MakeCalibration(coeff)
            except ValueError:
                hdtv.ui.warn("Could not parse line %d of file %s: ignored." % (n, fname))
        return calDict
        
    def CreateCalList(self, calDict):
        """
        Creates a printable list of all calibrations in calDict
        <specname>: <cal0> <cal1> ...
        """
        lines = list()
        names = calDict.keys()
        names.sort()
        for name in names:
            cal = calDict[name]
            lines.append(name + ": "+hdtv.cal.PrintCal(cal))
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
        usage = "%prog [OPTIONS] <p0> <p1> [<p2> ...]"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, usage=usage)
        parser.add_option("-s", "--spectrum", action = "store", default = "active", 
                          help = "spectrum ids to apply calibration to")
        hdtv.cmdline.AddCommand(prog, self.CalPosSet, parser = parser,
                                minargs = 2)
                                
        prog = "calibration position unset"
        usage = "%prog [OPTIONS]"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, usage=usage)
        parser.add_option("-s", "--spectrum", action = "store", default = "active", 
                          help = "spectrum ids to unset calibration")
        hdtv.cmdline.AddCommand(prog, self.CalPosUnset, parser = parser,nargs=0)
        
        prog = "calibration position copy"
        usage = "%prog <source_id> <ids>"
        description = "apply the calibration that is used for the spectrum"
        description+= "selected by source_id to the spectra with ids."
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage=usage)
        hdtv.cmdline.AddCommand(prog, self.CalPosCopy, parser = parser,minargs=2)
        
        prog = "calibration position enter"
        description  = "Fit a calibration polynomial to the energy/channel pairs given. "
        description += "Hint: specifying degree=0 will fix the linear term at 1. "
        description += "Specify spec=None to only fit the calibration."
        usage = "%prog [OPTIONS] <ch0> <E0> [<ch1> <E1> ...]"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage=usage)
        parser.add_option("-s", "--spectrum", action = "store",
                          default = "active", help = "spectrum ids to apply calibration to")
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
        parser.add_option("-i", "--ignore-errors", action = "store_true",
                          default = False,
                          help = "set all weights to 1 in fit (ignore error bars even if given)")
        hdtv.cmdline.AddCommand(prog, self.CalPosEnter, level=0, parser = parser,
                                minargs = 0, fileargs = True) # Number of args can be 0 if "-f" is given 

        prog = "calibration position nuclid"
        description = "Fit a calibration polynominal to a given nuclid."
        usage = "%prog [OPTIONS] <nuclid0> [<nuclid1> ...]" 
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage=usage)
        parser.add_option("-S", "--sigma", action = "store", default = "0.0001",
                help = "allowed error by variation of energy/chanel")
        parser.add_option("-s", "--spectrum", action = "store", default = None,
                        help = "spectrum ids to apply calibration to", nargs = 1)
        hdtv.cmdline.AddCommand(prog, self.CalPosNuc, parser = parser) 
        
        prog = "calibration position read"
        usage = usage = "%prog [OPTIONS] <filename>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, usage = usage)
        parser.add_option("-s", "--spectrum", action = "store", default = "active", 
                          help = "spectrum ids to apply calibration to")
        hdtv.cmdline.AddCommand(prog, self.CalPosRead, parser = parser,
                                nargs = 1, fileargs = True)
        

        prog = "calibration position assign"
        description = "Calibrate the active spectrum by asigning energies to fitted peaks. "
        description += "peaks are specified by their index and the peak number within the peak "
        description += "(if number is ommitted the first (and only?) peak is taken)."
        usage = "%prog [OPTIONS] <id0> <E0> [<od1> <E1> ...]"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-s", "--spectrum", action = "store", default = "active",
                        help = "spectrum ids to apply calibration to")
        parser.add_option("-d", "--degree", action = "store", default = "1",
                        help = "degree of calibration polynomial fitted [default: %default]")
        parser.add_option("-f", "--show-fit", action = "store_true", default = False,
                        help = "show fit used to obtain calibration")
        parser.add_option("-r", "--show-residual", action = "store_true", default = False,
                        help = "show residual of calibration fit")
        parser.add_option("-t", "--show-table", action = "store_true", default = False,
                        help = "print table of energies given and energies obtained from fit")
        parser.add_option("-i", "--ignore-errors", action = "store_true",
                          default = False,
                          help = "set all weights to 1 in fit (ignore error bars even if given)")
        hdtv.cmdline.AddCommand("calibration position assign", self.CalPosAssign,
                                parser = parser, minargs = 2)
    
        prog = "calibration position list"
        usage = "%prog <filename>"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, usage=usage)
        hdtv.cmdline.AddCommand(prog, self.CalPosList, parser=parser, nargs =0)
        
        prog = "calibration position list write"
        usage = "%prog <filename>"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, usage=usage)
        parser.add_option("-F", "--force", action="store_true", default=False,
                help = "overwrite existing files without asking")
        hdtv.cmdline.AddCommand(prog, self.CalPosListWrite,parser=parser, 
                                nargs =1, fileargs=True)
        
        prog = "calibration position list read"
        usage = "%prog <filename>"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, usage=usage)
        hdtv.cmdline.AddCommand(prog, self.CalPosListRead,parser=parser,
                                nargs = 1, fileargs = True)
                                
        prog = "calibration position list clear"
        usage = "%prog <filename>"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, usage=usage)
        hdtv.cmdline.AddCommand(prog, self.CalPosListClear,parser=parser, nargs =0)
        
        
    def CalPosSet(self, args, options):
        """
        Create calibration from the coefficients p of a polynomial
        """
        # parsing command
        try:
            cal = [float(i) for i in args]
            ids = hdtv.util.ID.ParseIds(options.spectrum, self.spectra)
        except:
            return "USAGE"
        if len(ids) == 0:
            hdtv.ui.warn("Nothing to do")
            return
        # do the work
        self.spectra.ApplyCalibration(ids, cal)
        return True
    
    def CalPosUnset(self, args, options):
        """
        Unset calibration
        """
        # parsing command
        try:
            ids = hdtv.util.ID.ParseIds(options.spectrum, self.spectra)
        except:
            return "USAGE"
        if len(ids) == 0:
            hdtv.ui.warn("Nothing to do")
            return
        self.spectra.ApplyCalibration(ids, None)
        return True
    
    def CalPosCopy(self, args, options):
        """ 
        Copy calibration from one spectrum to others
        """
        try:
            ids = hdtv.util.ID.ParseIds(args, self.spectra)
        except:
            return "USAGE"
        source_id = ids[0]
        ids = ids[1:]
        self.EnergyCalIf.CopyCal(source_id, ids)
    
    def CalPosEnter(self, args, options):
        """
        Create calibration from pairs of channel and energy
        """
        # parsing command
        try:
            pairs = hdtv.util.Pairs(hdtv.errvalue.ErrValue)
            degree = int(options.degree)
            if not options.file is None: # Read from file     
                pairs.fromFile(options.file)
            else:
                if len(args) % 2 != 0: # Read from command line
                    hdtv.ui.error("Number of parameters must be even")
                    raise hdtv.cmdline.HDTVCommandError
                for p in range(0, len(args), 2):
                    pairs.add(args[p], args[p + 1])
            sids = hdtv.util.ID.ParseIds(options.spectrum, self.spectra)
        except:
            return "USAGE"
        try:
            # do the work
            cal = self.EnergyCalIf.CalFromPairs(pairs, degree, options.show_table,
                                            options.draw_fit, options.draw_residual,
                                            ignoreErrors=options.ignore_errors)
        except RuntimeError, msg:
            hdtv.ui.error(str(msg))
            return False
        
        if len(sids)==0:
            hdtv.ui.msg("calibration: %s" %hdtv.cal.PrintCal(cal))
            return True
        self.spectra.ApplyCalibration(sids, cal)        
        return True

    def CalPosNuc(self, args, options): 
        """
        Create a calibration for given nuclid. 
        """

        if args == []:
            raise hdtv.cmdline.HDTVCommandError("You must name at least one nuclid.")

        #option sigma
        try:
            sigma = float(options.sigma) 
        except:
            raise hdtv.cmdline.HDTVCommandError("Invalid sigma")

        #option spectrum
        spectrumID = []
        try:
            spectrumIDList = list(options.spectrum)
            optionSpectrum = True #check if option spectrum is called
        except:
            optionSpectrum = False

        if optionSpectrum == True:
            # TODO: Use build in -s parsing
            if len(spectrumIDList)>1:
                for i in range(1,len(spectrumIDList)-1,2): #check if string is like '1,2,3 ...'
                    if spectrumIDList[i] != ',':
                        raise hdtv.cmdline.HDTVCommandError("Invalid spectrumID, it has to look like '0,1'")
            for i in range(0,len(spectrumIDList),2): #makes a list of all spectrum IDs
                try:
                    spectrumID.append(int(spectrumIDList[i])) #check if spectrumIDs are integers and save them
                except:
                    raise hdtv.cmdline.HDTVCommandError("Invalid specrtumID, it has to look like '0,1'")
        else:
            if not __main__.spectra.activeID in __main__.spectra.visible:#check if active spectrum is visible
                raise hdtv.cmdline.HDTVCommandError("Active spectrum is not visible, no action taken")
            spectrumID.append(int(self.spectra.activeID)) #when no Option is called the active spectrum is used
                 
        nuclid = args
        Energies = []
        Peaks = []
        
        #position of the fitted peaks saved in Peaks       
        for ID in spectrumID:
            try:
                fits = self.spectra.dict[hdtv.util.ID(ID)].dict
                for fit in fits.values():
                    Peaks.append(fit.ExtractParams()[0][0]['channel'].value)
            except: #errormessage if there is no spectrum with the given ID
                raise hdtv.cmdline.HDTVCommandError("Spectrum with ID "+str(ID)+" is not visible, no action taken")

        
        #finds the right energies for the given nuclid(s) from table
        for nucl in nuclid:
            for Energy in EnergyCalibration.SearchEnergies(nucl):
                Energies.append(Energy)

        Match = EnergyCalibration.MatchPeaksAndEnergies(Peaks, Energies, sigma)#mathes the right peaks with the right energy
        
        #prints all important values
        nuclidStr = '' 
        spectrumIDStr = ''
        for nucl in nuclid:
            nuclidStr = nuclidStr+' '+str(nucl)
        for spec in spectrumID:
            spectrumIDStr = spectrumIDStr+' '+str(spec)

        print "Create a calibration for nuclid "+nuclidStr+" (sigma: "+str(sigma)+", spectrum"+spectrumIDStr+")" 

        #calibration
        degree = 1 
        fitter = hdtv.cal.CalibrationFitter()
        for p in Match: #builds pairs
            fitter.AddPair(p[0], p[1])
        fitter.FitCal(degree, ignoreErrors=True)
        print fitter.ResultStr()
        cal = fitter.calib
        for ID in spectrumID:
            self.spectra.ApplyCalibration(ID, cal) #do the calibration
    
    def CalPosRead(self, args, options):
        """
        Read calibration from file
        """
        # parsing command
        try:
            sids = hdtv.util.ID.ParseIds(options.spectrum, self.spectra)
            fname = args[0]
        except:
            return "USAGE"
            
        if len(sids) == 0:
            hdtv.ui.warn("Nothing to do")
            return
        # do the work
        try:
            cal = self.EnergyCalIf.CalFromFile(fname)
            self.spectra.ApplyCalibration(sids, cal)
        except ValueError:
            hdtv.ui.error("Malformed calibration parameter file \'%s\'." % fname)
            return False
        except IOError, msg:
            hdtv.ui.error(str(msg))
            return False
        return True
            

    def CalPosAssign(self, args, options):
        """ 
        Calibrate the active spectrum by assigning energies to fitted peaks

        Peaks are specified by their id and the peak number within the fit.
        Syntax: id.number
        If no number is given, the first peak in the fit is used.
        """
        if self.spectra.activeID == None:
            hdtv.ui.warn("No active spectrum, no action taken.")
            return False
        spec = self.spectra.GetActiveObject() 
        # parsing of command
        try:
            if len(args) % 2 != 0:
                hdtv.ui.error("Number of arguments must be even")
                raise hdtv.cmdline.HDTVCommandError
            else:
                pairs = hdtv.util.Pairs()
                for i in range(0, len(args),2):
                    ID = hdtv.util.ID.ParseIds(args[i], spec,only_existent=False )[0]
                    value = hdtv.errvalue.ErrValue(args[i+1])
                    pairs.add(ID, value)
            sids = hdtv.util.ID.ParseIds(options.spectrum, self.spectra)
            if len(sids)==0:
                sids = [self.spectra.activeID]
            degree = int(options.degree)
        except:
            return "USAGE"
        # do the work
        try:
            cal = self.EnergyCalIf.CalFromFits(spec.dict, pairs, degree, 
                                           table=options.show_table, 
                                           fit=options.show_fit, 
                                           residual=options.show_residual,
                                           ignoreErrors=options.ignore_errors)
        except RuntimeError, msg:
            hdtv.ui.error(str(msg))
            return False
        self.spectra.ApplyCalibration(sids, cal)
        return True
      

    def CalPosList(self, args, options):
        """
        Print currently known calibration list
        """
        text = self.EnergyCalIf.CreateCalList(self.spectra.caldict)
        hdtv.ui.msg(text)
       

    def CalPosListWrite(self, args, options):
        """
        Write calibration list to file
        """
        text = self.EnergyCalIf.CreateCalList(self.spectra.caldict)
        fname = args[0]
        if not options.force and os.path.exists(fname):
            hdtv.ui.warn("This file already exists:")
            overwrite = None
            while not overwrite in ["Y","y","N","n","","B","b"]:
                question = "Do you want to replace it [y,n] or backup it [B]:"
                overwrite = raw_input(question)
            if overwrite in ["b","B",""]:
                os.rename(fname,"%s.back" %fname)
            elif overwrite in ["n","N"]:
                return
        calfile = file(fname, "w")
        calfile.write(text)

    def CalPosListRead(self, args, options):
        """
        Read calibrations for several spectra from file
        """
        caldict = self.EnergyCalIf.CalsFromList(args[0])
        if caldict is None:
            return
        # update calcdict of main session
        self.spectra.caldict.update(caldict)
        for name in caldict.iterkeys():
            for sid in self.spectra.dict.iterkeys():
                if self.spectra.dict[sid].name==name:
                    cal = caldict[name]
                    self.spectra.ApplyCalibration([sid], cal)
 
    def CalPosListClear(self, args, options):
        """
        Clear list of name <-> calibration pairs
        """
        for name in self.spectra.caldict.iterkeys():
            for sid in self.spectra.dict.iterkeys():
                if self.spectra.dict[sid].name==name:
                    self.spectra.ApplyCalibration([sid], None)
        self.spectra.caldict.clear()
        

import __main__
__main__.eff = EffCalIf(__main__.spectra)
__main__.ecal = EnergyCalIf(__main__.spectra)

