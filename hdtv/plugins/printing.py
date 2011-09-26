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
            self.PrintHistogram(spec, x1, x2)
          
        # apply limits to plot  
        pylab.xlim(x1,x2)
        
        # show finished plot and/or save
        pylab.show()
        
        
        
    def PrintHistogram(self, spec,x1,x2):
        # create values for x axis
        en = numpy.arange(x1,x2)
        # transform from channel numbers to energy
        en = self.apply_calibration(en, spec.cal)
        # get numbers of bins
        nbins = len(en)
        # extract bin contents to numpy array
        data = numpy.zeros(nbins)
        for i in range(nbins):
            data[i]=spec.hist.hist.GetBinContent(x1+i)
        print data
        print en
        #create spectrum plot
        pylab.step(en, data)
        
#    def slice_spec(en, data, xmin, xmax):
#    """
#    returns the part of the spectrum that is between xmin and xmax
#    """
#    if xmin is not None:
#        index = numpy.argmin(numpy.abs(en-xmin))
#        data = numpy.delete(data,numpy.s_[:index])
#        en = numpy.delete(en,numpy.s_[:index])
#    if xmax is not None:
#        index = numpy.argmin(numpy.abs(en-xmax))
#        data = numpy.delete(data, numpy.s_[index:])
#        en = numpy.delete(en,numpy.s_[index:])
#    return (en, data)

    def apply_calibration(self, en, cal):
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
        pass

    def PrintMarker(self, marker):
        pass



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
