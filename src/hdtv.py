import ROOT
import math
import os
from window import Window, Fit, XMarker
from fitpanel import FitPanel
from specreader import *
from tvcut import Cut

ROOT.TH1.AddDirectory(ROOT.kFALSE)

if ROOT.gSystem.Load("../lib/gspec.so") < 0:
	raise RuntimeError, "Library not found (gspec.so)"

class CutWindow(Window):
	def __init__(self):
		Window.__init__(self)
		
		self.fCutMarkers = []
		self.fCutBgMarkers = []
		
		self.fDefaultCal = ROOT.GSCalibration(0.0, 0.5)
		
		self.SetTitle("Cut Window")
		
	def PutCutMarker(self):
		self.PutPairedXMarker("CUT", self.fCutMarkers, 1)
		
	def PutCutBgMarker(self):
		self.PutPairedXMarker("CUT_BG", self.fCutBgMarkers)
		
	def DeleteAllCutMarkers(self):
		for marker in self.fCutMarkers:
			marker.Delete(self.fViewport, False)
		for marker in self.fCutBgMarkers:
			marker.Delete(self.fViewport, False)
			
		self.fCutMarkers = []
		self.fCutBgMarkers = []
			
		self.fViewport.Update(True)
		
	def KeyHandler(self, key):
		handled = True
		
		if Window.KeyHandler(self, key):
			pass
		elif key == ROOT.kKey_c:
			self.PutCutMarker()
		elif key == ROOT.kKey_b:
			self.PutCutBgMarker()
		elif key == ROOT.kKey_Escape:
			self.DeleteAllCutMarkers()
		else:
			handled = False
			
		return handled
		
class SpecWindow(Window):
	def __init__(self):
		Window.__init__(self)
		
		self.fPeakMarkers = []
		self.fRegionMarkers = []
		self.fBgMarkers = []
		self.fFitPanel = FitPanel()
		
		self.fDefaultCal = ROOT.GSCalibration(0.0, 0.5)
		
		self.SetTitle("Spectrum Window")
		
	def KeyHandler(self, key):
		handled = True
	
		if Window.KeyHandler(self, key):
			pass
		elif key == ROOT.kKey_b:
			self.PutBackgroundMarker()
	  	elif key == ROOT.kKey_r:
			self.PutRegionMarker()
	  	elif key == ROOT.kKey_p:
			self.PutPeakMarker()
	  	elif key == ROOT.kKey_Escape:
	  		self.DeleteAllFitMarkers()
	  	elif key == ROOT.kKey_F:
	  		self.Fit()
	  	elif key == ROOT.kKey_I:
	  		self.IntegrateAll()
	  	else:
	  		handled = False
	  		
	  	return handled
		
	def PutRegionMarker(self):
		self.PutPairedXMarker("REGION", self.fRegionMarkers, 1)
			
	def PutBackgroundMarker(self):
		self.PutPairedXMarker("BACKGROUND", self.fBgMarkers)
		
	def PutPeakMarker(self):
		pos = self.fViewport.GetCursorX()
  		self.fPeakMarkers.append(XMarker("PEAK", pos))
  		self.fPeakMarkers[-1].Realize(self.fViewport)
  		
  	def DeleteAllFitMarkers(self):
		for marker in self.fPeakMarkers:
  			marker.Delete(self.fViewport, False)
		for marker in self.fBgMarkers:
  			marker.Delete(self.fViewport, False)
  		for marker in self.fRegionMarkers:
  			marker.Delete(self.fViewport, False)
	  			
  		self.fPendingMarker = None
  		self.fPeakMarkers = []
  		self.fBgMarkers = []
  		self.fRegionMarkers = []
  		
  		for view in self.fViews:
	  		if view.fCurrentFit:
				view.fCurrentFit.Delete(self.fViewport, False)
				view.fCurrentFit = None
						
		self.fViewport.Update(True)
		
	def Integrate(self, spec, bgFunc=None, corr=1.0):
		if not self.fPendingMarker and len(self.fRegionMarkers) == 1:
			ch_1 = self.E2Ch(self.fRegionMarkers[0].e1)
			ch_2 = self.E2Ch(self.fRegionMarkers[0].e2)
				
			fitter = ROOT.GSFitter(ch_1, ch_2)
			                       
			for marker in self.fBgMarkers:
				fitter.AddBgRegion(self.E2Ch(marker.e1), self.E2Ch(marker.e2))
				
			if not bgFunc and len(self.fBgMarkers) > 0:
				bgFunc = fitter.FitBackground(spec.hist)
			                       
			total_int = fitter.Integrate(spec.hist)
			if bgFunc:
				bg_int = bgFunc.Integral(math.ceil(min(ch_1, ch_2) - 0.5) - 0.5,
				                         math.ceil(max(ch_1, ch_2) - 0.5) + 0.5)
			else:
				bg_int = 0.0
			                          
			#self.fFitPanel.SetText("%.2f %.2f %.2f" % (total_int, bg_int, total_int - bg_int))
			
			integral = total_int - bg_int
			integral_error = math.sqrt(total_int + bg_int)
			
			return (integral * corr, integral_error * corr)
			
	def IntegrateAll(self):
		self.Integrate(self.fViews[0].fSpectra[0])
		
	def Fit(self):
	  	if not self.fPendingMarker and len(self.fRegionMarkers) == 1 and len(self.fPeakMarkers) > 0:
			# Make sure a fit panel is displayed
			if not self.fFitPanel:
				self.fFitPanel = FitPanel()
				
			if self.fFitPanel.fFormatList.GetSelected() == 1:
				reportStr = "Fit Error Int Error Mean Delta/2\n"
			else:
				reportStr = ""
			i = 0
			
			for view in self.fViews:
				spec = view.fSpectra[0]
				fitter = ROOT.GSFitter(spec.E2Ch(self.fRegionMarkers[0].e1),
				                       spec.E2Ch(self.fRegionMarkers[0].e2))
				                       
				for marker in self.fBgMarkers:
					fitter.AddBgRegion(spec.E2Ch(marker.e1), spec.E2Ch(marker.e2))
				
				for marker in self.fPeakMarkers:
					fitter.AddPeak(spec.E2Ch(marker.e1))
					
				bgFunc = None
				if len(self.fBgMarkers) > 0:
					bgFunc = fitter.FitBackground(spec.hist)
					
				# Fit left tails
				fitter.SetLeftTails(self.fFitPanel.GetLeftTails())
				fitter.SetRightTails(self.fFitPanel.GetRightTails())
				
				func = fitter.Fit(spec.hist, bgFunc)
								
				# FIXME: why is this needed? Possibly related to some
				# subtle issue with PyROOT memory management
				# Todo: At least a clean explaination, possibly a better
				#   solution...
				view.SetCurrentFit(Fit(ROOT.TF1(func), ROOT.TF1(bgFunc), spec.cal),
				                   self.fViewport)
				                   
				# view.fCurrentFit.Report(self.fFitPanel)
				fit_vol = view.fCurrentFit.GetVolume()
				int_vol = self.Integrate(spec, bgFunc)
				
				if self.fFitPanel.fFormatList.GetSelected() == 1:
					reportStr += "%.1f %.1f %.1f %.1f %.1f %.1f\n" % (fit_vol[0], fit_vol[1],
																	  int_vol[0], int_vol[1],
																	  (fit_vol[0] + int_vol[0]) / 2.0,
																	  abs(fit_vol[0] - int_vol[0]) / 2.0)
				else:
					#vol = (fit_vol[0] + int_vol[0]) / 2.0
					#error = max(abs(fit_vol[0] - int_vol[0]) / 2.0, int_vol[1])
					vol = fit_vol[0]
					error = fit_vol[1]
					reportStr += "%.1f %.1f\n" % (vol, error)
				
				i += 1
				# reportStr += "%.2f %.2f\n" % (ROOT.GSFitter.GetPeakVol(view.fCurrentFit.peakFunc, 0),
				#							  self.Integrate(view.fSpectra[0]))
			
			self.fFitPanel.SetText(reportStr)	
				
			for marker in self.fPeakMarkers:
				marker.Delete(self.fViewport)
		
		
