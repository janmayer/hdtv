/*
 * gSpec - a viewer for gamma spectra
 *  Copyright (C) 2006  Norbert Braun <n.braun@ikp.uni-koeln.de>
 *
 * This file is part of gSpec.
 *
 * gSpec is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * gSpec is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
 * for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with gSpec; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
 * 
 */

#include "gspec.h"

/* GSMainFrame::GSMainFrame(const TGWindow *p,UInt_t w,UInt_t h) {
  //TGHScrollBar *fScroll;

  // Create a main frame
  //fMain = new TGMainFrame(p,w,h);
  // Create canvas widget
  fViewer = new GSViewer(p,w,h);
  //fMain->AddFrame(fViewer, new TGLayoutHints(kLHintsExpandX| kLHintsExpandY,
                                                      //0,0,0,0));

  // Set a name to the main frame
  //fViewer->SetWindowName("gSpec");
  // Map all subwindows of main frame
  //fViewer->MapSubwindows();
  // Initialize the layout algorithm
  //fViewer->Resize(fMain->GetDefaultSize());
  // Map main frame
  //fViewer->MapWindow();

 // GSTextSpectrumReader *ts = new GSTextSpectrumReader("test.asc");

  //fSpec = new GSSpectrum("hist1", "hist1", ts->GetNumLines() + 2);
  //ts->ToROOT(fSpec);
  //fSpec->SetCal(0.0, 1.0, 0.0);
  //fViewer->LoadSpectrum(fSpec);

  //  fSpec->Draw();

//  delete ts;
}

GSMainFrame::~GSMainFrame() {
  // Clean up used widgets: frames, buttons, layouthints
  //fViewer->Cleanup();
  //delete fMain;
  delete fViewer;
  //delete fSpec;
} */

int main(int argc, char **argv) {
  TApplication theApp("App",&argc,argv);
  new GSViewer(gClient->GetRoot(),800,400);
  theApp.Run();
  return 0;
}
