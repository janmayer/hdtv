# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2019  The HDTV development team (see file AUTHORS)
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

import xml.etree.ElementTree as ET

from uncertainties import ufloat

import hdtv.ui
from hdtv.cmdline import HDTVCommandError
from hdtv.fit import Fit
from hdtv.fitter import Fitter
from hdtv.util import LockViewport, Position

# Increase the version number if you changed something related to the xml output.
# If your change affect the reading, you should increase the major number
# and supply an appropriate new ReadFitlist function for the new xml version.
# If it is just a small change or bug fix, change the minor number.
#
# Do not remove old ReadFunctions!

VERSION = "1.5"


class FitXml:
    """
    Class to save and read fit lists to and from xml file
    """

    def __init__(self, spectra):
        self.spectra = spectra
        self.version = VERSION
        # Please point the following functions to the appropriate functions
        self.RestoreFromXml = self.RestoreFromXml_v1_5
        self.Xml2Fit = self.Xml2Fit_v1

    #### creating of xml #####################################################
    def WriteFitlist(self, file_object, sid=None):
        """
        Write Fitlist to file
        """
        if sid is None:
            sid = self.spectra.activeID
        try:
            fits = self.spectra.dict[sid].dict
        except KeyError:
            raise HDTVCommandError("No spectrum with id %s loaded." % sid)
        root = self.CreateXml(fits)
        # save to file
        tree = ET.ElementTree(root)
        tree.write(file_object)

    def CreateXml(self, fits):
        """
        Creates a xml tree for fits
        """
        # create xml tree
        root = ET.Element("hdtv")
        root.set("version", VERSION)
        for fit in sorted(fits.values(), key=lambda fit: fit.ID):
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
        for opt, status in fit.fitter.peakModel.fOptStatus.items():
            fitElement.set(opt, str(status))
        fitElement.set("nParams", str(fit.fitter.backgroundModel.fParStatus["nparams"]))
        fitElement.set("chi", str(fit.chi))
        # <spectrum>
        spec = fit.spec
        specElement = ET.SubElement(fitElement, "spectrum")
        specElement.set("name", str(spec.name))
        polynom = " ".join([f"{c:e}" for c in spec.cal.GetCoeffs()])
        specElement.set("calibration", polynom)
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
        bgElement = ET.SubElement(fitElement, "background")
        nparams = len(fit.bgParams)
        bgElement.set("nparams", str(nparams))
        bgElement.set("chisquare", str(fit.bgChi))
        bgElement.set("backgroundModel", fit.fitter.backgroundModel.name)
        # <coeff>
        for i in range(nparams):
            paramElement = ET.SubElement(bgElement, "param")
            paramElement.set("npar", str(i))
            # <value>
            valueElement = ET.SubElement(paramElement, "value")
            valueElement.text = str(fit.bgParams[i].nominal_value)
            # <error>
            errorElement = ET.SubElement(paramElement, "error")
            errorElement.text = str(fit.bgParams[i].std_dev)
        # <peak>
        for peak in fit.peaks:
            peakElement = ET.SubElement(fitElement, "peak")
            # <uncal>
            uncalElement = ET.SubElement(peakElement, "uncal")
            # Parameter
            for param in sorted(fit.fitter.fParStatus.keys()):
                paramElement = ET.SubElement(uncalElement, param)
                status = fit.fitter.fParStatus[param]
                if isinstance(status, list):
                    index = fit.peaks.index(peak)
                    status = status[index]
                paramElement.set("status", str(status))
                param = getattr(peak, param)
                if param is not None:
                    # <value>
                    if param.nominal_value is not None:
                        valueElement = ET.SubElement(paramElement, "value")
                        valueElement.text = str(param.nominal_value)
                    # <error>
                    if param.std_dev is not None:
                        errorElement = ET.SubElement(paramElement, "error")
                        errorElement.text = str(param.std_dev)
            # <cal>
            calElement = ET.SubElement(peakElement, "cal")
            # Parameter
            for param in sorted(fit.fitter.fParStatus.keys()):
                paramElement = ET.SubElement(calElement, param)
                status = fit.fitter.fParStatus[param]
                if isinstance(status, list):
                    index = fit.peaks.index(peak)
                    status = status[index]
                paramElement.set("status", str(status))
                param = getattr(peak, "%s_cal" % param)
                if param is not None:
                    # <value>
                    if param.nominal_value is not None:
                        valueElement = ET.SubElement(paramElement, "value")
                        valueElement.text = str(param.nominal_value)
                    # <error>
                    if param.std_dev is not None:
                        errorElement = ET.SubElement(paramElement, "error")
                        errorElement.text = str(param.std_dev)
            # <extras>
            extraElement = ET.SubElement(peakElement, "extras")
            for param in sorted(peak.extras.keys()):
                paramElement = ET.SubElement(extraElement, param)
                param = peak.extras[param]
                try:
                    if param.nominal_value is not None:
                        valueElement = ET.SubElement(paramElement, "value")
                        valueElement.text = str(param.nominal_value)
                    if param.std_dev is not None:
                        errorElement = ET.SubElement(paramElement, "error")
                        errorElement.text = str(param.std_dev)
                except BaseException:
                    paramElement.text = str(param)
        if fit.integral:
            for integral_type, integral in fit.integral.items():
                if integral is None:
                    continue
                integralElement = ET.SubElement(fitElement, "integral")
                integralElement.set("integraltype", integral_type)
                for cal_type, cal_integral in integral.items():
                    calElement = ET.SubElement(integralElement, cal_type)
                    for name, param in cal_integral.items():
                        if name not in ["id", "stat", "type"]:
                            paramElement = ET.SubElement(calElement, name)
                            if param.nominal_value is not None:
                                valueElement = ET.SubElement(paramElement, "value")
                                valueElement.text = str(param.nominal_value)
                            if param.std_dev is not None:
                                errorElement = ET.SubElement(paramElement, "error")
                                errorElement.text = str(param.std_dev)
        return fitElement

    def _indent(self, elem, level=0):
        """
        This function formats the xml in-place for prettyprinting

        Source: http://effbot.org/zone/element-lib.htm#prettyprint
        See also https://stackoverflow.com/a/4590052
        """
        i = "\n" + level * "  "
        j = "\n" + (level - 1) * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for subelem in elem:
                self._indent(subelem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = j
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = j

    ##### Reading of xml #####################################################

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
        Reads parameter info from a xml element and creates an ufloat
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
        return ufloat(value, error, tag=free)

    def ReadFitlist(
        self,
        file_object,
        sid=None,
        calibrate=False,
        refit=False,
        interactive=True,
        fname=None,
    ):
        """
        Reads fitlist from xml files
        """

        with LockViewport(self.spectra.viewport):
            if sid is None:
                sid = self.spectra.activeID
            if sid not in self.spectra.ids:
                raise HDTVCommandError("No spectrum with id %s loaded." % sid)
            count = 0
            try:
                fname = f"'{fname or file_object.name}'"
            except AttributeError:
                fname = "fitlist"
            try:
                tree = ET.parse(file_object)
                root = tree.getroot()
                if root.tag != "hdtv" or root.get("version") is None:
                    e = "this is not a valid hdtv file"
                    raise SyntaxError(e)
                # current version
                if root.get("version") == self.version:
                    count, fits = self.RestoreFromXml(
                        root,
                        sid,
                        calibrate=calibrate,
                        refit=refit,
                        interactive=interactive,
                    )
                else:
                    # old versions
                    oldversion = root.get("version")
                    hdtv.ui.warning(
                        "The XML version of this file (%s) is outdated." % oldversion
                    )
                    if oldversion == "1.4":
                        hdtv.ui.msg(
                            "But this version should be fully compatible with the new version."
                        )
                        count, fits = self.RestoreFromXml_v1_4(
                            root, sid, calibrate=calibrate, refit=refit
                        )
                    if oldversion == "1.3":
                        hdtv.ui.msg(
                            "But this version should be fully compatible with the new version."
                        )
                        count, fits = self.RestoreFromXml_v1_3(
                            root, sid, calibrate=calibrate, refit=refit
                        )
                    if oldversion == "1.2":
                        hdtv.ui.msg(
                            "But this version should be fully compatible with the new version."
                        )
                        count, fits = self.RestoreFromXml_v1_2(
                            root, sid, calibrate=calibrate, refit=refit
                        )
                    if oldversion == "1.1":
                        hdtv.ui.msg(
                            "But this version should be fully compatible with the new version."
                        )
                        count, fits = self.RestoreFromXml_v1_1(
                            root, sid, calibrate=calibrate, refit=refit
                        )
                    if oldversion == "1.0":
                        hdtv.ui.msg(
                            "Restoring only fits belonging to spectrum %s" % sid
                        )
                        hdtv.ui.msg(
                            "There may be fits belonging to other spectra in this file."
                        )
                        if interactive:
                            input("Please press enter to continue...\n")
                        count, fits = self.RestoreFromXml_v1_0(
                            root, [sid], calibrate=False, refit=refit
                        )
                    if oldversion.startswith("0"):
                        hdtv.ui.msg(
                            "Only the fit markers have been saved in this file."
                        )
                        hdtv.ui.msg("All the fits therefore have to be repeated.")
                        hdtv.ui.msg("This will take some time...")
                        if interactive:
                            input("Please press enter to continue...\n")
                        count, fits = self.RestoreFromXml_v0(root, True)
            except SyntaxError as e:
                raise HDTVCommandError(f"Error reading fits from {fname}.")
            else:
                msg = "%s loaded: " % (fname)
                if count == 1:
                    msg += "1 fit restored."
                else:
                    msg += "%d fits restored." % count
                hdtv.ui.msg(msg)
                return count, fits

    #### version 1* ###############################################################
    def RestoreFromXml_v1_5(
        self, root, sid, calibrate=False, refit=False, interactive=True
    ):
        """
        Restores fits from xml file (version = 1.5)

        Changes to version 1.4:
        Notation of the parameters for the background model has been modified to
        allow for a more general interpretation as arbitrary fit parameters.
        No big change!
        """
        return self.RestoreFromXml_v1_4(
            root, sid, calibrate, refit, interactive=interactive
        )

    def RestoreFromXml_v1_4(
        self, root, sid, calibrate=False, refit=False, interactive=True
    ):
        """
        Restores fits from xml file (version = 1.4)

        Changes to version 1.3:
        Information about the integral over the fit region (and bg, if
        available) are supplied. No big change!
        """

        spec = self.spectra.dict[sid]
        count = 0
        do_fit = ""
        fits = []
        spec_name_last = ""
        for fitElement in root.findall("fit"):
            if calibrate:
                spectrum = fitElement.find("spectrum")
                spec_name = spectrum.get("name")
                spec_cal = spectrum.get("calibration")
                if spec_cal and spec_name != spec_name_last and spec_name:
                    if spec_name != spec.name:
                        hdtv.ui.warning(
                            f"Applying calibration for '{spec_name}' to '{spec.name}'."
                        )
                    spec_name_last = spec_name
                    cal = [float(c) for c in spec_cal.split()]
                    self.spectra.ApplyCalibration([sid], cal)
                    hdtv.ui.debug(f"Applying calibration {spec_cal}.")

            (fit, success) = self.Xml2Fit_v1(fitElement, calibration=spec.cal)
            # restore fit
            if success and not refit:
                try:
                    fit.Restore(spec=spec)
                except (TypeError, IndexError) as err:
                    hdtv.ui.debug("An exception occurred while restoring the peaks")
                    hdtv.ui.debug(err)
                    success = False
            # deal with failure
            if not success or refit:
                if refit:
                    do_fit = "a"
                if do_fit not in ["V", "v"]:  # Ne(v)er
                    if do_fit not in ["A", "a"]:  # (A)lways
                        do_fit = None
                    while do_fit not in ["Y", "y", "N", "n", "", "A", "a", "V", "v"]:
                        question = "Could not restore fit. Refit? [(Y)es/(n)o/(a)lways/ne(v)er]"
                        do_fit = input(question)
                    if do_fit in ["Y", "y", "", "A", "a"]:
                        fit.FitPeakFunc(spec)
            # finish this fit
            fits.append(fit)
        # add fits to spectrum
        for fit in fits:
            spec.Insert(fit)
            count += 1
            if sid not in self.spectra.visible:
                fit.Hide()
        return count, fits

    def RestoreFromXml_v1_3(
        self, root, sid, calibrate=False, refit=False, interactive=True
    ):
        """
        Restores fits from xml file (version = 1.3)

        Changes to version 1.2:
        Now it is possible to store additional user supplied parameter for
        each peak. No big change!
        """
        return self.RestoreFromXml_v1_4(
            root, sid, calibrate, refit, interactive=interactive
        )

    def RestoreFromXml_v1_2(
        self, root, sid, calibrate=False, refit=False, interactive=True
    ):
        """
        Restores fits from xml file (version = 1.2)

        Changes to version 1.1:
        Calibrated AND Uncalibrated marker positions are saved in version 1.2,
        where as in version 1.1 only one of both has been saved. No big change!
        """
        return self.RestoreFromXml_v1_3(
            root, sid, calibrate, refit, interactive=interactive
        )

    def RestoreFromXml_v1_1(
        self, root, sid, calibrate=False, refit=False, interactive=True
    ):
        """
        Restores fits from xml file (version = 1.1)

        Changes compared to version 1.0:
        In this version a file contains only fits belonging to one spectra
        this changes the xml hierachy a little, the fit elements are now direct
        childs of the root element. The spectrum element is still there, but now
        a child of each fit element and not longer used in hdtv for anything
        """
        return self.RestoreFromXml_v1_2(
            root, sid, calibrate, refit, interactive=interactive
        )

    def RestoreFromXml_v1_0(
        self, root, sids=None, calibrate=False, refit=False, interactive=False
    ):
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
        index = {}
        for specElement in root.iter():
            name = specElement.get("name")
            index[name] = specElement
        # <spectrum>
        all_fits = []
        for sid in sids:
            spec = self.spectra.dict[sid]
            try:
                specElement = index[spec.name]
            except KeyError:
                #    msg ="No informations for spectrum %s (id=%d) in file" %(spec, sid)
                #    hdtv.ui.warning(msg)
                continue
            # load the calibration from file
            if calibrate:
                try:
                    calibration = list(
                        map(float, specElement.get("calibration").split())
                    )
                    spec.cal = calibration
                except AttributeError:
                    # No calibration was saved
                    msg = "Could not read calibration for spectrum %s (id=%d)" % (
                        spec,
                        sid,
                    )
                    hdtv.ui.warning(msg)
            # <fits>
            fits = []
            for fitElement in specElement.findall("fit"):
                (fit, success) = self.Xml2Fit_v1(fitElement, spec.cal)
                count = count + 1
                # restore fit
                if success and not refit:
                    try:
                        fit.Restore(spec=spec)
                    except (TypeError, IndexError):
                        success = False
                # deal with failure
                if not success or refit:
                    if refit:
                        do_fit = "a"
                    if do_fit not in ["V", "v"]:  # Ne(v)er
                        if do_fit not in ["A", "a"]:  # (A)lways
                            do_fit = None
                        while do_fit not in [
                            "Y",
                            "y",
                            "N",
                            "n",
                            "",
                            "A",
                            "a",
                            "V",
                            "v",
                        ]:
                            question = "Could not restore fit. Refit? [(Y)es/(n)o/(a)lways/ne(v)er]"
                            do_fit = input(question)
                        if do_fit in ["Y", "y", "", "A", "a"]:
                            fit.FitPeakFunc(spec)
                # finish this fit
                spec.Insert(fit)
                if sid not in self.spectra.visible:
                    fit.Hide()
                fits.append(fit)
                all_fits.append(fit)
        return count, all_fits

    def Xml2Fit_v1(self, fitElement, calibration=None):
        """
        Creates a fit object from information found in a xml file
        """
        # <fit>
        success = True
        peakModel = fitElement.get("peakModel")
        bgElement = fitElement.find("background")
        # Simple fix for older xml file versions, where the only background
        # model was a polynomial, and therefore it did not have to be stored

        try:
            backgroundModel = bgElement.get("backgroundModel")
        except AttributeError:
            backgroundModel = "polynomial"
        if backgroundModel is None:
            backgroundModel = "polynomial"
        fitter = Fitter(peakModel, backgroundModel)
        fit = Fit(fitter, cal=calibration)

        for opt in fitter.peakModel.fOptStatus:
            if opt in fitElement.attrib:
                fitter.SetParameter(opt, fitElement.get(opt))
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
            endElement = bgElement.find("end")
            end = self._getPosFromElement(endElement, fit)
            fit.ChangeMarker("bg", end, "set")
        # <regionMarker>
        for regionElement in fitElement.findall("regionMarker"):
            # Read begin marker
            beginElement = regionElement.find("begin")
            begin = self._getPosFromElement(beginElement, fit)
            fit.ChangeMarker("region", begin, "set")
            # Read end marker
            endElement = regionElement.find("end")
            end = self._getPosFromElement(endElement, fit)
            fit.ChangeMarker("region", end, "set")
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
                pass
            params = []

            # Distinguish between old notation of background parameters (coeff, ncoeff),
            # which interprets the parameters as coefficients of a polynomial, and the
            # new notation (params, npar), which interprets them as arbitrary parameters.
            paramCounterName = "npar"
            paramElements = bgElement.findall("param")
            if not paramElements:
                paramElements = bgElement.findall("coeff")
                paramCounterName = "deg"

            for paramElement in paramElements:
                npar = int(paramElement.get(paramCounterName))
                # <value>
                valueElement = paramElement.find("value")
                value = float(valueElement.text)
                # <error>
                errorElement = paramElement.find("error")
                error = float(errorElement.text)
                param = ufloat(value, error)
                params.append([npar, param])
            params.sort()
            fit.bgParams = [p[1] for p in params]

        # <peak>
        statusdict = {}
        for peakElement in fitElement.findall("peak"):
            # <uncal>
            uncalElement = peakElement.find("uncal")
            parameter = {}
            for paramElement in uncalElement:
                # parameter value/error
                name = paramElement.tag
                parameter[name] = self._readParamElement(paramElement)
                # parameter status
                status = paramElement.get("status", "free")
                try:
                    statusdict[name].append(status)
                except KeyError:
                    statusdict[name] = [status]
            # <extras>
            extraElement = peakElement.find("extras")
            extras = {}
            if extraElement is not None:
                for paramElement in extraElement:
                    name = paramElement.tag
                    if len(paramElement) == 1:
                        extras[name] = paramElement.text
                    else:
                        # <value>
                        valueElement = paramElement.find("value")
                        value = float(valueElement.text)
                        # <error>
                        errorElement = paramElement.find("error")
                        error = float(errorElement.text)
                        extras[name] = ufloat(value, error)
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
            for name in list(statusdict.keys()):
                # check if status is the same for all peaks
                check = set(statusdict[name])
                if len(check) == 1:
                    status = statusdict[name][0]
                else:
                    status = statusdict[name]
                fitter.SetParameter(name, status)
        integrals = {}
        for integral in fitElement.findall("integral"):
            integral_type = integral.get("integraltype")
            integrals[integral_type] = {}
            for calElement in integral:
                cal_type = calElement.tag
                integrals[integral_type][cal_type] = {}
                for paramElement in calElement:
                    # <value>
                    valueElement = paramElement.find("value")
                    value = float(valueElement.text)
                    # <error>
                    errorElement = paramElement.find("error")
                    error = float(errorElement.text)
                    coeff = ufloat(value, error)
                    integrals[integral_type][cal_type][paramElement.tag] = coeff
        if not integrals:
            integrals = None
        for integral_type in ["sub", "bg"]:
            if integrals and integral_type not in integrals:
                integrals[integral_type] = None
        fit.integral = integrals
        return (fit, success)

    ##### version 0.* ########################################################

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
        for specElement in root.iter():
            name = specElement.get("name")
            # find this spectrum from Element in the real world
            spec = None
            for sid in spectra.ids:
                if spectra.dict[sid].name == name:
                    spec = spectra.dict[sid]
            # maybe the spectrum that is referred to in XML is currently not
            # loaded
            if spec is None:
                continue
            # <fit>
            for fitElement in specElement:
                count = count + 1
                peakModel = fitElement.get("peakModel")
                # Simple fix for older xml file versions, where the only background
                # model was a polynomial, and therefore it did not have to be stored
                fitter = Fitter(peakModel, "polynomial")
                # <result>
                params = {}
                for resultElement in fitElement.findall("result"):
                    for paramElement in resultElement:
                        parname = paramElement.tag
                        status = paramElement.get("status")
                        try:
                            params[parname].append(status)
                        except KeyError:
                            params[parname] = [status]
                for parname in list(params.keys()):
                    status = params[parname]
                    fitter.SetParameter(parname, status)
                fit = Fit(fitter, cal=spec.cal)
                # <background>
                for bgElement in fitElement.findall("background"):
                    # Read begin/p1 marker
                    beginElement = bgElement.find("begin")
                    if beginElement is None:  # Maybe old Element (ver 0.1)
                        beginElement = bgElement.find("p1")
                    begin = float(beginElement.find("uncal").text)
                    fit.ChangeMarker("bg", fit.cal.Ch2E(begin), "set")
                    # Read end/p2 marker
                    endElement = bgElement.find("end")
                    if endElement is None:  # Maybe old Element (ver 0.1)
                        endElement = bgElement.find("p2")
                    end = float(endElement.find("uncal").text)
                    fit.ChangeMarker("bg", fit.cal.Ch2E(end), "set")
                # <region>
                for regionElement in fitElement.findall("region"):
                    # Read begin/p1 marker
                    beginElement = regionElement.find("begin")
                    if beginElement is None:  # Maybe old Element (ver 0.1)
                        beginElement = regionElement.find("p1")
                    begin = float(beginElement.find("uncal").text)
                    fit.ChangeMarker("region", fit.cal.Ch2E(begin), "set")
                    # Read end/p2 marker
                    endElement = regionElement.find("end")
                    if endElement is None:  # Maybe old Element (ver 0.1)
                        endElement = regionElement.find("p2")
                    end = float(endElement.find("uncal").text)
                    fit.ChangeMarker("region", fit.cal.Ch2E(end), "set")
                # <peak>
                for peakElement in fitElement.findall("peak"):
                    # Read position/p1 marker
                    posElement = peakElement.find("position")
                    if posElement is None:
                        posElement = peakElement.find("p1")
                    pos = float(posElement.find("uncal").text)
                    fit.ChangeMarker("peak", fit.cal.Ch2E(pos), "set")
                if do_fit:
                    fit.FitPeakFunc(spec)
                spec.Insert(fit)
            return count, [fit]
