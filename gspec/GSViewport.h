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

#include <vector>
#include <TGFrame.h>
#include <TGScrollBar.h>
#include "GSPainter.h"
#include "GSDisplaySpec.h"
#include "GSMarker.h"

class GSViewport : public TGFrame { 
 public:
  GSViewport(const TGWindow *p, UInt_t w, UInt_t h);
  ~GSViewport(void);
  void SetOffset(double offset);
  inline double GetOffset(void) { return fOffset; }
  void Update(bool redraw=false);
  void HandleScrollbar(Long_t parm);
  void SetXVisibleRegion(double region);
  void XZoomAroundCursor(double f);
  void ToBegin(void);
  void ShowAll(void);
  void SetViewMode(EViewMode vm);
  inline EViewMode GetViewMode(void) { return fPainter->GetViewMode(); }
  void SetLogScale(Bool_t l);
  inline void ToggleLogScale(void) { SetLogScale(!GetLogScale()); }
  inline Bool_t GetLogScale(void) { return fPainter->GetLogScale(); }
  void Layout(void);
  void UpdateScrollbarRange(void);
  inline void SetScrollbar(TGHScrollBar *sb) { fScrollbar = sb; }
  double GetCursorX(void);
  int FindMarkerNearestCursor(int tol=3);
  
  /*** Object management functions ***/
  int AddMarker(double pos, int color=defaultColor, bool update=true);
  GSMarker *GetMarker(int id);
  int FindNearestMarker(double e, double tol=-1.0);
  void DeleteMarker(int id, bool update=true);
  void DeleteAllMarkers(bool update=true);
  int AddSpec(const TH1I *spec, int color=defaultColor, bool update=true);
  GSDisplaySpec *GetDisplaySpec(int id);
  //void SetSpecCal(int id, double cal0, double cal1, double cal2, double cal3, bool update);
  void DeleteSpec(int id, bool update=true);
  void DeleteAllSpecs(bool update=true);
  int AddFunc(const TF1 *func, int color=defaultColor, bool update=true);
  GSDisplayFunc *GetDisplayFunc(int id);
  //void SetFuncCal(int id, double cal0, double cal1, double cal2, double cal3, bool update);
  void DeleteFunc(int id, bool update=true);
  void DeleteAllFuncs(bool update=true);
   
  ClassDef(GSViewport, 1)
  
 protected:
  void DoRedraw(void);
  void DrawRegion(UInt_t x1, UInt_t x2);
  Bool_t HandleMotion(Event_t *ev);
  Bool_t HandleButton(Event_t *ev);
  Bool_t HandleCrossing(Event_t *ev);
  void DrawCursor(void);
  void ShiftOffset(int dO);
  template <class itemType>
  int FindFreeId(std::vector<itemType> &items);
  template <class itemType>
  void DeleteItem(std::vector<itemType> &items, int id);
 
 protected:
  double fXVisibleRegion, fYVisibleRegion;
  double fYMinVisibleRegion;
  double fOffset;
  double fMinEnergy, fMaxEnergy;
  std::vector<GSDisplaySpec *> fSpectra;
  std::vector<GSDisplayFunc *> fFunctions;
  std::vector<GSMarker *> fMarkers;
  Bool_t fYAutoScale;
  Bool_t fNeedClear;
  TGGC *fCursorGC;
  UInt_t fCursorX, fCursorY;
  Bool_t fCursorVisible;
  Bool_t fDragging;
  UInt_t fLeftBorder, fRightBorder, fTopBorder, fBottomBorder;
  GSPainter *fPainter;
  TGHScrollBar *fScrollbar;

  //  ClassDef(ViewerFrame,0)
};

#endif
