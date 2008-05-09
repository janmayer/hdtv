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
 
/* The position of a marker is considered to be in energy units if
   no calibration is given, and in channel units otherwise. */

#ifndef __GSMarker_h__
#define __GSMarker_h__

#include <TGFrame.h>
#include <TColor.h>

#include "GSCalibration.h"

class GSMarker {
 public:
  GSMarker(int n, double p1, double p2=0.0, int col=5);
  ~GSMarker();

  inline TGGC *GetGC_1() { return fDash1 ? fDashedGC : fGC; }
  inline TGGC *GetGC_2() { return fDash2 ? fDashedGC : fGC; }
  inline int GetN() { return fN; }
  inline double GetP1() { return fP1; }
  inline double GetP2() { return fP2; }
  
  inline void SetN(int n)
    { fN = n; }
  inline void SetPos(double p1, double p2=0.0)
    { fP1 = p1; fP2 = p2; }
  inline void SetDash(bool dash1, bool dash2=false)
    { fDash1 = dash1; fDash2 = dash2; }
 
 protected:
  bool fDash1, fDash2;
  TGGC *fGC, *fDashedGC;
  double fP1, fP2;
  int fN;
};

#endif
