import os
import __main__

spectra = __main__.spectra
spectra.RemoveAll()

testspectrum= os.path.join(__main__.hdtvpath, "test", "fitxml", "osiris_bg.ascii")
testXML = os.path.join(__main__.hdtvpath, "test", "fitxml", "osiris_bg.xml")

__main__.s.LoadSpectra(testspectrum)

# 1.) all parameter free, just one peak, no background, theuerkauf modell
__main__.f.SetPeakModel("theuerkauf")
__main__.f.ResetParameters()
fit = __main__.f.GetActiveFit()
fit.PutRegionMarker(1450)
fit.PutRegionMarker(1470)
fit.PutPeakMarker(1460)
__main__.f.Fit()
__main__.f.KeepFit()

# 2.) all parameter free, just one peak, background
__main__.f.ResetParameters()
fit = __main__.f.GetActiveFit()
fit.PutRegionMarker(500)
fit.PutRegionMarker(520)
fit.PutPeakMarker(511)
fit.PutBgMarker(480)
fit.PutBgMarker(490)
fit.PutBgMarker(530)
fit.PutBgMarker(540)
__main__.f.Fit()
__main__.f.KeepFit()


# 3.) all parameter free, more than one peak
__main__.f.ResetParameters()
fit = __main__.f.GetActiveFit()
fit.PutRegionMarker(1395)
fit.PutRegionMarker(1415)
fit.PutPeakMarker(1400)
fit.PutPeakMarker(1410)
fit.PutBgMarker(1350)
fit.PutBgMarker(1355)
fit.PutBgMarker(1420)
fit.PutBgMarker(1425)
__main__.f.Fit()
__main__.f.KeepFit()

# 4.) one parameter status!=free, but equal for all peaks
__main__.f.ResetParameters()
fit = __main__.f.GetActiveFit()
fit.PutRegionMarker(960)
fit.PutRegionMarker(975)
fit.PutPeakMarker(965)
fit.PutPeakMarker(970)
fit.PutBgMarker(950)
fit.PutBgMarker(955)
fit.PutBgMarker(980)
fit.PutBgMarker(985)
__main__.f.SetParameter("width", "equal")
__main__.f.Fit()
__main__.f.KeepFit()


# 5.) different parameter status for each peak
__main__.f.ResetParameters()
fit = __main__.f.GetActiveFit()
fit.PutRegionMarker(1750)
fit.PutRegionMarker(1780)
fit.PutPeakMarker(1765)
fit.PutPeakMarker(1770)
fit.PutBgMarker(1700)
fit.PutBgMarker(1710)
fit.PutBgMarker(1800)
fit.PutBgMarker(1810)
__main__.f.SetParameter("tl", "free, none")
__main__.f.Fit()
__main__.f.KeepFit()


print 'Saving fits to file %s' % testXML
__main__.fitxml.WriteFitlist(testXML)
print 'Deleting all fits'
__main__.spectra[0].RemoveObjects(spectra[0].keys())
print 'Reading fits from file %s' %testXML
__main__.fitxml.ReadFitlist(testXML)

