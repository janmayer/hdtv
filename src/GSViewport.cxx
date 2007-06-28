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

#include "GSViewport.h"
#include <Riostream.h>

GSViewport::GSViewport(const TGWindow *p, UInt_t w, UInt_t h)
  : TGFrame(p, w, h)
{
  SetBackgroundColor(GetBlackPixel());
  fLazyOffset = 0.0;
  fXVisibleRegion = 100.0;
  fMinEnergy = 0;
  fMaxEnergy = 5000;
  fUpdateLocked = 0;
  fNbins = 0;
  fSpec = NULL;
  fDispSpec = NULL;
  fYAutoScale = true;
  fNeedClear = false;
  fDragging = false;
  fLeftBorder = 60;
  fRightBorder = 3;
  fTopBorder = 3;
  fBottomBorder = 30;

  AddInput(kPointerMotionMask | kEnterWindowMask | kLeaveWindowMask
		   | kButtonPressMask | kButtonReleaseMask);

  GCValues_t gval;
  gval.fMask = kGCForeground | kGCFunction;
  gval.fFunction = kGXxor;
  gval.fForeground = GetWhitePixel();
  fCursorGC = gClient->GetGCPool()->GetGC(&gval, true);
  fCursorVisible = false;
  fSpecPainter = new GSSpecPainter();
  fSpecPainter->SetDrawable(GetId());
  fSpecPainter->SetAxisGC(GetHilightGC().GetGC());
  fSpecPainter->SetClearGC(GetBlackGC().GetGC());
  fSpecPainter->SetLogScale(false);
  fSpecPainter->SetXZoom(1.0);
  fSpecPainter->SetYZoom(0.1);
}

GSViewport::~GSViewport() {
  cout << "viewport destructor" << endl;
  fClient->GetGCPool()->FreeGC(fCursorGC);   //?
  if(fDispSpec)
	delete fDispSpec;
}

void GSViewport::SetLogScale(Bool_t l)
{
  fSpecPainter->SetLogScale(l);
  Update(true);
}

void GSViewport::ShiftOffset(int dO)
{
  Bool_t cv = fCursorVisible;
  UInt_t x, y, w, h;
  double az;

  x = fLeftBorder + 2;
  y = fTopBorder + 2;
  w = fWidth - fLeftBorder - fRightBorder - 4;
  h = fHeight - fTopBorder - fBottomBorder - 4;

  if(!fSpec) return;
  
  // TODO: debug code, remove
  if(dO == 0) {
	cout << "WARNING: Pointless call to ShiftOffset()." << endl;
	return;
  }

  if(cv) DrawCursor();

  if(dO < -((Int_t) w) || dO > ((Int_t) w)) { // entire area needs updating
	gVirtualX->FillRectangle(GetId(), GetBlackGC()(), x, y, w+1, h+1);
	fSpecPainter->DrawSpectrum(fDispSpec, x, x+w);
  } else if(dO < 0) {   // move right (note that dO ist negative)
	gVirtualX->CopyArea(GetId(), GetId(), GetWhiteGC()(), x, y,
						w + dO + 1, h + 1, x - dO, y);
	// Note that the area filled by FillRectangle() will not include
	// the border drawn by DrawRectangle() on the right and the bottom
	gVirtualX->FillRectangle(GetId(), GetBlackGC()(), x, y, -dO, h+1);
	fSpecPainter->DrawSpectrum(fDispSpec, x, x-dO);
  } else { // if(dO > 0) : move left (we caught dO == 0 above)
	gVirtualX->CopyArea(GetId(), GetId(), GetWhiteGC()(), x + dO, y,
						w - dO + 1, h + 1, x, y);
	gVirtualX->FillRectangle(GetId(), GetBlackGC()(), x+w-dO+1, y, dO, h+1);
	fSpecPainter->DrawSpectrum(fDispSpec, x+w-dO+1, x+w);
  }

  // Redrawing the entire scale is not terribly efficent, but
  // for now I am lazy...
  fSpecPainter->ClearXScale();
  fSpecPainter->DrawXScale(x, x+w);

  if(cv) DrawCursor();
}

