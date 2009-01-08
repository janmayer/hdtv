/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2009  Norbert Braun <n.braun@ikp.uni-koeln.de>
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

#include "View1D.h"
#include <TMath.h>
#include <Riostream.h>

namespace HDTV {
namespace Display {

const double View1D::DEFAULT_MAX_ENERGY = 1000.0;
const double View1D::MIN_ENERGY_REGION = 1e-2;

View1D::View1D(const TGWindow *p, UInt_t w, UInt_t h)
  : HDTV::Display::View(p, w, h)
{
  SetBackgroundColor(GetBlackPixel());
  fXVisibleRegion = DEFAULT_MAX_ENERGY;
  fYMinVisibleRegion = 20.0;
  fYVisibleRegion = fYMinVisibleRegion;
  fYOffset = 0.0;
  fXOffset = 0.0;
  fMinEnergy = 0.0;
  fMaxEnergy = DEFAULT_MAX_ENERGY;
  fYAutoScale = true;
  fNeedClear = false;
  
  fLeftBorder = 60;
  fRightBorder = 3;
  fTopBorder = 4;
  fBottomBorder = 30;
  
  fScrollbar = NULL;
  fStatusBar = NULL;

  fPainter = new HDTV::Display::Painter();
  fPainter->SetDrawable(GetId());
  fPainter->SetAxisGC(GetHilightGC().GetGC());
  fPainter->SetClearGC(GetBlackGC().GetGC());
  fPainter->SetLogScale(false);
  fPainter->SetXVisibleRegion(fXVisibleRegion);
  fPainter->SetYVisibleRegion(fYVisibleRegion);
}

View1D::~View1D() {
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

void View1D::SetStatusBar(TGStatusBar *sb)
{
  fStatusBar = sb;
  UpdateStatusScale();
}

template <class itemType>
int View1D::FindFreeId(std::vector<itemType> &items)
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
void View1D::DeleteItem(std::vector<itemType> &items, int id)
{
  if(id < 0 || id >= items.size())
  	return;
  
  delete items[id];
  items[id] = NULL;
  
  while(items.back() == NULL)
  	items.pop_back();
}

/*** Object management functions ***/
int View1D::AddXMarker(double pos, int color, bool update)
{
  int id = FindFreeId(fXMarkers);

  fXMarkers[id] = new XMarker(1, pos, 0.0, color);
  
  if(update)
    Update(true);
  
  return id;
}

XMarker *View1D::GetXMarker(int id)
{
  if(id < 0 || id >= fXMarkers.size())
    return NULL;
  return fXMarkers[id];
}

int View1D::FindNearestXMarker(double e, double tol)
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

void View1D::DeleteXMarker(int id, bool update)
{
  DeleteItem(fXMarkers, id);
  if(update)
    Update(true);
}

void View1D::DeleteAllXMarkers(bool update)
{
  for(int i=0; i < fXMarkers.size(); i++)
    delete fXMarkers[i];
    
  fXMarkers.clear();
  
  if(update)
  	Update(true);
}

int View1D::AddYMarker(double pos, int color, bool update)
{
  int id = FindFreeId(fYMarkers);

  fYMarkers[id] = new YMarker(1, pos, 0.0, color);
  
  if(update)
    Update(true);
  
  return id;
}

YMarker *View1D::GetYMarker(int id)
{
  if(id < 0 || id >= fYMarkers.size())
    return NULL;
  return fYMarkers[id];
}

void View1D::DeleteYMarker(int id, bool update)
{
  DeleteItem(fYMarkers, id);
  if(update)
    Update(true);
}

void View1D::DeleteAllYMarkers(bool update)
{
  for(int i=0; i < fYMarkers.size(); i++)
    delete fYMarkers[i];
    
  fYMarkers.clear();
  
  if(update)
  	Update(true);
}

int View1D::AddSpec(const TH1 *spec, int color, bool update)
{
  int id = FindFreeId(fSpectra);
  fSpectra[id] = new DisplaySpec(spec, color);
  
  if(update)
	Update(true);
  
  return id;
}

DisplaySpec *View1D::GetDisplaySpec(int id)
{
  if(id < 0 || id >= fSpectra.size())
  	return NULL;
  return fSpectra[id];
}

/* void View1D::SetSpecCal(int id, double cal0, double cal1, double cal2, double cal3, bool update)
{
	GSDisplaySpec *ds = GetDisplaySpec(id);
	if(ds)
	  ds->SetCal(cal0, cal1, cal2, cal3);
	  
	if(update)
	  Update(true);
} */

void View1D::DeleteSpec(int id, bool update)
{
  DeleteItem(fSpectra, id);
  if(update)
    Update(true);
}

void View1D::DeleteAllSpecs(bool update)
{
  for(int i=0; i < fSpectra.size(); i++)
    delete fSpectra[i];
    
  fSpectra.clear();
  
  if(update)
  	Update(true);
}

int View1D::AddFunc(const TF1 *func, int color, bool update)
{
  int id = FindFreeId(fFunctions);
  fFunctions[id] = new DisplayFunc(func, color);
  
  if(update)
    Update(true);
  
  return id;
}

DisplayFunc *View1D::GetDisplayFunc(int id)
{
  if(id < 0 || id >= fFunctions.size())
  	return NULL;
  return fFunctions[id];
}

/* void View1D::SetFuncCal(int id, double cal0, double cal1, double cal2, double cal3, bool update)
{
	GSDisplayFunc *df = GetDisplayFunc(id);
	if(df)
	  df->SetCal(cal0, cal1, cal2, cal3);
	  
	if(update)
	  Update(true);
} */

void View1D::DeleteFunc(int id, bool update)
{
  DeleteItem(fFunctions, id);
  if(update)
    Update(true);
}

void View1D::DeleteAllFuncs(bool update)
{
  for(int i=0; i < fFunctions.size(); i++)
    delete fFunctions[i];
    
  fFunctions.clear();
  
  if(update)
  	Update(true);
}

void View1D::SetLogScale(Bool_t l)
{
  fPainter->SetLogScale(l);
  Update(true);
}

void View1D::YAutoScaleOnce(bool update)
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

void View1D::ShiftOffset(int dO)
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

void View1D::SetViewMode(HDTV::Display::ViewMode vm)
{
  if(vm != fPainter->GetViewMode()) {
	fPainter->SetViewMode(vm);
	fNeedClear = true;
	gClient->NeedRedraw(this);
  }
}

double View1D::GetCursorX()
{
  return fPainter->XtoE(fCursorX);
}

double View1D::GetCursorY()
{
  return fPainter->YtoC(fCursorY);
}

int View1D::FindMarkerNearestCursor(int tol)
{
  return FindNearestXMarker(fPainter->XtoE(fCursorX), fPainter->dXtodE(tol));
}

void View1D::XZoomAroundCursor(double f)
{
  fXOffset += fPainter->GetXOffsetDelta(fCursorX, f);
  fXVisibleRegion /= f;

  Update(false);
}

void View1D::YZoomAroundCursor(double f)
{
  fYOffset += fPainter->GetYOffsetDelta(fCursorY, f);
  fYVisibleRegion /= f;
  fYAutoScale = false;
  
  Update(false);
}

void View1D::ToBegin(void)
{
  SetXOffset(fMinEnergy);
}

void View1D::ShowAll(void)
{
  fMinEnergy = 0.0;
  fMaxEnergy = 0.0;
  double minE, maxE;
  int i;
  
  for(i=0; i<fSpectra.size(); i++) {
    minE = fSpectra[i]->GetMinE();
    maxE = fSpectra[i]->GetMaxE();
    
    if(minE < fMinEnergy) fMinEnergy = minE;
    if(maxE > fMaxEnergy) fMaxEnergy = maxE;
  }

  if(i == 0)
    fMaxEnergy = DEFAULT_MAX_ENERGY;
  
  fXOffset = fMinEnergy;
  fXVisibleRegion = TMath::Max(fMaxEnergy - fMinEnergy, MIN_ENERGY_REGION);
  
    
  Update(false);
}

/* View1D::Update

   This function brings the viewport up-to-date after a change in any
   relevant parameters. It tries to do so with minimal effort,
   i.e. not by redrawing unconditionally.
*/
void View1D::Update(bool redraw)
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

void View1D::DrawRegion(UInt_t x1, UInt_t x2)
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

void View1D::UpdateScrollbarRange(void)
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

void View1D::SetXOffset(double offset, bool update)
{
  fXOffset = offset;
  if(update)
    Update();
}

void View1D::SetYOffset(double offset, bool update)
{
  fYOffset = offset;
  fYAutoScale = false;
  if(update)
    Update();
}

void View1D::ShiftXOffset(double f, bool update)
{
  fXOffset += f * fXVisibleRegion;
  if(update)
    Update();
}


void View1D::ShiftYOffset(double f, bool update)
{
  fYOffset += f * fYVisibleRegion;
  fYAutoScale = false;
  if(update)
    Update();
}

void View1D::SetYAutoScale(bool as, bool update)
{
  fYAutoScale = as;
  if(update)
    Update();
}

void View1D::SetXVisibleRegion(double region, bool update)
{
  fXVisibleRegion = region;
  if(update)
    Update();
}

void View1D::SetYVisibleRegion(double region, bool update)
{
  fYVisibleRegion = region;
  if(update)
    Update();
}

void View1D::HandleScrollbar(Long_t parm)
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

void View1D::UpdateStatusPos()
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

void View1D::UpdateStatusScale()
{
  if(fStatusBar) {
    if(fYAutoScale)
      fStatusBar->SetText("AUTO", 1);
    else
      fStatusBar->SetText("", 1);
  }
}

void View1D::SetStatusText(const char *text)
{
  if(fStatusBar)
    fStatusBar->SetText(text, 2);
}

Bool_t View1D::HandleMotion(Event_t *ev)
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

Bool_t View1D::HandleButton(Event_t *ev)
{
  if(ev->fType == kButtonPress) {
	switch(ev->fCode) {
	  case 1:
	    fDragging = true;
	    break;
	  case 4:
	    XZoomAroundCursor(M_SQRT2);
	    break;
	  case 5:
	    XZoomAroundCursor(M_SQRT1_2);
	    break;
	}
  } else if(ev->fType == kButtonRelease) {
  	if(ev->fCode == 1)
      fDragging = false;
  }
}

Bool_t View1D::HandleCrossing(Event_t *ev)
{
  if(ev->fType == kEnterNotify) {
	if(fCursorVisible) DrawCursor();
	/* fCursorX = ev->fX;
	fCursorY = ev->fY; */
	DrawCursor();
	UpdateStatusPos();
  } else if(ev->fType == kLeaveNotify) {
	if(fCursorVisible) DrawCursor();
	if(fStatusBar) fStatusBar->SetText("", 0);
  }
}

void View1D::Layout(void)
{ 
  fPainter->SetBasePoint(fLeftBorder + 2, fHeight - fBottomBorder - 2);
  fPainter->SetSize(fWidth - fLeftBorder - fRightBorder - 4,
						fHeight - fTopBorder - fBottomBorder - 4);
}

/* View1D::DoRedraw

   Redraws the Viewport completely.  If fNeedClear is set, it is
   cleared first, otherwise it is just redrawn. This is a callback for
   the windowing system. It should not be called directly, but via 
   gClient->NeedRedraw() .
*/
void View1D::DoRedraw(void)
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

} // end namespace Display
} // end namespace HDTV
