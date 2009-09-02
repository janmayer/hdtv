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

import hdtv.spectrum
import hdtv.efficiency
import hdtv.cmdline
import hdtv.cmdhelper
import hdtv.options
import hdtv.ui

class EffCalIf(object):
    
    def __init__(self, spectra):
        
        self.spectra = spectra
        
    def SetFun(self, name, spectrumID):
        """
        Set efficiency function to use
        
        
        Allowed names:  * "wunder" for "Wunder"-Efficiency
                        * "wiedenhoever" for Wiedenhoever-Efficiency
                        * "poly" for polynomial efficiency
        """ 
        try:
            name = name.lower()
            if name == "wunder":
                self.spectra[spectrumID].fEffCal = hdtv.efficiency.WunderEff()
            elif name == "wiedenhoever":
                self.spectra[spectrumID].fEffCal = hdtv.efficiency.WiedenhoeverEff()
            elif name == "poly":
                self.spectra[spectrumID].fEffCal = hdtv.efficiency.PolyEff()
            else:
                hdtv.ui.error("No such efficiency function %s", name)
                return 
        except IndexError:
            hdtv.ui.error("Invalid spectrum ID %d", spectrumID)
            
    def SetPar(self, parameter, spectrumID):
        """
        Set parameter for efficiency function
        """ 
        try:
            self.spectra[spectrumID].fEffCal.parameter = parameter
        except IndexError:
            hdtv.ui.error("Invalid spectrum ID %d", spectrumID)
            
    def Assign(self, todo):
        """
        Assign efficiency for fit
        """
        pass
    
    def ReadPar(self, filename, spectrumID):
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
            
    def ReadCov(self, filename, spectrumID):
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
    
    def WritePar(self, filename, spectrumID):
        """
        Save efficiency parameter
        """
        try:
            self.spectra[spectrumID].fEffCal.savePar(filename)
        except IOError, msg:
            hdtv.ui.error(str(msg))
        except IndexError:
            hdtv.ui.error("Invalid spectrum ID %d", spectrumID)
            
    def WriteCov(self, filename, spectrumID):
        """
        Save efficiency parameter
        """
        try:
            self.spectra[spectrumID].fEffCal.saveCov(filename)
        except IOError, msg:
            hdtv.ui.error(str(msg))
        except IndexError:
            hdtv.ui.error("Invalid spectrum ID %d", spectrumID)
            
    def List(self):
        """
        List currently used efficiencies
        """
        pass
    
    def Plot(self, spectrumID):
        """
        Plot efficiency
        """
        self.spectra[spectrumID].fEffCal.TF1.Draw()
    
    
class EffCalHDTVInterface(object):
    
    def __init__(self, spectra):
        
        self.effIf = EffCalIf(spectra)
        self.spectra = spectra
        self.opt = dict()
        
        self.opt["eff_fun"] = hdtv.options.Option(default = "wunder")
        hdtv.options.RegisterOption("calibration.efficiency.function", self.opt["eff_fun"])
        
        prog = "calibration efficiency function"
        description = "Set efficiency function"
        usage = "%prog [wunder|wiedenhoever|poly]"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-s", "--spectrum", help="Spectrum ID to set efficiency for", action = "store",
                          default = "active")
        hdtv.cmdline.AddCommand(prog, self.SetFun, parser = parser)
        
        prog = "calibration efficiency read pararameter"
        description = "Read parameter for efficiency function from file"
        usage = "%prog <parameter-file>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-s", "--spectrum", help="Spectrum IDs to read parameters for", action = "store",
                          default = "active")
        hdtv.cmdline.AddCommand(prog, self.ReadPar, parser = parser, fileArgs = True, nargs=1)
        
        prog = "calibration efficiency read covariance"
        description = "Read covariance matrix of efficiency function from file"
        usage = "%prog <covariance-file>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-s", "--spectrum", help="Spectrum IDs to read covariance for", action = "store",
                          default = "active")
        hdtv.cmdline.AddCommand(prog, self.ReadCov, parser = parser, fileArgs = True, nargs=1)
        
        prog = "calibration efficiency write parameter"
        description = "Write paremeters of efficiency function from file"
        usage = "%prog <covariance-file>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-s", "--spectrum", help="Spectrum ID from which to save parameters", action = "store",
                          default = "active")
        hdtv.cmdline.AddCommand(prog, self.WritePar, parser = parser, fileArgs = True, nargs=1)
        
        
        prog = "calibration efficiency write covariance"
        description = "Write covariance matrix of efficiency function from file"
        usage = "%prog <covariance-file>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-s", "--spectrum", help="Spectrum ID from which to save covariance", action = "store",
                          default = "active")
        hdtv.cmdline.AddCommand(prog, self.WriteCov, parser = parser, fileArgs = True, nargs=1)
        
        prog = "calibration efficiency plot"
        description = "Plot efficiency of spectrum"
        usage = "%prog <spectrum-id>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.PlotEff, parser = parser, fileArgs = False, nargs=1)
        
        
        
    def SetFun(self, args, options):
        """
        set efficiency function
        """
        if len(args) != 1:
            return "USAGE"

        eff_fun = args[0]
        
        try:
            ids = hdtv.cmdhelper.ParseIds(options.spectrum, self.spectra)
        except ValueError:
            hdtv.ui.error("Invalid ID %s" % options.spectrum)
            return
        
        for ID in ids:
            self.effIf.SetFun(eff_fun, ID)
            

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
            self.effIf.ReadPar(filename, ID)

        
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
            self.effIf.ReadCov(filename, ID)

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
            self.effIf.WritePar(filename, ID)

        
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
            self.effIf.WriteCov(filename, ID)
            
    
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
            

import __main__
__main__.eff = EffCalHDTVInterface(__main__.spectra)
                
            
            

