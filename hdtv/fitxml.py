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

import hdtv.ui

from hdtv.util import Position
from hdtv.errvalue import ErrValue
from hdtv.fitter import Fitter
from hdtv.fit import Fit
from hdtv.peakmodels import FitValue, PeakModels

# Increase the version number if you changed something related to the xml output.
# If your change affect the reading, you should increase the major number 
# and supply an appropriate new ReadFitlist function for the new xml version.
# If it is just a small change or bug fix, change the minor number.
#
# Do not remove old ReadFunctions!
#
# There is a script in the test directory, to test reading and writing for 
# some test cases, please make sure that your changes do not break those test cases
VERSION="1.3"

class FitXml:
    """
    Class to save and read fit lists to and from xml file
    """
    def __init__(self, spectra):
      self.spectra = spectra
      self.version = VERSION
      # Please point the following functions to the appropriate functions
      self.RestoreFromXml = self.RestoreFromXml_v1_3
      self.Xml2Fit = self.Xml2Fit_v1
      
#### creating of xml ###########################################################
    def WriteFitlist(self, fname, sid=None):
        """
        Write Fitlist to file
        """
        if sid is None:
            sid = self.spectra.activeID
        try:
            fits = self.spectra.dict[sid].dict
        except KeyError:
            hdtv.ui.error("No spectrum with id %s loaded.") %sid
            return
        if len(fits)==0:
            hdtv.ui.warn("Empty fitlist, no action taken.")
            return
        root = self.CreateXml(fits)
        # save to file
        tree = ET.ElementTree(root)
        tree.write(fname)
            
    def CreateXml(self, fits):
        """
        Creates a xml tree for fits
        """
        # create xml tree
        root = ET.Element("hdtv")
        root.set("version", VERSION)
        for fit in fits.itervalues():
            root.append(self.Fit2Xml(fit))
        self._indent(root)
        return root
            
    def Fit2Xml(self, fit):
        """
        Creates xml element for a fit
        """
        # <fit>
        fitElement = ET.Element("fit")
        fitElement.set("peakModel", fit.fitter.peakModel.name)
        fitElement.set("bgDegree", str(fit.fitter.bgdeg))
        fitElement.set("chi", str(fit.chi))
        # <spectrum>
        spec = fit.spec
        specElement = ET.SubElement(fitElement,"spectrum")
        specElement.set("name", str(spec.name))
        polynom = str()
        for p in spec.cal.GetCoeffs():
            polynom += " %f "%p
        specElement.set("calibration", polynom.strip())
        # <bgMarker>
        for marker in fit.bgMarkers:
            markerElement = ET.SubElement(fitElement, "bgMarker")
            # <begin>
            beginElement = ET.SubElement(markerElement, "begin")
            # <cal>
            calElement = ET.SubElement(beginElement, "cal")
            calElement.text = str(marker.p1.pos_cal)
            # <uncal>
            uncalElement = ET.SubElement(beginElement, "uncal")
            uncalElement.text = str(marker.p1.pos_uncal)
            # <end>
            endElement = ET.SubElement(markerElement, "end")
            # <cal>
            calElement = ET.SubElement(endElement, "cal")
            calElement.text = str(marker.p2.pos_cal)
            # <uncal>
            uncalElement = ET.SubElement(endElement, "uncal")
            uncalElement.text = str(marker.p2.pos_uncal)
        # <regionMarker>
        for marker in fit.regionMarkers:
            markerElement = ET.SubElement(fitElement, "regionMarker")
            # <begin>
            beginElement = ET.SubElement(markerElement, "begin")
            # <cal>
            calElement = ET.SubElement(beginElement, "cal")
            calElement.text = str(marker.p1.pos_cal)
            # <uncal>
            uncalElement = ET.SubElement(beginElement, "uncal")
            uncalElement.text = str(marker.p1.pos_uncal)
            # <p2>
            endElement = ET.SubElement(markerElement, "end")
            # <cal>
            calElement = ET.SubElement(endElement, "cal")
            calElement.text = str(marker.p2.pos_cal)
            # <uncal>
            uncalElement = ET.SubElement(endElement, "uncal")
            uncalElement.text = str(marker.p2.pos_uncal)
        # <peakMarker>
        for marker in fit.peakMarkers:
            markerElement = ET.SubElement(fitElement, "peakMarker")
            # <begin>
            positionElement = ET.SubElement(markerElement, "position")
            # <cal>
            calElement = ET.SubElement(positionElement, "cal")
            calElement.text = str(marker.p1.pos_cal)
            # <uncal>
            uncalElement = ET.SubElement(positionElement, "uncal")
            uncalElement.text = str(marker.p1.pos_uncal) 
        # <background>
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
                    if not param.value is None:
                        valueElement = ET.SubElement(paramElement, "value")
                        valueElement.text = str(param.value)
                    # <error>
                    if not param.error is None:
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
                    if not param.value is None:
                        valueElement = ET.SubElement(paramElement, "value")
                        valueElement.text = str(param.value)
                    # <error>
                    if not param.error is None:
                        errorElement = ET.SubElement(paramElement, "error")
                        errorElement.text = str(param.error)
            # <extras>
            extraElement = ET.SubElement(peakElement, "extras")
            for param in peak.extras.keys():
                paramElement = ET.SubElement(extraElement, param)
                param = peak.extras[param]
                try:
                    if not param.value is None:
                        valueElement = ET.SubElement(paramElement, "value")
                        valueElement.text = str(param.value)
                    if not param.error is None:
                        errorElement = ET.SubElement(paramElement, "error")
                        errorElement.text = str(param.error)
                except:
                    paramElement.text = str(param)
        return fitElement
        
    def _indent(self, elem, level=0):
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
                self._indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
        
