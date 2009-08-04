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
import os
import glob
import xml.etree.cElementTree as ET
import hdtv.spectrum
import hdtv.peakmodels

# Increase the version number if you changed something related to the xml output.
# If your change affect the reading, you should increase the major number 
# and supply an appropriate new ReadFitlist function for the new xml version.
# If it is just a small change or bug fix, change the minor number.
# There is a script in the test directory, to test reading and writing for 
# some test cases, please make sure that your changes do not break those test cases
VERSION="1.0"

class FitXml:
    """
    Class to save and read fit lists to and from xml file
    """
    def __init__(self, spectra):
        self.spectra = spectra

    def CreateXML(self):
        """
        create XMl for all known fits
        """
        spectra = self.spectra
        # <hdtv>
        root = ET.Element("hdtv")
        root.set("version", VERSION)    
        # <spectrum>
        for spec in spectra.itervalues():
            if not hasattr(spec, "__len__") or len(spec)==0: continue
            specElement = ET.SubElement(root, "spectrum")
            specElement.set("name", str(spec))
            polynom = str()
            for p in spec.cal.GetCoeffs():
                polynom += " %f "%p
            specElement.set("calibration", polynom.strip())
            # <fit>
            for fit in spec.itervalues():
                fitElement = ET.SubElement(specElement, "fit")
                fitElement.set("peakModel", fit.fitter.peakModel.name)
                fitElement.set("bgDegree", str(fit.fitter.bgdeg))
                fitElement.set("chi", str(fit.chi))
                # <bgMarker>
                for marker in fit.bgMarkers:
                    markerElement = ET.SubElement(fitElement, "bgMarker")
                    # <begin>
                    beginElement = ET.SubElement(markerElement, "begin")
                    # <cal>
                    calElement = ET.SubElement(beginElement, "cal")
                    calElement.text = str(marker.p1)
                    # <uncal>
                    uncalElement = ET.SubElement(beginElement, "uncal")
                    uncalElement.text = str(spec.cal.E2Ch(marker.p1))
                    # <end>
                    endElement = ET.SubElement(markerElement, "end")
                    # <cal>
                    calElement = ET.SubElement(endElement, "cal")
                    calElement.text = str(marker.p2)
                    # <uncal>
                    uncalElement = ET.SubElement(endElement, "uncal")
                    uncalElement.text = str(spec.cal.E2Ch(marker.p2))
                # <regionMarker>
                for marker in fit.regionMarkers:
                    markerElement = ET.SubElement(fitElement, "regionMarker")
                    # <begin>
                    beginElement = ET.SubElement(markerElement, "begin")
                    # <cal>
                    calElement = ET.SubElement(beginElement, "cal")
                    calElement.text = str(marker.p1)
                    # <uncal>
                    uncalElement = ET.SubElement(beginElement, "uncal")
                    uncalElement.text = str(spec.cal.E2Ch(marker.p1))
                    # <p2>
                    endElement = ET.SubElement(markerElement, "end")
                    # <cal>
                    calElement = ET.SubElement(endElement, "cal")
                    calElement.text = str(marker.p2)
                    # <uncal>
                    uncalElement = ET.SubElement(endElement, "uncal")
                    uncalElement.text = str(spec.cal.E2Ch(marker.p2))
                # <peakMarker>
                for marker in fit.peakMarkers:
                    markerElement = ET.SubElement(fitElement, "peakMarker")
                    # <begin>
                    positionElement = ET.SubElement(markerElement, "position")
                    # <cal>
                    calElement = ET.SubElement(positionElement, "cal")
                    calElement.text = str(marker.p1)
                    # <uncal>
                    uncalElement = ET.SubElement(positionElement, "uncal")
                    uncalElement.text = str(spec.cal.E2Ch(marker.p1))
                # <background>
                if not fit.fitter.bgFitter is None:
                    bgElement = ET.SubElement(fitElement,"background")
                    deg = len(fit.bgCoeffs)-1
                    bgElement.set("deg", str(deg))
                    bgElement.set("chisquare", str(fit.bgChi))
                    # <coeff>
                    for i in range(0,deg+1):
                        coeffElement = ET.SubElement(bgElement, "coeff")
                        coeffElement.set("deg", str(i))
                        # <value>
                        valueElement = ET.SubElement(coeffElement, "value")
                        valueElement.text = str(fit.bgCoeffs[i].value)
                        # <error>
                        errorElement = ET.SubElement(coeffElement, "error")
                        errorElement.text = str(fit.bgCoeffs[i].error)
                # <peak>
                for peak in fit.peaks:
                    peakElement = ET.SubElement(fitElement, "peak")
                    # <uncal>
                    uncalElement = ET.SubElement(peakElement, "uncal")
                    # Parameter
                    for param in fit.fitter.fParStatus.iterkeys():
                        paramElement = ET.SubElement(uncalElement, param)
                        status = fit.fitter.fParStatus[param]
                        if type(status)==list:
                            index = fit.peaks.index(peak)
                            status = status[index]
                        paramElement.set("status", str(status))
                        param = getattr(peak, param)
                        if not param is None: 
                            # <value>
                            valueElement = ET.SubElement(paramElement, "value")
                            valueElement.text = str(param.value)
                            # <error>
                            errorElement = ET.SubElement(paramElement, "error")
                            errorElement.text = str(param.error)
                    # <cal>
                    calElement = ET.SubElement(peakElement, "cal")
                    # Parameter
                    for param in fit.fitter.fParStatus.iterkeys():
                        paramElement = ET.SubElement(calElement, param)
                        status = fit.fitter.fParStatus[param]
                        if type(status)==list:
                            index = fit.peaks.index(peak)
                            status = status[index]
                        paramElement.set("status", str(status))
                        param = getattr(peak, "%s_cal" %param)
                        if not param is None: 
                            # <value>
                            valueElement = ET.SubElement(paramElement, "value")
                            valueElement.text = str(param.value)
                            # <error>
                            errorElement = ET.SubElement(paramElement, "error")
                            errorElement.text = str(param.error)
        self.indent(root)
        return root


    def WriteFitlist(self, fname):
        """
        Writes fit list belonging to the currently loaded spectra to xml file
        """
        root = self.CreateXML()
        fname = os.path.expanduser(fname)
        tree = ET.ElementTree(root)
        tree.write(fname)


    def ReadFitlist(self, fnames):
        """
        Read fits from xml file

        This function parses the xml tree to memory and checks the version
        and calls the appropriate function for further processing.
        """
        if type(fnames) in [str,unicode]:
            fnames = [fnames]
        for fname in fnames:
            path = os.path.expanduser(fname)
            for filename in glob.glob(path):
                try:
                    tree = ET.parse(filename)
                    root = tree.getroot()
                
                    if root.get("version").startswith("0"):
                        print "The XML version of %s is old." %fname
                        do_fit = None
                        while not do_fit in ["Y","y","N","n",""]:
                            question = "Do you want to update it to the current version? [Y/n]"
                            print "The old files will be kept as backup with the suffix _v0"
                            print "The conversion will take some time..."
                            do_fit = raw_input(question)
                        if do_fit in ["Y","y",""]:
                            # we first have to delete all fits, that are already open,
                            # because otherwise they also will be saved in the new file                        
                            tmp = self.CreateXML()
                            for spectra in self.spectra.values():
                                try:
                                    spectra.RemoveAll()
                                except AttributeError:
                                    # there are no fits for that spectrum
                                    pass
                            # then we can deal with the old file and do all the fits
                            self.ReadFitlist_v0(root, True)
                            # backup old file
                            os.rename(filename, "%s_v0" %filename)
                            # and write the new file
                            self.WriteFitlist(filename)
                            # afterwards we restore again all the other fits
                            v = VERSION.split('.')[0]
                            newest_ReadFunc = getattr(self, "ReadFitlist_v%s" %v)
                            newest_ReadFunc(tmp)                       
                        else:
                            self.ReadFitlist_v0(root)
                    if root.get("version").startswith("1"):
                        self.ReadFitlist_v1(root)
                except SyntaxError, e:
                    print "Error reading \'" + filename + "\':\n\t", e
                else:
                    print "\'" + filename + "\' loaded."
                    
    def _getPosFromElement(self, XMLelement, fit=None):
        """
        Read position in energy domain from XML element.
        """
        try:
            pos = float(XMLelement.find("uncal").text)
            pos = fit.cal.Ch2E(pos)    
        except AttributeError:
            # Try to read "cal" element if "uncal" element does not exist
            pos = float(XMLelement.find("cal").text)
        return pos
                    

    def ReadFitlist_v1(self, root):
        """
        Reads fits from xml file (version = 1.*) 
    
        This version is able to restore the fits from the XML.
        Changes compared to version 0.*:
            * changed some node namings:
                ** <background> -> <bgMarker>
                ** <region>     -> <regionMarker>
                ** <peak>       -> <peakMarker>
                ** <result>     -> <peak>
            * new node for the background polynome <background>
            * saved chisquare of the fits
            * calibrated and uncalibrated values for each peak parameter
        """
        spectra = self.spectra
        do_fit = None
        # <spectrum>
        for specElement in root.getiterator():
            name = specElement.get("name")
            # find this spectrum from XML in the real world
            spec = None
            for sid in spectra.keys():
                if spectra[sid].fHist.GetName()==name:
                    # maybe we have to create a SpectrumCompound first
                    if not hasattr(spectra[sid], "GetFreeID"):
                        # create SpectrumCompound object 
                        spec = hdtv.spectrum.SpectrumCompound(spectra[sid].viewport, spectra[sid])
                        # replace the simple spectrum object by the SpectrumCompound
                        spectra[sid]=spec
                    spec = spectra[sid]
            # maybe the spectrum that is referred to in XML is currently not loaded
            if spec is None: continue
            # read and set calibration

            try:
                calibration = map(float, specElement.get("calibration").split())
                spec.SetCal(calibration)
            except AttributeError:
                # No calibration was saved
                print "Could not read calibration for spectrum ", name 
                
            # <fit>
            for fitElement in specElement:
                restore_success = True
                peakModel = fitElement.get("peakModel")
                bgdeg = int(fitElement.get("bgDegree"))
                fitter = hdtv.fitter.Fitter(peakModel, bgdeg)
                # <peak>
                params = dict()
                for peakElement in fitElement.findall("peak"):
                    uncalElement = peakElement.find("uncal")
                    for paramElement in uncalElement:
                        parname = paramElement.tag
                        status = paramElement.get("status", "free")
                        try:
                            params[parname].append(status)
                        except KeyError:
                            params[parname]=[status]
                for parname in params.keys():
                    status = params[parname]
                    # check if all values in status are the same
                    if status.count(status[0])==len(status):
                        status = str(status[0])
                    else:
                        status = ','.join(status)
                    fitter.SetParameter(parname, status)
                fit = hdtv.fit.Fit(fitter, spec.color, spec.cal)
                fit.chi = float(fitElement.get("chi"))
                # <bgMarker>
                for bgElement in fitElement.findall("bgMarker"):
                    # Read begin marker
                    beginElement = bgElement.find("begin")
                    begin = self._getPosFromElement(beginElement, fit)   
                    fit.PutBgMarker(begin)
                    
                    # Read end marker
                    endElement = bgElement.find("end");
                    end = self._getPosFromElement(endElement, fit)
                    fit.PutBgMarker(end)
                # <regionMarker>
                for regionElement in fitElement.findall("regionMarker"):
                    # Read begin marker
                    beginElement = regionElement.find("begin");
                    begin = self._getPosFromElement(beginElement, fit)
                    fit.PutRegionMarker(begin)
                    # Read end marker
                    endElement = regionElement.find("end");
                    end = self._getPosFromElement(endElement, fit)
                    fit.PutRegionMarker(end)
                # <peakMarker>
                for peakElement in fitElement.findall("peakMarker"):
                    # Read position marker
                    posElement = peakElement.find("position")
                    pos = self._getPosFromElement(posElement, fit)
                    fit.PutPeakMarker(pos)
                # <background>
                bgElement = fitElement.find("background")
                if bgElement:
                    fit.bgChi = float(bgElement.get("chisquare"))
                    coeffs = list()
                    for coeffElement in bgElement.findall("coeff"):
                        deg = int(coeffElement.get("deg")) 
                        # <value>
                        valueElement = coeffElement.find("value")
                        value = float(valueElement.text)
                        # <error>
                        errorElement = coeffElement.find("error")
                        error = float(errorElement.text)
                        coeff = hdtv.util.ErrValue(value, error)
                        coeffs.append([deg, coeff])
                    coeffs.sort()
                    fit.bgCoeffs = [c[1] for c in coeffs]
                # <peak>
                for peakElement in fitElement.findall("peak"):
                    # <uncal>
                    uncalElement = peakElement.find("uncal")
                    parameter = dict()
                    for paramElement in uncalElement:
                        name = paramElement.tag
                        # <value>
                        valueElement = paramElement.find("value")
                        if valueElement is None:
                            parameter[name]=None
                            continue
                        value = float(valueElement.text)
                        # <error>
                        errorElement = paramElement.find("error")
                        error = float(errorElement.text)
                        status = paramElement.get("status", "free")
                        if status in ["free", "equal", "calculated"]:
                            free = True
                        else:
                            free = False
                        parameter[name] = hdtv.peakmodels.FitValue(value, error, free)
                    try:
                        peak = fit.fitter.peakModel.Peak(cal=spec.cal, **parameter)
                    except TypeError:
                        restore_success = False
                        continue       
                    fit.peaks.append(peak)
                # make sure the peaks are in the right order
                fit.peaks.sort()
                
                if restore_success:
                    try:
                        fit.Restore(spec, silent=True)
                        spec.Add(fit)
                    except TypeError:
                        restore_success = False
                    
                if not restore_success:
                    if do_fit not in ["V", "v"]: # Ne(v)er
                        if do_fit not in ["A", "a"]: # (A)lways
                            do_fit = None
                        while not do_fit in ["Y","y","N","n","", "A", "a", "V", "v"]:
                            question = "Could not restore fit. Refit? [(Y)es/(n)o/(a)lways/ne(v)er]"
                            do_fit = raw_input(question)
                        if do_fit in ["Y", "y", "", "A", "a"]:
                            fit.FitPeakFunc(spec)
                            spec.Add(fit)
                            fit.Focus()
                        
                if not sid in spectra.visible:
                    fit.Hide()
                

    def ReadFitlist_v0(self, root, do_fit=False):
        """
        Reads fits from xml file (version = 0.*) 
    
        Note: For performance reasons this does not reconstruct the fit results. 
        It only sets the markers and restores the status of the fitter. The user 
        must repeat the fit, if he/she wants to see the results again.
        (This should be improved in later versions.)
        """
        spectra = self.spectra
        # <spectrum>
        for specElement in root.getiterator():
            name = specElement.get("name")
            # find this spectrum from Element in the real world
            spec = None
            for sid in spectra.keys():
                if spectra[sid].fHist.GetName()==name:
                    # maybe we have to create a SpectrumCompound first
                    if not hasattr(spectra[sid], "GetFreeID"):
                        # create SpectrumCompound object 
                        spec = hdtv.spectrum.SpectrumCompound(spectra[sid].viewport, spectra[sid])
                        # replace the simple spectrum object by the SpectrumCompound
                        spectra[sid]=spec
                    spec = spectra[sid]
            # maybe the spectrum that is referred to in XML is currently not loaded
            if spec is None: continue
            # <fit>
            for fitElement in specElement:
                peakModel = fitElement.get("peakModel")
                bgdeg = int(fitElement.get("bgDegree"))
                fitter = hdtv.fitter.Fitter(peakModel, bgdeg)
                # <result>
                params = dict()
                for resultElement in fitElement.findall("result"):
                    for paramElement in resultElement:
                        parname = paramElement.tag
                        status = paramElement.get("status")
                        try:
                            params[parname].append(status)
                        except KeyError:
                            params[parname]=[status]
                for parname in params.keys():
                    status = params[parname]
                    # check if all values in status are the same
                    if status.count(status[0])==len(status):
                        status = str(status[0])
                    else:
                        status = ','.join(status)
                    fitter.SetParameter(parname, status)
                fit = hdtv.fit.Fit(fitter, spec.color, spec.cal)
                # <background>
                for bgElement in fitElement.findall("background"):
                    # Read begin/p1 marker
                    beginElement = bgElement.find("begin");
                    if beginElement == None: # Maybe old Element (ver 0.1)
                        beginElement = bgElement.find("p1")
                    begin = float(beginElement.find("uncal").text)
                    fit.PutBgMarker(fit.cal.Ch2E(begin))
                    # Read end/p2 marker
                    endElement = bgElement.find("end");
                    if endElement == None: # Maybe old Element (ver 0.1)
                        endElement = bgElement.find("p2")
                    end = float(endElement.find("uncal").text)
                    fit.PutBgMarker(fit.cal.Ch2E(end))
                # <region>
                for regionElement in fitElement.findall("region"):
                    # Read begin/p1 marker
                    beginElement = regionElement.find("begin");
                    if beginElement == None: # Maybe old Element (ver 0.1)
                        beginElement = regionElement.find("p1")
                    begin = float(beginElement.find("uncal").text)
                    fit.PutRegionMarker(fit.cal.Ch2E(begin))
                    
                    # Read end/p2 marker
                    endElement = regionElement.find("end");
                    if endElement == None: # Maybe old Element (ver 0.1)
                        endElement = regionElement.find("p2")
                    end = float(endElement.find("uncal").text)
                    fit.PutRegionMarker(fit.cal.Ch2E(end))
                # <peak>
                for peakElement in fitElement.findall("peak"):
                    # Read position/p1 marker
                    posElement = peakElement.find("position")
                    if posElement == None:
                        posElement = peakElement.find("p1") 
                    pos = float(posElement.find("uncal").text)
                    fit.PutPeakMarker(fit.cal.Ch2E(pos))
                if do_fit:
                    fit.FitPeakFunc(spec)
                spec.Add(fit)
                

    def indent(self, elem, level=0):
        """
        This function formats the xml in-place for prettyprinting 

        Source: http://effbot.org/zone/element-lib.htm#prettyprint
        """
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i



