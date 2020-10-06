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

#include "Marker.hh"

#include <TColor.h>
#include <TROOT.h>

#include "DisplayStack.hh"
#include "View1D.hh"

namespace HDTV {
namespace Display {

Marker::Marker(int n, double p1, double p2, int col)
    : DisplayObj{}, fDash1{false}, fDash2{false}, fGC{nullptr}, fDashedGC{nullptr}, fP1{p1}, fP2{p2}, fN{n} {
  if (n > 1 && p1 > p2) {
    std::swap(fP1, fP2);
  }
  InitGC(col);
}

Marker::~Marker() { FreeGC(); }

void Marker::InitGC(int col) {
  auto color = dynamic_cast<TColor *>(gROOT->GetListOfColors()->At(col));
  GCValues_t gval;
  gval.fMask = kGCForeground | kGCLineStyle;
  gval.fForeground = color->GetPixel();
  gval.fLineStyle = kLineSolid;
  fGC = gClient->GetGCPool()->GetGC(&gval, true);

  gval.fForeground = color->GetPixel();
  gval.fLineStyle = kLineOnOffDash;
  fDashedGC = gClient->GetGCPool()->GetGC(&gval, true);
}

void Marker::FreeGC() {
  gClient->GetGCPool()->FreeGC(fGC);
  gClient->GetGCPool()->FreeGC(fDashedGC);
}

void Marker::SetColor(int col) {
  //! Set color for this marker

  FreeGC();
  InitGC(col);
  Update();
}

} // end namespace Display
} // end namespace HDTV
