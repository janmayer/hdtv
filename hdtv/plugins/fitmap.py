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

import hdtv.cmdline
import hdtv.cmdhelper
import hdtv.ui

from hdtv.errvalue import ErrValue


def LevelsFromNudat(filename, ignore_uncertain=True):
    levels = list()
    lines = file(filename).readlines()
    for l in lines:
        words = l.split()
        # remove trailing isotop
        words = words[1:]
        # stretch lines to have at least 5 words
        while len(words)<6:
            words.append("")
        # level energies
        if words[0]=="L":
            en = words[1]
            if float(en)==0:
                error = 0
                words.insert(3, words[2])
            else:
                try:
                    index = words[2].index("(")
                    error = words[2][:index]
                    words.insert(3,words[2][index:])
                except:
                    error = words[2]
            if words[3]=="?":
                uncertain=True
            else:
                uncertain=False
            if ignore_uncertain and uncertain:
                continue
            (value, error) = hdtv.errvalue.ErrValue._fromString("%s(%s)" %(en,error))
            levels.append(hdtv.errvalue.ErrValue(value, error))
    return levels

class FitMap(object):
    def __init__(self, spectra):
        hdtv.ui.msg("loading plugin for setting nominal positions to peaks")
        self.spectra = spectra
        
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
        hdtv.cmdline.AddCommand(prog, self.FitPosMap, nargs=1, parser = parser)

        prog = "cal pos recalibrate"
        description = "use stored nominal positions of peaks to recalibrate the spectrum"
        usage = "%prog"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
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
    
#    def FitPosMap(self, args, options):
#        """
#        Read a list of energies from nudat file and map to the fitted peaks.
#        
#        The spectrum must be roughly calibrated for this to work.
#        """ 
#        nudat = hdtv.util.LevelsFromNudat(fname, ignoreUncertain=True)
#        if self.spectra.activeID == None:
#            hdtv.ui.warn("No active spectrum, no action taken.")
#            return False
#        spec = self.spectra.GetActiveObject()
#        for fit in spec.dict.itervalues():
#            fit = spec.dict[ID]
#            for peak in fit.peaks:
#                tol = 3
#                enlit = [n for n in nudat if n.equal(peak.pos_cal, f=tol)]
#                while len(enlit)>1 and tol >0:
#                    tol -= 1
#                    enlit = [n for n in nudat if n.equal(peak.pos_cal, f=tol)]
#                if len(enlit)>0:
#                    pairs.add(peak.pos, enlit[0])
        
        
        
        
    def CalPosRecalibrate(self, args, options):
        pass


# plugin initialisation
import __main__
__main__.fitmap = FitMap(__main__.spectra)       

