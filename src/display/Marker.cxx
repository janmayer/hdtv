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

#include "Marker.h"
#include "DisplayStack.h"
#include "View1D.h"

#include <TROOT.h>

#include <Riostream.h>

namespace HDTV {
namespace Display {

Marker::Marker(int n, double p1, double p2, int col)
   : DisplayObj()
{
  fN = n;

  if(n <= 1 || p1 <= p2) {
	fP1 = p1;
	fP2 = p2;
  } else {
	fP1 = p2;
	fP2 = p1;
  }
  
  fDash1 = fDash2 = false;

  TColor *color = dynamic_cast<TColor*>(gROOT->GetListOfColors()->At(col));
  GCValues_t gval;
  gval.fMask = kGCForeground | kGCLineStyle;
  gval.fForeground = color->GetPixel();
  gval.fLineStyle = kLineSolid;
  fGC = gClient->GetGCPool()->GetGC(&gval, true);
  
  gval.fForeground = color->GetPixel();
  gval.fLineStyle = kLineOnOffDash;
  fDashedGC = gClient->GetGCPool()->GetGC(&gval, true);
}

Marker::~Marker(void)
{
  gClient->GetGCPool()->FreeGC(fGC);
  gClient->GetGCPool()->FreeGC(fDashedGC);
}

DisplayStack::ObjList& Marker::GetList(DisplayStack *stack)
{
  // Return the stacks object list where this kind of object should be inserted

  return stack->fMarkers;
}

} // end namespace Display
} // end namespace HDTV