class HDTV:
	def __init__(self):
		self.fCutWindow = CutWindow()
		self.fSpecWindow = SpecWindow()
		
		## Init environment ##
		view = self.fCutWindow.AddView()
		self.fCutWindow.SpecGet("/home/braun/Diplom/final/mat/all/all.pry", view)
		self.fCutWindow.SetView(0)
		self.fCutWindow.ShowFull()
		self.fMatbase = "/home/braun/Diplom/final/mat"
		
		## Debug ##
		#view = self.fSpecWindow.AddView("debug")
		#self.fSpecWindow.SpecGet("/home/braun/tv-remote/test.asc", view)
		#self.fSpecWindow.SetView(0)
		
	# This is *very* ugly. We really should be using something
	# like signals and slots, or write something similar ourselves...
	def RegisterKeyHandler(self, classname):
		self.fCutWindow.RegisterKeyHandler("%s.CutKeyHandler" % classname)
		self.fSpecWindow.RegisterKeyHandler("%s.fSpecWindow.KeyHandler" % classname)
		
	def Cut(self):
		cutwin = self.fCutWindow
		self.fSpecWindow.DeleteAllViews()
	
		if not cutwin.fPendingMarker and len(cutwin.fCutMarkers) == 1:
			for cor in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
				cut = Cut()
				
				for bgMarker in cutwin.fCutBgMarkers:
					cut.fBgRegions.append(cutwin.E2Ch(bgMarker.e1))
					cut.fBgRegions.append(cutwin.E2Ch(bgMarker.e2))
				
				fname = cut.Cut(self.fMatbase + "/cor%d/cor%d.mtx" % (cor, cor),
								cutwin.E2Ch(cutwin.fCutMarkers[0].e1),
				        		cutwin.E2Ch(cutwin.fCutMarkers[0].e2))
				        		
				view = self.fSpecWindow.AddView("cor%d" % cor)				
				self.fSpecWindow.SpecGet(fname, view)
				
		self.fSpecWindow.SetView(0)
		
	def CutKeyHandler(self, key):
		handled = True
		
		if self.fCutWindow.KeyHandler(key):
			pass
		elif key == ROOT.kKey_C:
			self.Cut()
		else:
			handled = False
			
		return handled
