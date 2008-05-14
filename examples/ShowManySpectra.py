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
from hdtv.display import Window

# Don't add created spectra to the ROOT directory
ROOT.TH1.AddDirectory(ROOT.kFALSE)

# create a standard window
win = Window()

#### show several superposed spectra
# add a view
view0=win.AddView("Several Spectra")
# create a calibration
cal1= ROOT.GSCalibration(-789.006, 0.698618, 4.8471e-05)
# load first spectrum
win.LoadSpec("spectra/231Th_35down.ascii", cal=cal1)
# create a calibration
cal2 = ROOT.GSCalibration(-319.27, 0.669421, 4.84477e-05 )
# load second spectrum
win.LoadSpec("spectra/231Th_40down.ascii", cal=cal2)
# create a calibration
cal3 = ROOT.GSCalibration(-303.644, 0.666922, 4.86769e-05)
# load third spectrum
win.LoadSpec("spectra/231Th_45down.ascii", cal=cal3)

#### show each spectra in its own view
## add a view
view1=win.AddView("35 down")
## load a spectrum
win.LoadSpec("spectra/231Th_35down.ascii", view=view1, cal=cal1)
# add another view
view2=win.AddView("40 down")
# load a spectrum to the new view
win.LoadSpec("spectra/231Th_40down.ascii", view=view2, cal=cal2)
# add another view
view3=win.AddView("45 down")
# load a spectrum to the new view
win.LoadSpec("spectra/231Th_45down.ascii", view=view3, cal=cal3)

### select a view to show, by default the last view 
### which has been loaded with a spectrum is displayed. 
win.SetView(0)
## show full range of spectrum
win.Expand()

