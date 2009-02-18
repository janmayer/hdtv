/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2008  Norbert Braun <n.braun@ikp.uni-koeln.de>
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

#include "Painter.h"
#include "DisplaySpec.h"
#include "DisplayFunc.h"
#include "XMarker.h"
#include "YMarker.h"

#include <Riostream.h>


namespace HDTV {
namespace Display {

Painter::Painter()
{
  SetXVisibleRegion(100.0);
  SetYVisibleRegion(100.0);
  SetLogScale(false);
  SetBasePoint(0, 0);
  SetSize(0, 0);
  SetViewMode(kVMHollow);
  SetXOffset(0.0);
  SetYOffset(0.0);

  fFont = gClient->GetResourcePool()->GetDefaultFont();
  fFontStruct = fFont->GetFontStruct();
}

void Painter::DrawFunction(DisplayFunc *dFunc, int x1, int x2)
{
  int x;
  int y;
  int hClip = fYBase - fHeight;
  int lClip = fYBase;
  double ch;

  /* Do x axis clipping */
  int minX = EtoX(dFunc->GetMinE());
  int maxX = EtoX(dFunc->GetMaxE());

  if(x1 < minX) x1 = minX;
  if(x2 > maxX)	x2 = maxX;

  int ly, cy;
  ch = dFunc->E2Ch(XtoE((double) x1 - 0.5));
  ly = CtoY(dFunc->Eval(ch));

  for(x=x1; x<=x2; x++) {
    ch = dFunc->E2Ch(XtoE((double) x + 0.5));
    y = cy = CtoY(dFunc->Eval(ch));
    
    if(TMath::Min(y, ly) <= lClip && TMath::Max(y, ly) >= hClip) {
      if(cy < hClip) cy = hClip;
      else if(cy > lClip) cy = lClip;
      if(ly < hClip) ly = hClip;
      else if(ly > lClip) ly = lClip;
    
      gVirtualX->DrawLine(fDrawable, dFunc->GetGC()->GetGC(),
      					  x, ly, x, cy);
    }
    
    ly = y;
  }
}

void Painter::DrawSpectrum(DisplaySpec *dSpec, int x1, int x2)
{
  int x;
  int y;
  int hClip = fYBase - fHeight;
  int lClip = fYBase;
  

  /* Do x axis clipping */
  int minX = EtoX(dSpec->GetMinE());
  int maxX = EtoX(dSpec->GetMaxE());

  if(x1 < minX) x1 = minX;
  if(x2 > maxX)	x2 = maxX;

  switch(fViewMode) {
  case kVMSolid:
	for(x=x1; x<=x2; x++) {
	  y = GetYAtPixel(dSpec, x);
	  if(y < hClip) y = hClip;
	  if(y > lClip) y = lClip;
	  gVirtualX->DrawLine(fDrawable, dSpec->GetGC()->GetGC(),
						  x, fYBase, x, y);
	}
	break;
	
  case kVMDotted:
	for(x=x1; x<=x2; x++) {
	  y = GetYAtPixel(dSpec, x);
	  if(y >= hClip && y <= lClip)
		gVirtualX->DrawRectangle(fDrawable, dSpec->GetGC()->GetGC(),
								 x, y, 0, 0);
	}
	break;
	
  case kVMHollow:
	int ly, y1, y2;
	ly = GetYAtPixel(dSpec, x1-1);

	for(x=x1; x<=x2; x++) {
	  y = GetYAtPixel(dSpec, x);
	  
	  if(y < ly) {
		if(ly >= hClip && y <= lClip) {
		  y1 = ly;
		  if(y1 > lClip) y1 = lClip;
		  y2 = y;
		  if(y2 < hClip) y2 = hClip;
		  gVirtualX->DrawLine(fDrawable, dSpec->GetGC()->GetGC(),
							  x, y1, x, y2);
		}
	  } else {
		if(y >= hClip && ly <= lClip) {
		  y1 = ly;
		  if(y1 < hClip) y1 = hClip;
		  y2 = y;
		  if(y2 > lClip) y2 = lClip;
		  if(x > fXBase)
			gVirtualX->DrawLine(fDrawable, dSpec->GetGC()->GetGC(),
								x-1, y1, x-1, y2);
		  if(y <= lClip)
		    gVirtualX->DrawRectangle(fDrawable, dSpec->GetGC()->GetGC(),
									 x, y2, 0, 0);
		}
	  }
	  
	  ly = y;
	}
	break;
  }
}

void Painter::DrawXMarker(XMarker *marker, int x1, int x2)
{
  int xm1, xm2;

  /* Draw first marker of the pair */
  xm1 = EtoX(marker->GetE1());
  if(xm1 >= x1 && xm1 <= x2)
	gVirtualX->DrawLine(fDrawable, marker->GetGC_1()->GetGC(), 
						xm1, fYBase, xm1, fYBase - fHeight);

  if(marker->GetN() > 1) {
	/* Draw second marker of the pair */
	xm2 = EtoX(marker->GetE2());

	if(xm2 >= x1 && xm2 <= x2)
	  gVirtualX->DrawLine(fDrawable, marker->GetGC_2()->GetGC(), 
						  xm2, fYBase, xm2, fYBase - fHeight);

	/* Draw connecting line */
	if(xm1 < x1) xm1 = x1;
	if(xm2 > x2) xm2 = x2;

	if(xm1 <= xm2)
	  gVirtualX->DrawLine(fDrawable, marker->GetGC_C()->GetGC(),
						  xm1, fYBase - fHeight, xm2, fYBase - fHeight);
  }
}

void Painter::DrawYMarker(YMarker *marker, int x1, int x2)
{
  int y;
  
  /* Draw first marker of the pair */
  y = CtoY(marker->GetP1());
  if(y <= fYBase && y >= (fYBase - fHeight)) {
    gVirtualX->DrawLine(fDrawable, marker->GetGC_1()->GetGC(),
                        x1, y, x2, y);
  }
  
  /* Draw second marker of the pair */
  if(marker->GetN() > 1) {
    y = CtoY(marker->GetP2());
    if(y <= fYBase && y >= (fYBase - fHeight)) {
      gVirtualX->DrawLine(fDrawable, marker->GetGC_2()->GetGC(),
                          x1, y, x2, y);
    }
  }
}

void Painter::UpdateYZoom()
{
  double yRange = fYVisibleRegion;

  if(fLogScale)
  	yRange = ModLog(fYOffset + fYVisibleRegion) - ModLog(fYOffset);

  fYZoom = fHeight / yRange;
}

void Painter::SetSize(int w, int h)
{
  fWidth = w;
  fHeight = h;
  fXZoom = fWidth / fXVisibleRegion;
  UpdateYZoom();
}

double Painter::GetCountsAtPixel(DisplaySpec *dSpec, UInt_t x)
{
  // Get counts at screen X position x
  // FIXME: this could be significantly optimized...
  
  // Calculate the lower and upper edge of the screen bin in fractional
  // histogram channels, applying the calibration if specified
  double c1 = dSpec->E2Ch(XtoE((double) x - 0.5));
  double c2 = dSpec->E2Ch(XtoE((double) x + 0.5));
  
  // Our calibration may have a negative slope...
  if(c1 > c2) {
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
  if(b1 == b2)
    return dSpec->GetClippedBinContent(b1);

  // Get bins to consider for maximum: b1..b2 (inclusive)
  if(dSpec->GetBinCenter(b1) < c1) b1++;
  if(dSpec->GetBinCenter(b2) >= c2) b2 --;
  
  if(b2 >= b1) {
    // "Zoomed out" mode
    return dSpec->GetRegionMax(b1, b2);
  } else {
    // "Zoomed in" mode, special case
    double c = dSpec->E2Ch(XtoE((double) x));
    Int_t b = dSpec->FindBin(c);
    return dSpec->GetClippedBinContent(b);
  }
}

/* Modified log function:
          = log(x) + 1,    1 <= x
ModLog(x) = x,            -1 <  x <   1
          = -log(-x) - 1,       x <= -1
          
This function is continous with a continous first derivative,
positive monotonic, and goes from R to R  */
double Painter::ModLog(double x)
{
  if(x > 1.0) {
    return TMath::Log(x) + 1.0;
  } else if(x > -1.0) {
    return x;
  } else {
    return -TMath::Log(-x) - 1.0;
  }
}

/* Inverse modified log (see definition above) */
double Painter::InvModLog(double x)
{
  if(x > 1.0) {
    return TMath::Exp(x - 1.0);
  } else if(x > -1.0) {
    return x;
  } else {
    return -TMath::Exp(-x - 1.0);
  }
}

int Painter::CtoY(double c)
{
  if(fLogScale)
	c = ModLog(c) - ModLog(fYOffset);
  else
    c = c - fYOffset;

  return fYBase - (int) TMath::Ceil(c * fYZoom - 0.5);
}

double Painter::YtoC(int y)
{
  double c;
  c = (double) (fYBase - y) / fYZoom;

  if(fLogScale)
	c = InvModLog(c + ModLog(fYOffset));
  else
    c = c + fYOffset;

  return c;
}

double Painter::GetXOffsetDelta(int x, double f)
{
  return dXtodE(x - fXBase) * (1.0 - 1.0/f);
}

double Painter::GetYOffsetDelta(int y, double f)
{ 
  if(fLogScale) {
    // This case is presently unhandled...
    return 0.0;
  } else {
    return (1.0 - 1.0/f) * (double)(fYBase - y) / fYZoom;
  }
}

double Painter::GetYAutoZoom(DisplaySpec *dSpec)
{
  double e1, e2;
  int b1, b2;
  
  e1 = XtoE(fXBase);
  e2 = XtoE(fXBase + fWidth);
  b1 = dSpec->FindBin(dSpec->E2Ch(e1));
  b2 = dSpec->FindBin(dSpec->E2Ch(e2));

  return (double) dSpec->GetMax_Cached(b1, b2) * 1.02;
}

void Painter::ClearTopXScale()
{
  // This function will clear the region containing the
  // bottom X scale so that it can be redrawn with a different
  // offset. We need to be careful not to affect the y scale,
  // since it is not necessarily redrawn as well.
  gVirtualX->FillRectangle(fDrawable, fClearGC,
						   fXBase-2, fYBase-fHeight-11,
						   fWidth+4, 9);
  gVirtualX->FillRectangle(fDrawable, fClearGC,
						   fXBase-40, fYBase-fHeight-32,
						   fWidth+60, 20);
}

void Painter::ClearBottomXScale()
{
  // This function will clear the region containing the
  // bottom X scale so that it can be redrawn with a different
  // offset. We need to be careful not to affect the y scale,
  // since it is not necessarily redrawn as well.
  gVirtualX->FillRectangle(fDrawable, fClearGC,
						   fXBase-2, fYBase+3,
						   fWidth+4, 9);
  gVirtualX->FillRectangle(fDrawable, fClearGC,
						   fXBase-40, fYBase+12,
						   fWidth+60, 20);
}

void Painter::GetTicDistance(double tic, double& major_tic, double& minor_tic, int& n)
{
  double exp;

  // limit tic distance to a sensible value
  if(tic < 0.001)
	tic = 0.001;

  // Write tic in the form tic * exp, where exp = 10^n with n \in N
  // and 1 < tic <= 10
  exp = 1.0;
  n = 0;
  while(tic <= 1.0) {
  	tic *= 10;
  	exp *= 0.1;
	n--;
  }

  while(tic > 10.0) {
  	tic *= 0.1;
  	exp *= 10;
	n++;
  }

  if(tic > 5.0) {
	major_tic = 10.0 * exp;
	minor_tic = 5.0 * exp;
	n++;
  } else if(tic > 2.0) {
	major_tic = 5.0 * exp;
	minor_tic = 1.0 * exp;
  } else { // if(tic > 1.0)
	major_tic = 2.0 * exp;
	minor_tic = 1.0 * exp;
  }
}

void Painter::DrawXNonlinearScale(UInt_t x1, UInt_t x2, bool top, const Calibration& cal)
{
  int x;
  int y = top ? fYBase - fHeight - 2 : fYBase + 2;
  int sgn = top ? -1 : 1;
  char tmp[16];
  char fmt[5] = "%.0f";
  size_t len;
  int i, i2;
  double major_tic, minor_tic;

  //GetTicDistance(cal.E2Ch(XtoE(x1)) - cal.E2Ch(XtoE(x2)), major_tic, minor_tic, n);
  minor_tic = 10.0;
  major_tic = 50.0;

  // Set the required precision
  //if(n < 0)
  //  fmt[2] = '0' - n;

  // Draw the minor tics
  i = (int) TMath::Ceil(cal.E2Ch(XtoE(x1)) / minor_tic);
  i2 = (int) TMath::Floor(cal.E2Ch(XtoE(x2)) / minor_tic);

  for(; i<=i2; ++i) {
	x = (UInt_t) EtoX(cal.Ch2E((double) i * minor_tic));
	gVirtualX->DrawLine(fDrawable, fAxisGC, x, y, x, y+5*sgn);
  }

  // Draw the major tics
  i = (int) TMath::Ceil(cal.E2Ch(XtoE(x1)) / major_tic);
  i2 = (int) TMath::Floor(cal.E2Ch(XtoE(x2)) / major_tic);

  for(; i<=i2; ++i) {
	x = (UInt_t) EtoX(cal.Ch2E((double) i * major_tic));
	gVirtualX->DrawLine(fDrawable, fAxisGC, x, y, x, y+9*sgn);
  
	// TODO: handle len > 16
	len = snprintf(tmp, 16, fmt, (double) major_tic * i);
	if(top)
      DrawString(fAxisGC, x, y-12, tmp, len, kCenter, kBottom);
    else
      DrawString(fAxisGC, x, y+12, tmp, len, kCenter, kTop);
  }
  
}

void Painter::DrawXScale(UInt_t x1, UInt_t x2)
{
  UInt_t x;
  UInt_t y = fYBase + 2;
  char tmp[16];
  char fmt[5] = "%.0f";
  size_t len;
  int i, i2;
  double major_tic, minor_tic;
  int n;

  GetTicDistance((double) 50.0 / fXZoom, major_tic, minor_tic, n);

  // Set the required precision
  if(n < 0)
	fmt[2] = '0' - n;

  // Draw the minor tics
  i = (int) TMath::Ceil(XtoE(x1) / minor_tic);
  i2 = (int) TMath::Floor(XtoE(x2) / minor_tic);

  for(; i<=i2; ++i) {
	x = (UInt_t) EtoX((double) i * minor_tic);
	gVirtualX->DrawLine(fDrawable, fAxisGC, x, y, x, y+5);
  }

  // Draw the major tics
  i = (int) TMath::Ceil(XtoE(x1) / major_tic);
  i2 = (int) TMath::Floor(XtoE(x2) / major_tic);

  for(; i<=i2; ++i) {
	x = (UInt_t) EtoX((double) i * major_tic);
	gVirtualX->DrawLine(fDrawable, fAxisGC, x, y, x, y+9);
  
	// TODO: handle len > 16
	len = snprintf(tmp, 16, fmt, (double) major_tic * i);
	DrawString(fAxisGC, x, y+12, tmp, len, kCenter, kTop);
  }
  
}

void Painter::DrawYScale()
{
  if(fLogScale)
	DrawYLogScale();
  else
	DrawYLinearScale();
}

void Painter::DrawString(GContext_t gc, int x, int y, char *str, size_t len,
							   HTextAlign hAlign, VTextAlign vAlign)
{
  int max_ascent, max_descent;
  int width;

  gVirtualX->GetFontProperties(fFontStruct, max_ascent, max_descent);
  width = gVirtualX->TextWidth(fFontStruct, str, len);

  switch(hAlign) {
  case kLeft: break;
  case kCenter: x -= width/2; break;
  case kRight: x -= width; break;
  }

  switch(vAlign) {
  case kBottom: y -= max_descent; break;
  case kBaseline: break;
  case kMiddle:  y += (max_ascent - max_descent) / 2; break;
  case kTop: y += max_ascent;
  }

  gVirtualX->DrawString(fDrawable, gc, x, y, str, len);
}

void Painter::DrawYLinearScale()
{
  UInt_t x = fXBase - 2;
  UInt_t y;
  char tmp[16];
  size_t len;
  int i, i2;
  double major_tic, minor_tic;
  int n;

  GetTicDistance((double) 50.0 / fYZoom, major_tic, minor_tic, n);

  // Draw the minor tics
  i = (int) TMath::Ceil(YtoC(fYBase) / minor_tic);
  i2 = (int) TMath::Floor(YtoC(fYBase - fHeight) / minor_tic);

  for(; i<=i2; ++i) {
	y = (UInt_t) CtoY((double) i * minor_tic);
	gVirtualX->DrawLine(fDrawable, fAxisGC, x-5, y, x, y);
  }

  // Draw the major tics
  i = (int) TMath::Ceil(YtoC(fYBase) / major_tic);
  i2 = (int) TMath::Floor(YtoC(fYBase - fHeight) / major_tic);

  for(; i<=i2; ++i) {
	y = (UInt_t) CtoY((double) i * major_tic);
	gVirtualX->DrawLine(fDrawable, fAxisGC, x-9, y, x, y);
  
	// TODO: handle len > 16
	len = snprintf(tmp, 16, "%.4g", (double) major_tic * i);
	DrawString(fAxisGC, x-12, y, tmp, len, kRight, kMiddle);
  }
  
}

void Painter::DrawYLogScale()
{
  int yTop = fYBase - fHeight; 
  int minDist;
  double cMin, cMax;

  cMin = YtoC(fYBase);
  cMax = YtoC(yTop);
 
  // Calculate the distance (in pixels) between the closest tics
  // (either 9 and 10 or the upmost tics drawn)
  if(cMax > 10.0)
	minDist = CtoY(9.0) - CtoY(10.0);
  else
	minDist = CtoY(TMath::Floor(YtoC(yTop)) - 1.0) - CtoY(TMath::Floor(YtoC(yTop)));

  if(cMax > 0.0)
    _DrawYLogScale(minDist, +1, cMin, cMax);
  
  if(cMax >= 0.0 && cMin <= 0.0)
    DrawYMajorTic(0.0);
    
  if(cMin < 0.0)
    _DrawYLogScale(minDist, -1, -cMax, -cMin);
}
  
void Painter::_DrawYLogScale(int minDist, int sgn, double cMin, double cMax)
{
  double exp = 1.0;
  int c = 1;
  
  // Find out where to begin
  while((10.0 * exp) < cMin) {
    exp *= 10.0;
  }
  while((double)c * exp < cMin) {
    c += 1;
  }

  // Scale: 0, 1, 2, 3, ..., 9, 10, 20, ... without minor tics
  if(minDist >= 20) {
	while((double)c*exp <= cMax) {
	  DrawYMajorTic((double)sgn * c * exp);

	  if(++c > 9) {
		exp *= 10.0;
		c = 1;
	  }
	}

	return;
  }

  // Scale: 0, 1, 3, 10, 30, ... with minor tics at 2, 4, 5, ..., 9, 20, ...
  minDist = CtoY(1.0) - CtoY(3.0);
  
  if(minDist >= 30) {
	while((double)c*exp <= cMax) {
	  if(c == 1 || c == 3) 
		DrawYMajorTic((double)sgn * c * exp);
	  else
		DrawYMinorTic((double)sgn * c * exp);

	  if(++c > 9) {
		exp *= 10.0;
		c = 1;
	  }
	}

	// Label the last minor tic drawn, if appropriate
	if(c == 1)
	  DrawYMajorTic((double)sgn * 0.9 * exp, false);
	else if(c > 5)
	  DrawYMajorTic((double)sgn * (c-1) * exp, false);

	return;
  }

  // Scale: 0, 1, 10, 100, ... with minor tics at 3, 30, ...
  if(minDist >= 5) {
	while((double)c*exp <= cMax) {
	  if(c == 1) {
		DrawYMajorTic((double)sgn * c * exp);
		c = 3;
	  } else {
		DrawYMinorTic((double)sgn * c * exp);
		c = 1;
		exp *= 10.0;
	  }
	}

	return;
  }

  // Scale: 0, 1, 10, 100 without minor tics
  while(exp <= cMax) {
	DrawYMajorTic((double)sgn * exp);
	exp *= 10.0;
  }
}

void Painter::DrawYMajorTic(double c, bool drawLine)
{
  UInt_t x = fXBase - 2;
  UInt_t y = (UInt_t) CtoY(c);
  char tmp[16];
  size_t len;
  
  if(drawLine)
	gVirtualX->DrawLine(fDrawable, fAxisGC, x-9, y, x, y);
  
  // TODO: handle len > 16
  len = snprintf(tmp, 16, "%.4g", c);
  DrawString(fAxisGC, x-12, y, tmp, len, kRight, kMiddle);
}

inline void Painter::DrawYMinorTic(double c)
{
  UInt_t x = fXBase - 2;
  UInt_t y = (UInt_t) CtoY(c);
  gVirtualX->DrawLine(fDrawable, fAxisGC, x-5, y, x, y);
}

} // end namespace Display
} // end namespace HDTV
