/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2009  The HDTV development team (see file AUTHORS)
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

#ifndef __View2D_h__
#define __View2D_h__

// Seems root 5 cint cannot handle the OS X stdint.h
#if defined(__APPLE__) && defined(__CINT__)
typedef unsigned int uint32_t;
#else
#include <cstdint>
#endif

#include <cmath>

#include <list>
#include <map>

#include "DisplayCut.hh"
#include "Painter.hh"
#include "View.hh"

class TGStatusBar;
class TH2;

namespace HDTV {
namespace Display {

//! View2D: Class implementing a scrollable matrix display
class View2D : public View {
public:
  View2D(const TGWindow *p, UInt_t w, UInt_t h, TH2 *mat);
  ~View2D() override;

  Pixmap_t RenderTile(int xoff, int yoff);
  void RenderCuts(int xoff, int yoff, Pixmap_t pixmap);
  void RenderCut(const DisplayCut &cut, int xoff, int yoff, Pixmap_t pixmap);
  Pixmap_t GetTile(int x, int y);
  void FlushTiles();
  void WeedTiles();
  void DoRedraw() override;
  void Layout() override;
  void Update();
  void UpdateStatusBar();
  void ZoomFull(Bool_t update = true);
  void ZoomAroundCursor(double fx, double fy, Bool_t update = true);
  double Log(double x);

  void SetStatusBar(TGStatusBar *sb) { fStatusBar = sb; }
  void SetDarkMode(bool dark = true);

  void AddCut(const TCutG &cut, bool invertAxes = false);
  void DeleteAllCuts();

  Bool_t HandleKey(Event_t *ev) override;

  void DrawPolyLine(Drawable_t id, GContext_t gc, Int_t n, short *points);

  /* Copied from GSViewport: Merge? */
  Bool_t HandleMotion(Event_t *ev) override;
  Bool_t HandleButton(Event_t *ev) override;
  Bool_t HandleCrossing(Event_t *ev) override;

  double XTileToE(int x) { return x / fPainter.GetXZoom() - fXEOffset; }
  double YTileToE(int y) { return y / fPainter.GetYZoom() + fYEOffset; }

  int EToXTile(double e) { return std::ceil((e + fXEOffset) * fPainter.GetXZoom() - 0.5); }

  int EToYTile(double e) { return std::ceil((e - fYEOffset) * fPainter.GetYZoom() - 0.5); }

  int XScrToTile(int x) { return x - fXTileOffset; }
  int YScrToTile(int y) { return -y + fYTileOffset; }
  double XScrToE(int x) { return XTileToE(XScrToTile(x)); }
  double YScrToE(int y) { return YTileToE(YScrToTile(y)); }
  int ZCtsToScr(double z) { return (z / fZVisibleRegion) * cZColorRange; }

  /*
  void SetXVisibleRegion(double xreg) { fXZoom = (double)fWidth / xreg; }
  void SetYVisibleRegion(double yreg) { fYZoom = (double)fHeight / yreg; }
  */

  void ShiftOffset(int dX, int dY);

  // Calculate floor(pos / cTileSize)
  int GetTileId(int pos) { return pos < 0 ? (pos / cTileSize) - 1 : pos / cTileSize; }

  void ZtoRGB(int z, int &r, int &g, int &b);
  int GetValueAtPixel(int xs, int ys);
  bool GetDarkMode() { return fDarkMode; }

protected:
  std::list<DisplayCut> fCuts;

  std::map<uint32_t, Pixmap_t> fTiles;
  double fZVisibleRegion;
  Bool_t fLogScale;

  TH2 *fMatrix;
  double fMatrixMax;

  double fXEOffset, fYEOffset;
  int fXTileOffset, fYTileOffset;
  bool fDarkMode;

  TGStatusBar *fStatusBar;

  static const int cZColorRange = 5 * 256;
  static const int cTileSize = 128;

  Painter fPainter;

  // Borders
  int fLeftBorder, fRightBorder, fTopBorder, fBottomBorder;

  // Viewport dimensions (updated by Layout())
  int fVPHeight, fVPWidth;

  ClassDefOverride(View2D, 1) // NOLINT
};

} // end namespace Display
} // end namespace HDTV

#endif
