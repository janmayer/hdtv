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

#ifndef __View1D_h__
#define __View1D_h__

#include <list>

#include "Calibration.hh"
#include "DisplayStack.hh"
#include "Painter.hh"
#include "View.hh"

enum XScaleType {
  X_SCALE_NONE = 0,
  X_SCALE_ENERGY = 1,
  X_SCALE_CHANNEL = 2,
};

enum YScaleType {
  Y_SCALE_NONE = 0,
  Y_SCALE_COUNTS = 1,
};

class TGHScrollBar;
class TGStatusBar;

namespace HDTV {
namespace Display {

//! Class implementing a display widget for 1d objects (spectra, functions, ...)
class View1D : public View {
  friend class DisplayObj;
  friend class DisplayBlock;

public:
  View1D(const TGWindow *p, UInt_t w, UInt_t h);
  ~View1D() override;

  void SetXOffset(double offset);
  void SetXCenter(double center);
  void SetYOffset(double offset);
  void ShiftXOffset(double f, bool update = true);
  void ShiftYOffset(double f, bool update = true);
  void SetStatusText(const char *text);

  void SetDarkMode(bool dark = true);

  double GetXOffset() { return fXOffset; }
  double GetXVisibleRegion() { return fXVisibleRegion; }
  double GetYOffset() { return fYOffset; }
  double GetYVisibleRegion() { return fYVisibleRegion; }
  bool GetDarkMode() { return fDarkMode; }

  void HandleScrollbar(Long_t parm);
  void SetXVisibleRegion(double region, bool update = true);
  void SetYVisibleRegion(double region, bool update = true);

  double GetYMinVisibleRegion() { return fYMinVisibleRegion; }

  void SetYMinVisibleRegion(double minRegion) {
    fYMinVisibleRegion = minRegion;
    Update();
  }

  void XZoomAroundCursor(double f);
  void YZoomAroundCursor(double f);
  void ToBegin();
  void ShowAll();
  void SetViewMode(ViewMode vm);

  ViewMode GetViewMode() { return fPainter.GetViewMode(); }

  void SetLogScale(Bool_t l);

  void ToggleLogScale() { SetLogScale(!GetLogScale()); }
  Bool_t GetLogScale() { return fPainter.GetLogScale(); }

  void SetUseNorm(Bool_t n);

  void ToggleUseNorm() { SetUseNorm(!GetUseNorm()); }
  Bool_t GetUseNorm() { return fPainter.GetUseNorm(); }
  void ToggleYAutoScale() { SetYAutoScale(!GetYAutoScale()); }

  void SetYAutoScale(bool as, bool update = true);

  Bool_t GetYAutoScale() { return fYAutoScale; }

  void YAutoScaleOnce(bool update = true);

  void SetCalibration(const Calibration &cal) { fCurrentCal = cal; }

  void Layout() override;
  void UpdateScrollbarRange();

  void SetScrollbar(TGHScrollBar *sb) { fScrollbar = sb; }

  void SetStatusBar(TGStatusBar *sb);
  double GetCursorX();
  double GetCursorY();

  void LockUpdate();
  void UnlockUpdate();
  void Update(bool forceRedraw = false);

  /*** Helper functions to draw scales ***/
  void DrawXScales(UInt_t x1, UInt_t x2);
  void ClearXScales();

  // Default parameters
  static const double DEFAULT_MAX_ENERGY;
  static const double MIN_ENERGY_REGION;

protected:
  DisplayStack *GetDisplayStack() { return &fDisplayStack; }
  void DoRedraw() override;
  void DoUpdate();
  Bool_t HandleMotion(Event_t *ev) override;
  Bool_t HandleButton(Event_t *ev) override;
  Bool_t HandleCrossing(Event_t *ev) override;
  void ShiftOffset(int dO);

  void UpdateStatusPos();
  void UpdateStatusScale();

protected:
  double fXVisibleRegion, fYVisibleRegion;
  double fYMinVisibleRegion;
  double fXOffset, fYOffset;
  double fMinEnergy, fMaxEnergy;
  bool fDarkMode;

  Calibration fCurrentCal;
  DisplayStack fDisplayStack;

  Bool_t fYAutoScale;
  Bool_t fNeedClear;
  UInt_t fLeftBorder, fRightBorder, fTopBorder, fBottomBorder;
  Painter fPainter;
  TGHScrollBar *fScrollbar;
  TGStatusBar *fStatusBar;
  XScaleType fTopScale, fBottomScale;
  YScaleType fLeftScale;

  int fUpdateLocked;
  bool fNeedsUpdate;
  bool fForceRedraw;

  ClassDefOverride(View1D, 1) // NOLINT
};

} // end namespace Display
} // end namespace HDTV

#endif
