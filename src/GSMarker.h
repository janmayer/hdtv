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

#ifndef __GSMarker_h__
#define __GSMarker_h__

#include <TGFrame.h>
#include <TColor.h>
#include "GSSpectrum.h"

class GSMarker {
 public:
  GSMarker(int n, double e1, double e2=0.0);
  ~GSMarker(void);

  inline TGGC *GetGC(void) { return fGC; }
  inline int GetN(void) { return fN; }
  inline double GetE1(void) { return fE1; }
  inline double GetE2(void) { return fE2; }

 private:
  TGGC *fGC;
  double fE1, fE2;
  int fN;
};

#endif
