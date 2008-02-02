/*
 * gSpec - a viewer for gamma spectra
 *  Copyright (C) 2006-2008  Norbert Braun <n.braun@ikp.uni-koeln.de>
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

#ifndef __GSXMarker_h__
#define __GSXMarker_h__

#include "GSMarker.h"
#include "GSCalibration.h"

class GSXMarker : public GSMarker {
  public:
    GSXMarker(int n, double p1, double p2=0.0, int col=5);
    inline TGGC *GetGC_C() { return (fDash1 && fDash2) ? fDashedGC : fGC; }
    inline double GetE1() { return fCal1 ? fCal1->Ch2E(fP1) : fP1; }
    inline double GetE2() { return fCal2 ? fCal2->Ch2E(fP2) : fP2; }
    inline void SetCal(GSCalibration *cal1)
      { fCal1 = cal1; fCal2 = cal1; }
    inline void SetCal(GSCalibration *cal1, GSCalibration *cal2)
      { fCal1 = cal1; fCal2 = cal2; }
      
  private:
    GSCalibration *fCal1, *fCal2;
};

#endif
