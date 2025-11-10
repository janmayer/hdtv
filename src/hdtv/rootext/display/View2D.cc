/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2010  The HDTV development team (see file AUTHORS)
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

#include "View2D.hh"

#include <iostream>

#include <KeySymbols.h>
#include <X11/Xlib.h>

#include <TGStatusBar.h>
#include <TH2.h>

namespace HDTV {
namespace Display {

View2D::View2D(const TGWindow *p, UInt_t w, UInt_t h, TH2 *mat)
    : View(p, w, h), fXEOffset{0.0}, fYEOffset{0.0}, fXTileOffset{0}, fYTileOffset{0}, fVPHeight{0}, fVPWidth{0} {
  fMatrix = mat;
  fMatrixMax = fMatrix->GetMaximum();

  fStatusBar = nullptr;

  fLeftBorder = 50;
  fRightBorder = 10;
  fTopBorder = 10;
  fBottomBorder = 30;

  View2D::Layout();
  ZoomFull(false);
  fZVisibleRegion = Log(fMatrixMax) + 1.0;
  fLogScale = true;

  fPainter.SetDrawable(GetId());

  AddInput(kKeyPressMask);

  SetDarkMode();
}

View2D::~View2D() { FlushTiles(); }

void View2D::AddCut(const TCutG &cut, bool invertAxes) {
  fCuts.emplace_back(cut, invertAxes);
  FlushTiles();
  gClient->NeedRedraw(this);
}

void View2D::DeleteAllCuts() {
  fCuts.clear();
  FlushTiles();
  gClient->NeedRedraw(this);
}

void View2D::ShiftOffset(int dX, int dY) {
  fXTileOffset += dX;
  fYTileOffset += dY;

  gClient->NeedRedraw(this);
}

/* Copied from GSViewport: Merge? */
Bool_t View2D::HandleMotion(Event_t *ev) {
  bool cv = fCursorVisible;
  int dX = static_cast<int>(fCursorX) - ev->fX;
  int dY = static_cast<int>(fCursorY) - ev->fY;
  if (cv) {
    DrawCursor();
  }

  fCursorX = ev->fX;
  fCursorY = ev->fY;

  if (fDragging) {
    ShiftOffset(-dX, -dY);
  }

  if (cv) {
    DrawCursor();
  }

  UpdateStatusBar();

  return true;
}

Bool_t View2D::HandleButton(Event_t *ev) {
  //! Callback for mouse button events

  if (ev->fType == kButtonPress) {
    switch (ev->fCode) {
    case 1:
      fDragging = true;
      break;
    case 4:
      if (ev->fState & kKeyShiftMask) {
        ZoomAroundCursor(1., M_SQRT2);
      } else if (ev->fState & kKeyControlMask) {
        ZoomAroundCursor(M_SQRT2, 1.);
      } else {
        ZoomAroundCursor(M_SQRT2, M_SQRT2);
      }
      break;
    case 5:
      if (ev->fState & kKeyShiftMask) {
        ZoomAroundCursor(1., M_SQRT1_2);
      } else if (ev->fState & kKeyControlMask) {
        ZoomAroundCursor(M_SQRT1_2, 1.);
      } else {
        ZoomAroundCursor(M_SQRT1_2, M_SQRT1_2);
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

Bool_t View2D::HandleKey(Event_t *ev) {
  UInt_t keysym;
  char buf[16];

  if (ev->fType == kGKeyPress) {
    gVirtualX->LookupString(ev, buf, 16, keysym);
    switch (keysym) {
    case kKey_w:
      fZVisibleRegion *= 2;
      Update();
      break;
    case kKey_s:
      fZVisibleRegion /= 2;
      Update();
      break;
    case kKey_z:
      ZoomAroundCursor(2.0, 2.0);
      break;
    case kKey_x:
      ZoomAroundCursor(0.5, 0.5);
      break;
    case kKey_1:
      ZoomAroundCursor(1.0 / fPainter.GetXZoom(), 1.0 / fPainter.GetYZoom());
      break;
    case kKey_f:
      ZoomFull();
      break;
    case kKey_l:
      fLogScale = !fLogScale;
      if (fLogScale) {
        fZVisibleRegion = Log(fMatrixMax);
      } else {
        fZVisibleRegion = fMatrixMax;
      }
      Update();
    }
  }

  return true;
}

void View2D::Update() {
  FlushTiles();
  gClient->NeedRedraw(this);
  UpdateStatusBar();
}

void View2D::ZoomAroundCursor(double fx, double fy, Bool_t update) {
  // Convert offset to energy units
  fXEOffset += (fXTileOffset - fLeftBorder) / fPainter.GetXZoom();
  fYEOffset += (fYTileOffset - fTopBorder - fVPHeight) / fPainter.GetYZoom();
  fXTileOffset = fLeftBorder;
  fYTileOffset = fTopBorder + fVPHeight;

  // Adjust offset such that the energy coordinates at the cursor position
  // stay constant
  fXEOffset -= fPainter.GetXOffsetDelta(fCursorX, fx);
  fYEOffset += fPainter.GetYOffsetDelta(fCursorY, fy);

  fPainter.SetXVisibleRegion(fPainter.GetXVisibleRegion() / fx);
  fPainter.SetYVisibleRegion(fPainter.GetYVisibleRegion() / fy);

  if (update) {
    Update();
  }
}

void View2D::ZoomFull(Bool_t update) {
  double xmin = fMatrix->GetXaxis()->GetXmin();
  double ymin = fMatrix->GetYaxis()->GetXmin();
  double xvis = fMatrix->GetXaxis()->GetXmax() - xmin;
  double yvis = fMatrix->GetYaxis()->GetXmax() - ymin;

  fPainter.SetXVisibleRegion(xvis);
  fPainter.SetYVisibleRegion(yvis);
  fXEOffset = -xmin;
  fYEOffset = ymin;

  fXTileOffset = fLeftBorder;
  fYTileOffset = fTopBorder + fVPHeight;

  if (update) {
    Update();
  }
}

double View2D::Log(double x) {
  if (x < 0.0) {
    return 0.0;
  } else if (x < 1.0) {
    return x;
  } else {
    return log(x) + 1.0;
  }
}

Bool_t View2D::HandleCrossing(Event_t *ev) {
  if (ev->fType == kEnterNotify) {
    if (fCursorVisible) {
      DrawCursor();
    }
    fCursorX = ev->fX;
    fCursorY = ev->fY;
    DrawCursor();
  } else if (ev->fType == kLeaveNotify) {
    if (fCursorVisible) {
      DrawCursor();
    }
  }

  return true;
}

void View2D::UpdateStatusBar() {
  char tmp[32];
  if (fStatusBar) {
    snprintf(tmp, 32, "%.1f %.1f", XScrToE(fCursorX), YScrToE(fCursorY));
    fStatusBar->SetText(tmp);
  }
}

void View2D::ZtoRGB(int z, int &r, int &g, int &b) {
  if (z < 0) {
    r = 0;
    g = 0;
    b = 0;
  } else if (z < 256) {
    r = 0;
    g = 0;
    b = z;
  } else if (z < 2 * 256) {
    r = 0;
    g = z - 256;
    b = 255;
  } else if (z < 3 * 256) {
    r = 0;
    g = 255;
    b = 3 * 256 - z - 1;
  } else if (z < 4 * 256) {
    r = z - 3 * 256;
    g = 255;
    b = 0;
  } else if (z < 5 * 256) {
    r = 255;
    g = 5 * 256 - z - 1;
    b = 0;
  } else {
    r = 255;
    g = 0;
    b = 0;
  }
}

int View2D::GetValueAtPixel(int x, int y) {
  double z;

  z = fMatrix->GetBinContent(fMatrix->FindBin(XTileToE(x), YTileToE(y)));

  if (fLogScale) {
    z = Log(z);
  }

  return ZCtsToScr(z);
}

Pixmap_t View2D::RenderTile(int xoff, int yoff) {
  int x, y, z;
  int r, g, b;
  Pixmap_t pixmap;
  Drawable_t img;
  ULong_t pixel;
  unsigned long r_mask, g_mask, b_mask;
  int r_shift, g_shift, b_shift;

  img = gVirtualX->CreateImage(cTileSize, cTileSize);

  /* Calculate shifts required for color channels. Positive shifts go to the
     left, negative shifts go to the right.

     NOTE: This code only works as long as the bit mask for each color channel
     contains only a single, continuous strings of 1s. Otherwise, much more
     complicated and slow code would be needed, as a single shift would no
     longer be sufficient.   */
  const XImage *x_img = reinterpret_cast<XImage *>(img);
  r_mask = x_img->red_mask;
  g_mask = x_img->green_mask;
  b_mask = x_img->blue_mask;

  r_shift = g_shift = b_shift = 0;
  while (r_mask) {
    r_mask >>= 1;
    r_shift++;
  }
  r_shift -= 8;
  while (g_mask) {
    g_mask >>= 1;
    g_shift++;
  }
  g_shift -= 8;
  while (b_mask) {
    b_mask >>= 1;
    b_shift++;
  }
  b_shift -= 8;

  r_mask = x_img->red_mask;
  g_mask = x_img->green_mask;
  b_mask = x_img->blue_mask;

  for (y = 0; y < cTileSize; y++) {
    for (x = 0; x < cTileSize; x++) {
      z = GetValueAtPixel(x + xoff * cTileSize, -(y + yoff * cTileSize));
      ZtoRGB(z, r, g, b);

      r = (r_shift > 0) ? (r << r_shift) : (r >> (-r_shift));
      g = (g_shift > 0) ? (g << g_shift) : (g >> (-g_shift));
      b = (b_shift > 0) ? (b << b_shift) : (b >> (-b_shift));
      pixel = (r & r_mask) | (g & g_mask) | (b & b_mask);
      gVirtualX->PutPixel(img, x, y, pixel);
    }
  }

  pixmap = gVirtualX->CreatePixmap(GetId(), cTileSize, cTileSize);
  if (fDarkMode) {
    gVirtualX->PutImage(pixmap, GetWhiteGC()(), img, 0, 0, 0, 0, cTileSize, cTileSize);
  } else {
    gVirtualX->PutImage(pixmap, GetBlackGC()(), img, 0, 0, 0, 0, cTileSize, cTileSize);
  }
  gVirtualX->DeleteImage(img);

  RenderCuts(xoff, yoff, pixmap);

  return pixmap;
}

void View2D::RenderCuts(int xoff, int yoff, Pixmap_t pixmap) {
  for (auto &cut : fCuts) {
    RenderCut(cut, xoff, yoff, pixmap);
  }
}

void View2D::RenderCut(const DisplayCut &cut, int xoff, int yoff, Pixmap_t pixmap) {
  const double x1 = XTileToE(xoff * cTileSize);
  const double y1 = YTileToE(-(yoff + 1) * cTileSize + 1);
  const double x2 = XTileToE((xoff + 1) * cTileSize - 1);
  const double y2 = YTileToE(-yoff * cTileSize);

  if (x2 < cut.BB_x1() || x1 > cut.BB_x2() || y2 < cut.BB_y1() || y1 > cut.BB_y2()) {
    return;
  }

  const int N = cut.GetPoints().size();
  TArrayS points(2 * N + 2);
  for (int i = 0; i < N; ++i) {
    points[2 * i] = EToXTile(cut.GetPoints()[i].x) - xoff * cTileSize;
    points[2 * i + 1] = -EToYTile(cut.GetPoints()[i].y) - yoff * cTileSize;
  }
  points[2 * N] = points[0];
  points[2 * N + 1] = points[1];

  if (fDarkMode) {
    DrawPolyLine(pixmap, GetWhiteGC()(), N + 1, points.GetArray());
  } else {
    DrawPolyLine(pixmap, GetBlackGC()(), N + 1, points.GetArray());
  }

  /* double x1 = EToXTile(cut.BB_x1()) - xoff*cTileSize;
  double y1 = -EToYTile(cut.BB_y1()) - yoff*cTileSize;
  double x2 = EToXTile(cut.BB_x2()) - xoff*cTileSize;
  double y2 = -EToYTile(cut.BB_y2()) - yoff*cTileSize;
  gVirtualX->DrawRectangle(pixmap, GetWhiteGC()(),
                           x1, y2, x2-x1, y1-y2); */
}

void View2D::DrawPolyLine(Drawable_t id, GContext_t gc, Int_t n, short *points) {
  XDrawLines(reinterpret_cast<::Display *>(gVirtualX->GetDisplay()), static_cast<Drawable>(id),
             reinterpret_cast<GC>(gc), reinterpret_cast<XPoint *>(points), n, CoordModeOrigin);
}

template <typename ContainerT, typename Cond> void erase_if(ContainerT &container, Cond cond) {
  auto it = container.begin();
  while (it != container.end()) {
    if (cond(*it)) {
      it = container.erase(it);
    } else {
      ++it;
    }
  }
}

void View2D::WeedTiles() {
  erase_if(fTiles, [&](decltype(fTiles)::value_type &tile) {
    int16_t x = tile.first & 0xFFFF;
    int16_t y = tile.first >> 16;
    int xpos = x * cTileSize + fXTileOffset;
    int ypos = y * cTileSize + fYTileOffset;

    if (xpos < -2 * cTileSize || xpos > static_cast<int>(fWidth) + cTileSize || ypos < -2 * cTileSize ||
        ypos > static_cast<int>(fHeight) + cTileSize) {
      // cout << "Deleting Tile " << x << " " << y << " " << xpos << " " << ypos
      // << endl;
      gVirtualX->DeletePixmap(tile.second);
      return true;
    }
    return false;
  });
}

//! Destroy all tiles in the cache, causing them to be redrawn when needed (e.g.
//! after a zoom level change)
void View2D::FlushTiles() {
  for (auto &tile : fTiles) {
    gVirtualX->DeletePixmap(tile.second);
  }
  fTiles.clear();
}

Pixmap_t View2D::GetTile(int x, int y) {
  uint32_t id = (y << 16) | (x & 0xFFFF);

  auto iter = fTiles.find(id);
  if (iter == fTiles.end()) {
    Pixmap_t tile = RenderTile(x, y);
    // cout << "Rendering Tile " << x << " " << y << endl;
    fTiles.insert(std::make_pair(id, tile));
    return tile;
  } else {
    return iter->second;
  }
}

//! Callback for changes in size of our screen area
void View2D::Layout() {
  // Convert offset to energy units
  fXEOffset += (fXTileOffset - fLeftBorder) / fPainter.GetXZoom();
  fYEOffset += (fYTileOffset - fTopBorder - fVPHeight) / fPainter.GetYZoom();

  fVPWidth = fWidth - fLeftBorder - fRightBorder;
  fVPHeight = fHeight - fTopBorder - fBottomBorder;

  fXTileOffset = fLeftBorder;
  fYTileOffset = fTopBorder + fVPHeight;

  fPainter.SetBasePoint(fLeftBorder, fHeight - fBottomBorder);
  fPainter.SetSize(fVPWidth, fVPHeight);

  FlushTiles();
}

void View2D::DoRedraw() {
  int x, y;
  int x1, y1, x2, y2;
  bool cv = fCursorVisible;
  Pixmap_t tile;
  unsigned int NTiles;
  int src_x, src_y, width, height, dest_x, dest_y;

  x1 = GetTileId(fLeftBorder - fXTileOffset);
  x2 = GetTileId(fLeftBorder + fVPWidth - fXTileOffset);
  y1 = GetTileId(fTopBorder - fYTileOffset);
  y2 = GetTileId(fTopBorder + fVPHeight - fYTileOffset);

  if (cv) {
    DrawCursor();
  }

  // gVirtualX->FillRectangle(GetId(), GetWhiteGC()(), 0, 0, fWidth, fHeight);

  for (x = x1; x <= x2; x++) {
    for (y = y1; y <= y2; y++) {
      tile = GetTile(x, y);

      // Calculate parameters for tile copy operation
      src_x = 0;
      src_y = 0;
      width = cTileSize;
      height = cTileSize;
      dest_x = x * cTileSize + fXTileOffset;
      dest_y = y * cTileSize + fYTileOffset;

      // Perform clipping
      if (dest_x + width > fLeftBorder + fVPWidth) {
        width = fLeftBorder + fVPWidth - dest_x;
      }

      if (dest_y + height > fTopBorder + fVPHeight) {
        height = fTopBorder + fVPHeight - dest_y;
      }

      if (dest_x < fLeftBorder) {
        src_x += fLeftBorder - dest_x;
        width -= fLeftBorder - dest_x;
        dest_x = fLeftBorder;
      }

      if (dest_y < fTopBorder) {
        src_y += fTopBorder - dest_y;
        height -= fTopBorder - dest_y;
        dest_y = fTopBorder;
      }

      if (fDarkMode) {
        gVirtualX->CopyArea(tile, GetId(), GetWhiteGC()(), src_x, src_y, width, height, dest_x, dest_y);
      } else {
        gVirtualX->CopyArea(tile, GetId(), GetBlackGC()(), src_x, src_y, width, height, dest_x, dest_y);
      }
    }
  }

  fPainter.SetXOffset(XScrToE(fLeftBorder));
  fPainter.SetYOffset(YScrToE(fTopBorder + fVPHeight));

  fPainter.ClearBottomXScale();
  fPainter.DrawXScale(fLeftBorder, fWidth - fRightBorder);
  if (fDarkMode) {
    gVirtualX->FillRectangle(GetId(), GetBlackGC()(), 0, 0, fLeftBorder, fHeight);
  } else {
    gVirtualX->FillRectangle(GetId(), GetWhiteGC()(), 0, 0, fLeftBorder, fHeight);
  }
  // fPainter.ClearYScale();
  fPainter.DrawYScale();

  if (cv) {
    DrawCursor();
  }

  NTiles = (fWidth / cTileSize + 4) * (fHeight / cTileSize + 4);
  if (fTiles.size() > NTiles) {
    // cout << "Weeding..." << endl;
    WeedTiles();
  }
}

void View2D::SetDarkMode(bool dark) {
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

  gClient->NeedRedraw(this, true);
}

} // end namespace Display
} // end namespace HDTV
