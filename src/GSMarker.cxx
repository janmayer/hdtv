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

#include "GSMarker.h"
#include <Riostream.h>

GSMarker::GSMarker(int n, double e1, double e2)
{
  fN = n;

  if(n <= 1 || e1 <= e2) {
	fE1 = e1;
	fE2 = e2;
  } else {
	fE1 = e2;
	fE2 = e1;
  }

  TColor *color = (TColor*) (gROOT->GetListOfColors()->At(5));
  GCValues_t gval;
  gval.fMask = kGCForeground;
  gval.fForeground = color->GetPixel();
  fGC = gClient->GetGCPool()->GetGC(&gval, true);
}

GSMarker::~GSMarker(void)
{
  gClient->GetGCPool()->FreeGC(fGC);
}
