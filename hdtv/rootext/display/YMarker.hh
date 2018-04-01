/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2009  Norbert Braun <n.braun@ikp.uni-koeln.de>
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

#ifndef __YMarker_h__
#define __YMarker_h__

#include "Marker.hh"

namespace HDTV {
namespace Display {

class View1D;

//! A horizontal marker (marking a point on the Y axis)
class YMarker : public Marker {
public:
  YMarker(int n, double p1, double p2 = 0.0, int col = 5);
  void PaintRegion(UInt_t x1, UInt_t x2, Painter &painter) override {
    if (IsVisible()) {
      painter.DrawYMarker(this, x1, x2);
    }
  }
};

} // end namespace Display
} // end namespace HDTV

#endif
