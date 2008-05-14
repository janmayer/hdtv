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
win.LoadSpec("spectra/231Th_35down.ascii")
win.LoadSpec("spectra/231Th_40down.ascii")
win.LoadSpec("spectra/231Th_45down.ascii")

#### show each spectra in its own view
## add a view
view1=win.AddView("35 down")
## load a spectrum
win.LoadSpec("spectra/231Th_35down.ascii", view=view1)
## add another view
view2=win.AddView("40 down")
## load a spectrum to the new view
win.LoadSpec("spectra/231Th_40down.ascii", view=view2)
## add another view
view3=win.AddView("45 down")
## load a spectrum to the new view
win.LoadSpec("spectra/231Th_45down.ascii", view=view3)

### select a view to show, by default the last view 
### which has been loaded with a spectrum is displayed. 
win.SetView(0)
## show full range of spectrum
win.Expand()

