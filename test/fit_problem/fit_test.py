from __main__ import *

import hdtv.fit
import hdtv.spectrum 


### start!
spectra.RemoveAll()

fspec = hdtv.spectrum.FileSpectrum(hdtvpath+"/test/fit_problem/test_tail.asc", cal=[0,0.5])
spec = hdtv.spectrum.SpectrumCompound(window.viewport, fspec)
ID=spectra.Add(spec)
spectra.ActivateObject(ID)

#fit = hdtv.fit.Fit(f.defaultFitter.Copy(), cal=spec.cal, color=spec.color)
#fit.PutBgMarker(50)
#fit.PutBgMarker(60)
#fit.PutBgMarker(590)
#fit.PutBgMarker(600)
#fit.FitBgFunc(spec)

#ID=spec.GetFreeID()
#spec[ID]=fit

spectra.Draw(window.viewport)