void GSViewport::SetViewMode(EViewMode vm)
{
  if(vm != fSpecPainter->GetViewMode()) {
	fSpecPainter->SetViewMode(vm);
	fNeedClear = true;
	gClient->NeedRedraw(this);
  }
}

void GSViewport::LoadSpectrum(GSSpectrum *spec)
{
  fSpec = spec;
  fDispSpec = new GSDisplaySpec(fSpec);

  fNbins = fSpec->GetNbinsX();
  fSpecPainter->SetSpectrum(fSpec);
}

/* void GSViewport::SetXZoom(double xzoom)
{
  fLazyXZoom = xzoom;
  if(fScrollbar)
	UpdateScrollbarRange();
  else
	Update();
} */

void GSViewport::XZoomAroundCursor(double f)
{
  //int dO;
  //dO = (int) TMath::Ceil(e * GetLazyXZoom() * (f - 1) - 0.5);

  // Make sure there is only one screen update, to avoid ugly flicker
  //fUpdateLocked++;

  //SetXZoom(fLazyXZoom * f);
  fLazyOffset += fSpecPainter->dXtodE(fCursorX - fSpecPainter->GetBaseX()) * (1.0 - 1.0/f);
  fXVisibleRegion /= f;

  //fLazyOffset += 15.0;
  
  //SetOffset(fLazyOffset + dO);
  //fLazyOffset += dO;

  // The offset in the SpecPainter class is of type UInt_t
  // and must not become negative.
  // TODO: is this sensible?
  // Note: Negative offsets are impossible to set on the scrollbar.
  //if(fLazyOffset < 0)
  //	fLazyOffset = 0;

  Update(false);
}

void GSViewport::ToBegin(void)
{
  SetOffset(fSpec->GetMinEnergy());
}

void GSViewport::ShowAll(void)
{
  fLazyOffset = fSpec->GetMinEnergy();
  fXVisibleRegion = fSpec->GetMaxEnergy() - fSpec->GetMinEnergy();
  Update(false);
}

/* GSViewport::Update

   This function brings the viewport up-to-date after a change in any
   relevant parameters. It tries to do so with minimal effort,
   i.e. not by redrawing unconditionally.
*/
void GSViewport::Update(bool redraw)
{
  double az;
  double dO, dOPix;

  cout << "Update() called" << endl;

  // TODO: still required?
  if(fUpdateLocked > 0) {
	fUpdateLocked--;
	return;
  }

  // Remember not to compare floating point values
  // for equality directly (rouding error problems)
  if(TMath::Abs(GetLazyXZoom() - fSpecPainter->GetXZoom()) > 1e-7) {
	redraw = true;
	fSpecPainter->SetXZoom(GetLazyXZoom());
  }

  if(TMath::Abs(fLazyOffset - fSpecPainter->GetOffset()) > 1e-5) {
	dO = fLazyOffset - fSpecPainter->GetOffset();
	fSpecPainter->SetOffset(fLazyOffset);
  }

  // TODO: GetYAutoZoom() is too costly
  az = fSpecPainter->GetYAutoZoom();

  if(TMath::Abs(az - fSpecPainter->GetYZoom()) > 1e-7) {
	redraw = true;
	fSpecPainter->SetYZoom(az);
  }

  // We can only use ShiftOffset if the shift is an integer number
  // of pixels, otherwise we will have to do a full redraw
  dOPix = fSpecPainter->dEtodX(dO);
  if(TMath::Abs(TMath::Ceil(dOPix - 0.5) - dOPix) > 1e-7)
	redraw = true;
  
  if(redraw) {
	cout << "redraw" << endl;
	fNeedClear = true;
	gClient->NeedRedraw(this);
  } else if(TMath::Abs(dOPix) > 0.5) {
	cout << "shift offset" << endl;
	ShiftOffset((int) TMath::Ceil(dOPix - 0.5));
  }
}

void GSViewport::CenterView()
{
  // TODO: implement correctly
  SetOffset(0);
}

void GSViewport::UpdateScrollbarRange(void)
{
  if(fScrollbar) {
	UInt_t rs = GetRequiredSize();
	UInt_t as = GetAvailSize();

	fScrollbar->SetRange(rs, as);
  }
}

