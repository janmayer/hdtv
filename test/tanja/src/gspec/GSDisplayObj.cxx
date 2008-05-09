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

#include "GSDisplayObj.h"

#include <TMath.h>
#include <TGFrame.h>
#include <TColor.h>
#include <TROOT.h>

#include <Riostream.h>

GSDisplayObj::GSDisplayObj(int col)
{
  // Set a trivial calibration
  SetCal(NULL);
  
  // Setup GC for color
  TColor *color = (TColor*) (gROOT->GetListOfColors()->At(col));
  GCValues_t gval;
  gval.fMask = kGCForeground;
  gval.fForeground = color->GetPixel();
  fGC = gClient->GetGCPool()->GetGC(&gval, true);
}

GSDisplayObj::~GSDisplayObj()
{
  gClient->GetGCPool()->FreeGC(fGC); 
  //cout << "GSDisplayObj destructor" << endl;
}

double GSDisplayObj::GetMinE()
{
  // Return the spectrums lower endpoint in energy units

  return TMath::Min(Ch2E((double) GetMinCh()),
					Ch2E((double) GetMaxCh()));
}

double GSDisplayObj::GetMaxE()
{
  // Return the spectrums upper endpoint in energy units

  return TMath::Max(Ch2E((double) GetMinCh()),
					Ch2E((double) GetMaxCh()));
}

double GSDisplayObj::GetERange()
{
  // Returns the width of the spectrum in energy units

  return TMath::Abs(Ch2E((double) GetMinCh())
					- Ch2E((double) GetMaxCh()));
}
