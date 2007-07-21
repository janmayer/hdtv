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

#include "GSViewer.h"

GSViewer::GSViewer(const TGWindow *p, UInt_t w, UInt_t h)
  : TGFrame(p, w, h)
{
  fViewport = new GSViewport(this, w-4, h-4);
  fScrollbar = new TGHScrollBar(this, 10, kDefaultScrollBarWidth);
  fSpec = NULL;
  fViewport->SetScrollbar(fScrollbar);

  MapSubwindows();

  AddInput(kKeyPressMask);
}

GSViewer::~GSViewer(void)
{ 
  delete fViewport;
}

Bool_t GSViewer::HandleKey(Event_t *ev)
{
  char buf[16];
  Int_t n;
  UInt_t keysym;
  EViewMode vm;

  if(!fViewport) return true;

  if(ev->fType == kGKeyPress) {
	gVirtualX->LookupString(ev, buf, 16, keysym);

	switch((EKeySym)keysym) {
	case kKey_m:
	  vm = fViewport->GetViewMode();
	  switch(vm) {
	  case kVMSolid:  fViewport->SetViewMode(kVMHollow); break;
	  case kVMHollow: fViewport->SetViewMode(kVMDotted); break;
	  case kVMDotted: fViewport->SetViewMode(kVMSolid);  break;
	  }
	  break;
    case kKey_q:
	  gApplication->Terminate(0);
	case kKey_z:
	  fViewport->XZoomAroundCursor(2.0);
	  break;
	case kKey_x:
	  fViewport->XZoomAroundCursor(0.5);
	  break;
	case kKey_l:
	  fViewport->ToggleLogScale();
	  break;
	case kKey_0:
	  fViewport->ToBegin();
	  break;
	case kKey_f:
	  fViewport->ShowAll();
	  break;
	}
  }

  return true;
}

void GSViewer::Layout(void)
{
  UInt_t sh = fScrollbar->GetDefaultHeight();
  UInt_t ch = fHeight - sh - 6;

  fViewport->MoveResize(2,2,fWidth-4,ch);
  fScrollbar->MoveResize(2,ch+4,fWidth-4, sh);
  //fViewport->UpdateScrollbarRange();
}

void GSViewer::MapSubwindows(void)
{
  if(fScrollbar) {
	fScrollbar->MapSubwindows();
	fScrollbar->MapWindow();
  }

  if(fViewport) {
	fViewport->MapSubwindows();
	fViewport->MapWindow();
  }

  Layout();
}

Bool_t GSViewer::ProcessMessage(Long_t msg, Long_t parm1, Long_t)
{
  if(GET_MSG(msg) == kC_HSCROLL) {
	if(GET_SUBMSG(msg) == kSB_SLIDERTRACK)
	  fViewport->HandleScrollbar(parm1);

  /* if(GET_SUBMSG(msg) == kSB_SLIDERTRACK)
	  cout << "kSB_SLIDERTRACK" << endl;
	else if(GET_SUBMSG(msg) == kSB_SLIDERPOS)
	cout << "kSB_SLIDERPOS" << endl; */
  }
}

void GSViewer::LoadSpectrum(GSSpectrum *spec)
{
  fSpec = spec;
  fViewport->LoadSpectrum(spec);
  fViewport->UpdateScrollbarRange();
}