##### Reading of xml ###########################################################
    
    def _getPosFromElement(self, markerElement, fit=None):
        """
        Read position in energy domain from XML element.
        """
        try:
            uncal = float(markerElement.find("uncal").text)
            pos = Position(uncal, fixedInCal=False, cal=fit.cal)
        except AttributeError:
            # Try to read "cal" element if "uncal" element does not exist
            cal = float(markerElement.find("cal").text)
            pos = Position(cal, fixedInCal=True, cal=fit.cal)
        return pos
    
    def _readParamElement(self, paramElement):
        """
        Reads parameter info from a xml element and creates a FitValue object
        """
        # status
        status = paramElement.get("status", "free")
        if status == "none":
            return None
        
        if status in ["free", "equal", "calculated"]:
            free = True
        else:
            free = False
        # <value>
        valueElement = paramElement.find("value")
        if valueElement is None or valueElement.text == "None":
            return None
        else:
            value = float(valueElement.text)
        # <error>
        errorElement = paramElement.find("error")
        error = float(errorElement.text)
        return FitValue(value, error, free)
        
    # FIXME: remove!
    def ReadPeaks(self, root):
        """
        Creates a list of peaks from xml data.
        This function reads only the peak data and ignores everything else,
        the peak objects are independent of a specific fit or spectrum and 
        have a fixed calibration. 
        Note: This is for standalone use, it is not possible to restore fits 
        with this list.
        """
        peaks = list()
        for fitElement in root.findall("fit"):
            peakmodel = PeakModels(fitElement.get("peakModel"))
            for peakElement in fitElement.findall("peak"):
                # <uncal>
                uncalElement = peakElement.find("uncal")
                parameter = dict()
                for paramElement in uncalElement:
                    name = paramElement.tag
                    parameter[name] = self._readParamElement(paramElement)
                peak = peakmodel(cal=None, **parameter)
                # additional parameter
                parameter = dict()
                # <cal>
                for paramElement in peakElement.findall("cal"):
                    name = paramElement.tag
                    parameter[name] = self._readParamElement(paramElement)
                # <more>
                for paramElement in peakElement.findall("more"):
                    name = paramElement.tag
                    parameter[name] = self._readParamElement(paramElement)
                for name in parameter.keys():
                    print name
                    setattr(peak, name, parameter[name])
                peaks.append(peak)
        return peaks


    def ReadFitlist(self, fname, sid=None, refit=False):
        """
        Reads fitlist from xml files
        """
        self.spectra.viewport.LockUpdate()
        if sid is None:
            sid = self.spectra.activeID
        if not sid in self.spectra.ids:
            hdtv.ui.error("No spectrum with id %s loaded.") %sid
            return
        count = 0
        try:
            tree = ET.parse(fname)
            root = tree.getroot()
            if not root.tag=="hdtv" or root.get("version") is None:
                e = "this is not a valid hdtv file"
                raise SyntaxError, e
            # current version
            if root.get("version")==self.version:
                count = self.RestoreFromXml(root, sid, refit=refit)
            else:
                # old versions
                oldversion = root.get("version")
                hdtv.ui.warn("The XML version of this file (%s) is outdated." %oldversion)
                if oldversion=="1.2":
                    hdtv.ui.msg("But this version should be fully compatible with the new version.")
                    count = self.RestoreFromXml_v1_2(root, sid, refit=refit)
                if oldversion=="1.1":
                    hdtv.ui.msg("But this version should be fully compatible with the new version.")
                    count = self.RestoreFromXml_v1_1(root, sid, refit=refit)
                if oldversion=="1.0":
                    hdtv.ui.msg("Restoring only fits belonging to spectrum %s" % sid)
                    hdtv.ui.msg("There may be fits belonging to other spectra in this file.")
                    raw_input("Please press enter to continue...\n")
                    count = self.RestoreFromXml_v1_0(root, [sid], calibrate=False, refit=refit)
                if oldversion.startswith("0"):
                    hdtv.ui.msg("Only the fit markers have been saved in this file.")
                    hdtv.ui.msg("All the fits therefor have to be repeated.")
                    hdtv.ui.msg("This will take some time...")
                    raw_input("Please press enter to continue...\n")
                    count = self.RestoreFromXml_v0(root, True)
        except SyntaxError, e:
            print "Error reading \'" + fname + "\':\n\t", e
        else:
            msg = "\'%s\' loaded" %(fname)
            if count ==1:
                msg+= ": 1 fit restored."
            else:
                msg+= ": %d fits restored" %count
            hdtv.ui.msg(msg)
        finally:
            self.spectra.viewport.UnlockUpdate()