void GSViewport::SetOffset(double offset)
{
  // SetOffset() takes a note that the offset will have to be changed
  // and informs the scrollbar about it, which will later cause an
  // Update(). If no scrollbar exists, Update() is called directly.

  fLazyOffset = offset;

  // If we have an associated scrollbar, set its position
  // and let the callback handle the rest...
  if(false) { //fScrollbar) {
	//fScrollbar->SetPosition(offset);
  } else {
	// ...otherwise, we only have to take note that it will have to be
	// done (and perform clipping).
	/* if(offset < 0)
	  offset = 0;

	if(offset > GetRequiredSize() - GetAvailSize())
	offset = GetRequiredSize() - GetAvailSize(); */

	//fLazyOffset = offset;
	Update();
  }
}

void GSViewport::HandleScrollbar(Long_t parm)
{
  // Callback for scrollbar motion

  //cout << "HandleScrollbar(): parm=" << parm << endl;

  // Capture nonsense input
  if(parm < 0)
	parm = 0;

  fLazyOffset = parm;
  Update();
}


Bool_t GSViewport::HandleMotion(Event_t *ev)
{
  bool cv = fCursorVisible;
  if(cv) DrawCursor();
  if(fDragging) {
	SetOffset(fLazyOffset + fSpecPainter->dXtodE(fCursorX - ev->fX));
  }
  fCursorX = ev->fX;
  fCursorY = ev->fY;
  if(cv) DrawCursor();
}

Bool_t GSViewport::HandleButton(Event_t *ev)
{
  if(ev->fType == kButtonPress)
	fDragging = true;
  else
	fDragging = false;
}

Bool_t GSViewport::HandleCrossing(Event_t *ev)
{
  if(ev->fType == kEnterNotify) {
	if(fCursorVisible) DrawCursor();
	fCursorX = ev->fX;
	fCursorY = ev->fY;
	DrawCursor();
  } else if(ev->fType == kLeaveNotify) {
	if(fCursorVisible) DrawCursor();
  }
}

void GSViewport::DrawCursor(void)
{
  gVirtualX->DrawLine(GetId(), fCursorGC->GetGC(), 1, fCursorY, fWidth, fCursorY);
  gVirtualX->DrawLine(GetId(), fCursorGC->GetGC(), fCursorX, 1, fCursorX, fHeight);
  fCursorVisible = !fCursorVisible;
}

void GSViewport::Layout(void)
{ 
  fSpecPainter->SetBasePoint(fLeftBorder + 2, fHeight - fBottomBorder - 2);
  fSpecPainter->SetSize(fWidth - fLeftBorder - fRightBorder - 4,
						fHeight - fTopBorder - fBottomBorder - 4);
}

/* GSViewport::DoRedraw

   Redraws the Viewport completely.  If fNeedClear is set, it is
   cleared first, otherwise it is just redrawn. This is a callback for
   the windowing system. It should not be called directly, but via 
   gClient->NeedRedraw() .
*/
void GSViewport::DoRedraw(void)
{
  Bool_t cv;
  UInt_t x, y, w, h;
  double az = fSpecPainter->GetYAutoZoom();
  x = fLeftBorder;
  y = fTopBorder;
  w = fWidth - fLeftBorder - fRightBorder;
  h = fHeight - fTopBorder - fBottomBorder;

  cout << "DoRedraw()" << endl;

  fSpecPainter->SetXZoom(GetLazyXZoom());
  fSpecPainter->SetOffset(fLazyOffset);

  cv = fCursorVisible;
  if(cv) DrawCursor();

  if(fNeedClear) {
	// Note that the area filled by FillRectangle() will not include
	// the border drawn by DrawRectangle() on the right and the bottom
	gVirtualX->FillRectangle(GetId(), GetBlackGC()(), 0, 0, fWidth, fHeight);
	fNeedClear = false;
  }

  gVirtualX->DrawRectangle(GetId(), GetHilightGC()(), x, y, w, h);

  if(fSpec) {
	fSpecPainter->DrawSpectrum(fDispSpec, x+2, x+w-2);
	fSpecPainter->DrawXScale(x+2, x+w-2);
	fSpecPainter->DrawYScale();
  }

  if(cv) DrawCursor();
}
