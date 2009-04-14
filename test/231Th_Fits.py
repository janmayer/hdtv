# -*- coding: utf-8 -*-

# works with revision 119

import hdtv.fit
import __main__ 

def DoFit(ID, spec, fitter, region, peaks, backgrounds):
	"""
	Do the actual fit
	"""
	fit = hdtv.fit.Fit(fitter, cal=spec.cal, color=spec.color)
	spec[ID]=fit
	for r in region:
		fit.PutRegionMarker(float(r))
	for b in backgrounds:
		fit.PutBgMarker(float(b))
	for p in peaks:
		fit.PutPeakMarker(float(p))
	fit.FitPeakFunc(spec)
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
spectra = __main__.spectra
spectra.RemoveAll()

__main__.s.LoadSpectra("~/hdtv/test/spectra/231Th*[down,up].ascii")
__main__.s.GetCalsFromList("~/hdtv/test/spectra/231Th_calibrations.txt")

Init(spectra)


### f.defaultFitter fit parameter
__main__.f.SetPeakModel("theuerkauf")
__main__.f.SetParameter("tr", "equal")
__main__.f.SetBgDeg(1)


#### Peak around 42 keV:
# FIXME: difficult background (all)
#ids = range(0,18)
#region      = [32,53]
#peaks       = [42]
#backgrounds = [20, 30, 55, 60]
#for ID in ids:
#	fitter = __main__.f.defaultFitter.Copy()
#	spec = spectra[ID]
#	DoFit(42, spec, fitter, region, peaks, backgrounds)



### Peak around 96 keV:
# FIXME: ids=0-3, 5
#ids = range(4,18)
#ids.remove(5)
#region 		= [84, 110]
#peaks		= [96]
#backgrounds = [75, 80, 111, 115]
#for ID  in  ids:
#	spec = spectra[ID]
#	fitter = __main__.f.defaultFitter.Copy()
#	DoFit(96, spec, fitter, region, peaks, backgrounds)


#### Peaks around 162 keV:
# FIXME: ids=0-3
#ids = range(4,18)
#region 		= [154, 174]
#peaks		= [162]
#backgrounds = [142, 152, 175, 180] 
#for ID  in  ids:
#	spec = spectra[ID]
#	fitter = __main__.f.defaultFitter.Copy()
#	DoFit(162, spec, fitter, region, peaks, backgrounds)


#### Peak around 221 keV:
# FIXME: ids=0,1
#ids = range(2,18)
#ids.remove(5)	# peak to small
#ids.remove(8)	# peak to small
#ids.remove(10) # peak to small 
#region 		= [215, 232]
#peaks		= [221.6]
#backgrounds	= [200, 212, 230, 233]
#for ID in ids:
#	spec = spectra[ID]
#	fitter = __main__.f.defaultFitter.Copy()
#	fitter.bgdeg = 2
#	DoFit(221, spec, fitter, region, peaks, backgrounds)


#### Peaks around 241 keV und 248 keV: 
#ids = range(0,18)
#region		= [230, 260]
#peaks		= [241.7, 248.8]
#backgrounds = [228, 233, 290, 295]
#for ID in ids:
#	spec = spectra[ID]
#	fitter = __main__.f.defaultFitter.Copy()
#	fitter.SetParameter("width", "5.6")
#	DoFit(241, spec, fitter, region, peaks, backgrounds)



#### Peak around 273 keV:
#ids = range(0,18)
#region      = [265, 290]
#peaks       = [272.7, 278.6]
#backgrounds = [260, 264, 291, 295]
#for ID in ids:
#	spec = spectra[ID]
#	fitter = __main__.f.defaultFitter.Copy()
#	fitter.SetParameter("width", "5.8")
#	DoFit(273, spec, fitter, region, peaks, backgrounds)


#### Peak around 302 keV:
#ids = range(0,18)
#region 		= [295, 310]
#peaks		= [302]
#backgrounds = [292, 294, 312, 315 ]
#for ID in ids:
#	spec = spectra[ID]
#	fitter = __main__.f.defaultFitter.Copy()
#	DoFit(302, spec, fitter, region, peaks, backgrounds)


#### Peaks around 317 keV und 325 keV:
#ids = range(0,18)
#region 		= [312, 340]
#peaks 		= [318, 325]
#backgrounds = [310, 312, 341, 346]
#for ID in ids:
#	spec = spectra[ID]
#	fitter = __main__.f.defaultFitter.Copy()
#	fitter.SetParameter("pos","hold")
#	DoFit(317, spec, fitter, region, peaks, backgrounds)


#### Peak around 351 keV:
#ids = range(0,18)
#region 		= [345, 360]
#peaks 		= [351]
#backgrounds = [190, 200, 360, 363]
#for ID in ids:
#	spec = spectra[ID]
#	fitter = __main__.f.defaultFitter.Copy()
#	DoFit(351, spec, fitter, region, peaks, backgrounds)


