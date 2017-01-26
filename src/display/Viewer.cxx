/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2009  The HDTV development team (see file AUTHORS)
 *
 * This file is part of HDTV.
 *
 * HDTV is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * HDTV is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
 * for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with HDTV; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
 * 
 */

#include "Viewer.h"

namespace HDTV {
namespace Display {

Viewer::Viewer(UInt_t w, UInt_t h, const char *title)
  : TGMainFrame(gClient->GetRoot(), w, h)
{
  Int_t parts[3] = {20, 15, 65};
  
  // FIXME: how is the memory for TGLayoutHints supposed to be handled correctly???
  
  fView = new View1D(this, w-4, h-4);
  AddFrame(fView, new TGLayoutHints(kLHintsExpandX | kLHintsExpandY, 0,0,0,0));
  
  fScrollbar = new TGHScrollBar(this, 10, kDefaultScrollBarWidth);
  AddFrame(fScrollbar, new TGLayoutHints(kLHintsExpandX, 0,0,0,0));
  
  fStatusBar = new TGStatusBar(this, 10, 16);
  fStatusBar->SetParts(parts, 3);
  
  AddFrame(fStatusBar, new TGLayoutHints(kLHintsExpandX, 0,0,0,0));
  
  fView->SetScrollbar(fScrollbar);
  fView->SetStatusBar(fStatusBar);

  SetWindowName(title);
  MapSubwindows();
  Resize(GetDefaultSize());
  MapWindow();
  
  fView->UpdateScrollbarRange();
  
  AddInput(kKeyPressMask);
}

Viewer::~Viewer()
{
  //! Destructor

  // This will delete all contained frames, and all layout hints.
  // DO NOT delete them again ``by hand''!
  Cleanup();
}

Bool_t Viewer::HandleKey(Event_t *ev)
{
  if(ev->fType == kGKeyPress) {
	memset(fKeyStr, 0, 16);
	gVirtualX->LookupString(ev, fKeyStr, 16, fKeySym);
	fKeyState = ev->fState;
	KeyPressed();
  }
	
  return true;
}

Bool_t Viewer::ProcessMessage(Long_t msg, Long_t parm1, Long_t)
{
  int handled = false;
  
  if(GET_MSG(msg) == kC_HSCROLL) {
	if(GET_SUBMSG(msg) == kSB_SLIDERTRACK) {
	  fView->HandleScrollbar(parm1);
	  handled = true;
	}
  }
  
  return handled;
}

} // end namespace Display
} // end namespace HDTV
