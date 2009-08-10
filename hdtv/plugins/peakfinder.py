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
# Peak finding and fitting plugin for HDTV
#-------------------------------------------------------------------------------


import hdtv.cmdline
import hdtv.fitter
import hdtv.peakmodels
import hdtv.options
import ROOT

class PeakFinder:
    
    def __init__(self, spectra):
        
        self.spectra = spectra
        print "loaded PeakFinder plugin"
        
        # Register configuration variables for fit peakfind
        opt = hdtv.options.Option(default = 2.5)
        hdtv.options.RegisterOption("fit.peakfind.sigma", opt)    
        opt = hdtv.options.Option(default = 0.05)
        hdtv.options.RegisterOption("fit.peakfind.threshold", opt)
        opt = hdtv.options.Option(default = False)
        hdtv.options.RegisterOption("fit.peakfind.no_fit", opt)
        
        
        prog = "fit peakfind"
        description = "Search for peaks in active spectrum in given range"
        usage = "%prog <start> <end>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-s", "--sigma", action = "store", default = hdtv.options.Get("fit.peakfind.sigma"),
                        help = "FWHM of peaks")
        parser.add_option("-t", "--threshold", action = "store", default = hdtv.options.Get("fit.peakfind.threshold"),
                        help = "Threshold of peaks to accept in fraction of the amplitude of highest peak (in %)")
        parser.add_option("-n", "--no-fit", action = "store_true", default = hdtv.options.Get("fit.peakfind.no_fit"),
                        help = "do not fit found peaks")
        parser.add_option("-p", "--peak-model", action = "store", default = "theuerkauf",
                        help = "fit found peaks")
        
        hdtv.cmdline.AddCommand(prog, self.PeakSearch, parser = parser, minargs = 0, fileargs = False)
        
        
    def PeakSearch(self, args, options):

        try:
            if not self.spectra.activeID in self.spectra.visible:
                print "Warning: active spectrum is not visible, no action taken"
                return True
        except KeyError:
            print "No active spectrum"
            return False
        

        sid = self.spectra.activeID
        tSpec = ROOT.TSpectrum()

        #  hist = self.spectra.GetActiveObject().fHist
        spec = hdtv.spectrum.SpectrumCompound(self.spectra[sid].viewport, self.spectra[sid])
        hist = spec.fHist
        
        
        # replace the simple spectrum object by the SpectrumCompound
        # TODO: Is this sensible? I don't get the logic, but it works.
        #self.spectra[sid] = spec
        #spec = self.spectra[sid]
        

        try:
            sigma_Ch = spec.cal.E2Ch(float(options.sigma))
            sigma_E  = float(options.sigma) 
            threshold = float(options.threshold)
        except ValueError:
            print "Invalid sigma/threshold"
            return False
        
        autofit = not options.no_fit
        peakModel = options.peak_model
        bgdeg = 2
        
        start = 0.0
        end = spec.cal.Ch2E(hist.GetNbinsX())
        try:
            if len(args) > 0:
                start = spec.cal.E2Ch(float(args[0]))
                print "new start", start
                
            if len(args) == 2:
                end = spec.cal.E2Ch(float(args[1]))
                print "new end", end
        except ValueError:
            print "Invalid start/end arguments"
            return False

        print "Search Peaks in region", start, "-", end, "(sigma=", sigma_E, "threshold=", threshold, "%)"
        
        # Invoke ROOT's peak finder
        hist.SetAxisRange(start, end)
        num_peaks = tSpec.Search(hist, sigma_Ch, "goff", threshold)
        foundpeaks = tSpec.GetPositionX()
        
        # Background fit
        # TODO: draw background
        hbg = tSpec.Background(hist, 20, "goff")

        parameter = dict()
        
        # Store peaks
        for i in range(0, num_peaks):
             fitter = hdtv.fitter.Fitter(peakModel, bgdeg)
             fit = hdtv.fit.Fit(fitter)     
             pos_E = spec.cal.Ch2E(foundpeaks[i])
             pos_Ch = foundpeaks[i]
             bin = hist.GetXaxis().FindBin(foundpeaks[i])
             yp = hist.GetBinContent(bin)
             
         
             fit.PutPeakMarker(pos_E)
             region_width = sigma_E * 3.
             fit.PutRegionMarker(pos_E - region_width/2.)
             fit.PutRegionMarker(pos_E + region_width/2.)
             free = True
             parameter["pos"] = hdtv.peakmodels.FitValue(pos_Ch, sigma_Ch / 2.0, free)
             parameter["width"] = hdtv.peakmodels.FitValue(sigma_Ch, 0, free)
             parameter["vol"] = hdtv.peakmodels.FitValue(0, 0, free)
#             parameter["vol"] = hdtv.peakmodels.FitValue(0, 0, free)
             free = False
             parameter["tl"] = hdtv.peakmodels.FitValue(None, None, free)
             parameter["tr"] = hdtv.peakmodels.FitValue(None, None, free)
             parameter["sw"] = hdtv.peakmodels.FitValue(None, None, free)
             parameter["sh"] = hdtv.peakmodels.FitValue(None, None, free)
             try:
                 peak = fit.fitter.peakModel.Peak(cal=spec.cal, **parameter)
             except:
                 print "Error creating peak"
                 print parameter
                 continue
             
             fit.peaks.append(peak)
             if autofit:          
                 fit.FitPeakFunc(spec, silent=True)
           
             ID = self.spectra[sid].Add(fit)
#             fit.Focus(view_width = region_width * 10)
             fit.SetTitle(str(ID) + "(*)")
        
        print "Found", num_peaks, "peaks"
        return True
    
# plugin initialisation
import __main__
if not hasattr(__main__, "spectra"):
    import hdtv.drawable
    __main__.spectra = hdtv.drawable.DrawableCompound(__main__.window.viewport)
__main__.peakfinder = PeakFinder(__main__.spectra)
