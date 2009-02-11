import ROOT
import hdtv.fit

class FitGUI:
	"""
	Class to add a TV-style peak fitting GUI to a window
	"""
	def __init__(self, window, show_panel=False):
		self.fWindow = window
		
		# Create fitter object to hold the graphical representation of the fit
		self.fFitter = hdtv.fit.Fit()
		self.fFitter.Realize(self.fWindow.fViewport)
		
		# Internal markers
		self.fPeakMarkers = []
		self.fRegionMarkers = []
		self.fBgMarkers = []
		
		# Create fit panel
		self.fFitPanel = FitPanel()
		self.fFitPanel.fFitHandler = self.Fit
		self.fFitPanel.fClearHandler = self.DeleteFit
		self.fFitPanel.fResetHandler = self.ResetFitParameters
		self.fFitPanel.fDecompHandler = self.fFitter.SetDecomp
		
		if show_panel:
			self.fFitPanel.Show()
			
		# Register hotkeys
		self.fWindow.AddHotkey(ROOT.kKey_b, self.PutBackgroundMarker)
		self.fWindow.AddHotkey(ROOT.kKey_r, self.PutRegionMarker)
		self.fWindow.AddHotkey(ROOT.kKey_p, self.PutPeakMarker)
	  	self.fWindow.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_F], self.DeleteFit)
	  	self.fWindow.AddHotkey(ROOT.kKey_B, self.FitBackground)
	  	self.fWindow.AddHotkey(ROOT.kKey_F, self.Fit)
	  	self.fWindow.AddHotkey(ROOT.kKey_I, self.Integrate)
	  	self.fWindow.AddHotkey(ROOT.kKey_D, lambda: self.SetDecomp(True))
	  	self.fWindow.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_D], lambda: self.SetDecomp(False))
	  	
	def SetDecomp(self, stat):
		self.fFitPanel.SetDecomp(stat)
		self.fFitter.SetDecomp(stat)
		
	def PutRegionMarker(self):
		"Put a region marker at the current cursor position (internal use only)"
		self.fWindow.PutPairedMarker("X", "REGION", self.fRegionMarkers, 1)
			
	def PutBackgroundMarker(self):
		"Put a background marker at the current cursor position (internal use only)"
		self.fWindow.PutPairedMarker("X", "BACKGROUND", self.fBgMarkers)
		
	def PutPeakMarker(self):
		"Put a peak marker at the current cursor position (internal use only)"
		pos = self.fWindow.fViewport.GetCursorX()
  		self.fPeakMarkers.append(hdtv.marker.Marker("PEAK", pos))
  		self.fPeakMarkers[-1].Draw(self.fWindow.fViewport)
		
	def ResetFitParameters(self):
		self.fFitter.ResetParameters()
		self.FitUpdateOptions()	
	
	def FitUpdateOptions(self):
		self.fFitPanel.SetOptions(self.fFitter.OptionsStr())
		
	def FitUpdateData(self):
		self.fFitPanel.SetData(self.fFitter.DataStr())
		
	def FitBackground(self):
		# Make sure a fit panel is displayed
		self.fFitPanel.Show()
		
		if not self.fWindow.fPendingMarker and \
			len(self.fBgMarkers) > 0:
			
			self.fFitter.bglist = map(lambda m: [m.p1, m.p2], self.fBgMarkers)
			self.fFitter.DoBgFit()
			
			self.FitUpdateData()
		
	def Fit(self):
		# Make sure a fit panel is displayed
		self.fFitPanel.Show()
		
		# Lock updates
		self.fWindow.fViewport.LockUpdate()
	
	  	if not self.fWindow.fPendingMarker and \
	  		len(self.fRegionMarkers) == 1 and \
	  		len(self.fPeakMarkers) > 0:

			# Do the fit
			self.fFitter.region = [self.fRegionMarkers[0].p1, self.fRegionMarkers[0].p2]
			self.fFitter.peaklist = map(lambda m: m.p1, self.fPeakMarkers)
			self.fFitter.DoPeakFit()
						                   
			self.FitUpdateData()
				
			for (marker, peak) in zip(self.fPeakMarkers, self.fFitter.resultPeaks):
				marker.p1 = peak.GetPos()
				marker.UpdatePos()

		# Update viewport if required
		self.fWindow.fViewport.UnlockUpdate()
  		
  	def DeleteFit(self):
		for marker in self.fPeakMarkers:
  			marker.Remove()
		for marker in self.fBgMarkers:
  			marker.Remove()
  		for marker in self.fRegionMarkers:
  			marker.Remove()
	  			
  		self.fWindow.fPendingMarker = None
  		self.fPeakMarkers = []
  		self.fBgMarkers = []
  		self.fRegionMarkers = []
  		
		self.fFitter.Reset()

		if self.fFitPanel:
			self.fFitPanel.SetData("")
		
	# FIXME: This function needs rework
	def Integrate(self):
		if not self.fWindow.fPendingMarker and len(self.fRegionMarkers) == 1:
			# Integrate histogram in requested region
			spec = self.fFitter.spec
			ch_1 = spec.E2Ch(self.fRegionMarkers[0].p1)
			ch_2 = spec.E2Ch(self.fRegionMarkers[0].p2)
				
			fitter = ROOT.GSFitter(ch_1, ch_2)
			total_int = fitter.Integrate(spec.fHist)
			total_err = math.sqrt(total_int)
			                       
			# Integrate background function in requested region if it
			# is available
			if self.fFitter and self.fFitter.bgfunc:
				bgfunc = self.fFitter.bgfunc
				bg_int = bgfunc.Integral(math.ceil(min(ch_1, ch_2) - 0.5) - 0.5,
				                         math.ceil(max(ch_1, ch_2) - 0.5) + 0.5)
				bg_err = math.sqrt(bg_int)
			else:
				bg_int = None

			# Output results
			if bg_int != None:
				sum_int = total_int - bg_int
				sum_err = math.sqrt(total_int + bg_int)

				text  = "Total:      %10.1f +- %7.1f\n" % (total_int, total_err)
				text += "Background: %10.1f +- %7.1f\n" % (bg_int, bg_err)
				text += "Sub:        %10.1f +- %7.1f\n" % (sum_int, sum_err)
			else:
				text = "Integral: %.1f +- %.1f\n" % (total_int, total_err)
			
			self.EnsureFitPanel()
			self.fFitPanel.SetText(text)

