#!/usr/bin/python -i
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This simple example shows how to use views to work with several spectra.
# A window can contain several views and every view can contain several spectra.
# The user can cycle through the views by using the PAGEUP and PAGEDOWN keys.
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


# create a standard window
win = Window()

#### show several superimposed spectra
# add a view
view0=win.AddView("Several Spectra")
# load first spectrum
view0.AddSpec(specfile1, cal=cal1, color=color.kBlue, update=False)
# load second spectrum
view0.AddSpec(specfile2, cal=cal2, color=color.kYellow, update=False)
# load third spectrum
view0.AddSpec(specfile3, cal=cal3, color=color.kGreen, update=False)

#### show each spectra in its own view
# add a view
view1=win.AddView("35 down")
# load a spectrum
view1.AddSpec(specfile1, cal=cal1, update=False)
# add another view
view2=win.AddView("40 down")
# load a spectrum to the new view
view2.AddSpec(specfile2, cal=cal2, update=False)
# add another view
view3=win.AddView("45 down")
# load a spectrum to the new view
view3.AddSpec(specfile3, cal=cal3, update=False)

### select a view to show, by default the last view 
### which has been loaded with a spectrum is displayed. 
win.ShowView(0)
## show full range of spectrum
win.Expand()

