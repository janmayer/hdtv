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
#include <TMath.h>
#include <Riostream.h>

GSViewport::GSViewport(const TGWindow *p, UInt_t w, UInt_t h)
  : TGFrame(p, w, h)
{
  SetBackgroundColor(GetBlackPixel());
  fXVisibleRegion = 100.0;
  fYMinVisibleRegion = 20.0;
  fYVisibleRegion = fYMinVisibleRegion;
  fOffset = 0.0;
  fMinEnergy = 0.0;
  fMaxEnergy = 100.0;
  fYAutoScale = true;
  fNeedClear = false;
  fDragging = false;
  fLeftBorder = 60;
  fRightBorder = 3;
  fTopBorder = 4;
  fBottomBorder = 30;

  AddInput(kPointerMotionMask | kEnterWindowMask | kLeaveWindowMask
		   | kButtonPressMask | kButtonReleaseMask);

  GCValues_t gval;
  gval.fMask = kGCForeground | kGCFunction;
  gval.fFunction = kGXxor;
  gval.fForeground = GetWhitePixel();
  fCursorGC = gClient->GetGCPool()->GetGC(&gval, true);
  fCursorVisible = false;
  fPainter = new GSPainter();
  fPainter->SetDrawable(GetId());
  fPainter->SetAxisGC(GetHilightGC().GetGC());
  fPainter->SetClearGC(GetBlackGC().GetGC());
  fPainter->SetLogScale(false);
  fPainter->SetXVisibleRegion(fXVisibleRegion);
  fPainter->SetYVisibleRegion(fYVisibleRegion);
}

GSViewport::~GSViewport() {
  //cout << "viewport destructor" << endl;
  fClient->GetGCPool()->FreeGC(fCursorGC);   //?
  for(int i=0; i < fSpectra.size(); i++)
    delete fSpectra[i];
    
  for(int i=0; i < fFunctions.size(); i++)
  	delete fFunctions[i];

  for(int i=0; i < fMarkers.size(); i++)
	delete fMarkers[i];
	
  delete fPainter;
}

template <class itemType>
int GSViewport::FindFreeId(std::vector<itemType> &items)
{
  int id = -1;
  
  for(int i=0; i < items.size(); i++) {
  	if(items[i] == NULL) {
  	  id = i;
  	  break;
  	}
  }
  
  if(id < 0) {
    id = items.size();
    items.push_back(NULL);
  }

  return id;
}

template <class itemType>
void GSViewport::DeleteItem(std::vector<itemType> &items, int id)
{
  if(id < 0 || id >= items.size())
  	return;
  
  delete items[id];
  items[id] = NULL;
  
  while(items.back() == NULL)
  	items.pop_back();
}

/*** Object management functions ***/
int GSViewport::AddMarker(double pos, int color, bool update)
{
  int id = FindFreeId(fMarkers);

  fMarkers[id] = new GSMarker(1, pos, 0.0, color);
  
  if(update)
    Update(true);
  
  return id;
}

GSMarker *GSViewport::GetMarker(int id)
{
  if(id < 0 || id >= fMarkers.size())
    return NULL;
  return fMarkers[id];
}

int GSViewport::FindNearestMarker(double e, double tol)
{
  int id = -1;
  double minDist = 1e50;
  double dist;

  for(int i=0; i < fMarkers.size(); i++) {
  	dist = TMath::Abs(fMarkers[i]->GetE1() - e);
  	if(dist < minDist) {
  		minDist = dist;
  		id = i << 1;
  	}
  	
  	if(fMarkers[i]->GetN() > 1) {
  		dist = TMath::Abs(fMarkers[i]->GetE1() - e);
  		if(dist < minDist) {
  			minDist = dist;
  			id = (i << 1) + 1;
  		}
  	}
  }
  
  if(tol >= 0 && minDist > tol)
  	id = -1;
  	
  return id;
}

void GSViewport::DeleteMarker(int id, bool update)
{
  DeleteItem(fMarkers, id);
  if(update)
    Update(true);
}

void GSViewport::DeleteAllMarkers(bool update)
{
  for(int i=0; i < fMarkers.size(); i++)
    delete fMarkers[i];
    
  fMarkers.clear();
  
  if(update)
  	Update(true);
}

int GSViewport::AddSpec(const TH1I *spec, int color, bool update)
{
  int id = FindFreeId(fSpectra);
  fSpectra[id] = new GSDisplaySpec(spec, color);
  
  fMinEnergy = fSpectra[0]->GetMinE();
  fMaxEnergy = fSpectra[0]->GetMaxE();
  
  if(update)
	Update(true);
  
  return id;
}

GSDisplaySpec *GSViewport::GetDisplaySpec(int id)
{
  if(id < 0 || id >= fSpectra.size())
  	return NULL;
  return fSpectra[id];
}