class FitPanel:
	def __init__(self):
		self._dispatchers = []
		self.fFitHandler = None
		self.fClearHandler = None
		self.fResetHandler = None
		self.fDecompHandler = None
		self.fVisible = False
	
		self.fMainFrame = ROOT.TGMainFrame(ROOT.gClient.GetRoot(), 300, 500)
		self.fMainFrame.DontCallClose()
		disp = ROOT.TPyDispatcher(self.Hide)
		self.fMainFrame.Connect("CloseWindow()", "TPyDispatcher", disp, "Dispatch()")
		self._dispatchers.append(disp)
		
		## Button frame ##
		self.fButtonFrame = ROOT.TGHorizontalFrame(self.fMainFrame)

		self.fFitButton = ROOT.TGTextButton(self.fButtonFrame, "Fit")
		disp = ROOT.TPyDispatcher(self.FitClicked)
		self.fFitButton.Connect("Clicked()", "TPyDispatcher", disp, "Dispatch()")
		self._dispatchers.append(disp)
		self.fButtonFrame.AddFrame(self.fFitButton)
						
		self.fClearButton = ROOT.TGTextButton(self.fButtonFrame, "Clear")
		disp = ROOT.TPyDispatcher(self.ClearClicked)
		self.fClearButton.Connect("Clicked()", "TPyDispatcher", disp, "Dispatch()")
		self._dispatchers.append(disp)
		self.fButtonFrame.AddFrame(self.fClearButton)
		
		self.fResetButton = ROOT.TGTextButton(self.fButtonFrame, "Reset")
		disp = ROOT.TPyDispatcher(self.ResetClicked)
		self.fResetButton.Connect("Clicked()", "TPyDispatcher", disp, "Dispatch()")
		self._dispatchers.append(disp)
		self.fButtonFrame.AddFrame(self.fResetButton)
		
		self.fHideButton = ROOT.TGTextButton(self.fButtonFrame, "Hide")
		disp = ROOT.TPyDispatcher(self.HideClicked)
		self.fHideButton.Connect("Clicked()", "TPyDispatcher", disp, "Dispatch()")
		self._dispatchers.append(disp)
		self.fButtonFrame.AddFrame(self.fHideButton)
		
		self.fDecompButton = ROOT.TGCheckButton(self.fButtonFrame, "Show decomposition")
		disp = ROOT.TPyDispatcher(self.DecompClicked)
		self.fDecompButton.Connect("Clicked()", "TPyDispatcher", disp, "Dispatch()")
		self._dispatchers.append(disp)
		self.fButtonFrame.AddFrame(self.fDecompButton,
		       ROOT.TGLayoutHints(ROOT.kLHintsLeft, 10, 0, 0, 0))
		
		self.fMainFrame.AddFrame(self.fButtonFrame,
		       ROOT.TGLayoutHints(ROOT.kLHintsExpandX, 10, 5, 10, 10))
				
		## Fit info ##
		self.fFitInfo = ROOT.TGTab(self.fMainFrame)
		self.fMainFrame.AddFrame(self.fFitInfo,
		       ROOT.TGLayoutHints(ROOT.kLHintsExpandX | ROOT.kLHintsExpandY))

		optionsFrame = self.fFitInfo.AddTab("Options")
		fitFrame = self.fFitInfo.AddTab("Fit")
		# listFrame = self.fFitInfo.AddTab("Peak list")
		
		self.fOptionsText = ROOT.TGTextView(optionsFrame, 400, 500)
		optionsFrame.AddFrame(self.fOptionsText,
		       ROOT.TGLayoutHints(ROOT.kLHintsExpandX | ROOT.kLHintsExpandY))
	
		self.fFitText = ROOT.TGTextView(fitFrame, 400, 500)
		fitFrame.AddFrame(self.fFitText,
		       ROOT.TGLayoutHints(ROOT.kLHintsExpandX | ROOT.kLHintsExpandY))
			
		self.fMainFrame.SetWindowName("Fit")
		self.fMainFrame.MapSubwindows()
		self.fMainFrame.Resize(self.fMainFrame.GetDefaultSize())
		
	# Note that deleting the window on close, and recreating it when needed,
	# causes a BadWindow (invalid Window parameter) error from time to time
	# (the exact conditions are not completely understood).
	# In addition, just hiding the window has the advantage that all settings
	# (text entries, checkboxes, ...) are automatically remembered.
	def Hide(self):
		if self.fVisible:
			self.fMainFrame.UnmapWindow()
			self.fVisible = False
			
	def Show(self):
		if not self.fVisible:
			self.fMainFrame.MapWindow()
			self.fVisible = True
		
	# FIXME: This should *really* take advantage of signals and slots...
	def FitClicked(self):
		if self.fFitHandler:
			self.fFitHandler()
			
	def ClearClicked(self):
		if self.fClearHandler:
			self.fClearHandler()
			
	def ResetClicked(self):
		if self.fResetHandler:
			self.fResetHandler()
		
	def HideClicked(self):
		self.Hide()
		
	def DecompClicked(self):
		if self.fDecompHandler:
			self.fDecompHandler(bool(self.fDecompButton.IsOn()))
			
	def SetDecomp(self, stat):
		if stat:
			self.fDecompButton.SetState(ROOT.kButtonDown)
		else:
			self.fDecompButton.SetState(ROOT.kButtonUp)
		
	def SetData(self, text):
		if not text:
			self.fFitText.Clear()
		else:
			self.fFitText.LoadBuffer(text)
		
	def SetOptions(self, text):
		if not text:
			self.fOptionsText.Clear()
		else:
			self.fOptionsText.LoadBuffer(text)
