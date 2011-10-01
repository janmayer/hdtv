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

    
class PrintOut(object):
    def __init__(self, spectra):
        self.spectra = spectra

        
    def Execute(self):
        """
        creates a plot with all currently visible objects
        """
        # extract visible spectrum objects
        ids = list(self.spectra.visible)
        specs = [self.spectra.dict[i] for i in ids]
        
        # create matplotlib plot
        pylab.rc("font", size=16)
        pylab.rc("lines",linewidth=1)
        pylab.rc("svg",embed_char_paths = False)
        
        pylab.figure(figsize=(8.5,4.2))
               
        # add spectra, fits, marker etc.
        for spec in specs:
            self.PrintHistogram(spec)
            # extract visible fits for this spectrum
            fids = list(spec.visible)
            fits = [spec.dict[i] for i in fids]
            for fit in fits:
                if self.spectra.window.IsInVisibleRegion(fit):
                    self.PrintFit(fit)
         
         # viewport limits
        x1= self.spectra.viewport.GetXOffset()
        x2= x1+ self.spectra.viewport.GetXVisibleRegion()
        y1 = self.spectra.viewport.GetYOffset()
        y2= y1 + self.spectra.viewport.GetYVisibleRegion()
                    
        # apply limits to plot  
        pylab.xlim(x1,x2)
        pylab.ylim(y1,y2)
        
        # show finished plot and/or save
        pylab.show()
        
    def PrintHistogram(self, spec):
        """
        print histogramm 
        """
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
        
    def PrintFit(self, fit):
        """
        print fit including peak marker and functions
        """
        for p in fit.peakMarkers:
            self.PrintMarker(p)
        # peak function
        func = fit.dispPeakFunc
        if func:
            self.PrintFunc(func, fit.cal, fit.color)
        # background function
        bgfunc = fit.dispBgFunc
        if bgfunc:
            self.PrintFunc(bgfunc, fit.cal, fit.color)
        # maybe functions for each peak 
        if fit._showDecomp:
            for p in fit.peaks:
                peakfunc = p.displayObj
                self.PrintFunc(peakfunc, fit.cal, fit.color)
            

    def PrintMarker(self, marker):
        """
        print marker
        """
        pos = marker.p1.pos_cal
        (r,g,b)= hdtv.color.GetRGB(marker.color)
        pylab.axvline(pos, color=(r,g,b))
        
    def PrintFunc(self, func, cal, color):
        """
        print function by evaluation it at several points
        """
        x1 = func.GetMinCh()
        x2 = func.GetMaxCh()
        nbins = int(x2-x1)*20
        en = numpy.linspace(x1,x2,nbins)
        data = numpy.zeros(nbins)
        for i in range(nbins):
            data[i]=func.Eval(en[i])
        en = self.ApplyCalibration(en, cal)
        #create function plot
        (r,g,b)= hdtv.color.GetRGB(color)
        pylab.plot(en, data, color=(r,g,b))
        
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