#### Peaks around 378 keV, 388 keV:
# FIXME: ids 0-3
# FIXME: double or triple?
#ids = range(4,18)
#region		= [370, 395]
#peaks		= [377.9, 385.8]
#backgrounds = [362, 368, 392, 396]
#for ID in ids:
#	spec = spectra[ID]
#	fitter = __main__.f.defaultFitter.Copy()
#	fitter.SetParameter("pos", "hold, free")
#	DoFit(378, spec, fitter, region, peaks, backgrounds)


#### Peaks around 402 keV:
# ids 0-1: big background
# FIXME: ids 2-5
#ids = range(6,18)
#region 		= [395, 410]
#peaks		= [402]
#backgrounds = [365, 370, 420, 425]
#for ID in ids:
#	spec = spectra[ID]
#	fitter = __main__.f.defaultFitter.Copy()
#	DoFit(402, spec, fitter, region, peaks, backgrounds)


#### Peaks around 447 keV and 466.5 keV:
# FIXME: ids 0-1
#ids 2-3: big background
# FIXME: ids 4-7 sophisticated background needed 
#ids = range(8,18)
#region 		= [440, 480]
#peaks		= [447.75, 466.5]
#backgrounds = [430, 435, 480, 485]
#for ID in ids:
#	spec = spectra[ID]
#	fitter = __main__.f.defaultFitter.Copy()
#	fitter.SetParameter("pos", "hold")
#	DoFit(447, spec, fitter, region, peaks, backgrounds)


#### Peak around 490.5 keV;
#ids = range(0,18)
#ids.remove(2) 	# big background
#ids.remove(3)	# big background
#ids.remove(6)	# big background
#ids.remove(7)	# big background
#region 		= [485, 504]
#peaks		= [490.5]
#backgrounds	= [480, 484, 505, 510]
#for ID in ids:
#	spec = spectra[ID]
#	fitter = __main__.f.defaultFitter.Copy()
#	if ID==11: # Extra Wurst
#		fitter.SetParameter("pos", "490.37")
#	else:
#		fitter.SetParameter("pos", "free")
#	DoFit(491, spec, fitter, region, peaks, backgrounds)


#### Peak around 553 keV:
# FIXME: ids= 0,1
#ids = range(2,18)
#ids.remove(4)	# big background
#ids.remove(5)	# big background
#region 		= [545, 566]
#peaks		= [553]
#backgrounds = [537, 542, 567 , 570]
#for ID in ids:
#	spec = spectra[ID]
#	fitter = __main__.f.defaultFitter.Copy()
#	DoFit(553, spec, fitter, region, peaks, backgrounds)


#### Peaks around 578 keV and 592 keV:
#ids = range(0,18)
#ids.remove(4)	# big background
#ids.remove(5)	# big background
#region		= [570, 600]
#peaks		= [578, 592]
#backgrounds	= [565, 568, 600, 603]
#fitter = __main__.f.defaultFitter.Copy()
#fitter.SetParameter('pos', 'free, hold')
#for ID in ids:
#	spec = spectra[ID]
#	fitter = __main__.f.defaultFitter.Copy()
#	fitter.SetParameter('pos', 'free, hold')
#	for ID in [8,9]:	# difficult background
#		DoFit(578, spec, fitter, region, peaks, [569, 571, 599, 601])
#	else:
#		DoFit(578, spec, fitter, region, peaks, backgrounds)


#### Peaks around 643.5 keV and 653 keV:
ids = range(8,18)
# FIXME: ids 0-5
# ids = 6+7 big background
#ids.remove(10)	# big background
#ids.remove(11)	# big background
#region 		= [638, 665]
#peaks 		= [645, 653]
#backgrounds = [630, 635, 670, 675]
#for ID in ids:
#	fitter = __main__.f.defaultFitter.Copy()
#	spec = spectra[ID]
#	DoFit(643, spec, fitter, region, peaks, backgrounds)


#### Peak around 682 keV:
#ids = range(0,18)
#ids.remove(2)	# to small
#ids.remove(3)	# to small
#ids.remove(6)	# big background
#ids.remove(7)	# big background
#region 		= [670, 690]
#peaks		= [682]
#backgrounds = [665, 668, 691, 693]
#for ID in ids:
#	spec = spectra[ID]
#	fitter = __main__.f.defaultFitter.Copy()
#	DoFit(682, spec, fitter, region, peaks, backgrounds)

# FIXME: HERE


#### Peaks around 706 keV, 721 keV, 746 keV:
#ids=range(0,18)
#ids.remove(6)	# big background
#ids.remove(7) 	# big background
#region		= [ 695, 760]
#peaks		= [706, 721, 746]
#backgrounds = [730,740]
#fitter = __main__.f.defaultFitter.Copy()
#for ID in ids:
#	spec = spectra[ID]
#	fitter = __main__.f.defaultFitter.Copy()
#	DoFit(706, spec, fitter, region, peaks, backgrounds)


