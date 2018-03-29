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

#ifndef __DisplayCut_h__
#define __DisplayCut_h__

#include <vector>

class TCutG;

namespace HDTV {
namespace Display {

class DisplayCut {
  public:
    class CutPoint {
      public:
        CutPoint(double _x, double _y)  { x = _x; y = _y; }
        double x, y;
    };

    DisplayCut() {}
    DisplayCut(int n, const double* x, const double* y)
        { Init(n, x, y); }
    DisplayCut(const TCutG& cut, bool invertAxes=false);

    const std::vector<CutPoint>& GetPoints() const
        { return fPoints; }
    inline double BB_x1() const { return fX1; }
    inline double BB_y1() const { return fY1; }
    inline double BB_x2() const { return fX2; }
    inline double BB_y2() const { return fY2; }

  private:
    void Init(int n, const double* x, const double* y);
    std::vector<CutPoint> fPoints;
    double fX1, fY1, fX2, fY2;   // bounding box
};

} // end namespace Display
} // end namespace HDTV

#endif
