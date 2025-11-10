# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2009  The HDTV development team (see file AUTHORS)
#
# This file is part of HDTV.
#
# HDTV is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# HDTV is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with HDTV; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import ROOT


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
        self.fButtonFrame.AddFrame(
            self.fDecompButton, ROOT.TGLayoutHints(ROOT.kLHintsLeft, 10, 0, 0, 0)
        )

        self.fMainFrame.AddFrame(
            self.fButtonFrame, ROOT.TGLayoutHints(ROOT.kLHintsExpandX, 10, 5, 10, 10)
        )

        ## Fit info ##
        self.fFitInfo = ROOT.TGTab(self.fMainFrame)
        self.fMainFrame.AddFrame(
            self.fFitInfo, ROOT.TGLayoutHints(ROOT.kLHintsExpandX | ROOT.kLHintsExpandY)
        )

        optionsFrame = self.fFitInfo.AddTab("Options")
        fitFrame = self.fFitInfo.AddTab("Fit")
        # listFrame = self.fFitInfo.AddTab("Peak list")

        self.fOptionsText = ROOT.TGTextView(optionsFrame, 400, 500)
        optionsFrame.AddFrame(
            self.fOptionsText,
            ROOT.TGLayoutHints(ROOT.kLHintsExpandX | ROOT.kLHintsExpandY),
        )

        self.fFitText = ROOT.TGTextView(fitFrame, 400, 500)
        fitFrame.AddFrame(
            self.fFitText, ROOT.TGLayoutHints(ROOT.kLHintsExpandX | ROOT.kLHintsExpandY)
        )

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