#### Peaks around 801 keV, 806 keV, 814 keV:
#region 		= [795, 820]
#peaks		= [801, 806, 814]
#backgrounds	= [770, 780, 920, 930]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(795, spec, fitter, region, peaks, backgrounds)


#### Peaks around 827 keV, 835 keV, 839 keV, 849 keV:
#region 		= [820, 855]
#peaks		= [827, 835, 839, 849]
#backgrounds = [770, 780, 920, 930]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(820, spec, fitter, region, peaks, backgrounds)


#### Peaks between 862 keV and 907 keV:
#region 		= [855, 915]
#peaks		= [862, 869, 882, 894, 907]
#backgrounds	= [770, 780, 920, 930]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(855,spec, fitter, region, peaks, backgrounds)


#### Peaks around 950 kev, and 953 keV:
#region 		= [940, 970]
#peaks		= [950, 953]
#backgrounds = [940, 970]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(950, spec, fitter, region, peaks, backgrounds)


#### Peak around 980 keV:
#region 		= [970, 988]
#peaks		= [979]
#backgrounds = [920, 930, 1040, 1050]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(980, spec, fitter, region, peaks, backgrounds)


#### Peaks around 1002 keV, 1010.5 keV, 1021 keV:
#region 		= [995, 1030]
#peaks		= [1002, 1010.5, 1021]
#backgrounds	= [920, 630, 1040, 1050]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(1002, spec, fitter, region, peaks, backgrounds)


#### Peaks around 1068 keV, 1085.5 keV:
#region 		= [1055, 1095]
#peaks		= [1068, 1085.5]
#backgrounds = [1045, 1050, 1145, 1150]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(1055, spec, fitter, region, peaks, backgrounds)


#### Peaks around 1105 keV, 1109 keV:
#region 		= [1095, 1115]
#peaks     	= [1105, 1109]
#backgrounds	= [1090, 1092, 1145, 1150]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(1105, spec, fitter, region, peaks, backgrounds)


#### Peak around 1121 keV:
#region		= [115, 1130]
#peaks		= [1121]
#backgrounds = [1040, 1050, 1145, 1150]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(1121, spec, fitter, region, peaks, backgrounds)


#### Peak around 1139 keV:
#region 		= [1130, 1150]
#peaks		= [ 1139]
#backgrounds = [1040, 1050, 1148, 1150]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(1139, spec, fitter, region, peaks, backgrounds)

#### Peak around 1169 keV:
#region 		= [1162, 1177]
#peaks		= [1169]
#backgrounds = [1159, 1161, 1189, 1191]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(1169, spec, fitter, region, peaks, backgrounds)


#### Peak around 1183 keV:
#region 		= [1175, 1188]
#peaks		= [1183]
#backgrounds = [1155, 1156, 1174, 1175]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(1183, spec, fitter, region, peaks, backgrounds)


##### dicker Untergrund zwischen 1190 keV und 1335 keV  in 35 Grad unpol


#### Peak around 1345 keV:
#region		= [1340, 1351]
#peaks		= [1345]
#backgrounds = [1339, 1340, 1350, 1352]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(1345, spec, fitter, region, peaks, backgrounds)


#### Peak around 1357 keV:
#region 		= [1352, 1366]
#peaks		= [1357]
#backgrounds = [1350, 1352, 1369, 1373]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(1357, spec, fitter, region, peaks, backgrounds)


#### Peak around 1379 keV:
#region		= [1372, 1388]
#peaks		= [1379]
#backgrounds = [1370, 1372, 1414, 1416]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(1379, spec, fitter, region, peaks, backgrounds)


#### Peaks around 1392 keV, 1402 keV, 1410 keV:
#region		= [1388, 1415]
#peaks		= [1392, 1402.5, 1410]
#backgrounds = [1370, 1372, 1415, 1417]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(1392, spec, fitter, region, peaks, backgrounds)


#### Peaks around 1423 keV, 1436 keV:
#region		= [1415, 1450]
#peaks 		= [1423, 1436]
#backgrounds = [1372, 1374, 1450, 1452]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(1423, spec, fitter, region, peaks, backgrounds)


#### Peaks around 1459 keV, 1470 keV:
#region		= [1450, 1475]
#peaks 		= [1459, 1470]
#backgrounds = [1445, 1450, 1518, 1520]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(1459, spec, fitter, region, peaks, backgrounds)


#### Peaks around 1500 keV, 1509 keV and 1516 keV:
#region 		= [1495, 1522]
#peaks 		= [1500, 1509, 1516]
#backgrounds = [1490, 1495, 1524, 1526]
#fitter = __main__.f.defaultFitter.Copy()
#for spec in spectra.itervalues():
#	DoFit(1500,spec, fitter, region, peaks, backgrounds)

##### und ein paar mehr bei höheren Energien

 


### draw all fits and everything
spectra.Draw(__main__.window.viewport)
#for spec in spectra.itervalues():
#	spec.HideAll()




		
