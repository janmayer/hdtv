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

#include "Painter.hh"

#include <TGX11.h>

#include "DisplayFunc.hh"
#include "DisplaySpec.hh"
#include "XMarker.hh"
#include "YMarker.hh"

namespace HDTV {
namespace Display {

Painter::Painter()
    : fWidth{1}, fHeight{1}, fXBase{0}, fYBase{0}, fXZoom{0.01}, fYZoom{0.01}, fXVisibleRegion{100.0},
      fYVisibleRegion{100.0}, fXOffset{0.0}, fYOffset{0.0}, fLogScale{false}, fUseNorm{false}, fViewMode{kVMHollow},
      fDrawable{static_cast<Drawable_t>(-1)}, fAxisGC{static_cast<GContext_t>(-1)}, fClearGC{static_cast<GContext_t>(
                                                                                        -1)},
      fFont{gClient->GetResourcePool()->GetDefaultFont()}, fFontStruct{fFont->GetFontStruct()} {}

void Painter::DrawFunction(DisplayFunc *dFunc, int x1, int x2) {
  //! Function to draw a DisplayFunc object

  int x;
  int y;
  int hClip = fYBase - fHeight;
  int lClip = fYBase;
  double ch;
  double norm = fUseNorm ? dFunc->GetNorm() : 1.0;

  // Do x axis clipping
  x1 = std::max(x1, EtoX(dFunc->GetMinE()));
  x2 = std::min(x2, EtoX(dFunc->GetMaxE()));

  int ly, cy;
  ch = dFunc->E2Ch(XtoE(x1 - 0.5));
  ly = CtoY(norm * dFunc->Eval(ch));

  for (x = x1; x <= x2; x++) {
    ch = dFunc->E2Ch(XtoE(x + 0.5));
    y = cy = CtoY(norm * dFunc->Eval(ch));

    if (std::min(y, ly) <= lClip && std::max(y, ly) >= hClip) {
      if (cy < hClip) {
        cy = hClip;
      } else if (cy > lClip) {
        cy = lClip;
      }

      if (ly < hClip) {
        ly = hClip;
      } else if (ly > lClip) {
        ly = lClip;
      }

      gVirtualX->DrawLine(fDrawable, dFunc->GetGC()->GetGC(), x, ly, x, cy);
    }

    ly = y;
  }
}

void Painter::DrawSpectrum(DisplaySpec *dSpec, int x1, int x2) {
  //! Function to draw a DisplaySpec object

  int x;
  int y;
  int hClip = fYBase - fHeight;
  int lClip = fYBase;

  // Do x axis clipping
  x1 = std::max(x1, EtoX(dSpec->GetMinE()));
  x2 = std::min(x2, EtoX(dSpec->GetMaxE()));

  switch (fViewMode) {
  case kVMSolid:
    for (x = x1; x <= x2; x++) {
      y = GetYAtPixel(dSpec, x);
      if (y < hClip) {
        y = hClip;
      }
      if (y > lClip) {
        y = lClip;
      }
      gVirtualX->DrawLine(fDrawable, dSpec->GetGC()->GetGC(), x, fYBase, x, y);
    }
    break;

  case kVMDotted:
    for (x = x1; x <= x2; x++) {
      y = GetYAtPixel(dSpec, x);
      if (y >= hClip && y <= lClip) {
        gVirtualX->DrawRectangle(fDrawable, dSpec->GetGC()->GetGC(), x, y, 0, 0);
      }
    }
    break;

  case kVMHollow:
    int ly, y1, y2;
    ly = GetYAtPixel(dSpec, x1 - 1);

    for (x = x1; x <= x2; x++) {
      y = GetYAtPixel(dSpec, x);

      if (y < ly) {
        if (ly >= hClip && y <= lClip) {
          y1 = ly;
          if (y1 > lClip) {
            y1 = lClip;
          }
          y2 = y;
          if (y2 < hClip) {
            y2 = hClip;
          }
          gVirtualX->DrawLine(fDrawable, dSpec->GetGC()->GetGC(), x, y1, x, y2);
        }
      } else {
        if (y >= hClip && ly <= lClip) {
          y1 = ly;
          if (y1 < hClip) {
            y1 = hClip;
          }
          y2 = y;
          if (y2 > lClip) {
            y2 = lClip;
          }
          if (x > fXBase) {
            gVirtualX->DrawLine(fDrawable, dSpec->GetGC()->GetGC(), x - 1, y1, x - 1, y2);
          }
          if (y <= lClip) {
            gVirtualX->DrawRectangle(fDrawable, dSpec->GetGC()->GetGC(), x, y2, 0, 0);
          }
        }
      }

      ly = y;
    }
    break;
  }
}

void Painter::DrawXMarker(XMarker *marker, int x1, int x2) {
  //! Function to draw an XMarker object

  int xm1, xm2;

  // Draw first marker of the pair
  xm1 = EtoX(marker->GetE1());
  if ((xm1 + marker->GetWidth(fFontStruct)) >= x1 && xm1 <= x2) {
    gVirtualX->DrawLine(fDrawable, marker->GetGC_1()->GetGC(), xm1, fYBase, xm1, fYBase - fHeight);

    if (!marker->GetID().empty()) {
      Rectangle_t rect{};
      rect.fX = x1;
      rect.fY = fYBase - fHeight;
      rect.fWidth = x2 - x1 + 1;
      rect.fHeight = fHeight;
      gVirtualX->SetClipRectangles(marker->GetGC_1()->GetGC(), 0, 0, &rect, 1);
      DrawString(marker->GetGC_1()->GetGC(), xm1 + 2, fYBase - fHeight + 2, marker->GetID().c_str(),
                 marker->GetID().size(), kLeft, kTop);
      marker->GetGC_1()->SetClipMask(kNone);
    }
  }

  if (marker->GetN() > 1) {
    // Draw second marker of the pair
    xm2 = EtoX(marker->GetE2());

    if (xm2 >= x1 && xm2 <= x2) {
      gVirtualX->DrawLine(fDrawable, marker->GetGC_2()->GetGC(), xm2, fYBase, xm2, fYBase - fHeight);
    }

    // Draw connecting line
    if (xm1 > xm2) {
      int tmp = xm2;
      xm2 = xm1;
      xm1 = tmp;
    }

    if (xm1 < x1) {
      xm1 = x1;
    }
    if (xm2 > x2) {
      xm2 = x2;
    }

    if (xm1 <= xm2) {
      int h;
      if (marker->fConnectTop) {
        h = fYBase - fHeight;
      } else {
        h = fYBase;
      }
      gVirtualX->DrawLine(fDrawable, marker->GetGC_C()->GetGC(), xm1, h, xm2, h);
    }
  }
}

void Painter::DrawYMarker(YMarker *marker, int x1, int x2) {
  //! Function to draw a YMarker object

  int y;

  // Draw first marker of the pair
  y = CtoY(marker->GetP1());
  if (y <= fYBase && y >= (fYBase - fHeight)) {
    gVirtualX->DrawLine(fDrawable, marker->GetGC_1()->GetGC(), x1, y, x2, y);
  }

  // Draw second marker of the pair
  if (marker->GetN() > 1) {
    y = CtoY(marker->GetP2());
    if (y <= fYBase && y >= (fYBase - fHeight)) {
      gVirtualX->DrawLine(fDrawable, marker->GetGC_2()->GetGC(), x1, y, x2, y);
    }
  }
}

void Painter::DrawIDList(const std::list<DisplayObj *> &objects) {
  //! Draw a colered list of IDs. This is a quick hack, really.
  int x = fXBase;

  std::string tmp;
  for (const auto &obj : objects) {
    if (auto spec = dynamic_cast<const DisplaySpec *>(obj)) {
      if (!spec->IsVisible()) {
        continue;
      }
      tmp = spec->GetID();
      tmp.push_back(' ');
      gVirtualX->DrawString(fDrawable, spec->GetGC()->GetGC(), x, fYBase - fHeight - 5, tmp.c_str(), tmp.size());
      x += gVirtualX->TextWidth(fFontStruct, tmp.c_str(), tmp.size());
    }
  }
}

void Painter::UpdateYZoom() {
  double yRange = fYVisibleRegion;

  if (fLogScale) {
    yRange = ModLog(fYOffset + fYVisibleRegion) - ModLog(fYOffset);
  }

  fYZoom = fHeight / yRange;
}

void Painter::SetSize(int w, int h) {
  fWidth = w;
  fHeight = h;
  fXZoom = fWidth / fXVisibleRegion;
  UpdateYZoom();
}

int Painter::GetYAtPixel(DisplaySpec *dSpec, Int_t x) {
  if (fUseNorm) {
    return CtoY(dSpec->GetNorm() * GetCountsAtPixel(dSpec, x));
  } else {
    return CtoY(GetCountsAtPixel(dSpec, x));
  }
}

double Painter::GetCountsAtPixel(DisplaySpec *dSpec, Int_t x) {
  //! Get counts at screen X position x
  // FIXME: this could be significantly optimized...

  // Calculate the lower and upper edge of the screen bin in fractional
  // histogram channels, applying the calibration if specified
  double c1 = dSpec->E2Ch(XtoE(x - 0.5));
  double c2 = dSpec->E2Ch(XtoE(x + 0.5));

  // Our calibration may have a negative slope...
  if (c1 > c2) {
    double ct = c1;
    c1 = c2;
    c2 = ct;
  }

  // In "zoomed out" mode (many histogram bins per screen bin), each screen
  // bin is set to the maximum counts of all histogram bin whose center
  // lies within the screen bin. This ensures that peaks stay visible, but
  // avoids artificial broadening of peaks (as every histogram bin counts
  // towards exactly one screen bin).
  // In "zoomed in" mode (many screen bins per histogram bin), each screen
  // bin is set to the value of the histogram bin it lies in.
  Int_t b1 = dSpec->FindBin(c1);
  Int_t b2 = dSpec->FindBin(c2);

  // Shortcut for "zoomed in" mode
  if (b1 == b2) {
    return dSpec->GetClippedBinContent(b1);
  }

  // Get bins to consider for maximum: b1..b2 (inclusive)
  if (dSpec->GetBinCenter(b1) < c1) {
    b1++;
  }
  if (dSpec->GetBinCenter(b2) >= c2) {
    b2--;
  }

  if (b2 >= b1) {
    // "Zoomed out" mode
    return dSpec->GetRegionMax(b1, b2);
  } else {
    // "Zoomed in" mode, special case
    double c = dSpec->E2Ch(XtoE(static_cast<double>(x)));
    Int_t b = dSpec->FindBin(c);
    return dSpec->GetClippedBinContent(b);
  }
}

double Painter::ModLog(double x) {
  //! Modified log function:
  //!           = log(x) + 1,    1 <= x
  //! ModLog(x) = x,            -1 <  x <   1
  //!           = -log(-x) - 1,       x <= -1
  //!
  //! This function is continous with a continous first derivative,
  //! positive monotonic, and goes from R to R

  if (x > 1.0) {
    return std::log(x) + 1.0;
  } else if (x > -1.0) {
    return x;
  } else {
    return -std::log(-x) - 1.0;
  }
}

double Painter::InvModLog(double x) {
  //! Inverse modified log (see Painter::ModLog for definition)

  if (x > 1.0) {
    return std::exp(x - 1.0);
  } else if (x > -1.0) {
    return x;
  } else {
    return -std::exp(-x - 1.0);
  }
}

int Painter::CtoY(double c) {
  if (fLogScale) {
    c = ModLog(c) - ModLog(fYOffset);
  } else {
    c = c - fYOffset;
  }

  return fYBase - static_cast<int>(std::ceil(c * fYZoom - 0.5));
}

double Painter::YtoC(int y) {
  double c;
  c = static_cast<double>(fYBase - y) / fYZoom;

  if (fLogScale) {
    c = InvModLog(c + ModLog(fYOffset));
  } else {
    c = c + fYOffset;
  }

  return c;
}

double Painter::GetXOffsetDelta(int x, double f) { return dXtodE(x - fXBase) * (1.0 - 1.0 / f); }

double Painter::GetYOffsetDelta(int y, double f) {
  if (fLogScale) {
    // This case is presently unhandled...
    return 0.0;
  } else {
    return (1.0 - 1.0 / f) * static_cast<double>(fYBase - y) / fYZoom;
  }
}

double Painter::GetYAutoZoom(DisplaySpec *dSpec) {
  double e1, e2;
  int b1, b2;
  double norm = fUseNorm ? dSpec->GetNorm() * 1.02 : 1.02;

  e1 = XtoE(fXBase);
  e2 = XtoE(fXBase + fWidth);
  b1 = dSpec->FindBin(dSpec->E2Ch(e1));
  b2 = dSpec->FindBin(dSpec->E2Ch(e2));

  return dSpec->GetMax_Cached(b1, b2) * norm;
}

void Painter::ClearTopXScale() {
  //! This function will clear the region containing the
  //! bottom X scale so that it can be redrawn with a different
  //! offset. We need to be careful not to affect the y scale,
  //! since it is not necessarily redrawn as well.
  gVirtualX->FillRectangle(fDrawable, fClearGC, fXBase - 2, fYBase - fHeight - 11, fWidth + 4, 9);
  gVirtualX->FillRectangle(fDrawable, fClearGC, fXBase - 40, fYBase - fHeight - 32, fWidth + 60, 20);
}

void Painter::ClearBottomXScale() {
  //! This function will clear the region containing the
  //! bottom X scale so that it can be redrawn with a different
  //! offset. We need to be careful not to affect the y scale,
  //! since it is not necessarily redrawn as well.
  gVirtualX->FillRectangle(fDrawable, fClearGC, fXBase - 2, fYBase + 3, fWidth + 4, 9);
  gVirtualX->FillRectangle(fDrawable, fClearGC, fXBase - 40, fYBase + 12, fWidth + 60, 20);
}

void Painter::GetTicDistance(double tic, double &major_tic, double &minor_tic, int &n) {
  double exp;

  // limit tic distance to a sensible value
  if (tic < 0.001) {
    tic = 0.001;
  }

  // Write tic in the form tic * exp, where exp = 10^n with n \in N
  // and 1 < tic <= 10
  exp = 1.0;
  n = 0;
  while (tic <= 1.0) {
    tic *= 10;
    exp *= 0.1;
    n--;
  }

  while (tic > 10.0) {
    tic *= 0.1;
    exp *= 10;
    n++;
  }

  if (tic > 5.0) {
    major_tic = 10.0 * exp;
    minor_tic = 5.0 * exp;
    n++;
  } else if (tic > 2.0) {
    major_tic = 5.0 * exp;
    minor_tic = 1.0 * exp;
  } else { // if(tic > 1.0)
    major_tic = 2.0 * exp;
    minor_tic = 1.0 * exp;
  }
}

void Painter::DrawXNonlinearScale(Int_t x1, Int_t x2, bool top, const Calibration &cal) {
  int x;
  int y = top ? fYBase - fHeight - 2 : fYBase + 2;
  int sgn = top ? -1 : 1;
  char tmp[16];
  char fmt[5] = "%.0f";
  size_t len;
  int i, i2;
  double major_tic, minor_tic;

  // GetTicDistance(cal.E2Ch(XtoE(x1)) - cal.E2Ch(XtoE(x2)), major_tic,
  // minor_tic, n);
  minor_tic = 10.0;
  major_tic = 50.0;

  // Set the required precision
  // if(n < 0)
  //  fmt[2] = '0' - n;

  // Draw the minor tics
  i = std::ceil(cal.E2Ch(XtoE(x1)) / minor_tic);
  i2 = std::floor(cal.E2Ch(XtoE(x2)) / minor_tic);

  for (; i <= i2; ++i) {
    x = EtoX(cal.Ch2E(i * minor_tic));
    gVirtualX->DrawLine(fDrawable, fAxisGC, x, y, x, y + 5 * sgn);
  }

  // Draw the major tics
  i = std::ceil(cal.E2Ch(XtoE(x1)) / major_tic);
  i2 = std::floor(cal.E2Ch(XtoE(x2)) / major_tic);

  for (; i <= i2; ++i) {
    x = EtoX(cal.Ch2E(i * major_tic));
    gVirtualX->DrawLine(fDrawable, fAxisGC, x, y, x, y + 9 * sgn);

    // TODO: handle len > 16
    len = snprintf(tmp, 16, fmt, major_tic * i);
    if (top) {
      DrawString(fAxisGC, x, y - 12, tmp, len, kCenter, kBottom);
    } else {
      DrawString(fAxisGC, x, y + 12, tmp, len, kCenter, kTop);
    }
  }
}

void Painter::DrawXScale(Int_t x1, Int_t x2) {
  Int_t x;
  Int_t y = fYBase + 2;
  char tmp[16];
  char fmt[5] = "%.0f";
  size_t len;
  int i, i2;
  double major_tic, minor_tic;
  int n;

  GetTicDistance(50.0 / fXZoom, major_tic, minor_tic, n);

  // Set the required precision
  if (n < 0) {
    fmt[2] = '0' - n;
  }

  // Draw the minor tics
  i = std::ceil(XtoE(x1) / minor_tic);
  i2 = std::floor(XtoE(x2) / minor_tic);

  for (; i <= i2; ++i) {
    x = EtoX(i * minor_tic);
    gVirtualX->DrawLine(fDrawable, fAxisGC, x, y + 1, x, y + 5);
  }

  // Draw the major tics
  i = std::ceil(XtoE(x1) / major_tic);
  i2 = std::floor(XtoE(x2) / major_tic);

  for (; i <= i2; ++i) {
    x = EtoX(i * major_tic);
    gVirtualX->DrawLine(fDrawable, fAxisGC, x, y + 1, x, y + 9);

    // TODO: handle len > 16
    len = snprintf(tmp, 16, fmt, major_tic * i);
    DrawString(fAxisGC, x, y + 12, tmp, len, kCenter, kTop);
  }
}

void Painter::DrawYScale() {
  if (fLogScale) {
    DrawYLogScale();
  } else {
    DrawYLinearScale();
  }
}

void Painter::DrawString(GContext_t gc, int x, int y, const char *str, size_t len, HTextAlign hAlign,
                         VTextAlign vAlign) {
  int max_ascent, max_descent;
  int width;

  gVirtualX->GetFontProperties(fFontStruct, max_ascent, max_descent);
  width = gVirtualX->TextWidth(fFontStruct, str, len);

  switch (hAlign) {
  case kLeft:
    break;
  case kCenter:
    x -= width / 2;
    break;
  case kRight:
    x -= width;
    break;
  }

  switch (vAlign) {
  case kBottom:
    y -= max_descent;
    break;
  case kBaseline:
    break;
  case kMiddle:
    y += (max_ascent - max_descent) / 2;
    break;
  case kTop:
    y += max_ascent;
  }

  gVirtualX->DrawString(fDrawable, gc, x, y, str, len);
}

void Painter::DrawYLinearScale() {
  int x = fXBase - 2;
  int y;
  char tmp[16];
  size_t len;
  int i, i2;
  double major_tic, minor_tic;
  int n;

  GetTicDistance(50.0 / fYZoom, major_tic, minor_tic, n);

  // Draw the minor tics
  i = std::ceil(YtoC(fYBase) / minor_tic);
  i2 = std::floor(YtoC(fYBase - fHeight) / minor_tic);

  for (; i <= i2; ++i) {
    y = CtoY(i * minor_tic);
    gVirtualX->DrawLine(fDrawable, fAxisGC, x - 5, y, x, y);
  }

  // Draw the major tics
  i = std::ceil(YtoC(fYBase) / major_tic);
  i2 = std::floor(YtoC(fYBase - fHeight) / major_tic);

  for (; i <= i2; ++i) {
    y = CtoY(i * major_tic);
    gVirtualX->DrawLine(fDrawable, fAxisGC, x - 9, y, x, y);

    // TODO: handle len > 16
    len = snprintf(tmp, 16, "%.4g", major_tic * i);
    DrawString(fAxisGC, x - 12, y, tmp, len, kRight, kMiddle);
  }
}

void Painter::DrawYLogScale() {
  int yTop = fYBase - fHeight;
  int minDist;
  double cMin, cMax;

  cMin = YtoC(fYBase);
  cMax = YtoC(yTop);

  // Calculate the distance (in pixels) between the closest tics
  // (either 9 and 10 or the upmost tics drawn)
  if (cMax > 10.0) {
    minDist = CtoY(9.0) - CtoY(10.0);
  } else {
    minDist = CtoY(std::floor(YtoC(yTop)) - 1.0) - CtoY(std::floor(YtoC(yTop)));
  }

  if (cMax > 0.0) {
    _DrawYLogScale(minDist, +1, cMin, cMax);
  }

  if (cMax >= 0.0 && cMin <= 0.0) {
    DrawYMajorTic(0.0);
  }

  if (cMin < 0.0) {
    _DrawYLogScale(minDist, -1, -cMax, -cMin);
  }
}

void Painter::_DrawYLogScale(int minDist, int sgn, double cMin, double cMax) {
  double exp = 1.0;
  int c = 1;

  // Find out where to begin
  while ((10.0 * exp) < cMin) {
    exp *= 10.0;
  }
  while (c * exp < cMin) {
    c += 1;
  }

  // Scale: 0, 1, 2, 3, ..., 9, 10, 20, ... without minor tics
  if (minDist >= 20) {
    while (c * exp <= cMax) {
      DrawYMajorTic(sgn * c * exp);

      if (++c > 9) {
        exp *= 10.0;
        c = 1;
      }
    }

    return;
  }

  // Scale: 0, 1, 3, 10, 30, ... with minor tics at 2, 4, 5, ..., 9, 20, ...
  minDist = CtoY(1.0) - CtoY(3.0);

  if (minDist >= 30) {
    while (c * exp <= cMax) {
      if (c == 1 || c == 3) {
        DrawYMajorTic(sgn * c * exp);
      } else {
        DrawYMinorTic(sgn * c * exp);
      }

      if (++c > 9) {
        exp *= 10.0;
        c = 1;
      }
    }

    // Label the last minor tic drawn, if appropriate
    if (c == 1) {
      DrawYMajorTic(sgn * 0.9 * exp, false);
    } else if (c > 5) {
      DrawYMajorTic(sgn * (c - 1) * exp, false);
    }

    return;
  }

  // Scale: 0, 1, 10, 100, ... with minor tics at 3, 30, ...
  if (minDist >= 5) {
    while (c * exp <= cMax) {
      if (c == 1) {
        DrawYMajorTic(sgn * c * exp);
        c = 3;
      } else {
        DrawYMinorTic(sgn * c * exp);
        c = 1;
        exp *= 10.0;
      }
    }

    return;
  }

  // Scale: 0, 1, 10, 100 without minor tics
  while (exp <= cMax) {
    DrawYMajorTic(sgn * exp);
    exp *= 10.0;
  }
}

void Painter::DrawYMajorTic(double c, bool drawLine) {
  int x = fXBase - 2;
  int y = CtoY(c);
  char tmp[16];
  size_t len;

  if (drawLine) {
    gVirtualX->DrawLine(fDrawable, fAxisGC, x - 9, y, x, y);
  }

  // TODO: handle len > 16
  len = snprintf(tmp, 16, "%.4g", c);
  DrawString(fAxisGC, x - 12, y, tmp, len, kRight, kMiddle);
}

inline void Painter::DrawYMinorTic(double c) {
  int x = fXBase - 2;
  int y = CtoY(c);
  gVirtualX->DrawLine(fDrawable, fAxisGC, x - 5, y, x, y);
}

} // end namespace Display
} // end namespace HDTV
