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
  fOffset is an x shift, in pixels (to make mouse scrolling easy)

  fXZoom is in pixels per energy
  fYZoom is in pixels per count
*/

#ifndef __GSSpecPainter_h__
#define __GSSpecPainter_h__

#include <TGFrame.h>
#include "GSDisplaySpec.h"
#include "GSSpectrum.h"

enum EViewMode {
  kVMSolid = 1,
  kVMHollow = 2,
  kVMDotted = 3
};

class GSSpecPainter { 
 public:
  GSSpecPainter(void);
  ~GSSpecPainter(void);
  inline void SetSpectrum(GSSpectrum *spec) { fSpec = spec; }
  inline void SetXZoom(double xzoom) { fXZoom = xzoom; }
  inline double GetXZoom(void) { return fXZoom; }
  inline void SetYZoom(double yzoom) { fYZoom = yzoom; }
  inline double GetYZoom(void) { return fYZoom; }
  inline void SetLogScale(Bool_t l) { fLogScale = l; }
  inline Bool_t GetLogScale(void) { return fLogScale; }
  inline void SetViewMode(EViewMode vm) { fViewMode = vm; }
  inline EViewMode GetViewMode(void) { return fViewMode; }
  inline void SetBasePoint(int x, int y) { fXBase = x; fYBase = y; }
  inline UInt_t GetBaseX(void) { return fXBase; }
  inline void SetSize(int w, int h) { fWidth = w; fHeight = h; }
  inline UInt_t GetWidth(void) { return fWidth; }
  inline void SetDrawable(Drawable_t drawable) { fDrawable = drawable; }
  inline void SetAxisGC(GContext_t gc) { fAxisGC = gc; }
  inline void SetClearGC(GContext_t gc) { fClearGC = gc; }
  inline void SetOffset(double offset) { fOffset = offset; }
  inline double GetOffset(void) { return fOffset; }
  inline UInt_t GetAvailSize(void) { return fWidth; }
  inline UInt_t GetRequiredSize(double xzoom)
	{ return fSpec ? (UInt_t) TMath::Ceil(fSpec->GetEnergyRange() * xzoom) : 0; }

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

  void DrawSpectrum(GSDisplaySpec *dSpec, UInt_t x1, UInt_t x2);
  double GetYAutoZoom(void);
  void DrawXScale(UInt_t x1, UInt_t x2);
  void ClearXScale(void);
  void DrawYScale(void);

 protected:
  void DrawYLinearScale(void);
  void DrawYLogScale(void);
  void DrawYMajorTic(double c, bool drawLine=true);
  inline void DrawYMinorTic(double c);
  int GetCountsAtPixel(UInt_t x);

  inline int GetYAtPixel(UInt_t x)
	{ return CtoY(GetCountsAtPixel(x)); }

  int CtoY(double c);
  double YtoC(int y);
  void GetTicDistance(double tic, double& major_tic, double& minor_tic, int& n);

 protected:
  double fXZoom, fYZoom;  // px / keV, px / count
  double fOffset;
  Bool_t fLogScale;
  UInt_t fXBase, fYBase;
  UInt_t fWidth, fHeight;
  GSSpectrum *fSpec;
  EViewMode fViewMode;
  Drawable_t fDrawable;
  GContext_t fAxisGC;
  GContext_t fClearGC;

  //  ClassDef(ViewerFrame,0)
};

#endif