#### version 1* ###############################################################
    def RestoreFromXml_v1_3(self, root, sid, refit=False):
        """
        Restores fits from xml file (version = 1.3)
        
        Changes to version 1.2:
        Now it is possible to store additional user supplied parameter for
        each peak. No big change!
        """
        spec = self.spectra.dict[sid]
        count = 0
        do_fit = ""
        fits = list()
        for fitElement in root.findall("fit"):
            (fit, success) = self.Xml2Fit_v1(fitElement, calibration=spec.cal)
            # restore fit
            if success and not refit:
                try:
                    fit.Restore(spec=spec, silent=True)
                except (TypeError, IndexError):
                    success = False
            # deal with failure
            if not success or refit:
                if refit:
                    do_fit = "a"
                if do_fit not in ["V", "v"]: # Ne(v)er
                    if do_fit not in ["A", "a"]: # (A)lways
                        do_fit = None
                    while not do_fit in ["Y","y","N","n","", "A", "a", "V", "v"]:
                        question = "Could not restore fit. Refit? [(Y)es/(n)o/(a)lways/ne(v)er]"
                        do_fit = raw_input(question)
                    if do_fit in ["Y", "y", "", "A", "a"]:
                        fit.FitPeakFunc(spec)
            # finish this fit
            fits.append(fit)
        # add fits to spectrum
        fits.sort()
        for fit in fits:
            ID = spec.Insert(fit)
            count += 1
            if not sid in self.spectra.visible:
                fit.Hide()
        return count
        
    def RestoreFromXml_v1_2(self, root, sid, refit=False):
        """
        Restores fits from xml file (version = 1.2)
        
        Changes to version 1.1:
        Calibrated AND Uncalibrated marker positions are saved in version 1.2,
        where as in version 1.1 only one of both has been saved. No big change!
        """
        return self.RestoreFromXml_v1_3(root, sid, refit)
        
    def RestoreFromXml_v1_1(self, root, sid, refit=False):
        """
        Restores fits from xml file (version = 1.1)
        
        Changes compared to version 1.0:
        In this version a file contains only fits belonging to one spectra
        this changes the xml hierachy a little, the fit elements are now direct 
        childs of the root element. The spectrum element is still there, but now 
        a child of each fit element and not longer used in hdtv for anything
        """
        return self.RestoreFromXml_v1_2(root, sid, refit)
        
    def RestoreFromXml_v1_0(self, root, sids=None, calibrate=False, refit=False):
        """
        Restores fits from xml file (version = 1.0) 
    
        This version is able to restore the fits from the XML.
        Changes compared to version 0.1:
            * changed some node namings:
                ** <background> -> <bgMarker>
                ** <region>     -> <regionMarker>
                ** <peak>       -> <peakMarker>
                ** <result>     -> <peak>
            * new node for the background polynomial <background>
            * saved chisquare of the fits
            * calibrated and uncalibrated values for each peak parameter
        """
        do_fit = None
        count = 0
        # default is to look for all loaded spectra
        if sids is None:
            sids = self.spectra.ids
        # create an index of spectra that are saved in xml
        index = dict()
        for specElement in root.getiterator():
            name = specElement.get("name")
            index[name] = specElement
        # <spectrum>
        for sid in sids:
            spec = self.spectra.dict[sid]
            try:
                specElement = index[spec.name]
            except KeyError:
            #    msg ="No informations for spectrum %s (id=%d) in file" %(spec, sid)
            #    hdtv.ui.warn(msg)
                continue
            # load the calibration from file
            if calibrate:
                try:
                    calibration = map(float, specElement.get("calibration").split())
                    spec.cal = calibration
                except AttributeError:
                    # No calibration was saved
                    msg ="Could not read calibration for spectrum %s (id=%d)" % (spec,sid)
                    hdtv.ui.warn(msg)
            # <fits>
            fits = list()
            for fitElement in specElement.findall("fit"):
                (fit, success) = self.Xml2Fit_v1(fitElement, spec.cal)
                count = count+1
                # restore fit
                if success and not refit:
                    try:
                        fit.Restore(spec=spec, silent=True)
                    except (TypeError, IndexError):
                        success = False
                # deal with failure
                if not success or refit:
                    if refit:
                        do_fit = "a"
                    if do_fit not in ["V", "v"]: # Ne(v)er
                        if do_fit not in ["A", "a"]: # (A)lways
                            do_fit = None
                        while not do_fit in ["Y","y","N","n","", "A", "a", "V", "v"]:
                            question = "Could not restore fit. Refit? [(Y)es/(n)o/(a)lways/ne(v)er]"
                            do_fit = raw_input(question)
                        if do_fit in ["Y", "y", "", "A", "a"]:
                            fit.FitPeakFunc(spec)
                # finish this fit
                ID = spec.Insert(fit)
                if not sid in self.spectra.visible:
                    fit.Hide()
        return count

    def Xml2Fit_v1(self, fitElement, calibration=None):
        """
        Creates a fit object from information found in a xml file
        """
        # <fit>
        success = True
        peakModel = fitElement.get("peakModel")
        bgdeg = int(fitElement.get("bgDegree"))
        fitter = Fitter(peakModel, bgdeg)
        fit = Fit(fitter, cal=calibration)
        try:
            fit.chi = float(fitElement.get("chi"))
        except ValueError:
            fit.chi = None
        # <bgMarker>
        for bgElement in fitElement.findall("bgMarker"):
            # Read begin marker
            beginElement = bgElement.find("begin")
            begin = self._getPosFromElement(beginElement, fit)   
            fit.ChangeMarker("bg", begin, "set")
            # Read end marker
            endElement = bgElement.find("end");
            end = self._getPosFromElement(endElement, fit)
            fit.ChangeMarker("bg",end, "set")
        # <regionMarker>
        for regionElement in fitElement.findall("regionMarker"):
            # Read begin marker
            beginElement = regionElement.find("begin")
            begin = self._getPosFromElement(beginElement, fit)
            fit.ChangeMarker("region",begin,"set")
            # Read end marker
            endElement = regionElement.find("end");
            end = self._getPosFromElement(endElement, fit)
            fit.ChangeMarker("region",end, "set")
            # <peakMarker>
        for peakElement in fitElement.findall("peakMarker"):
            # Read position marker
            posElement = peakElement.find("position")
            pos = self._getPosFromElement(posElement, fit)
            fit.ChangeMarker("peak", pos, "set")
        # <background>
        bgElement = fitElement.find("background")
        if bgElement:
            try: 
                fit.bgChi = float(bgElement.get("chisquare"))
            except ValueError:
                hdtv.ui.error("Error reading chisquare for background element: %s" % bgElement.get("chisquare"))
                success = False
            coeffs = list()
            for coeffElement in bgElement.findall("coeff"):
                deg = int(coeffElement.get("deg")) 
                # <value>
                valueElement = coeffElement.find("value")
                value = float(valueElement.text)
                # <error>
                errorElement = coeffElement.find("error")
                error = float(errorElement.text)
                coeff = ErrValue(value, error)
                coeffs.append([deg, coeff])
            coeffs.sort()
            fit.bgCoeffs = [c[1] for c in coeffs]
        # <peak>
        statusdict=dict()
        for peakElement in fitElement.findall("peak"):
            # <uncal>
            uncalElement = peakElement.find("uncal")
            parameter = dict()
            for paramElement in uncalElement:
                # parameter value/error
                name = paramElement.tag
                parameter[name] = self._readParamElement(paramElement)
                # parameter status
                status = paramElement.get("status", "free")
                try:
                    statusdict[name].append(status)
                except KeyError:
                    statusdict[name]=[status]
            # <extras>
            extraElement = peakElement.find("extras")
            extras = dict()
            if extraElement is not None:
                for paramElement in extraElement:
                    name = paramElement.tag
                    if len(paramElement) ==1:
                        extras[name] = paramElement.text
                    else:
                        # <value>
                        valueElement = paramElement.find("value")
                        value = float(valueElement.text)
                        # <error>
                        errorElement = paramElement.find("error")
                        error = float(errorElement.text)
                        extras[name] = ErrValue(value, error)
            # create peak
            try:
                peak = fit.fitter.peakModel.Peak(cal=calibration, **parameter)
            except TypeError:
                hdtv.ui.error("Error reading peak with parameters: %s" % str(parameter))
                success = False
                continue
            peak.extras = extras
            fit.peaks.append(peak)
            # set parameter status of fitter
            for name in statusdict.keys():
                status = statusdict[name]
                # check if all values in status are the same
                if status.count(status[0])==len(status):
                    status = str(status[0])
                else:
                    status = ','.join(status)
                fitter.SetParameter(name, status)
        return (fit, success)

