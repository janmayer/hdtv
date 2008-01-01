import ROOT

class FitPanel:
	def __init__(self):
		self.fMainFrame = ROOT.TGMainFrame(ROOT.gClient.GetRoot(), 300, 500)
		
		## Tails frame ##
		self.fTailsFrame = ROOT.TGCompositeFrame(self.fMainFrame)
		layout = ROOT.TGMatrixLayout(self.fTailsFrame, 2, 3, 5, 2)
		self.fTailsFrame.SetLayoutManager(layout)

		self.fLTButton = ROOT.TGCheckButton(self.fTailsFrame, "Left tails")
		self.fTailsFrame.AddFrame(self.fLTButton)
		
		self.fLTValue = ROOT.TGTextEntry(self.fTailsFrame)
		self.fTailsFrame.AddFrame(self.fLTValue)
		
		self.fLTFit = ROOT.TGCheckButton(self.fTailsFrame, "Fit")
		self.fTailsFrame.AddFrame(self.fLTFit)
				
		self.fRTButton = ROOT.TGCheckButton(self.fTailsFrame, "Right tails")
		self.fRTButton.SetTextJustify(ROOT.kTextTop)
		self.fTailsFrame.AddFrame(self.fRTButton)
		
		self.fRTValue = ROOT.TGTextEntry(self.fTailsFrame)
		self.fTailsFrame.AddFrame(self.fRTValue)
		
		self.fRTFit = ROOT.TGCheckButton(self.fTailsFrame, "Fit")
		self.fTailsFrame.AddFrame(self.fRTFit)
		
		self.fMainFrame.AddFrame(self.fTailsFrame,
				ROOT.TGLayoutHints(ROOT.kLHintsExpandX, 2, 2, 2, 2))
				
		## Button frame ##
		self.fButtonFrame = ROOT.TGHorizontalFrame(self.fMainFrame)

		self.fFitButton = ROOT.TGTextButton(self.fButtonFrame, "Fit")
		self.fButtonFrame.AddFrame(self.fFitButton)
		ROOT.TQObject.Connect(self.fFitButton, SIGNAL("Clicked()"), self.FitClicked)
				
		self.fClearButton = ROOT.TGTextButton(self.fButtonFrame, "Clear")
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
		self.fMainFrame.MapWindow()
		
	def FitClicked(self):
		print "Hello test"
		
	def SetText(self, text):
		#self.fFitInfo.LoadBuffer(text)
		pass