/* void GSViewport::SetSpecCal(int id, double cal0, double cal1, double cal2, double cal3, bool update)
{
	GSDisplaySpec *ds = GetDisplaySpec(id);
	if(ds)
	  ds->SetCal(cal0, cal1, cal2, cal3);
	  
	if(update)
	  Update(true);
} */

void GSViewport::DeleteSpec(int id, bool update)
{
  DeleteItem(fSpectra, id);
  if(update)
    Update(true);
}

void GSViewport::DeleteAllSpecs(bool update)
{
  for(int i=0; i < fSpectra.size(); i++)
    delete fSpectra[i];
    
  fSpectra.clear();
  
  if(update)
  	Update(true);
}

int GSViewport::AddFunc(const TF1 *func, int color, bool update)
{
  int id = FindFreeId(fFunctions);
  fFunctions[id] = new GSDisplayFunc(func, color);
  
  if(update)
    Update(true);
  
  return id;
}

GSDisplayFunc *GSViewport::GetDisplayFunc(int id)
{
  if(id < 0 || id >= fFunctions.size())
  	return NULL;
  return fFunctions[id];
}

/* void GSViewport::SetFuncCal(int id, double cal0, double cal1, double cal2, double cal3, bool update)
{
	GSDisplayFunc *df = GetDisplayFunc(id);
	if(df)
	  df->SetCal(cal0, cal1, cal2, cal3);
	  
	if(update)
	  Update(true);
} */

void GSViewport::DeleteFunc(int id, bool update)
{
  DeleteItem(fFunctions, id);
  if(update)
    Update(true);
}

void GSViewport::DeleteAllFuncs(bool update)
{
  for(int i=0; i < fFunctions.size(); i++)
    delete fFunctions[i];
    
  fFunctions.clear();
  
  if(update)
  	Update(true);
}

void GSViewport::SetLogScale(Bool_t l)
{
  fPainter->SetLogScale(l);
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

  // TODO: debug code, remove
  if(dO == 0) {
	cout << "WARNING: Pointless call to ShiftOffset()." << endl;
	return;
  }

  if(cv) DrawCursor();

  if(dO < -((Int_t) w) || dO > ((Int_t) w)) { // entire area needs updating
	gVirtualX->FillRectangle(GetId(), GetBlackGC()(), x, y, w+1, h+1);
	DrawRegion(x, x+w);
  } else if(dO < 0) {   // move right (note that dO ist negative)
	gVirtualX->CopyArea(GetId(), GetId(), GetWhiteGC()(), x, y,
						w + dO + 1, h + 1, x - dO, y);
	// Note that the area filled by FillRectangle() will not include
	// the border drawn by DrawRectangle() on the right and the bottom
	gVirtualX->FillRectangle(GetId(), GetBlackGC()(), x, y, -dO, h+1);
	DrawRegion(x, x-dO);
  } else { // if(dO > 0) : move left (we caught dO == 0 above)
	gVirtualX->CopyArea(GetId(), GetId(), GetWhiteGC()(), x + dO, y,
						w - dO + 1, h + 1, x, y);
	gVirtualX->FillRectangle(GetId(), GetBlackGC()(), x+w-dO+1, y, dO, h+1);
	DrawRegion(x+w-dO+1, x+w);
  }

  // Redrawing the entire scale is not terribly efficent, but
  // for now I am lazy...
  fPainter->ClearXScale();
  fPainter->DrawXScale(x, x+w);

  if(cv) DrawCursor();
}

void GSViewport::SetViewMode(EViewMode vm)
{
  if(vm != fPainter->GetViewMode()) {
	fPainter->SetViewMode(vm);
	fNeedClear = true;
	gClient->NeedRedraw(this);
  }
}

double GSViewport::GetCursorX(void)
{
  return fPainter->XtoE(fCursorX);
}

int GSViewport::FindMarkerNearestCursor(int tol)
{
  return FindNearestMarker(fPainter->XtoE(fCursorX), fPainter->dXtodE(tol));
}

void GSViewport::XZoomAroundCursor(double f)
{
  fOffset += fPainter->dXtodE(fCursorX - fPainter->GetBaseX()) * (1.0 - 1.0/f);
  fXVisibleRegion /= f;

  Update(false);
}

void GSViewport::ToBegin(void)
{
  SetOffset(fMinEnergy);
}

