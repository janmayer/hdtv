# -*- coding: utf-8 -*-

# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 20011-2013  The HDTV development team (see file AUTHORS)
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
import hdtv.ui
import hdtv.cmdline
import hdtv.cal
import hdtv.color

import numpy
import scipy
import pylab
import math



    
class PrintOut(object):
    def __init__(self, spectra):
        self.spectra = spectra
        
    def Execute(self):
        # extract visible spectrum objects
        ids = list(self.spectra.visible)
        specs = [self.spectra.dict[i] for i in ids]
        
        # create matplotlib plot
        pylab.rc("font", size=16)
        pylab.rc("lines",linewidth=1)
        pylab.rc("svg",embed_char_paths = False)
        
        pylab.figure(figsize=(8.5,4.2))

        # viewport limits
        x1= int(math.floor(self.spectra.viewport.GetOffset()))
        x2= int(x1+ math.ceil(self.spectra.viewport.GetXVisibleRegion()))
        
        # add spectra, fits, marker etc.
        for spec in specs:
            self.PrintHistogram(spec)
            # extract visible fits for this spectrum
            fids = list(spec.visible)
            fits = [spec.dict[i] for i in fids]
            for fit in fits:
                if self.spectra.window.IsInVisibleRegion(fit):
                    self.PrintFit(fit)
                    
          
        # apply limits to plot  
        pylab.xlim(x1,x2)
        
        # show finished plot and/or save
        pylab.show()
        

    def PrintHistogram(self, spec):
        nbins = spec.hist.hist.GetNbinsX()
        # create values for x axis
        en = numpy.arange(nbins)
        # shift in order to get values at bin center
        en=en-0.5
        # calibrate 
        en = self.ApplyCalibration(en, spec.cal)
        # extract bin contents to numpy array
        data = numpy.zeros(nbins)
        for i in range(nbins):
            data[i]=spec.hist.hist.GetBinContent(i)
        #create spectrum plot
        (r,g,b)= hdtv.color.GetRGB(spec.color)
        pylab.step(en, data, color=(r,g,b))
        

    def ApplyCalibration(self, en, cal):
        """ 
        return calibrated values
        """
        if cal and not cal.IsTrivial():
            calpolynom = hdtv.cal.GetCoeffs(cal)
            # scipy needs highes order first
            calpolynom.reverse()
            en = scipy.polyval(calpolynom, en)
        return en

    def PrintFit(self, fit):
        for p in fit.peakMarkers:
            self.PrintMarker(p)

    def PrintMarker(self, marker):
        pos = marker.p1.pos_cal
        (r,g,b)= hdtv.color.GetRGB(marker.color)
        pylab.axvline(pos, color=(r,g,b))


class PrintInterface(object):
    def __init__(self, spectra):
        self.spectra = spectra
                
        # command line interface 
        prog = "print"
        description = "create print out"
        usage = "%prog"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        #parser.add_option("-s", "--spectrum", action = "store", default = "active",
        #                            help = "for which the fits should be saved (default=active)")
        hdtv.cmdline.AddCommand(prog, self.Print, parser=parser)

    
    def Print(self, args, options):
        p= PrintOut(self.spectra)
        p.Execute()
    
# plugin initialisation
import __main__
__main__.p =PrintInterface(__main__.spectra)
hdtv.ui.msg("Loaded user interface for printing")
