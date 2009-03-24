# -*- coding: utf-8 -*-


# works with revision 119

from __main__ import *


def DoFit(spec, fitter, region, peaks, backgrounds):
	"""
	Do the actual fit
	"""
	import hdtv.fit
	fit = hdtv.fit.Fit(fitter.Copy(), cal=spec.cal, color=spec.color)
	for r in region:
		fit.PutRegionMarker(r)
	for b in backgrounds:
		fit.PutBgMarker(b)
	for p in peaks:
		fit.PutPeakMarker(p)
	if len(fit.bgMarkers)>0:
		fit.FitBgFunc(spec)
	fit.FitPeakFunc(spec)
	ID= spec.GetFreeID()
	spec[ID]=fit


def Init(spectra):
	"""
	create SpectrumCompound objects from all spectra
	"""
	for sid in spectra.keys():
		spec = spectra[sid]
		if not hasattr(spec, "GetFreeID"):
			import hdtv.spectrum
			# create SpectrumCompound object 
			spec = hdtv.spectrum.SpectrumCompound(spec.viewport, spec)
			# replace the simple spectrum object by the SpectrumCompound
		spectra[sid]=spec


### start!
spectra.RemoveAll()

s.LoadSpectra(hdtvpath+"/test/spectra/231Th*[down,up].ascii")
s.GetCalsFromList(hdtvpath+"/test/spectra/231Th_calibrations.txt")

Init(spectra)


### f.defaultFitter fit parameter
f.SetPeakModel("theuerkauf")
f.SetParameter("tr", "free")
f.SetBgDeg(1)

#execfile("231Th_42keV.py")




### Peak around 96 keV:
region 		= [85, 106]
peaks		= [96]
backgrounds = [75, 80, 110, 115]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 162 keV and 187 keV:
region 		= [150, 190]
peaks		= [162, 186]
backgrounds = [150, 145, 195, 200] 
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peak around 221 keV:
region 		= [215, 230]
peaks		= [221.6]
backgrounds	= [175, 210, 231, 232]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 241 keV und 248 keV:
region		= [230, 260]
peaks		= [241, 248]
backgrounds = [210, 220, 365, 370]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peak around 273 keV:
region      = [265, 290]
peaks       = [273]
backgrounds = [260, 264, 291, 295]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peak around 302 keV:
region 		= [295, 310]
peaks		= [302]
backgrounds = [260, 262, 365, 370]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 317 keV und 325 keV:
region 		= [310, 340]
peaks 		= [317, 325]
backgrounds = [260, 265, 365, 370]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peak around 351 keV:
region 		= [345, 364]
peaks 		= [351]
backgrounds = [190, 200, 365, 370]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 378 keV, 388 keV:
region		= [370, 395]
peaks		= [378, 388]
backgrounds = [362, 368, 420, 425]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 402 keV:
region 		= [395, 410]
peaks		= [402]
backgrounds = [365, 370, 420, 425]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 447 keV and 466.5 keV:
region 		= [440, 480]
peaks		= [447, 466.5]
backgrounds = [430, 435, 480, 485]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peak around 490.5 keV;
region 		= [485, 500]
peaks		= [490.5]
backgrounds	= [480, 484, 505, 510]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peak around 553 keV:
region 		= [545, 565]
peaks		= [553]
backgrounds = [505, 510, 670, 675]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 578 keV and 592 keV:
region		= [570, 600]
peaks		= [578, 592]
backgrounds	= [565, 568, 610, 615]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 643.5 keV and 653 keV:
region 		= [635, 665]
peaks 		= [643.5, 653]
backgrounds = [620, 630, 670, 675]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 682 keV and 685 keV:
region 		= [675, 695]
peaks		= [682, 685]
backgrounds = [670, 675, 770, 780]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 706 keV, 721 keV, 746 keV:
region		= [ 695, 760]
peaks		= [706, 721, 746]
backgrounds = [730,740]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 801 keV, 806 keV, 814 keV:
region 		= [795, 820]
peaks		= [801, 806, 814]
backgrounds	= [770, 780, 920, 930]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 827 keV, 835 keV, 839 keV, 849 keV:
region 		= [820, 855]
peaks		= [827, 835, 839, 849]
backgrounds = [770, 780, 920, 930]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks between 862 keV and 907 keV:
region 		= [855, 915]
peaks		= [862, 869, 882, 894, 907]
backgrounds	= [770, 780, 920, 930]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 950 kev, and 953 keV:
region 		= [940, 970]
peaks		= [950, 953]
backgrounds = [940, 970]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peak around 980 keV:
region 		= [970, 988]
peaks		= [979]
backgrounds = [920, 930, 1040, 1050]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 1002 keV, 1010.5 keV, 1021 keV:
region 		= [995, 1030]
peaks		= [1002, 1010.5, 1021]
backgrounds	= [920, 630, 1040, 1050]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 1068 keV, 1085.5 keV:
region 		= [1055, 1095]
peaks		= [1068, 1085.5]
backgrounds = [1045, 1050, 1145, 1150]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 1105 keV, 1109 keV:
region 		= [1095, 1115]
peaks     	= [1105, 1109]
backgrounds	= [1090, 1092, 1145, 1150]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peak around 1121 keV:
region		= [115, 1130]
peaks		= [1121]
backgrounds = [1040, 1050, 1145, 1150]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peak around 1139 keV:
region 		= [1130, 1150]
peaks		= [ 1139]
backgrounds = [1040, 1050, 1148, 1150]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)

### Peak around 1169 keV:
region 		= [1162, 1177]
peaks		= [1169]
backgrounds = [1159, 1161, 1189, 1191]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peak around 1183 keV:
region 		= [1175, 1188]
peaks		= [1183]
backgrounds = [1155, 1156, 1174, 1175]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


#### dicker Untergrund zwischen 1190 keV und 1335 keV  in 35 Grad unpol


### Peak around 1345 keV:
region		= [1340, 1351]
peaks		= [1345]
backgrounds = [1339, 1340, 1350, 1352]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peak around 1357 keV:
region 		= [1352, 1366]
peaks		= [1357]
backgrounds = [1350, 1352, 1369, 1373]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peak around 1379 keV:
region		= [1372, 1388]
peaks		= [1379]
backgrounds = [1370, 1372, 1414, 1416]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 1392 keV, 1402 keV, 1410 keV:
region		= [1388, 1415]
peaks		= [1392, 1402.5, 1410]
backgrounds = [1370, 1372, 1415, 1417]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 1423 keV, 1436 keV:
region		= [1415, 1450]
peaks 		= [1423, 1436]
backgrounds = [1372, 1374, 1450, 1452]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 1459 keV, 1470 keV:
region		= [1450, 1475]
peaks 		= [1459, 1470]
backgrounds = [1445, 1450, 1518, 1520]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)


### Peaks around 1500 keV, 1509 keV and 1516 keV:
region 		= [1495, 1522]
peaks 		= [1500, 1509, 1516]
backgrounds = [1490, 1495, 1524, 1526]
fitter = f.defaultFitter.Copy()
for spec in spectra.itervalues():
	DoFit(spec, fitter, region, peaks, backgrounds)

#### und ein paar mehr bei höheren Energien

 


### draw all fits and everything
spectra.Draw(window.viewport)
for spec in spectra.itervalues():
	spec.HideAll()




		
