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

#ifndef __GSViewport_h__
#define __GSViewport_h__

#include <TGFrame.h>
#include <TGScrollBar.h>
#include "GSSpecPainter.h"
#include "GSSpectrum.h"
#include "GSDisplaySpec.h"

class GSViewport : public TGFrame { 
 public:
  GSViewport(const TGWindow *p, UInt_t w, UInt_t h);
  ~GSViewport(void);
  void SetOffset(double offset);
  inline double GetOffset(void) { return fLazyOffset; }
  void Update(bool redraw=false);
  void HandleScrollbar(Long_t parm);
  void LoadSpectrum(GSSpectrum *spec);
  void SetXVisibleRegion(double region);
  void XZoomAroundCursor(double f);
  void ToBegin(void);
  void ShowAll(void);
  void SetViewMode(EViewMode vm);
  inline EViewMode GetViewMode(void) { return fSpecPainter->GetViewMode(); }
  void SetLogScale(Bool_t l);
  inline void ToggleLogScale(void) { SetLogScale(!GetLogScale()); }
  inline Bool_t GetLogScale(void) { return fSpecPainter->GetLogScale(); }
  void Layout(void);
  void UpdateScrollbarRange(void);
  inline void SetScrollbar(TGHScrollBar *sb) { fScrollbar = sb; }
  
  /* inline UInt_t GetAvailSize(void) { fSpecPainter->GetAvailSize(); }
  inline UInt_t GetRequiredSize(void)
  { return (UInt_t) ((fMaxEnergy - fMinEnergy) * GetLazyXZoom()); } */

 protected:
  void DoRedraw(void);
  Bool_t HandleMotion(Event_t *ev);
  Bool_t HandleButton(Event_t *ev);
  Bool_t HandleCrossing(Event_t *ev);
  void DrawCursor(void);
  void ShiftOffset(int dO);

  // Return the X zoom which _should_ currently be used,
  // even if the update has not taken place yet.
  inline double GetLazyXZoom(void)
	{ return ((double)fSpecPainter->GetWidth()) / fXVisibleRegion; }

 protected:
  double fLazyOffset;
  double fXVisibleRegion;
  double fMinEnergy, fMaxEnergy;
  int fUpdateLocked;
  int fNbins;
  GSSpectrum *fSpec;
  GSDisplaySpec *fDispSpec;
  Bool_t fYAutoScale;
  Bool_t fNeedClear;
  TGGC *fCursorGC;
  UInt_t fCursorX, fCursorY;
  Bool_t fCursorVisible;
  Bool_t fDragging;
  UInt_t fLeftBorder, fRightBorder, fTopBorder, fBottomBorder;
  GSSpecPainter *fSpecPainter;
  TGHScrollBar *fScrollbar;

  //  ClassDef(ViewerFrame,0)
};

#endif
