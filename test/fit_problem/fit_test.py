from __main__ import *

from hdtv.fit import Fit
from hdtv.spectrum import FileSpectrum, SpectrumCompound


### start!
spectra.RemoveAll()

fspec = FileSpectrum(hdtvpath+"/test/fit_problem/231Th_10down.ascii")
spec = SpectrumCompound(window.viewport, fspec)
spectra.Add(spec)

fit = Fit(f.defaultFitter.Copy(), cal=spec.cal, color=spec.color)
fit.PutRegionMarker(490)
fit.PutRegionMarker(540)
fit.PutPeakMarker(500)
fit.PutPeakMarker(525)
fit.FitPeakFunc(spec)

spec.Add(fit)

spectra.Draw(window.viewport)



