/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2010  The HDTV development team (see file AUTHORS)
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

#include "DisplayCut.hh"

#include <cmath>

#include <TCutG.h>

namespace HDTV {
namespace Display {

namespace {

std::vector<DisplayCut::CutPoint> make_points(const double *x_begin, const double *x_end, const double *y_begin) {
  std::vector<DisplayCut::CutPoint> points;
  if (x_end > x_begin) {
    points.reserve(std::distance(x_begin, x_end));
    while (x_begin != x_end) {
      points.emplace_back(*x_begin++, *y_begin++);
    }
  }
  return points;
}

} // namespace

DisplayCut::DisplayCut(int n, const double *x, const double *y)
    : fPoints{make_points(x, x + n, y)}, fX1{0.0}, fY1{0.0}, fX2{0.0}, fY2{0.0} {
  UpdateBoundingBox();
}

DisplayCut::DisplayCut(const TCutG &cut, bool invertAxes)
    : fPoints{invertAxes ? make_points(cut.GetY(), cut.GetY() + cut.GetN(), cut.GetX())
                         : make_points(cut.GetX(), cut.GetX() + cut.GetN(), cut.GetY())},
      fX1{0.0}, fY1{0.0}, fX2{0.0}, fY2{0.0} {
  UpdateBoundingBox();
}

void DisplayCut::UpdateBoundingBox() {
  if (fPoints.empty()) {
    fX1 = 0.0;
    fX2 = 0.0;
    fY1 = 0.0;
    fY2 = 0.0;
    return;
  }

  fX1 = std::numeric_limits<double>::max();
  fX2 = std::numeric_limits<double>::min();

  fY1 = std::numeric_limits<double>::max();
  fY2 = std::numeric_limits<double>::min();

  for (auto &point : fPoints) {
    fX1 = std::min(fX1, point.x);
    fX2 = std::max(fX2, point.x);
    fY1 = std::min(fY1, point.y);
    fY2 = std::max(fY2, point.y);
  }
}

} // end namespace Display
} // end namespace HDTV
