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
import ROOT
import hdtv.util
import os
from array import array

class CalibrationFitter:
    def __init__(self):
        self.Reset()
        
    def Reset(self):
        self.pairs = []
        self.calib = None
        self.chi2 = None
        
    def AddPair(self, ch, e):
        self.pairs.append([ch, e])
        
    def FitCal(self, degree):
        """
        Use the reference peaks found in the histogram to fit the actual
        calibration function.
        If degree == 0, the linear coefficient of the polynomial is fixed at 1.
        """
        if degree < 0:
            raise ValueError, "Degree cannot be negative"

        if len(self.pairs) < degree+1:
            raise RuntimeError, "You must specify at least as many channel/energy pairs as there are free parameters"
        
        # Create ROOT linear fitter
        if degree == 0:
            linfit = ROOT.TLinearFitter(1, "pol1")
            linfit.FixParameter(1, 1.0)
            degree = 1
        else:
            linfit = ROOT.TLinearFitter(1, "pol%d" % degree, "")
        
        # Copy data into fitter
        v = array('d', [0.0])
            
        for (ch,e) in self.pairs:
            v[0] = ch
            linfit.AddPoint(v,e)
                    
        # Do the fit
        if linfit.Eval() != 0:
            raise RuntimeError, "Fit failed"
    
        # Save the fit result
        self.calib = MakeCalibration([linfit.GetParameter(i) for i in range(0, degree+1)])
    
        self.chi2 = linfit.GetChisquare()
        
    def ResultStr(self):
        """
        Return string describing the result of the calibration
        """
        if self.calib == None:
            raise RuntimeError, "No calibration available (did you call FitCal()?)"
        
        s = "Calibration: "
        s += " ".join(["%.6e" % x for x in self.calib.GetCoeffs()])
        s += "\n"
        s += "Chi^2: %.4f" % self.chi2
        
        return s
        
    def ResultTable(self):
        """
        Return a table showing the fit results
        """
        if self.calib == None:
            raise RuntimeError, "No calibration available (did you call FitCal()?)"
  
        header = ["Channel", "E_given", "E_fit", "Residual"]
        keys = "channel", "e_given", "e_fit", "residual"
        tabledata = list()
        
        for (ch, e_given) in self.pairs:
        
            tableline = dict()
            e_fit = self.calib.Ch2E(ch)
            residual = e_given - e_fit
            
            tableline["channel"] = "%10.2f" % ch
            tableline["e_given"] = "%10.2f" % e_given
            tableline["e_fit"] = "%10.2f" % e_fit
            tableline["residual"] = "%10.2f" % residual
            tabledata.append(tableline)
            
        return hdtv.util.Table(tabledata, keys, header = header, sortBy="channel")
        
    def DrawCalFit(self):
        """
        Draw fit used for calibration
        """
        if self.calib == None:
            raise RuntimeError, "No calibration available (did you call FitCal()?)"
            
        canvas = ROOT.TCanvas("CalFit", "Calibration Fit")
        # Prevent canvas from being closed as soon as this function finishes
        ROOT.SetOwnership(canvas, False)
    
        min_ch = self.pairs[0][0]
        max_ch = self.pairs[0][0]
        graph = ROOT.TGraph(len(self.pairs))
        ROOT.SetOwnership(graph, False)
        
        i = 0
        for (ch,e) in self.pairs:
            min_ch = min(min_ch, ch)
            max_ch = max(max_ch, ch)
                
            graph.SetPoint(i, ch, e)
            i += 1
        
        coeffs = self.calib.GetCoeffs()
        func = ROOT.TF1("CalFitFunc", "pol%d" % (len(coeffs)-1),
                        min_ch, max_ch)
        ROOT.SetOwnership(func, False)
        for i in range(0, len(coeffs)):
            func.SetParameter(i, coeffs[i])

        graph.SetTitle("Calibration Fit")
        graph.GetXaxis().SetTitle("Channel")
        graph.GetXaxis().CenterTitle()
        graph.GetYaxis().SetTitle("Energy")
        graph.GetYaxis().CenterTitle()
        
        graph.Draw("A*")
        func.Draw("SAME")
        
    def DrawCalResidual(self):
        """
        Debug: draw residual of fit used for calibration
        """
        if self.calib == None:
            raise RuntimeError, "No calibration available (did you call FitCal()?)"
            
        canvas = ROOT.TCanvas("CalResidual", "Calibration Residual")
        # Prevent canvas from being closed as soon as this function finishes
        ROOT.SetOwnership(canvas, False)
    
        min_ch = self.pairs[0][0]
        max_ch = self.pairs[0][0]
        graph = ROOT.TGraph(len(self.pairs))
        ROOT.SetOwnership(graph, False)
        
        i = 0
        for (ch,e) in self.pairs:
            min_ch = min(min_ch, ch)
            max_ch = max(max_ch, ch)
            
            graph.SetPoint(i, ch, e - self.calib.Ch2E(ch))
            i += 1
                
        nullfunc = ROOT.TF1("CalResidualFunc", "pol0", min_ch, max_ch)
        ROOT.SetOwnership(nullfunc, False)
        
        graph.SetTitle("Residual of calibration fit")
        graph.GetXaxis().SetTitle("Channel")
        graph.GetXaxis().CenterTitle()
        graph.GetYaxis().SetTitle("Energy difference")
        graph.GetYaxis().CenterTitle()

        graph.Draw("A*")
        nullfunc.Draw("SAME")


def MakeCalibration(cal):
    """ 
    Create a ROOT.HDTV.Calibration object from a python list
    """
    if not isinstance(cal, ROOT.HDTV.Calibration):
        if cal==None:
            cal = [0,1]
        calarray = ROOT.TArrayD(len(cal))
        for (i,c) in zip(range(0,len(cal)),cal):
            calarray[i] = c
        # create the calibration object
        cal = ROOT.HDTV.Calibration(calarray)
    return cal

def CalFromFile(fname):
    """
    Read calibration polynom from file
    
    There should be one coefficient in each line, starting with p0
    """
    fname = os.path.expanduser(fname)
    try:
        f = open(fname)
    except IOError, msg:
        print msg
        return []
    try:
        calpoly = []
        for line in f:
            l = line.strip()
            if l != "":
                calpoly.append(float(l))
    except ValueError:
        f.close()
        print "Malformed calibration parameter file."
        raise ValueError
    f.close()
    return MakeCalibration(calpoly)

def CalFromPairs(pairs, degree=1, table=False, fit=False, residual=False):
    """
    Create calibration from pairs of channel and energy
    """
    fitter = CalibrationFitter()            
    for p in pairs:
        fitter.AddPair(p[0], p[1])
    fitter.FitCal(degree)
    print fitter.ResultStr()
    if table:
        print ""
        print fitter.ResultTable()
    if fit:
        fitter.DrawCalFit()
    if residual:
        fitter.DrawCalResidual()
    return fitter.calib

