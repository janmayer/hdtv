import os
import xml.etree.ElementTree as ET
import hdtv.cmdline
import hdtv.spectrum
import __main__ 


def WriteFitlist(filename=None):
	spectra = __main__.spectra
	# <hdtv>
	root = ET.Element("hdtv")
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
			fitXML.set("peakmodel", fit.fitter.peakModel.Name())
			fitXML.set("bgDegree", str(fit.fitter.bgdeg))
			# <background>
			for marker in fit.bgMarkers:
				markerXML = ET.SubElement(fitXML, "background")
				# <p1>
				p1XML = ET.SubElement(markerXML, "p1")
				# <cal>
				calXML = ET.SubElement(p1XML, "cal")
				calXML.text = str(marker.p1)
				# <uncal>
				uncalXML = ET.SubElement(p1XML, "uncal")
				uncalXML.text = str(spec.cal.E2Ch(marker.p1))
				# <p2>
				p2XML = ET.SubElement(markerXML, "p2")
				# <cal>
				calXML = ET.SubElement(p2XML, "cal")
				calXML.text = str(marker.p2)
				# <uncal>
				uncalXML = ET.SubElement(p2XML, "uncal")
				uncalXML.text = str(spec.cal.E2Ch(marker.p2))
			# <region>
			for marker in fit.regionMarkers:
				markerXML = ET.SubElement(fitXML, "region")
				# <p1>
				p1XML = ET.SubElement(markerXML, "p1")
				# <cal>
				calXML = ET.SubElement(p1XML, "cal")
				calXML.text = str(marker.p1)
				# <uncal>
				uncalXML = ET.SubElement(p1XML, "uncal")
				uncalXML.text = str(spec.cal.E2Ch(marker.p1))
				# <p2>
				p2XML = ET.SubElement(markerXML, "p2")
				# <cal>
				calXML = ET.SubElement(p2XML, "cal")
				calXML.text = str(marker.p2)
				# <uncal>
				uncalXML = ET.SubElement(p2XML, "uncal")
				uncalXML.text = str(spec.cal.E2Ch(marker.p2))
			# <peak>
			for marker in fit.peakMarkers:
				markerXML = ET.SubElement(fitXML, "peak")
				# <p1>
				p1XML = ET.SubElement(markerXML, "p1")
				# <cal>
				calXML = ET.SubElement(p1XML, "cal")
				calXML.text = str(marker.p1)
				# <uncal>
				uncalXML = ET.SubElement(p1XML, "uncal")
				uncalXML.text = str(spec.cal.E2Ch(marker.p1))
			# <result>
			for result in fit.fitter.GetResults():
				resultXML = ET.SubElement(fitXML, "result")
				# Parameter
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
	if filename:
		tree = ET.ElementTree(root)
		tree.write(os.path.expanduser(filename))
	else:
		indent(root)
		ET.dump(root)

def ReadFitlist(filename):
	spectra = __main__.spectra
	tree = ET.parse(filename)
	root = tree.getroot()
	for specXML in root.getiterator():
		name == specXML.get("name")
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
		for fitXML in specXML:
			peakModel = fitXML.get("peakModel")
			bgdeg = fitXML.get("bgDegree")
			fitter = hdtv.fitter.Fitter(peakModel, bgdeg)
			fit = hdtv.fit.Fit(fitter, spec.color, spec.cal)
			


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


# command line interface
hdtv.cmdline.AddCommand("fit write", lambda args: WriteFitlist(args[0]), 
						nargs=1, usage="fit write <filename>")
hdtv.cmdline.AddCommand("fit read", lambda args: ReadFitlist(args[0]), 
						nargs=1, usage="fit read <filename>")
print "loaded fitXML plugin"

