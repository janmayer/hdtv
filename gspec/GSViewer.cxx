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

#include <Riostream.h>
#include <TPython.h>

#include "GSViewer.h"

GSViewer::GSViewer(UInt_t w, UInt_t h, const char *title)
  : TGMainFrame(gClient->GetRoot(), w, h)
{
  Int_t parts[2] = {20, 80};
  
  fViewport = new GSViewport(this, w-4, h-4);
  AddFrame(fViewport, new TGLayoutHints(kLHintsExpandX | kLHintsExpandY, 0,0,0,0));
  
  fScrollbar = new TGHScrollBar(this, 10, kDefaultScrollBarWidth);
  AddFrame(fScrollbar, new TGLayoutHints(kLHintsExpandX, 0,0,0,0));
  
  fStatusBar = new TGStatusBar(this, 10, 16);
  fStatusBar->SetParts(parts, 2);
  AddFrame(fStatusBar, new TGLayoutHints(kLHintsExpandX, 0,0,0,0));
  
  fViewport->SetScrollbar(fScrollbar);
  fViewport->SetStatusBar(fStatusBar);

  SetWindowName(title);
  MapSubwindows();
  Resize(GetDefaultSize());
  MapWindow();
  
  fViewport->UpdateScrollbarRange();
  
  AddInput(kKeyPressMask);
}

GSViewer::~GSViewer(void)
{ 
  Cleanup();
}

/* Python interface (very, very UGLY) */
void GSViewer::RegisterKeyHandler(const char *cmd)
{
	fKeyHandlerCmd.assign(cmd);
}

Bool_t GSViewer::HandleKey(Event_t *ev)
{
  char buf[16];
  UInt_t keysym;
  ostringstream cmd;
    
  if(ev->fType == kGKeyPress && fKeyHandlerCmd.size() > 0) {
	gVirtualX->LookupString(ev, buf, 16, keysym);
	cmd << fKeyHandlerCmd << "(" << keysym << ")";
	TPython::Exec(cmd.str().c_str());
  }
	
  return true;
}

Bool_t GSViewer::ProcessMessage(Long_t msg, Long_t parm1, Long_t)
{
  if(GET_MSG(msg) == kC_HSCROLL) {
	if(GET_SUBMSG(msg) == kSB_SLIDERTRACK)
	  fViewport->HandleScrollbar(parm1);
  }
}
