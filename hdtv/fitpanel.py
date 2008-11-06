import ROOT

class FitPanel:
	def __init__(self):
		self._dispatchers = []
		self.fFitHandler = None
		self.fClearHandler = None
		self.fVisible = False
	
		self.fMainFrame = ROOT.TGMainFrame(ROOT.gClient.GetRoot(), 300, 500)
		self.fMainFrame.DontCallClose()
		disp = ROOT.TPyDispatcher(self.Hide)
		self.fMainFrame.Connect("CloseWindow()", "TPyDispatcher", disp, "Dispatch()")
		self._dispatchers.append(disp)
		
		## Tails frame ##
		self.fTailsFrame = ROOT.TGCompositeFrame(self.fMainFrame)
		layout = ROOT.TGMatrixLayout(self.fTailsFrame, 2, 3, 5, 2)
		self.fTailsFrame.SetLayoutManager(layout)

		self.fLTEnable = ROOT.TGCheckButton(self.fTailsFrame, "Left tails")
		self.fTailsFrame.AddFrame(self.fLTEnable)
		
		self.fLTValue = ROOT.TGTextEntry(self.fTailsFrame)
		self.fTailsFrame.AddFrame(self.fLTValue)
		
		self.fLTFit = ROOT.TGCheckButton(self.fTailsFrame, "Fit")
		self.fTailsFrame.AddFrame(self.fLTFit)
				
		self.fRTEnable = ROOT.TGCheckButton(self.fTailsFrame, "Right tails")
		self.fTailsFrame.AddFrame(self.fRTEnable)
		
		self.fRTValue = ROOT.TGTextEntry(self.fTailsFrame)
		self.fTailsFrame.AddFrame(self.fRTValue)
		
		self.fRTFit = ROOT.TGCheckButton(self.fTailsFrame, "Fit")
		self.fTailsFrame.AddFrame(self.fRTFit)
		
		self.fMainFrame.AddFrame(self.fTailsFrame,
				ROOT.TGLayoutHints(ROOT.kLHintsExpandX, 2, 2, 2, 2))
				
		## Output format frame (currently disabled)
		#self.fFormatFrame = ROOT.TGHorizontalFrame(self.fMainFrame)
		
		#self.fFormatList = ROOT.TGComboBox(self.fFormatFrame)
		#self.fFormatList.AddEntry("Fit and Integral", 1)
		#self.fFormatList.AddEntry("fits.dat (fit only)", 2)
		#self.fFormatList.Select(1)
		#self.fFormatList.SetHeight(24)
		#self.fFormatFrame.AddFrame(self.fFormatList,
	    #		ROOT.TGLayoutHints(ROOT.kLHintsExpandX, 2, 2, 2, 2))
		
		#self.fMainFrame.AddFrame(self.fFormatFrame,
		#		ROOT.TGLayoutHints(ROOT.kLHintsExpandX, 2, 2, 2, 2))
			
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
		
		self.fMainFrame.AddFrame(self.fButtonFrame,
				ROOT.TGLayoutHints(ROOT.kLHintsExpandX, 2, 2, 2, 2))
				
		## Fit info ##
		self.fFitInfo = ROOT.TGTextView(self.fMainFrame, 400, 500)
		self.fMainFrame.AddFrame(self.fFitInfo,
				ROOT.TGLayoutHints(ROOT.kLHintsExpandX | ROOT.kLHintsExpandY, 2,2,2,2))
	
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
		
	def SetText(self, text):
		self.fFitInfo.LoadBuffer(text)
		
	def GetLeftTails(self):
		if self.fLTEnable.IsOn():
			if self.fLTFit.IsOn():
				return -1.0   # Fit it
			else:
				# This may throw an exception, but we leave it for the caller to handle
				return float(self.fLTValue.GetText())
		else:
			return 100000.0   # Effectively disabled
			
	def GetRightTails(self):
		if self.fRTEnable.IsOn():
			if self.fRTFit.IsOn():
				return -1.0   # Fit it
			else:
				# This may throw an exception, but we leave it for the caller to handle
				return float(self.fRTValue.GetText())
		else:
			return 100000.0   # Effectively disabled
