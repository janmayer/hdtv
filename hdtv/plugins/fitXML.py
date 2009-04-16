import xml.etree.ElementTree as ET

def WriteFitlist(spectra, filename=None, prettyprint=True):
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
				p1XML.set("calibrated", "%.3f" %marker.p1)
				p1XML.text = str(spec.cal.E2Ch(marker.p1))
				p2XML = ET.SubElement(markerXML, "p2")
				p2XML.set("calibrated", "%.3f" %marker.p2)
				p2XML.text = str(spec.cal.E2Ch(marker.p2))
			for marker in fit.regionMarkers:
				markerXML = ET.SubElement(fitXML, "region")
				p1XML = ET.SubElement(markerXML, "p1")
				p1XML.set("calibrated", "%.3f" %marker.p1)
				p1XML.text = str(spec.cal.E2Ch(marker.p1))
				p2XML = ET.SubElement(markerXML, "p2")
				p2XML.set("calibrated", "%.3f" %marker.p2)
				p2XML.text = str(spec.cal.E2Ch(marker.p2))
			for marker in fit.peakMarkers:
				markerXML = ET.SubElement(fitXML, "peaks")
				p1XML = ET.SubElement(markerXML, "p1")
				p1XML.set("calibrated", "%.3f" %marker.p1)
				p1XML.text = str(spec.cal.E2Ch(marker.p1))
			for result in fit.fitter.GetResults():
				resultXML = ET.SubElement(fitXML, "results")
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
	if prettyprint:
		indent(root)
	if filename:
		tree = ET.ElementTree(root)
		tree.write(filename)
	else:
		ET.dump(root)

		
def ReadFitlist(filename):
	tree = ET.parse(filename)
	root = tree.getroot()
	for spec in root.getiterator():
		pass

def indent(elem, level=0):
	"""
	in-place prettyprint formatter
	from: http://effbot.org/zone/element-lib.htm#prettyprint
	"""
	i = "\n" + level*"  "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "  "
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			indent(elem, level+1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i


print "loaded fitXML plugin"