##### version 0.* ##############################################################

    def RestoreFromXml_v0(self, root, do_fit=False):
        """
        Reads fits from xml file (version = 0.*) 
    
        Note: For performance reasons this does not reconstruct the fit results. 
        It only sets the markers and restores the status of the fitter. The user 
        must repeat the fit, if he/she wants to see the results again.
        (This should be improved in later versions.)
        """
        count = 0
        spectra = self.spectra
        # <spectrum>
        for specElement in root.getiterator():
            name = specElement.get("name")
            # find this spectrum from Element in the real world
            spec = None
            for sid in spectra.ids:
                if spectra.dict[sid].name==name:
                    spec = spectra.dict[sid]
            # maybe the spectrum that is referred to in XML is currently not loaded
            if spec is None: continue
            # <fit>
            for fitElement in specElement:
                count = count+1
                peakModel = fitElement.get("peakModel")
                bgdeg = int(fitElement.get("bgDegree"))
                fitter = itter(peakModel, bgdeg)
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
                fit = Fit(fitter, cal=spec.cal)
                # <background>
                for bgElement in fitElement.findall("background"):
                    # Read begin/p1 marker
                    beginElement = bgElement.find("begin");
                    if beginElement == None: # Maybe old Element (ver 0.1)
                        beginElement = bgElement.find("p1")
                    begin = float(beginElement.find("uncal").text)
                    fit.ChangeMarker("bg", fit.cal.Ch2E(begin), "set")
                    # Read end/p2 marker
                    endElement = bgElement.find("end");
                    if endElement == None: # Maybe old Element (ver 0.1)
                        endElement = bgElement.find("p2")
                    end = float(endElement.find("uncal").text)
                    fit.ChangeMarker("bg",fit.cal.Ch2E(end), "set")
                # <region>
                for regionElement in fitElement.findall("region"):
                    # Read begin/p1 marker
                    beginElement = regionElement.find("begin");
                    if beginElement == None: # Maybe old Element (ver 0.1)
                        beginElement = regionElement.find("p1")
                    begin = float(beginElement.find("uncal").text)
                    fit.ChangeMarker("region",fit.cal.Ch2E(begin),"set")
                    # Read end/p2 marker
                    endElement = regionElement.find("end");
                    if endElement == None: # Maybe old Element (ver 0.1)
                        endElement = regionElement.find("p2")
                    end = float(endElement.find("uncal").text)
                    fit.ChangeMarker("region", fit.cal.Ch2E(end), "set")
                # <peak>
                for peakElement in fitElement.findall("peak"):
                    # Read position/p1 marker
                    posElement = peakElement.find("position")
                    if posElement == None:
                        posElement = peakElement.find("p1") 
                    pos = float(posElement.find("uncal").text)
                    fit.ChangeMarker("peak",fit.cal.Ch2E(pos), "set")
                if do_fit:
                    fit.FitPeakFunc(spec)
                spec.Insert(fit)
            return count


