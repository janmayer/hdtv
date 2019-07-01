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

#ifndef __DisplayFunc_h__
#define __DisplayFunc_h__

#include <TF1.h>

#include "DisplayBlock.hh"
#include "Painter.hh"

namespace HDTV {
namespace Display {

//! Wrapper around a ROOT TF1 object being displayed
class DisplayFunc : public DisplayBlock {
public:
  explicit DisplayFunc(TF1 *func, int col = DEFAULT_COLOR);

  TF1 *GetFunc() { return fFunc; }
  double Eval(double x) { return fFunc->Eval(x); }

  double GetMinCh() override {
    double min, max;
    fFunc->GetRange(min, max);
    return min;
  }

  double GetMaxCh() override {
    double min, max;
    fFunc->GetRange(min, max);
    return max;
  }

  void PaintRegion(UInt_t x1, UInt_t x2, Painter &painter) override {
    if (IsVisible()) {
      painter.DrawFunction(this, x1, x2);
    }
  }

  int GetZIndex() const override { return Z_INDEX_FUNC; }

private:
  TF1 *fFunc;
};

} // end namespace Display
} // end namespace HDTV

#endif
