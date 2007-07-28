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

/*
  A note about the coordinate system:
  fXBase is the point that corresponds to energy 0 (if fOffset = 0)
  fYBase is the point that corresponds to zero counts
  fOffset is an x shift, in pixels

  fXZoom is in pixels per energy
  fYZoom is in pixels per count
*/

#ifndef __GSSpecPainter_h__
#define __GSSpecPainter_h__

#include <TGResourcePool.h>
#include <TGFont.h>
#include <TGFrame.h>
#include "GSDisplaySpec.h"
#include "GSMarker.h"
#include "GSSpectrum.h"

enum EViewMode {
  kVMSolid = 1,
  kVMHollow = 2,
  kVMDotted = 3
};

enum EHTextAlign {
  kLeft = 1,
  kCenter = 2,
  kRight = 3
};

enum EVTextAlign {
  kBottom = 1,
  kBaseline = 2,
  kMiddle = 3,
  kTop = 4
};

class GSSpecPainter { 
 public:
  GSSpecPainter(void);
  ~GSSpecPainter(void);
  inline void SetXVisibleRegion(double xv) 
	{ fXVisibleRegion = xv; fXZoom = fWidth / fXVisibleRegion; }
  inline double GetXVisibleRegion(void) { return fXVisibleRegion; }
  inline void SetYVisibleRegion(double yv) 
	{ fYVisibleRegion = yv; UpdateYZoom(); }
  inline double GetYVisibleRegion(void) { return fYVisibleRegion; }
  inline double GetXZoom(void) { return fXZoom; }
  inline double GetYZoom(void) { return fYZoom; }
  inline void SetLogScale(Bool_t l) 
	{ fLogScale = l; UpdateYZoom(); }
  inline Bool_t GetLogScale(void) { return fLogScale; }
  inline void SetViewMode(EViewMode vm) { fViewMode = vm; }
  inline EViewMode GetViewMode(void) { return fViewMode; }
  inline void SetBasePoint(int x, int y) { fXBase = x; fYBase = y; }
  inline UInt_t GetBaseX(void) { return fXBase; }
  void SetSize(int w, int h);
  inline UInt_t GetWidth(void) { return fWidth; }
  inline UInt_t GetHeight(void) { return fHeight; }
  inline void SetDrawable(Drawable_t drawable) { fDrawable = drawable; }
  inline void SetAxisGC(GContext_t gc) { fAxisGC = gc; }
  inline void SetClearGC(GContext_t gc) { fClearGC = gc; }
  inline void SetOffset(double offset) { fOffset = offset; }
  inline double GetOffset(void) { return fOffset; }

  inline double XtoE(UInt_t x)
	{ return (double) (x - fXBase) / fXZoom + fOffset; }
  inline int EtoX(double e) 
	{ return (int) TMath::Ceil(((e - fOffset) * fXZoom) + fXBase - 0.5); }
  inline double XtoE(double x)
	{ return (x - (double) fXBase) / fXZoom + fOffset; }
  inline double dXtodE(int dX)
	{ return ((double) dX / fXZoom); }
  inline double dEtodX(double dE)
	{ return dE * fXZoom; }

  void DrawSpectrum(GSDisplaySpec *dSpec, int x1, int x2);
  void DrawMarker(GSMarker *marker, int x1, int x2);
  double GetYAutoZoom(GSDisplaySpec *dSpec);
  void DrawXScale(UInt_t x1, UInt_t x2);
  void ClearXScale(void);
  void DrawYScale(void);

 protected:
  void DrawYLinearScale(void);
  void DrawYLogScale(void);
  void DrawYMajorTic(double c, bool drawLine=true);
  void DrawString(GContext_t gc, int x, int y, char *str, size_t len,
				  EHTextAlign hAlign, EVTextAlign vAlign);
  inline void DrawYMinorTic(double c);
  int GetCountsAtPixel(GSDisplaySpec *dSpec, UInt_t x);

  inline int GetYAtPixel(GSDisplaySpec *dSpec, UInt_t x)
	{ return CtoY(GetCountsAtPixel(dSpec, x)); }

  int CtoY(double c);
  double YtoC(int y);
  void GetTicDistance(double tic, double& major_tic, double& minor_tic, int& n);
  void UpdateYZoom(void);

 protected:
  double fXZoom, fYZoom;  // px / keV, px / count
  double fXVisibleRegion, fYVisibleRegion;
  double fOffset;
  Bool_t fLogScale;
  UInt_t fXBase, fYBase;
  UInt_t fWidth, fHeight;
  EViewMode fViewMode;
  Drawable_t fDrawable;
  GContext_t fAxisGC;
  GContext_t fClearGC;
  const TGFont *fFont;
  FontStruct_t fFontStruct;

  //  ClassDef(ViewerFrame,0)
};

#endif
