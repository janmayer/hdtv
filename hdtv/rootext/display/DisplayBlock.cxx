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

#include "DisplayBlock.h"
#include "DisplayObj.h"
#include "DisplayStack.h"
#include "View1D.h"

#include <TMath.h>
#include <TGFrame.h>
#include <TColor.h>
#include <TROOT.h>

namespace HDTV {
namespace Display {

DisplayBlock::DisplayBlock(int col)
  : DisplayObj(),
    fCal(),
    fNorm(1.0)
{
  //! Constructor
  
  InitGC(col);
}

DisplayBlock::~DisplayBlock()
{
  //! Destructor

  gClient->GetGCPool()->FreeGC(fGC);
}

inline void DisplayBlock::InitGC(int col)
{
  // Setup GC for requested color
  TColor *color = dynamic_cast<TColor*>(gROOT->GetListOfColors()->At(col));
  GCValues_t gval;
  gval.fMask = kGCForeground;
  gval.fForeground = color->GetPixel();
  fGC = gClient->GetGCPool()->GetGC(&gval, true);
}

void DisplayBlock::SetColor(int col)
{
  // Free old GC
  gClient->GetGCPool()->FreeGC(fGC);
  
  // Setup GC for color
  InitGC(col);
  
  Update();
}

double DisplayBlock::GetMinE()
{
  //! Return the spectrums lower endpoint in energy units

  return TMath::Min(Ch2E((double) GetMinCh()),
					Ch2E((double) GetMaxCh()));
}

double DisplayBlock::GetMaxE()
{
  //! Return the spectrums upper endpoint in energy units

  return TMath::Max(Ch2E((double) GetMinCh()),
					Ch2E((double) GetMaxCh()));
}

double DisplayBlock::GetERange()
{
  //! Returns the width of the spectrum in energy units

  return TMath::Abs(Ch2E((double) GetMinCh())
					- Ch2E((double) GetMaxCh()));
}

} // end namespace Display
} // end namespace HDTV
