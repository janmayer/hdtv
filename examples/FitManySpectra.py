#!/usr/bin/python -i
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This example shows, that it is possible to load several spectra to different
# views and fit each separatly with the same fit values.
#-------------------------------------------------------------------------------


# set the pythonpath
import sys
sys.path.append("..")

#import some modules
import ROOT
import hdtv.color as color
from hdtv.window import Window

# Don't add created spectra to the ROOT directory
ROOT.TH1.AddDirectory(ROOT.kFALSE)

specfile1 = "spectra/231Th_35down.ascii"
specfile2 = "spectra/231Th_40down.ascii"
specfile3 = "spectra/231Th_45down.ascii"

cal1 =  [-789.006, 0.698618, 4.8471e-05]
cal2 = [-319.27, 0.669421, 4.84477e-05 ]
cal3 = [-303.644, 0.666922, 4.86769e-05]

# fit infos
region = [230.,345.]
peaks = [242,247,273,302,325]
backgrounds = None

# create a standard window
win = Window()

#### show each spectra in its own view
# add a view
view1=win.AddView("35 down")
# load a spectrum
spec1 = view1.AddSpec(specfile1, cal=cal1, update=False)
# create fit
fit1 = spec1.AddFit(region, peaks, backgrounds, ltail=-1, rtail=-1)
# add another view
view2=win.AddView("40 down")
# load a spectrum to the new view
spec2 = view2.AddSpec(specfile2, cal=cal2, update=False)
# create fit
fit2 = spec2.AddFit(region, peaks, backgrounds, ltail=-1, rtail=-1)
# add another view
view3=win.AddView("45 down")
# load a spectrum to the new view
spec3 = view3.AddSpec(specfile3, cal=cal3, update=False)
# create fit
fit3 = spec3.AddFit(region, peaks, backgrounds, ltail=-1, rtail=-1)

### select a view to show, by default the last view 
### which has been loaded with a spectrum is displayed. 
win.ShowView(0)
## show full range of spectrum
win.Expand()

# do the fits and show the results
peaks1 = fit1.DoFit()
print "Fits for 35 down:"
for p in peaks1:
	print "Peak %s" % peaks1.index(p)
	print p
peaks2 = fit2.DoFit()
print "Fits for 40 down:"
for p in peaks2:
	print "Peak %s" % peaks2.index(p)
	print p
peaks3 = fit3.DoFit()
print "Fits for 45 down:"
for p in peaks3:
	print "Peak %s" % peaks3.index(p)
	print p



