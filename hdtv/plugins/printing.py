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

import os
import numpy
import scipy
import pylab

import matplotlib.transforms as transforms




    
class PrintOut(object):
    def __init__(self, spectra, energies=False):
        self.spectra = spectra
        self.labels = energies
        
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
            # add workFit
            fits.append(self.spectra.workFit)
            for fit in fits:
                if self.spectra.window.IsInVisibleRegion(fit, part=True):
                    self.PrintFit(fit)
         
         # viewport limits
        x1= self.spectra.viewport.GetXOffset()
        x2= x1+ self.spectra.viewport.GetXVisibleRegion()
        y1 = self.spectra.viewport.GetYOffset()
        y2= y1 + self.spectra.viewport.GetYVisibleRegion()
                    
        # apply limits to plot  
        pylab.xlim(x1,x2)
        pylab.ylim(y1,y2)
        

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
        pylab.step(en, data, color=(r,g,b), label=spec.name)
        
        
    def PrintFit(self, fit):
        """
        print fit including peak marker and functions
        """
        # peak marker
        for p in fit.peakMarkers:
            self.PrintMarker(p)
        # print all marker for a workFit
        if fit.active:
            for m in fit.bgMarkers:
                self.PrintMarker(m)
            for m in fit.regionMarkers:
                self.PrintMarker(m)
        # peak function
        func = fit.dispPeakFunc
        if fit.active:
            color = hdtv.color.region
        else:
            color = fit.color
        if func:
            self.PrintFunc(func, fit.cal, color)
        # background function
        bgfunc = fit.dispBgFunc
        if fit.active:
            color = hdtv.color.bg
        else:
            color = fit.color
        if bgfunc:
            self.PrintFunc(bgfunc, fit.cal, fit.color)
        for p in fit.peaks:
            # maybe energy labels for each peak
            if self.labels:
                self.PrintLabel(p)
            # maybe functions for each peak 
            if fit._showDecomp:
                peakfunc = p.displayObj
                self.PrintFunc(peakfunc, p.cal, p.color)
            
    def PrintMarker(self, marker):
        """
        print marker
        """
        if marker.active:
            color = marker._activeColor
        else:
            color = marker.color
        (r,g,b)= hdtv.color.GetRGB(color)
        pos = marker.p1.pos_cal
        pylab.axvline(pos, color=(r,g,b))
        if marker.p2 is not None:
            pos = marker.p2.pos_cal
            pylab.axvline(pos, color=(r,g,b))
           
            
    def PrintLabel(self, peak):
        x = peak.pos_cal.value
        ax = pylab.gca()
        trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)
        pylab.text(x,0.9, peak.pos_cal.fmt(),transform=trans)


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
        description = "prints all visible items to file. Supported formats: emf, eps, pdf, png, ps, raw, rgba, svg, svgz. "
        usage = "%prog <filename>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-F","--force",action = "store_true", default=False,
                            help = "overwrite existing files without asking") 
        parser.add_option("-y","--ylabel",action="store", default=None,
                            help = "add label for y-axis")
        parser.add_option("-x","--xlabel",action="store", default=None,
                            help = "add label for x-axis")
        parser.add_option("-t","--title",action="store", default=None,
                            help = "add title for plot")
        parser.add_option("-l", "--legend",action="store_true", default=False,
                            help = "add legend")
        parser.add_option("-e", "--energies",action="store_true", default=False,
                            help = "add energy labels to each fitted peak")
        hdtv.cmdline.AddCommand(prog, self.Print,  nargs=1, fileargs=True, parser=parser)

    
    def Print(self, args, options):
        fname = os.path.expanduser(args[0])
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
    
        p= PrintOut(self.spectra, options.energies)
        p.Execute()
        
        if options.title:
            pylab.title(options.title)
        if options.ylabel:
            pylab.ylabel(options.ylabel)
        if options.xlabel:
            pylab.xlabel(options.xlabel)
        if options.legend:
            pylab.legend(frameon=False)
        
        # save finished plot to file
        try:    
            pylab.savefig(fname, bbox_inches="tight")
        except ValueError as msg:
            hdtv.ui.error(str(msg))

    
# plugin initialisation
import __main__
__main__.p =PrintInterface(__main__.spectra)
hdtv.ui.msg("Loaded user interface for printing")
