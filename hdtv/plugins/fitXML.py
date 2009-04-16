import xml.etree.ElementTree as ET

def WriteFitlist(spectra, filename=None):
	root = ET.Element("hdtv")
	for spec in spectra.itervalues():
		specXML = ET.SubElement(root, "spectrum")
		specXML.set("name", str(spec))
		polynom = str()
		for p in spec.cal.GetCoeffs():
			polynom += " %f "%p
		specXML.set("calibration", polynom.strip())
		for fit in spec.itervalues():
			fitXML = ET.SubElement(specXML, "fit")
			fitXML.set("peakmodel", fit.fitter.peakModel.Name())
			fitXML.set("bgDegree", str(fit.fitter.bgdeg))
			for marker in fit.bgMarkers:
				markerXML = ET.SubElement(fitXML, "background")
				p1XML = ET.SubElement(markerXML, "p1")
				p1XML.set("calibrated", str(marker.p1))
				p1XML.text = str(spec.cal.E2Ch(marker.p1))
				p2XML = ET.SubElement(markerXML, "p2")
				p2XML.set("calibrated", str(marker.p2))
				p2XML.text = str(spec.cal.E2Ch(marker.p2))
			for marker in fit.regionMarkers:
				markerXML = ET.SubElement(fitXML, "region")
				p1XML = ET.SubElement(markerXML, "p1")
				p1XML.set("calibrated", str(marker.p1))
				p1XML.text = str(spec.cal.E2Ch(marker.p1))
				p2XML = ET.SubElement(markerXML, "p2")
				p2XML.set("calibrated", str(marker.p2))
				p2XML.text = str(spec.cal.E2Ch(marker.p2))
			for marker in fit.peakMarkers:
				markerXML = ET.SubElement(fitXML, "peaks")
				p1XML = ET.SubElement(markerXML, "p1")
				p1XML.set("calibrated", str(marker.p1))
				p1XML.text = str(spec.cal.E2Ch(marker.p1))
			for result in fit.fitter.GetResults():
				resultXML = ET.SubElement(fitXML, "result")
				for param in fit.fitter.fParStatus.iterkeys():
					paramXML = ET.SubElement(resultXML, param)
					status = fit.fitter.fParStatus[param]
					paramXML.set("status", str(status))
					param = getattr(result, param)
					if not param is None:
						valueXML = ET.SubElement(paramXML, "value")
						valueXML.text = str(param.value)
						errorXML = ET.SubElement(paramXML, "error")
						errorXML.text = str(param.error)
	tree = ET.ElementTree(root)
	if filename:
		tree.write(filename)
	else:
		ET.dump(tree)

		
def ReadFitlist(filename):
	tree = ET.parse(filename)
	root = tree.getroot()
	for spec in root.getiterator():
		pass


print "loaded fitXML plugin"