void GSViewport::ShowAll(void)
{
  fOffset = fMinEnergy;
  fXVisibleRegion = fMaxEnergy - fMinEnergy;
    
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

  //cout << "Update() called" << endl;

  // Remember not to compare floating point values
  // for equality directly (rouding error problems)
  if(TMath::Abs(fXVisibleRegion - fPainter->GetXVisibleRegion()) > 1e-7) {
	redraw = true;
	fPainter->SetXVisibleRegion(fXVisibleRegion);
	UpdateScrollbarRange();
  }

  dO = fOffset - fPainter->GetOffset();
  if(TMath::Abs(dO) > 1e-5) {
	fPainter->SetOffset(fOffset);
  }

  if(fYAutoScale) {
    fYVisibleRegion = fYMinVisibleRegion;
    
    for(int i=0; i < fSpectra.size(); i++) {
      if(fSpectra[i])
	    fYVisibleRegion = TMath::Max(fYVisibleRegion, fPainter->GetYAutoZoom(fSpectra[i]));
	}
  }

  if(TMath::Abs(fYVisibleRegion - fPainter->GetYVisibleRegion()) > 1e-7) {
	redraw = true;
	fPainter->SetYVisibleRegion(fYVisibleRegion);
  }

  // We can only use ShiftOffset if the shift is an integer number
  // of pixels, otherwise we will have to do a full redraw
  dOPix = fPainter->dEtodX(dO);
  if(TMath::Abs(TMath::Ceil(dOPix - 0.5) - dOPix) > 1e-7) {
	redraw = true;
  }
  
  if(redraw) {
	//cout << "redraw" << endl;
	fNeedClear = true;
	gClient->NeedRedraw(this);
  } else if(TMath::Abs(dOPix) > 0.5) {
	ShiftOffset((int) TMath::Ceil(dOPix - 0.5));
  }

  UpdateScrollbarRange();
}

void GSViewport::DrawRegion(UInt_t x1, UInt_t x2)
{
  for(int i=0; i < fSpectra.size(); i++) {
    if(fSpectra[i] != NULL)
      fPainter->DrawSpectrum(fSpectra[i], x1, x2);
  }
    
  for(int i=0; i < fFunctions.size(); i++) {
    if(fFunctions[i] != NULL)
      fPainter->DrawFunction(fFunctions[i], x1, x2);
  }

  for(int i=0; i < fMarkers.size(); i++) {
    if(fMarkers[i] != NULL)
      fPainter->DrawMarker(fMarkers[i], x1, x2);
  }
}

void GSViewport::UpdateScrollbarRange(void)
{
  if(fScrollbar) {
	UInt_t as, rs, pos;
	double minE, maxE;

	as = fPainter->GetWidth();

	minE = fMinEnergy;
	minE = TMath::Min(minE, fPainter->GetOffset());
	
	maxE = fMaxEnergy;
	maxE = TMath::Max(maxE, fPainter->GetOffset() + fXVisibleRegion);

	rs = (UInt_t) TMath::Ceil(fPainter->dEtodX(maxE - minE));

	pos = (UInt_t) TMath::Ceil(fPainter->dEtodX(fPainter->GetOffset() - minE) - 0.5);

	fScrollbar->SetRange(rs, as);
	fScrollbar->SetPosition(pos);
  }
}

void GSViewport::SetOffset(double offset, bool update)
{
  fOffset = offset;
  if(update)
    Update();
}

void GSViewport::SetXVisibleRegion(double region, bool update)
{
  fXVisibleRegion = region;
  if(update)
    Update();
}

void GSViewport::HandleScrollbar(Long_t parm)
{
  // Callback for scrollbar motion

  // Capture nonsense input (TODO: still required?)
  if(parm < 0)
  	parm = 0;

  if(fOffset < fMinEnergy)
	fOffset += fPainter->dXtodE(parm);
  else
	fOffset = fMinEnergy + fPainter->dXtodE(parm);

  Update();
}


Bool_t GSViewport::HandleMotion(Event_t *ev)
{
  bool cv = fCursorVisible;
  if(cv) DrawCursor();
  if(fDragging) {
	SetOffset(fOffset + fPainter->dXtodE((int) fCursorX - ev->fX));
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
  fPainter->SetBasePoint(fLeftBorder + 2, fHeight - fBottomBorder - 2);
  fPainter->SetSize(fWidth - fLeftBorder - fRightBorder - 4,
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

  x = fLeftBorder;
  y = fTopBorder;
  w = fWidth - fLeftBorder - fRightBorder;
  h = fHeight - fTopBorder - fBottomBorder;

  //cout << "DoRedraw()" << endl;

  fPainter->SetXVisibleRegion(fXVisibleRegion);
  fPainter->SetYVisibleRegion(fYVisibleRegion);
  fPainter->SetOffset(fOffset);

  cv = fCursorVisible;
  if(cv) DrawCursor();

  if(fNeedClear) {
	// Note that the area filled by FillRectangle() will not include
	// the border drawn by DrawRectangle() on the right and the bottom
	gVirtualX->FillRectangle(GetId(), GetBlackGC()(), 0, 0, fWidth, fHeight);
	fNeedClear = false;
  }

  gVirtualX->DrawRectangle(GetId(), GetHilightGC()(), x, y, w, h);

  DrawRegion(x+2, x+w-2);
  fPainter->DrawXScale(x+2, x+w-2);
  fPainter->DrawYScale();
  
  if(cv) DrawCursor();
}
