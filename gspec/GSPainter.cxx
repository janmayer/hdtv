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

#include "GSPainter.h"
#include <Riostream.h>

GSPainter::GSPainter()
{
  SetXVisibleRegion(100.0);
  SetYVisibleRegion(100.0);
  SetLogScale(false);
  SetBasePoint(0, 0);
  SetSize(0, 0);
  SetViewMode(kVMHollow);
  SetOffset(0.0);

  fFont = gClient->GetResourcePool()->GetDefaultFont();
  fFontStruct = fFont->GetFontStruct();
}

GSPainter::~GSPainter()
{
}

void GSPainter::DrawFunction(GSDisplayFunc *dFunc, int x1, int x2)
{
  int x;
  int y;
  int hClip = fYBase - fHeight;
  int lClip = fYBase;

  /* Do x axis clipping */
  int minX = EtoX(dFunc->GetMinE());
  int maxX = EtoX(dFunc->GetMaxE());

  if(x1 < minX) x1 = minX;
  if(x2 > maxX)	x2 = maxX;

  int ly, cy;
  ly = CtoY(dFunc->Eval(XtoE((double) x1 - 0.5)));

  for(x=x1; x<=x2; x++) {
    y = cy = CtoY(dFunc->Eval(XtoE((double) x + 0.5)));
    
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

void GSPainter::DrawSpectrum(GSDisplaySpec *dSpec, int x1, int x2)
{
  int x;
  int y;
  int clip = fYBase - fHeight;

  /* Do x axis clipping */
  int minX = EtoX(dSpec->GetMinE());
  int maxX = EtoX(dSpec->GetMaxE());

  if(x1 < minX) x1 = minX;
  if(x2 > maxX)	x2 = maxX;

  switch(fViewMode) {
  case kVMSolid:
	for(x=x1; x<=x2; x++) {
	  y = GetYAtPixel(dSpec, x);
	  if(y < clip) y = clip;
	  gVirtualX->DrawLine(fDrawable, dSpec->GetGC()->GetGC(),
						  x, fYBase, x, y);
	}
	break;
	
  case kVMDotted:
	for(x=x1; x<=x2; x++) {
	  y = GetYAtPixel(dSpec, x);
	  if(y >= clip)
		gVirtualX->DrawRectangle(fDrawable, dSpec->GetGC()->GetGC(),
								 x, y, 0, 0);
	}
	break;
	
  case kVMHollow:
	int ly, cy;
	ly = GetYAtPixel(dSpec, x1-1);

	for(x=x1; x<=x2; x++) {
	  y = GetYAtPixel(dSpec, x);
	  
	  if(y < ly) {
		if(ly >= clip) {
		  cy = y;
		  if(cy < clip) cy = clip;
		  gVirtualX->DrawLine(fDrawable, dSpec->GetGC()->GetGC(),
							  x, ly, x, cy);
		}
	  } else {
		if(y >= clip) {
		  cy = ly;
		  if(cy < clip) cy = clip;
		  if(x > fXBase)
			gVirtualX->DrawLine(fDrawable, dSpec->GetGC()->GetGC(),
								x-1, cy, x-1, y);
		  gVirtualX->DrawRectangle(fDrawable, dSpec->GetGC()->GetGC(),
								   x, y, 0, 0);
		}
	  }
	  
	  ly = y;
	}
	break;
  }
}

void GSPainter::DrawMarker(GSMarker *marker, int x1, int x2)
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

void GSPainter::UpdateYZoom(void)
{
  double yRange = fYVisibleRegion;

  if(fLogScale)
  	yRange = TMath::Log(yRange) + 1.0;

  fYZoom = fHeight / yRange;
}

void GSPainter::SetSize(int w, int h)
{
  fWidth = w;
  fHeight = h;
  fXZoom = fWidth / fXVisibleRegion;
  UpdateYZoom();
}

int GSPainter::GetCountsAtPixel(GSDisplaySpec *dSpec, UInt_t x)
{
  double c1, c2;
  int n1, n2;
  
  c1 = dSpec->E2Ch(XtoE((double) x - 0.5));
  c2 = dSpec->E2Ch(XtoE((double) x + 0.5));

  if(c1 < c2) {
	n1 = (int) TMath::Ceil(c1 + 0.5);
	n2 = (int) TMath::Ceil(c2 - 0.5);
  } else {
	n1 = (int) TMath::Ceil(c2 + 0.5);
	n2 = (int) TMath::Ceil(c1 - 0.5);
  }

  if(n2 < n1)
	n2 = n1;

  return dSpec->GetRegionMax(n1, n2);
}

int GSPainter::CtoY(double c)
{
  if(fLogScale) {
	if(c > 0.5)
	  c = TMath::Log(c) + 1.0;
	else
	  c = 0.0;
  }

  return fYBase - (int) TMath::Ceil(c * fYZoom - 0.5);
}

double GSPainter::YtoC(int y)
{
  double c;
  c = (double) (fYBase - y) / fYZoom;

  if(fLogScale) {
	c = TMath::Exp(c - 1.0);
	if(c < 0.5)
	  c = 0.0;
  }

  return c;
}

double GSPainter::GetYAutoZoom(GSDisplaySpec *dSpec)
{
  double e1, e2;
  int b1, b2;
  
  e1 = XtoE(fXBase);
  e2 = XtoE(fXBase + fWidth);
  b1 = (int) TMath::Floor(dSpec->E2Ch(e1) + 1.5);
  b2 = (int) TMath::Ceil(dSpec->E2Ch(e2) + 0.5);

  return (double) dSpec->GetMax_Cached(b1, b2) * 1.02;
}

void GSPainter::ClearXScale(void)
{
  // This function will clear the region containing the
  // X scale so that it can be redrawn with a different
  // offset. We need to be careful not to affect the y scale,
  // since it is not necessarily redrawn as well.
  gVirtualX->FillRectangle(fDrawable, fClearGC,
						   fXBase-2, fYBase+3,
						   fWidth+4, 9);
  gVirtualX->FillRectangle(fDrawable, fClearGC,
						   fXBase-40, fYBase+12,
						   fWidth+60, 20);
}

void GSPainter::GetTicDistance(double tic, double& major_tic, double& minor_tic, int& n)
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

void GSPainter::DrawXScale(UInt_t x1, UInt_t x2)
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

  for(i; i<=i2; i++) {
	x = (UInt_t) EtoX((double) i * minor_tic);
	gVirtualX->DrawLine(fDrawable, fAxisGC, x, y, x, y+5);
  }

  // Draw the major tics
  i = (int) TMath::Ceil(XtoE(x1) / major_tic);
  i2 = (int) TMath::Floor(XtoE(x2) / major_tic);

  for(i; i<=i2; i++) {
	x = (UInt_t) EtoX((double) i * major_tic);
	gVirtualX->DrawLine(fDrawable, fAxisGC, x, y, x, y+9);
  
	// TODO: handle len > 16
	len = snprintf(tmp, 16, fmt, (double) major_tic * i);
	DrawString(fAxisGC, x, y+12, tmp, len, kCenter, kTop);
  }
  
}

void GSPainter::DrawYScale(void)
{
  if(fLogScale)
	DrawYLogScale();
  else
	DrawYLinearScale();
}

void GSPainter::DrawString(GContext_t gc, int x, int y, char *str, size_t len,
							   EHTextAlign hAlign, EVTextAlign vAlign)
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

void GSPainter::DrawYLinearScale(void)
{
  UInt_t x = fXBase - 2;
  UInt_t y;
  char tmp[16];
  char fmt[5] = "%.0f";
  size_t len;
  int i, i2;
  double major_tic, minor_tic;
  int n;

  GetTicDistance((double) 50.0 / fYZoom, major_tic, minor_tic, n);

  // Set the required precision
  if(n < 0)
	fmt[2] = '0' - n;

  // Draw the minor tics
  i2 = (int) TMath::Floor(YtoC(fYBase - fHeight) / minor_tic);

  for(i=0; i<=i2; i++) {
	y = (UInt_t) CtoY((double) i * minor_tic);
	gVirtualX->DrawLine(fDrawable, fAxisGC, x-5, y, x, y);
  }

  // Draw the major tics
  i2 = (int) TMath::Floor(YtoC(fYBase - fHeight) / major_tic);

  for(i=0; i<=i2; i++) {
	y = (UInt_t) CtoY((double) i * major_tic);
	gVirtualX->DrawLine(fDrawable, fAxisGC, x-9, y, x, y);
  
	// TODO: handle len > 16
	len = snprintf(tmp, 16, fmt, (double) major_tic * i);
	DrawString(fAxisGC, x-12, y, tmp, len, kRight, kMiddle);
  }
  
}

void GSPainter::DrawYLogScale(void)
{
  double exp = 1.0;
  int c = 1;

  UInt_t x = fXBase - 2;
  UInt_t y;
  int yTop = fYBase - fHeight;
  int minDist;

  // The tic at 0.0 needs special treatment...
  DrawYMajorTic(0.0);
 
  // Scale: 0, 1, 2, 3, ..., 9, 10, 20, ... without minor tics
  // Check if the two closest labels drawn are more than 20 pixels
  // apart.
  if(YtoC(yTop) > 10.0)
	minDist = CtoY(9.0) - CtoY(10.0);
  else
	minDist = CtoY(TMath::Floor(YtoC(yTop)) - 1.0) - CtoY(TMath::Floor(YtoC(yTop)));

  if(minDist >= 20) {
	while(CtoY(c) > yTop) {
	  DrawYMajorTic((double)c * exp);

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
	while(CtoY((double)c * exp) > yTop) {
	  if(c == 1 || c == 3) 
		DrawYMajorTic((double)c * exp);
	  else
		DrawYMinorTic((double)c * exp);

	  if(++c > 9) {
		exp *= 10.0;
		c = 1;
	  }
	}

	// Label the last minor tic drawn, if appropriate
	if(c == 1)
	  DrawYMajorTic(0.9 * exp, false);
	else if(c > 5)
	  DrawYMajorTic((c-1) * exp, false);

	return;
  }

  // Scale: 0, 1, 10, 100, ... with minor tics at 3, 30, ...
  if(minDist >= 5) {
	while(CtoY((double)c * exp) > yTop) {
	  if(c == 1) {
		DrawYMajorTic((double)c * exp);
		c = 3;
	  } else {
		DrawYMinorTic((double)c * exp);
		c = 1;
		exp *= 10.0;
	  }
	}

	return;
  }

  // Scale: 0, 1, 10, 100 without minor tics
  while(CtoY(exp) > yTop) {
	DrawYMajorTic(exp);
	exp *= 10.0;
  }
}

void GSPainter::DrawYMajorTic(double c, bool drawLine)
{
  UInt_t x = fXBase - 2;
  UInt_t y = (UInt_t) CtoY(c);
  char tmp[16];
  size_t len;
  
  if(drawLine)
	gVirtualX->DrawLine(fDrawable, fAxisGC, x-9, y, x, y);
  
  // TODO: handle len > 16
  len = snprintf(tmp, 16, "%.0f", c);
  DrawString(fAxisGC, x-12, y, tmp, len, kRight, kMiddle);
}

inline void GSPainter::DrawYMinorTic(double c)
{
  UInt_t x = fXBase - 2;
  UInt_t y = (UInt_t) CtoY(c);
  gVirtualX->DrawLine(fDrawable, fAxisGC, x-5, y, x, y);
}
