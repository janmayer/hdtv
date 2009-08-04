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

/*
  A note about the coordinate system:
  fXBase is the point that corresponds to energy 0 (if fOffset = 0)
  fYBase is the point that corresponds to zero counts
  fOffset is an x shift, in pixels

  fXZoom is in pixels per energy
  fYZoom is in pixels per count
*/

#ifndef __Painter_h__
#define __Painter_h__

#include <list>
#include <TGResourcePool.h>
#include <TGFont.h>
#include <TGFrame.h>
#include <TMath.h>
#include "Calibration.h"

namespace HDTV {
namespace Display {

class DisplayObj;

enum ViewMode {
  kVMSolid = 1,
  kVMHollow = 2,
  kVMDotted = 3
};

enum HTextAlign {
  kLeft = 1,
  kCenter = 2,
  kRight = 3
};

enum VTextAlign {
  kBottom = 1,
  kBaseline = 2,
  kMiddle = 3,
  kTop = 4
};

class DisplaySpec;
class DisplayFunc;
class XMarker;
class YMarker;

class Painter {
 public:
  Painter();
  inline void SetXVisibleRegion(double xv) 
	{ fXVisibleRegion = xv; fXZoom = fWidth / fXVisibleRegion; }
  inline double GetXVisibleRegion() { return fXVisibleRegion; }
  inline void SetYVisibleRegion(double yv) 
	{ fYVisibleRegion = yv; UpdateYZoom(); }
  inline double GetYVisibleRegion() { return fYVisibleRegion; }
  inline double GetXZoom() { return fXZoom; }
  inline double GetYZoom() { return fYZoom; }
  inline void SetLogScale(Bool_t l) 
	{ fLogScale = l; UpdateYZoom(); }
  inline Bool_t GetLogScale() { return fLogScale; }
  inline void SetUseNorm(Bool_t n) { fUseNorm = n; }
  inline Bool_t GetUseNorm() { return fUseNorm; }
  inline void SetViewMode(ViewMode vm) { fViewMode = vm; }
  inline ViewMode GetViewMode() { return fViewMode; }
  inline void SetBasePoint(int x, int y) { fXBase = x; fYBase = y; }
  inline Int_t GetBaseX() { return fXBase; }
  void SetSize(int w, int h);
  inline Int_t GetWidth() { return fWidth; }
  inline Int_t GetHeight() { return fHeight; }
  inline void SetDrawable(Drawable_t drawable) { fDrawable = drawable; }
  inline void SetAxisGC(GContext_t gc) { fAxisGC = gc; }
  inline void SetClearGC(GContext_t gc) { fClearGC = gc; }
  inline void SetXOffset(double offset) { fXOffset = offset; }
  inline void SetYOffset(double offset) { fYOffset = offset; UpdateYZoom(); }
  inline double GetXOffset() { return fXOffset; }
  inline double GetYOffset() { return fYOffset; }
  
  double GetXOffsetDelta(int x, double f);
  double GetYOffsetDelta(int y, double f);
  
  double ModLog(double x);
  double InvModLog(double x);

  inline double XtoE(Int_t x)
	{ return (double) (x - fXBase) / fXZoom + fXOffset; }
  inline int EtoX(double e) 
	{ return (int) TMath::Ceil(((e - fXOffset) * fXZoom) + fXBase - 0.5); }
  inline double XtoE(double x)
	{ return (x - (double) fXBase) / fXZoom + fXOffset; }
  inline double dXtodE(int dX)
	{ return ((double) dX / fXZoom); }
  inline double dEtodX(double dE)
	{ return dE * fXZoom; }
  inline double dYtodC(int dY)
    { return -((double) dY / fYZoom); }   // FIXME: only works for linear Y scale
  int CtoY(double c);
  double YtoC(int y);
  
  inline Bool_t IsWithin(Int_t x, Int_t y) {
    return (x >= fXBase && x <= fXBase + fWidth && y >= fYBase - fHeight && y <= fYBase);
  }

  void DrawSpectrum(DisplaySpec *dSpec, int x1, int x2);
  void DrawFunction(DisplayFunc *dFunc, int x1, int x2);
  void DrawXMarker(XMarker *marker, int x1, int x2);
  void DrawYMarker(YMarker *marker, int x1, int x2);
  double GetYAutoZoom(DisplaySpec *dSpec);
  void DrawXScale(Int_t x1, Int_t x2);
  void DrawXNonlinearScale(Int_t x1, Int_t x2, bool top, const Calibration& cal);
  void ClearTopXScale();
  void ClearBottomXScale();
  void DrawYScale();
  void DrawIDList(std::list<DisplayObj *> objects);
  
  //ClassDef(Painter, 1)

 protected:
  void DrawYLinearScale();
  void DrawYLogScale();
  void _DrawYLogScale(int minDist, int sgn, double cMin, double cMax);
  void DrawYMajorTic(double c, bool drawLine=true);
  void DrawString(GContext_t gc, int x, int y, const char *str, size_t len,
				  HTextAlign hAlign, VTextAlign vAlign);
  inline void DrawYMinorTic(double c);
  double GetCountsAtPixel(DisplaySpec *dSpec, Int_t x);
  int GetYAtPixel(DisplaySpec *dSpec, Int_t x);

  void GetTicDistance(double tic, double& major_tic, double& minor_tic, int& n);
  void UpdateYZoom();

 protected:
  double fXZoom, fYZoom;  // px / keV, px / count
  double fXVisibleRegion, fYVisibleRegion;
  double fXOffset, fYOffset;
  Bool_t fLogScale;
  Bool_t fUseNorm;
  Int_t fXBase, fYBase;
  Int_t fWidth, fHeight;
  ViewMode fViewMode;
  Drawable_t fDrawable;
  GContext_t fAxisGC;
  GContext_t fClearGC;
  const TGFont *fFont;
  FontStruct_t fFontStruct;
};

} // end namespace Display
} // end namespace HDTV

#endif
