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

#include "DisplayBlock.hh"

#include <cmath>

#include <TColor.h>
#include <TGFrame.h>
#include <TROOT.h>

#include "DisplayObj.hh"
#include "DisplayStack.hh"
#include "View1D.hh"

namespace HDTV {
namespace Display {

//! Constructor
DisplayBlock::DisplayBlock(int col) : DisplayObj(), fGC{nullptr}, fNorm{1.0} { InitGC(col); }

//! Destructor
DisplayBlock::~DisplayBlock() { gClient->GetGCPool()->FreeGC(fGC); }

inline void DisplayBlock::InitGC(int col) {
  // Setup GC for requested color
  auto color = dynamic_cast<TColor *>(gROOT->GetListOfColors()->At(col));
  GCValues_t gval;
  gval.fMask = kGCForeground;
  gval.fForeground = color->GetPixel();
  fGC = gClient->GetGCPool()->GetGC(&gval, true);
}

void DisplayBlock::SetColor(int col) {
  // Free old GC
  gClient->GetGCPool()->FreeGC(fGC);

  // Setup GC for color
  InitGC(col);

  Update();
}

//! Return the spectrums lower endpoint in energy units
double DisplayBlock::GetMinE() { return std::min(Ch2E(GetMinCh()), Ch2E(GetMaxCh())); }

//! Return the spectrums upper endpoint in energy units
double DisplayBlock::GetMaxE() { return std::max(Ch2E(GetMinCh()), Ch2E(GetMaxCh())); }

//! Returns the width of the spectrum in energy units
double DisplayBlock::GetERange() { return std::abs(Ch2E(GetMinCh()) - Ch2E(GetMaxCh())); }

} // end namespace Display
} // end namespace HDTV
