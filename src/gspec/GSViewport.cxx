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
  fYOffset = 0.0;
  fXOffset = 0.0;
  fMinEnergy = 0.0;
  fMaxEnergy = 100.0;
  fYAutoScale = true;
  fNeedClear = false;
  fDragging = false;
  fLeftBorder = 60;
  fRightBorder = 3;
  fTopBorder = 4;
  fBottomBorder = 30;
  
  fScrollbar = NULL;
  fStatusBar = NULL;

  AddInput(kPointerMotionMask | kEnterWindowMask | kLeaveWindowMask
		   | kButtonPressMask | kButtonReleaseMask);

  GCValues_t gval;
  gval.fMask = kGCForeground | kGCFunction;
  gval.fFunction = kGXxor;
  gval.fForeground = GetWhitePixel();
  fCursorGC = gClient->GetGCPool()->GetGC(&gval, true);
  fCursorVisible = false;
  fCursorX = 0;
  fCursorY = 0;
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

  for(int i=0; i < fXMarkers.size(); i++)
	delete fXMarkers[i];
	
  for(int i=0; i < fYMarkers.size(); i++)
    delete fYMarkers[i];
	
  delete fPainter;
}

void GSViewport::SetStatusBar(TGStatusBar *sb)
{
  fStatusBar = sb;
  UpdateStatusScale();
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
int GSViewport::AddXMarker(double pos, int color, bool update)
{
  int id = FindFreeId(fXMarkers);

  fXMarkers[id] = new GSXMarker(1, pos, 0.0, color);
  
  if(update)
    Update(true);
  
  return id;
}

GSXMarker *GSViewport::GetXMarker(int id)
{
  if(id < 0 || id >= fXMarkers.size())
    return NULL;
  return fXMarkers[id];
}

int GSViewport::FindNearestXMarker(double e, double tol)
{
  int id = -1;
  double minDist = 1e50;
  double dist;

  for(int i=0; i < fXMarkers.size(); i++) {
  	dist = TMath::Abs(fXMarkers[i]->GetE1() - e);
  	if(dist < minDist) {
  		minDist = dist;
  		id = i << 1;
  	}
  	
  	if(fXMarkers[i]->GetN() > 1) {
  		dist = TMath::Abs(fXMarkers[i]->GetE1() - e);
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

void GSViewport::DeleteXMarker(int id, bool update)
{
  DeleteItem(fXMarkers, id);
  if(update)
    Update(true);
}

void GSViewport::DeleteAllXMarkers(bool update)
{
  for(int i=0; i < fXMarkers.size(); i++)
    delete fXMarkers[i];
    
  fXMarkers.clear();
  
  if(update)
  	Update(true);
}

int GSViewport::AddYMarker(double pos, int color, bool update)
{
  int id = FindFreeId(fYMarkers);

  fYMarkers[id] = new GSYMarker(1, pos, 0.0, color);
  
  if(update)
    Update(true);
  
  return id;
}

GSYMarker *GSViewport::GetYMarker(int id)
{
  if(id < 0 || id >= fYMarkers.size())
    return NULL;
  return fYMarkers[id];
}

void GSViewport::DeleteYMarker(int id, bool update)
{
  DeleteItem(fYMarkers, id);
  if(update)
    Update(true);
}

void GSViewport::DeleteAllYMarkers(bool update)
{
  for(int i=0; i < fYMarkers.size(); i++)
    delete fYMarkers[i];
    
  fYMarkers.clear();
  
  if(update)
  	Update(true);
}

int GSViewport::AddSpec(const TH1D *spec, int color, bool update)
{
  int id = FindFreeId(fSpectra);
  fSpectra[id] = new GSDisplaySpec(spec, color);
  
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

void GSViewport::YAutoScaleOnce(bool update)
{
  fYVisibleRegion = fYMinVisibleRegion;
   
  for(int i=0; i < fSpectra.size(); i++) {
    if(fSpectra[i])
	  fYVisibleRegion = TMath::Max(fYVisibleRegion, fPainter->GetYAutoZoom(fSpectra[i]));
  }
  
  fYOffset = 0.0;
  
  if(update)
  	Update();
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

double GSViewport::GetCursorX()
{
  return fPainter->XtoE(fCursorX);
}

double GSViewport::GetCursorY()
{
  return fPainter->YtoC(fCursorY);
}

int GSViewport::FindMarkerNearestCursor(int tol)
{
  return FindNearestXMarker(fPainter->XtoE(fCursorX), fPainter->dXtodE(tol));
}

void GSViewport::XZoomAroundCursor(double f)
{
  fXOffset += fPainter->GetXOffsetDelta(fCursorX, f);
  fXVisibleRegion /= f;

  Update(false);
}

void GSViewport::YZoomAroundCursor(double f)
{
  fYOffset += fPainter->GetYOffsetDelta(fCursorY, f);
  fYVisibleRegion /= f;
  fYAutoScale = false;
  
  Update(false);
}

void GSViewport::ToBegin(void)
{
  SetXOffset(fMinEnergy);
}

void GSViewport::ShowAll(void)
{
  fMinEnergy = 0.0;
  fMaxEnergy = 0.0;
  double minE, maxE;
  
  for(int i=0; i<fSpectra.size(); i++) {
    minE = fSpectra[i]->GetMinE();
    maxE = fSpectra[i]->GetMaxE();
    
    if(minE < fMinEnergy) fMinEnergy = minE;
    if(maxE > fMaxEnergy) fMaxEnergy = maxE;
  }

  fXOffset = fMinEnergy;
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

  dO = fXOffset - fPainter->GetXOffset();
  if(TMath::Abs(dO) > 1e-5) {
	fPainter->SetXOffset(fXOffset);
  }

  if(fYAutoScale) {
    YAutoScaleOnce(false);
  }

  if(TMath::Abs(fYVisibleRegion - fPainter->GetYVisibleRegion()) > 1e-7) {
	redraw = true;
	fPainter->SetYVisibleRegion(fYVisibleRegion);
  }
  
  if(TMath::Abs(fYOffset - fPainter->GetYOffset()) > 1e-5) {
    redraw = true;
    fPainter->SetYOffset(fYOffset);
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
  UpdateStatusPos();
  UpdateStatusScale();
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

  for(int i=0; i < fXMarkers.size(); i++) {
    if(fXMarkers[i] != NULL)
      fPainter->DrawXMarker(fXMarkers[i], x1, x2);
  }
  
  for(int i=0; i < fYMarkers.size(); i++) {
    if(fYMarkers[i] != NULL)
      fPainter->DrawYMarker(fYMarkers[i], x1, x2);
  }
}

void GSViewport::UpdateScrollbarRange(void)
{
  if(fScrollbar) {
	UInt_t as, rs, pos;
	double minE, maxE;

	as = fPainter->GetWidth();

	minE = fMinEnergy;
	minE = TMath::Min(minE, fPainter->GetXOffset());
	
	maxE = fMaxEnergy;
	maxE = TMath::Max(maxE, fPainter->GetXOffset() + fXVisibleRegion);

	rs = (UInt_t) TMath::Ceil(fPainter->dEtodX(maxE - minE));

	pos = (UInt_t) TMath::Ceil(fPainter->dEtodX(fPainter->GetXOffset() - minE) - 0.5);

	fScrollbar->SetRange(rs, as);
	fScrollbar->SetPosition(pos);
  }
}

void GSViewport::SetXOffset(double offset, bool update)
{
  fXOffset = offset;
  if(update)
    Update();
}

void GSViewport::SetYOffset(double offset, bool update)
{
  fYOffset = offset;
  fYAutoScale = false;
  if(update)
    Update();
}

void GSViewport::ShiftYOffset(double f, bool update)
{
  fYOffset += f * fYVisibleRegion;
  fYAutoScale = false;
  if(update)
    Update();
}

void GSViewport::SetYAutoScale(bool as, bool update)
{
  fYAutoScale = as;
  if(update)
    Update();
}

void GSViewport::SetXVisibleRegion(double region, bool update)
{
  fXVisibleRegion = region;
  if(update)
    Update();
}

void GSViewport::SetYVisibleRegion(double region, bool update)
{
  fYVisibleRegion = region;
  if(update)
    Update();
}

void GSViewport::HandleScrollbar(Long_t parm)
{
  // Callback for scrollbar motion

  // Capture nonsense input (TODO: still required?)
  if(parm < 0)
  	parm = 0;

  if(fXOffset < fMinEnergy)
	fXOffset += fPainter->dXtodE(parm);
  else
	fXOffset = fMinEnergy + fPainter->dXtodE(parm);

  Update();
}

void GSViewport::UpdateStatusPos()
{
  char temp[32];
  
  if(fStatusBar) {
    if(fPainter->IsWithin(fCursorX, fCursorY)) {
      snprintf(temp, 32, "%.4g %.4g", fPainter->XtoE(fCursorX), fPainter->YtoC(fCursorY));
      fStatusBar->SetText(temp, 0);
    } else {
      fStatusBar->SetText("", 0);
    }
  }
}

void GSViewport::UpdateStatusScale()
{
  if(fStatusBar) {
    if(fYAutoScale)
      fStatusBar->SetText("AUTO", 1);
    else
      fStatusBar->SetText("", 1);
  }
}

Bool_t GSViewport::HandleMotion(Event_t *ev)
{
  bool cv = fCursorVisible;
  int dX = (int) fCursorX - ev->fX;
  if(cv) DrawCursor();
  
  fCursorX = ev->fX;
  fCursorY = ev->fY;
  
  if(fDragging) {
	SetXOffset(fXOffset + fPainter->dXtodE(dX));
  }
    
  // If we are dragging, Update() will update the statusbar
  if(!fDragging)  UpdateStatusPos();
  
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
	UpdateStatusPos();
  } else if(ev->fType == kLeaveNotify) {
	if(fCursorVisible) DrawCursor();
	if(fStatusBar) fStatusBar->SetText("", 0);
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
  fPainter->SetXOffset(fXOffset);
  fPainter->SetYOffset(fYOffset);

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
