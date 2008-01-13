import ROOT

class FitPanel:
	def __init__(self):
		self.fMainFrame = ROOT.TGMainFrame(ROOT.gClient.GetRoot(), 300, 500)
		
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
				
		## Button frame ##
		#self.fButtonFrame = ROOT.TGHorizontalFrame(self.fMainFrame)

		#self.fFitButton = ROOT.TGTextButton(self.fButtonFrame, "Fit")
		#self.fButtonFrame.AddFrame(self.fFitButton)
		# At least, it won't work this way...
		## ROOT.TQObject.Connect(self.fFitButton, SIGNAL("Clicked()"), self.FitClicked)
						
		#self.fClearButton = ROOT.TGTextButton(self.fButtonFrame, "Clear")
		#self.fButtonFrame.AddFrame(self.fClearButton)
		
		#self.fMainFrame.AddFrame(self.fButtonFrame,
		#		ROOT.TGLayoutHints(ROOT.kLHintsExpandX, 2, 2, 2, 2))
				
		## Fit info ##
		self.fFitInfo = ROOT.TGTextView(self.fMainFrame, 400, 500)
		self.fMainFrame.AddFrame(self.fFitInfo,
				ROOT.TGLayoutHints(ROOT.kLHintsExpandX | ROOT.kLHintsExpandY, 2,2,2,2))
	
		self.fMainFrame.SetWindowName("Fit")
		self.fMainFrame.MapSubwindows()
		self.fMainFrame.Resize(self.fMainFrame.GetDefaultSize())
		self.fMainFrame.MapWindow()
		
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
	

