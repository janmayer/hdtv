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

#include "View1D.hh"

#include <cmath>

#include <iostream>
#include <limits>

#include <TGScrollBar.h>
#include <TGStatusBar.h>

#include "DisplaySpec.hh"

// These defines seem to be missing on some systems (e.g. MAC OSX/darwin)
#ifndef M_SQRT2
#define M_SQRT2 1.4142135623730950488016887
#endif

#ifndef M_SQRT1_2
#define M_SQRT1_2 0.70710678118654752440
#endif
// END

namespace HDTV {
namespace Display {

const double View1D::DEFAULT_MAX_ENERGY = 1000.0;
const double View1D::MIN_ENERGY_REGION = 1e-2;

View1D::View1D(const TGWindow *p, UInt_t w, UInt_t h) : View(p, w, h), fCurrentCal(), fDisplayStack(this), fPainter() {
  // Constructor

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
  fTopBorder = 20;
  fBottomBorder = 30;

  // fTopScale = X_SCALE_CHANNEL;
  fTopScale = X_SCALE_NONE;
  fBottomScale = X_SCALE_ENERGY;
  fLeftScale = Y_SCALE_COUNTS;

  fScrollbar = nullptr;
  fStatusBar = nullptr;

  fPainter.SetDrawable(GetId());
  fPainter.SetLogScale(false);
  fPainter.SetXVisibleRegion(fXVisibleRegion);
  fPainter.SetYVisibleRegion(fYVisibleRegion);

  fUpdateLocked = 0;
  fNeedsUpdate = false;
  fForceRedraw = false;

  SetDarkMode();
}

View1D::~View1D() {
  //! Destructor

  fClient->GetGCPool()->FreeGC(fCursorGC); //?
}

void View1D::SetStatusBar(TGStatusBar *sb) {
  //! Sets the status bar on which to ouput our status messages.
  //! Set to NULL to not display any status messages at all.

  fStatusBar = sb;
  UpdateStatusScale();
}

void View1D::SetLogScale(Bool_t l) {
  //! Sets Y (counts) scale to logarithmic or linear

  fPainter.SetLogScale(l);
  Update(true);
}

void View1D::SetUseNorm(Bool_t n) {
  //! Sets whether to use normalization information included in histograms

  fPainter.SetUseNorm(n);
  Update(true);
}

void View1D::YAutoScaleOnce(bool update) {
  //! Sets the Y (counts) scale according to the autoscale rules, but does
  //! not actually enable autoscale mode.

  fYVisibleRegion = fYMinVisibleRegion;

  for (auto &obj : fDisplayStack.fObjects) {
    if (auto *spec = dynamic_cast<DisplaySpec *>(obj)) {
      if (spec->IsVisible()) {
        fYVisibleRegion = std::max(fYVisibleRegion, fPainter.GetYAutoZoom(spec));
      }
    }
  }

  fYOffset = 0.0;

  if (update) {
    Update();
  }
}

void View1D::ShiftOffset(int dO) {
  Bool_t cv = fCursorVisible;
  UInt_t x, y, w, h;

  x = fLeftBorder + 2;
  y = fTopBorder + 2;
  w = fWidth - fLeftBorder - fRightBorder - 4;
  h = fHeight - fTopBorder - fBottomBorder - 4;

  // TODO: debug code, remove
  if (dO == 0) {
    std::cout << "WARNING: Pointless call to ShiftOffset()." << std::endl;
    return;
  }

  if (cv) {
    DrawCursor();
  }

  const TGGC *gc;
  if (fDarkMode) {
    gc = &GetBlackGC();
  } else {
    gc = &GetWhiteGC();
  }

  if (static_cast<unsigned int>(std::abs(dO)) > w) {
    // entire area needs updating
    gVirtualX->FillRectangle(GetId(), (*gc)(), x, y, w + 1, h + 1);
    fDisplayStack.PaintRegion(x, x + w, fPainter);
  } else if (dO < 0) {
    // move right (note that dO ist negative)
    gVirtualX->CopyArea(GetId(), GetId(), (*gc)(), x, y, w + dO + 1, h + 1, x - dO, y);
    // Note that the area filled by FillRectangle() will not include
    // the border drawn by DrawRectangle() on the right and the bottom
    gVirtualX->FillRectangle(GetId(), (*gc)(), x, y, -dO, h + 1);
    fDisplayStack.PaintRegion(x, x - dO, fPainter);
  } else { // if(dO > 0) : move left (we caught dO == 0 above)
    gVirtualX->CopyArea(GetId(), GetId(), (*gc)(), x + dO, y, w - dO + 1, h + 1, x, y);
    gVirtualX->FillRectangle(GetId(), (*gc)(), x + w - dO + 1, y, dO, h + 1);
    fDisplayStack.PaintRegion(x + w - dO + 1, x + w, fPainter);
  }

  // Redrawing the entire scale is not terribly efficient, but
  // for now I am lazy...
  ClearXScales();
  DrawXScales(x, x + w);

  if (cv) {
    DrawCursor();
  }
}

void View1D::ClearXScales() {
  //! Clear the top and the bottom X scale, if it exists

  // Clear top X scale
  if (fTopScale != X_SCALE_NONE) {
    fPainter.ClearTopXScale();
  }

  // Clear bottom X scale
  if (fBottomScale != X_SCALE_NONE) {
    fPainter.ClearBottomXScale();
  }
}

void View1D::DrawXScales(UInt_t x1, UInt_t x2) {
  //! Draw the top and the bottom X scale

  // Draw top X scale
  switch (fTopScale) {
  case X_SCALE_ENERGY:
    fPainter.DrawXScale(x1, x2);
    break;
  case X_SCALE_CHANNEL:
    fPainter.DrawXNonlinearScale(x1, x2, true, fCurrentCal);
    break;
  default:
    break;
  }

  // Draw bottom X scale
  switch (fBottomScale) {
  case X_SCALE_ENERGY:
    fPainter.DrawXScale(x1, x2);
    break;
  case X_SCALE_CHANNEL:
    fPainter.DrawXNonlinearScale(x1, x2, false, fCurrentCal);
    break;
  default:
    break;
  }
}

void View1D::SetViewMode(HDTV::Display::ViewMode vm) {
  //! Set the paint mode for spectra

  if (vm != fPainter.GetViewMode()) {
    fPainter.SetViewMode(vm);
    fNeedClear = true;
    gClient->NeedRedraw(this);
  }
}

//! Returns the X position of the cursor, in energy units.
double View1D::GetCursorX() { return fPainter.XtoE(static_cast<Int_t>(fCursorX)); }

//! Returns the Y position of the cursor, in units of counts.
double View1D::GetCursorY() { return fPainter.YtoC(fCursorY); }

//! Zooms the X (energy) axis around the current cursor position by a factor f.
void View1D::XZoomAroundCursor(double f) {
  fXOffset += fPainter.GetXOffsetDelta(fCursorX, f);
  fXVisibleRegion /= f;

  Update();
}

//! Zooms the Y (counts) axis around the current cursor position by a factor f.
void View1D::YZoomAroundCursor(double f) {
  fYOffset += fPainter.GetYOffsetDelta(fCursorY, f);
  fYVisibleRegion /= f;
  fYAutoScale = false;

  Update();
}

//! Set the X (energy) axis offset such that its zero appears on the left edge
//! of the visible area. Leaves the zoom unchanged.
void View1D::ToBegin() { SetXOffset(fMinEnergy); }

//! Set the X (energy) axis zoom so that all spectra are fully visible. Shows a
//! range from 0 to DEFAULT_MAX_ENERGY if the view contains no spectra.
void View1D::ShowAll() {
  fMinEnergy = std::numeric_limits<double>::infinity();
  fMaxEnergy = -std::numeric_limits<double>::infinity();
  bool hadSpec = false;

  for (auto &obj : fDisplayStack.fObjects) {
    if (auto spec = dynamic_cast<DisplaySpec *>(obj)) {
      if (!spec->IsVisible()) {
        continue;
      }

      fMinEnergy = std::min(fMinEnergy, spec->GetMinE());
      fMaxEnergy = std::max(fMaxEnergy, spec->GetMaxE());
      hadSpec = true;
    }
  }

  if (!hadSpec) {
    fMinEnergy = 0.0;
    fMaxEnergy = DEFAULT_MAX_ENERGY;
  }

  fXOffset = fMinEnergy;
  fXVisibleRegion = std::max(fMaxEnergy - fMinEnergy, MIN_ENERGY_REGION);

  Update();
}

void View1D::LockUpdate() {
  //! Calls to Update() will not actually update the display any more.

  fUpdateLocked++;
}

void View1D::UnlockUpdate() {
  //! Calls to Update() will update the display again. If Update() was called in
  //! the
  //! meantime, this function will do the update.

  if (fUpdateLocked > 0) {
    fUpdateLocked--;
  }

  if (fUpdateLocked <= 0 && fNeedsUpdate) {
    DoUpdate();
  }
}

void View1D::Update(bool forceRedraw) {
  //! Do an update if possible, or remember to do it once it becomes possible
  //! again.

  // cout << "View1D::Update() called, fUpdateLocked=" << fUpdateLocked << endl;

  fForceRedraw = (fForceRedraw || forceRedraw);

  if (fUpdateLocked <= 0) {
    DoUpdate();
  } else {
    fNeedsUpdate = true;
  }
}

void View1D::DoUpdate() {
  //! This function brings the viewport up-to-date after a change in any
  //! relevant parameters. It tries to do so with minimal effort,
  //! i.e. not by redrawing unconditionally.

  double dO, dOPix;

  bool redraw = fForceRedraw; // Do we need a full redraw?

  // cout << "Update() called " << redraw << endl;

  // Remember not to compare floating point values
  // for equality directly (rouding error problems)
  if (std::abs(fXVisibleRegion - fPainter.GetXVisibleRegion()) > 1e-7) {
    redraw = true;
    fPainter.SetXVisibleRegion(fXVisibleRegion);
    UpdateScrollbarRange();
  }

  dO = fXOffset - fPainter.GetXOffset();
  if (std::abs(dO) > 1e-5) {
    fPainter.SetXOffset(fXOffset);
  }

  if (fYAutoScale) {
    YAutoScaleOnce(false);
  }

  if (std::abs(fYVisibleRegion - fPainter.GetYVisibleRegion()) > 1e-7) {
    redraw = true;
    fPainter.SetYVisibleRegion(fYVisibleRegion);
  }

  if (std::abs(fYOffset - fPainter.GetYOffset()) > 1e-5) {
    redraw = true;
    fPainter.SetYOffset(fYOffset);
  }

  // We can only use ShiftOffset if the shift is an integer number
  // of pixels, otherwise we will have to do a full redraw
  dOPix = fPainter.dEtodX(dO);
  if (std::abs(std::ceil(dOPix - 0.5) - dOPix) > 1e-7) {
    redraw = true;
  }

  if (redraw) {
    // cout << "redraw" << endl;
    fNeedClear = true;
    gClient->NeedRedraw(this);
  } else if (std::abs(dOPix) > 0.5) {
    ShiftOffset(std::ceil(dOPix - 0.5));
  }

  UpdateScrollbarRange();
  UpdateStatusPos();
  UpdateStatusScale();

  fNeedsUpdate = false;
  fForceRedraw = false;
}

void View1D::UpdateScrollbarRange() {
  if (fScrollbar) {
    UInt_t as = fPainter.GetWidth();
    double minE = std::min(fMinEnergy, fPainter.GetXOffset());
    double maxE = std::max(fMaxEnergy, fPainter.GetXOffset() + fXVisibleRegion);
    UInt_t rs = std::ceil(fPainter.dEtodX(maxE - minE));
    UInt_t pos = std::ceil(fPainter.dEtodX(fPainter.GetXOffset() - minE) - 0.5);

    fScrollbar->SetRange(rs, as);
    fScrollbar->SetPosition(pos);
  }
}

void View1D::SetXOffset(double offset) {
  //! Sets the offset of the X (energy) axis, in units of energy (??? FIXME).

  fXOffset = offset;
  Update();
}

void View1D::SetXCenter(double center) {
  //! Convenience function to set the center of the X (energy) axis

  SetXOffset(center - fXVisibleRegion / 2.);
}

void View1D::SetYOffset(double offset) {
  // Sets the offset of the Y (counts) axis, in units of counts.

  fYOffset = offset;
  fYAutoScale = false;
  Update();
}

void View1D::ShiftXOffset(double f, bool update) {
  //! Shifts the offset of the X (energy) axis by a factor of f of the
  //! currently visible region.

  fXOffset += f * fXVisibleRegion;
  if (update) {
    Update();
  }
}

void View1D::ShiftYOffset(double f, bool update) {
  //! Shifts the offset of the Y (counts) axis by a factor of f of the
  //! currently visible region.

  fYOffset += f * fYVisibleRegion;
  fYAutoScale = false;
  if (update) {
    Update();
  }
}

void View1D::SetYAutoScale(bool as, bool update) {
  //! Sets or unsets automatic scaling of the Y (counts) axis
  //! If automatic scaling is enabled, the Y axis will always range from
  //! zero to the number of counts in the maximum bin currently visible.

  fYAutoScale = as;
  if (update) {
    Update();
  }
}

void View1D::SetXVisibleRegion(double region, bool update) {
  //! Sets the X size of the visible region in units of energy

  fXVisibleRegion = region;
  if (update) {
    Update();
  }
}

void View1D::SetYVisibleRegion(double region, bool update) {
  //! Sets the Y size of the visible region in units of counts

  fYVisibleRegion = region;
  if (update) {
    Update();
  }
}

void View1D::HandleScrollbar(Long_t parm) {
  //! Callback for scrollbar motion

  // Capture nonsense input (TODO: still required?)
  if (parm < 0) {
    parm = 0;
  }

  if (fXOffset < fMinEnergy) {
    fXOffset += fPainter.dXtodE(parm);
  } else {
    fXOffset = fMinEnergy + fPainter.dXtodE(parm);
  }

  Update();
}

void View1D::UpdateStatusPos() {
  //! Update the cursor position in the status bar

  char temp[32];

  if (fStatusBar) {
    if (fPainter.IsWithin(fCursorX, fCursorY)) {
      snprintf(temp, 32, "%.4g %.4g", fPainter.XtoE(static_cast<Int_t>(fCursorX)), fPainter.YtoC(fCursorY));
      fStatusBar->SetText(temp, 0);
    } else {
      fStatusBar->SetText("", 0);
    }
  }
}

void View1D::UpdateStatusScale() {
  //! Update Y autoscale status in the status bar

  if (fStatusBar) {
    if (fYAutoScale && fPainter.GetUseNorm()) {
      fStatusBar->SetText("AUTO NORM", 1);
    } else if (fYAutoScale && !fPainter.GetUseNorm()) {
      fStatusBar->SetText("AUTO", 1);
    } else if (!fYAutoScale && fPainter.GetUseNorm()) {
      fStatusBar->SetText("NORM", 1);
    } else {
      fStatusBar->SetText("", 1);
    }
  }
}

void View1D::SetStatusText(const char *text) {
  //! Sets text to appear in the text section of the status bar

  if (fStatusBar) {
    fStatusBar->SetText(text, 2);
  }
}

Bool_t View1D::HandleMotion(Event_t *ev) {
  //! Callback for mouse motion

  bool cv = fCursorVisible;
  int accel = (ev->fState & kKeyControlMask) ? 10 : 1;
  int dX = accel * (static_cast<int>(fCursorX) - ev->fX);
  int dY = accel * (static_cast<int>(fCursorY) - ev->fY);
  if (cv) {
    DrawCursor();
  }

  fCursorX = ev->fX;
  fCursorY = ev->fY;

  if (fDragging) {
    SetXOffset(fXOffset + fPainter.dXtodE(dX));
    if (ev->fState & kKeyShiftMask) {
      SetYOffset(fYOffset + fPainter.dYtodC(dY));
    }
  }

  // If we are dragging, Update() will update the statusbar
  if (!fDragging) {
    UpdateStatusPos();
  }

  if (cv) {
    DrawCursor();
  }

  return true;
}

Bool_t View1D::HandleButton(Event_t *ev) {
  //! Callback for mouse button events

  if (ev->fType == kButtonPress) {
    switch (ev->fCode) {
    case 1:
      fDragging = true;
      break;
    case 4:
      if (ev->fState & kKeyShiftMask) {
        YZoomAroundCursor(M_SQRT2);
      } else {
        XZoomAroundCursor(M_SQRT2);
      }
      break;
    case 5:
      if (ev->fState & kKeyShiftMask) {
        YZoomAroundCursor(M_SQRT1_2);
      } else {
        XZoomAroundCursor(M_SQRT1_2);
      }
      break;
    case 6:
      if (ev->fState & kKeyShiftMask) {
        ShiftYOffset(-0.1, true);
      } else {
        ShiftXOffset(-0.1, true);
      }
      break;
    case 7:
      if (ev->fState & kKeyShiftMask) {
        ShiftYOffset(0.1, true);
      } else {
        ShiftXOffset(0.1, true);
      }
      break;
    }
  } else if (ev->fType == kButtonRelease) {
    if (ev->fCode == 1) {
      fDragging = false;
    }
  }

  return true;
}

Bool_t View1D::HandleCrossing(Event_t *ev) {
  //! Callback for mouse crossing events (mouse enters or leaves our screen
  //! area)

  if (ev->fType == kEnterNotify) {
    if (fCursorVisible) {
      DrawCursor();
    }
    /* fCursorX = ev->fX;
    fCursorY = ev->fY; */
    DrawCursor();
    UpdateStatusPos();
  } else if (ev->fType == kLeaveNotify) {
    if (fCursorVisible) {
      DrawCursor();
    }
    if (fStatusBar) {
      fStatusBar->SetText("", 0);
    }
  }

  return true;
}

void View1D::Layout() {
  //! Callback for changes in size of our screen area

  fPainter.SetBasePoint(fLeftBorder + 2, fHeight - fBottomBorder - 2);
  fPainter.SetSize(fWidth - fLeftBorder - fRightBorder - 4, fHeight - fTopBorder - fBottomBorder - 4);
}

void View1D::DoRedraw() {
  //! Redraws the Viewport completely.  If fNeedClear is set, it is
  //! cleared first, otherwise it is just redrawn. This is a callback for
  //! the windowing system. It should not be called directly, but via
  //! gClient->NeedRedraw() .

  Bool_t cv;
  UInt_t x, y, w, h;

  x = fLeftBorder;
  y = fTopBorder;
  w = fWidth - fLeftBorder - fRightBorder;
  h = fHeight - fTopBorder - fBottomBorder;

  // cout << "DoRedraw()" << endl;

  fPainter.SetXVisibleRegion(fXVisibleRegion);
  fPainter.SetYVisibleRegion(fYVisibleRegion);
  fPainter.SetXOffset(fXOffset);
  fPainter.SetYOffset(fYOffset);

  cv = fCursorVisible;
  if (cv) {
    DrawCursor();
  }

  if (fNeedClear) {
    // Note that the area filled by FillRectangle() will not include
    // the border drawn by DrawRectangle() on the right and the bottom
    if (fDarkMode) {
      gVirtualX->FillRectangle(GetId(), GetBlackGC()(), 0, 0, fWidth, fHeight);
    } else {
      gVirtualX->FillRectangle(GetId(), GetWhiteGC()(), 0, 0, fWidth, fHeight);
    }
    fNeedClear = false;
  }

  if (fDarkMode) {
    gVirtualX->DrawRectangle(GetId(), GetHilightGC()(), x, y, w, h);
  } else {
    gVirtualX->DrawRectangle(GetId(), GetShadowGC()(), x, y, w, h);
  }

  fDisplayStack.PaintRegion(x + 2, x + w - 2, fPainter);
  DrawXScales(x + 2, x + w - 2);
  fPainter.DrawYScale();
  fPainter.DrawIDList(fDisplayStack.fObjects);

  if (cv) {
    DrawCursor();
  }
}

void View1D::SetDarkMode(bool dark) {
  fDarkMode = dark;
  if (dark) {
    TGFrame::SetBackgroundColor(GetBlackPixel());
    fPainter.SetAxisGC(GetHilightGC().GetGC());
    fPainter.SetClearGC(GetBlackGC().GetGC());
  } else {
    TGFrame::SetBackgroundColor(GetWhitePixel());
    fPainter.SetAxisGC(GetShadowGC().GetGC());
    fPainter.SetClearGC(GetWhiteGC().GetGC());
  }

  fNeedClear = true;
  gClient->NeedRedraw(this, true);
}

} // end namespace Display
} // end namespace HDTV
