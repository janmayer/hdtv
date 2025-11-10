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

/* The position of a marker is considered to be in energy units if
   no calibration is given, and in channel units otherwise. */

#ifndef __Marker_h__
#define __Marker_h__

#include <string>

#include "DisplayObj.hh"

class TGGC;

namespace HDTV {
namespace Display {

//! A marker (displayed as a horizontal or vertical line)
class Marker : public DisplayObj {
  friend class Painter;
  friend class DisplayStack;

public:
  Marker(int n, double p1, double p2 = 0.0, int col = 5);
  ~Marker() override;

  TGGC *GetGC_1() { return fDash1 ? fDashedGC : fGC; }
  TGGC *GetGC_2() { return fDash2 ? fDashedGC : fGC; }
  int GetN() { return fN; }
  double GetP1() { return fP1; }
  double GetP2() { return fP2; }

  void SetN(int n) {
    fN = n;
    Update();
  }

  void SetPos(double p1, double p2 = 0.0) {
    fP1 = p1;
    fP2 = p2;
    Update();
  }

  void SetDash(bool dash1, bool dash2 = false) {
    fDash1 = dash1;
    fDash2 = dash2;
    Update();
  }

  void SetColor(int col);

  void SetID(int ID) {
    fID = std::to_string(ID);
    Update();
  }

  void SetID(const std::string *ID) {
    if (ID) {
      fID = *ID;
    } else {
      fID = "";
    }
    Update();
  }

  void SetID(const char *ID) {
    if (ID) {
      fID = ID;
    } else {
      fID = "";
    }
    Update();
  }

  std::string GetID() const { return fID; }
  int GetZIndex() const override { return Z_INDEX_MARKER; }

protected:
  void InitGC(int col);
  void FreeGC();
  std::string fID;

  bool fDash1, fDash2;
  TGGC *fGC, *fDashedGC;
  double fP1, fP2;
  int fN;
};

} // end namespace Display
} // end namespace HDTV

#endif
