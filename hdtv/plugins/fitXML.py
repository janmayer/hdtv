import os
import glob
import xml.etree.cElementTree as ET
import hdtv.cmdline
import hdtv.spectrum

# Increase the version number if you changed something related to the xml output.
# If your change affect the reading, you should increase the major number 
# and supply an appropriate new ReadFitlist function for the new xml version.
# If it is just a small change or bug fix, change the minor number.
# There is a script in the test directory, to test reading and writing for 
# some test cases, please make sure that your changes do not break those test cases
VERSION="0.11"

class FitXml:
    """
    Class to save and read fit lists to and from xml file
    """
    def __init__(self, spectra):
        print "loaded fitXML plugin"
        self.spectra = spectra
        # hdtv commands
        self.tv = TvFitXML(self)


    def WriteFitlist(self, filename=None):
        """
        Writes fit list belonging to the currently loaded spectra to xml file
        """
        spectra = self.spectra
        # <hdtv>
        root = ET.Element("hdtv")
        root.set("version", VERSION)    
        # <spectrum>
        for spec in spectra.itervalues():
            if not hasattr(spec, "__len__") or len(spec)==0: continue
            specXML = ET.SubElement(root, "spectrum")
            specXML.set("name", str(spec))
            polynom = str()
            for p in spec.cal.GetCoeffs():
                polynom += " %f "%p
            specXML.set("calibration", polynom.strip())
            # <fit>
            for fit in spec.itervalues():
                fitXML = ET.SubElement(specXML, "fit")
                fitXML.set("peakModel", fit.fitter.peakModel.Name())
                fitXML.set("bgDegree", str(fit.fitter.bgdeg))
                # <background>
                for marker in fit.bgMarkers:
                    markerXML = ET.SubElement(fitXML, "background")
                    # <begin>
                    beginXML = ET.SubElement(markerXML, "begin")
                    # <cal>
                    calXML = ET.SubElement(beginXML, "cal")
                    calXML.text = str(marker.p1)
                    # <uncal>
                    uncalXML = ET.SubElement(beginXML, "uncal")
                    uncalXML.text = str(spec.cal.E2Ch(marker.p1))
                    # <end>
                    p2XML = ET.SubElement(markerXML, "end")
                    # <cal>
                    calXML = ET.SubElement(p2XML, "cal")
                    calXML.text = str(marker.p2)
                    # <uncal>
                    uncalXML = ET.SubElement(p2XML, "uncal")
                    uncalXML.text = str(spec.cal.E2Ch(marker.p2))
                # <region>
                for marker in fit.regionMarkers:
                    markerXML = ET.SubElement(fitXML, "region")
                    # <begin>
                    beginXML = ET.SubElement(markerXML, "begin")
                    # <cal>
                    calXML = ET.SubElement(beginXML, "cal")
                    calXML.text = str(marker.p1)
                    # <uncal>
                    uncalXML = ET.SubElement(beginXML, "uncal")
                    uncalXML.text = str(spec.cal.E2Ch(marker.p1))
                    # <p2>
                    p2XML = ET.SubElement(markerXML, "end")
                    # <cal>
                    calXML = ET.SubElement(p2XML, "cal")
                    calXML.text = str(marker.p2)
                    # <uncal>
                    uncalXML = ET.SubElement(p2XML, "uncal")
                    uncalXML.text = str(spec.cal.E2Ch(marker.p2))
                # <peak>
                for marker in fit.peakMarkers:
                    markerXML = ET.SubElement(fitXML, "peak")
                    # <begin>
                    beginXML = ET.SubElement(markerXML, "position")
                    # <cal>
                    calXML = ET.SubElement(beginXML, "cal")
                    calXML.text = str(marker.p1)
                    # <uncal>
                    uncalXML = ET.SubElement(beginXML, "uncal")
                    uncalXML.text = str(spec.cal.E2Ch(marker.p1))
                # <result>
                for result in fit.fitter.GetResults():
                    resultXML = ET.SubElement(fitXML, "result")
                    # Parameter
                    for param in fit.fitter.fParStatus.iterkeys():
                        paramXML = ET.SubElement(resultXML, param)
                        status = fit.fitter.fParStatus[param]
                        if type(status)==list:
                            index = fit.fitter.GetResults().index(result)
                            status = status[index]
                        paramXML.set("status", str(status))
                        param = getattr(result, param)
                        if not param is None:
                            valueXML = ET.SubElement(paramXML, "value")
                            valueXML.text = str(param.value)
                            errorXML = ET.SubElement(paramXML, "error")
                            errorXML.text = str(param.error)
        self.indent(root)
        if filename:
            tree = ET.ElementTree(root)
            tree.write(os.path.expanduser(filename))
        else:
            ET.dump(root)


    def ReadFitlist(self, fnames):
        """
        Read fits from xml file

        This function parses the xml tree to memory and checks the version
        and calls the appropriate function for further processing.
        """
        if type(fnames) == str or type(fnames) == unicode:
            fnames = [fnames]
        for fname in fnames:
            path = os.path.expanduser(fname)
            for filename in glob.glob(path):
                tree = ET.parse(filename)
                root = tree.getroot()
                if root.get("version").startswith("0"):
                    self.ReadFitlist_v0(root)


    def ReadFitlist_v0(self, root):
        """
        Reads fits from xml file (version = 0.*) 
    
        Note: For performance reasons this does not reconstruct the fit results. 
        It only sets the markers and restores the status of the fitter. The user 
        must repeat the fit, if he/she wants to see the results again.
        (This should be improved in later versions.)
        """
        spectra = self.spectra
        # <spectrum>
        for specXML in root.getiterator():
            name = specXML.get("name")
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
            # <fit>
            for fitXML in specXML:
                peakModel = fitXML.get("peakModel")
                bgdeg = int(fitXML.get("bgDegree"))
                fitter = hdtv.fitter.Fitter(peakModel, bgdeg)
                # <result>
                params = dict()
                for resultXML in fitXML.findall("result"):
                    for paramXML in resultXML:
                        parname = paramXML.tag
                        status = paramXML.get("status")
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
                for bgXML in fitXML.findall("background"):
                    # Read begin/p1 marker
                    beginElement = bgXML.find("begin");
                    if beginElement == None: # Maybe old XML (ver 0.1)
                        beginElement = bgXML.find("p1")
                    begin = float(beginElement.find("uncal").text)
                    fit.PutBgMarker(fit.cal.Ch2E(begin))
                    # Read end/p2 marker
                    endElement = bgXML.find("end");
                    if endElement == None: # Maybe old XML (ver 0.1)
                        endElement = bgXML.find("p2")
                    end = float(endElement.find("uncal").text)
                    fit.PutBgMarker(fit.cal.Ch2E(end))
                # <region>
                for regionXML in fitXML.findall("region"):
                    # Read begin/p1 marker
                    beginElement = regionXML.find("begin");
                    if beginElement == None: # Maybe old XML (ver 0.1)
                        beginElement = regionXML.find("p1")
                    begin = float(beginElement.find("uncal").text)
                    fit.PutRegionMarker(fit.cal.Ch2E(begin))
                    
                    # Read end/p2 marker
                    endElement = regionXML.find("end");
                    if endElement == None: # Maybe old XML (ver 0.1)
                        endElement = regionXML.find("p2")
                    end = float(endElement.find("uncal").text)
                    fit.PutRegionMarker(fit.cal.Ch2E(end))
                # <peak>
                for peakXML in fitXML.findall("peak"):
                    # Read position/p1 marker
                    posElement = peakXML.find("position")
                    if posElement == None:
                        posElement = peakXML.find("p1") 
                    pos = float(posElement.find("uncal").text)
                    fit.PutPeakMarker(fit.cal.Ch2E(pos))
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


class TvFitXML:
    def __init__(self, fitxml):
        self.fitxml = fitxml
        self.spectra = self.fitxml.spectra
        
        # register tv commands
        hdtv.cmdline.command_tree.SetDefaultLevel(1)

        hdtv.cmdline.AddCommand("fit write", lambda args: self.fitxml.WriteFitlist(args[0]), 
                        nargs=1, usage="fit write <filename>")
        hdtv.cmdline.AddCommand("fit read", lambda args: self.fitxml.ReadFitlist(args[0]), 
                        nargs=1, fileargs=True, usage="fit read <filename>")

# plugin initialisation
import __main__
if not hasattr(__main__, "spectra"):
    import hdtv.drawable
    __main__.spectra = hdtv.drawable.DrawableCompound(__main__.window.viewport)
__main__.fitxml = FitXml( __main__.spectra)



