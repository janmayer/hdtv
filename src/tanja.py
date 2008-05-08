import ROOT
from window import Window, Fit

ROOT.TH1.AddDirectory(ROOT.kFALSE)

if ROOT.gSystem.Load("../lib/gspec.so") < 0:
	raise RuntimeError, "Library not found (gspec.so)"
	
class MyWindow(Window):
	def __init__(self):
		Window.__init__(self)
		
win = MyWindow()
win.RegisterKeyHandler("win.KeyHandler")

win.fDefaultCal = ROOT.GSCalibration(0.0, 0.5)
spec = win.SpecGet("/home/braun/Diplom/88Zr_angle_singles/0088/ge8.0088", None)
win.ShowFull()

fitter = ROOT.GSFitter(spec.E2Ch(1155.),
                       spec.E2Ch(1200.))
				                       
fitter.AddBgRegion(spec.E2Ch(1130.), spec.E2Ch(1140.))
fitter.AddBgRegion(spec.E2Ch(1170.), spec.E2Ch(1180.))

fitter.AddPeak(spec.E2Ch(1160.))
fitter.AddPeak(spec.E2Ch(1190.))

fitter.SetLeftTails(3.0)
					
bgFunc = fitter.FitBackground(spec.hist)
func = fitter.Fit(spec.hist, bgFunc)
								
# FIXME: why is this needed? Possibly related to some
# subtle issue with PyROOT memory management
# Todo: At least a clean explaination, possibly a better
#   solution...
fit = Fit(ROOT.TF1(func), ROOT.TF1(bgFunc), spec.cal)
fit.Realize(win.fViewport)

print "%8.1f "  % ROOT.GSFitter.GetPeakVol(func, 0)
print "%8.1f "  % ROOT.GSFitter.GetPeakVol(func, 1)
