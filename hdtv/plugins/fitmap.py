# -*- coding: utf-8 -*-

# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2010  The HDTV development team (see file AUTHORS)
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
import os

import hdtv.cmdline
import hdtv.cmdhelper
import hdtv.ui

from hdtv.errvalue import ErrValue

class FitMap(object):
    def __init__(self, spectra, ecal):
        hdtv.ui.msg("loading plugin for setting nominal positions to peaks")
        self.spectra = spectra
        self.ecal = ecal
        
        prog = "fit position assign"
        description = "assign energy valuey as nominal position for peak"
        usage = "%prog pid en [pid en ...] "
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.FitPosAssign, minargs=2, parser = parser)

        prog = "fit position erase"
        description = "erase nominal position for peaks"
        usage = "%prog pids"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.FitPosErase, minargs=1, parser = parser)

        prog = "fit position map"
        description = "read nominal position from nudat file"
        usage = "%prog filename"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.FitPosMap, nargs=1, fileargs=True, parser = parser)

        prog = "calibration position recalibrate"
        description = "use stored nominal positions of peaks to recalibrate the spectrum"
        usage = "%prog"
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
        parser.add_option("-i", "--ignore-errors", action = "store_true", default = False,
                          help = "set all weights to 1 in fit (ignore error bars even if given)")
        hdtv.cmdline.AddCommand(prog, self.CalPosRecalibrate, nargs=0, parser = parser)

    def FitPosAssign(self, args, options):
        """
        Assign a nominal value for the positon of peaks
        
        Peaks are specified by their id and the peak number within the fit.
        Syntax: id.number
        If no number is given, the first peak in the fit is used.
        """
        if self.spectra.activeID == None:
            hdtv.ui.warn("No active spectrum, no action taken.")
            return False
        spec = self.spectra.GetActiveObject() 
        if len(args) % 2 != 0:
            hdtv.ui.error("Number of arguments must be even")
            return "USAGE"
        else:
            for i in range(0, len(args),2):
                en = ErrValue(args[i+1])
                try:
                    (fid, pid) = hdtv.cmdhelper.ParsePeakID(args[i])
                except:
                    continue
                spec.dict[fid].peaks[pid].extras["pos_lit"] = en

    def FitPosErase(self, args, options):
        """
        Erase nominal values for the position of peaks
        
        Peaks are specified by their id and the peak number within the fit.
        Syntax: id.number
        If no number is given, the first peak in the fit is used.
        """
        if self.spectra.activeID == None:
            hdtv.ui.warn("No active spectrum, no action taken.")
            return False
        spec = self.spectra.GetActiveObject()
        for ID in args:
            try:
                (fid, pid) = hdtv.cmdhelper.ParsePeakID(ID)
                spec.dict[fid].peaks[pid].extras.pop("pos_lit")
            except:
                continue
    
    def FitPosMap(self, args, options):
        """
        Read a list of energies from file and map to the fitted peaks.
        
        The spectrum must be roughly calibrated for this to work.
        """ 
        f = hdtv.util.TxtFile(args[0])
        f.read()
        energies = list()
        for line in f.lines:
            energies.append(ErrValue(line.split(",")[0]))
        if self.spectra.activeID == None:
            hdtv.ui.warn("No active spectrum, no action taken.")
            return False
        spec = self.spectra.GetActiveObject()
        count = 0
        for fit in spec.dict.itervalues():
            for peak in fit.peaks:
                # erase old values
                try:
                    peak.extras.pop("pos_lit")
                except:
                    pass
                # start with a rather coarse search
                tol = 3
                enlit = [e for e in energies if e.equal(peak.pos_cal, f=tol)]
                # and then refine it, if necessary
                while len(enlit)>1 and tol >0:
                    tol -= 1
                    enlit = [e for e in energies if e.equal(peak.pos_cal, f=tol)]
                if len(enlit)>0:
                    peak.extras["pos_lit"] = enlit[0]
                    count +=1
        # give a feetback to the user
        hdtv.ui.msg("Mapped %s energies to peaks" %count)
    
    def CalPosRecalibrate(self, args, options):
        if self.spectra.activeID == None:
            hdtv.ui.warn("No active spectrum, no action taken.")
            return False
        spec = self.spectra.GetActiveObject() 
        # parsing of command line
        sids = hdtv.cmdhelper.ParseIds(options.spectrum, self.spectra)
        if len(sids)==0:
            sids = [self.spectra.activeID]
        degree = int(options.degree)
        pairs = hdtv.util.Pairs()
        for ID in spec.ids:
            fit = spec.dict[ID]
            for peak in fit.peaks:
                try:
                    enlit = peak.extras["pos_lit"]
                    pairs.add(peak.pos, enlit)
                except:
                    continue
        
        cal = self.ecal.CalFromPairs(pairs, degree, table=options.show_table, 
                                                    fit=options.show_fit, 
                                                    residual=options.show_residual,
                                                    ignoreErrors=options.ignore_errors)
        self.spectra.ApplyCalibration(sids, cal)
        return True

# plugin initialisation
import __main__
if not __main__.ecal:
    import calInterface
    __main__.ecal = calInterface.EnergyCalIf(__main__.spectra)
__main__.fitmap = FitMap(__main__.spectra, __main__.ecal)       

