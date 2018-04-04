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

#ifndef __DisplayBlock_h__
#define __DisplayBlock_h__

#include "Calibration.hh"
#include "DisplayObj.hh"

class TGGC;

namespace HDTV {
namespace Display {

//! DisplayBlock: common baseclass for DisplayFunc and DisplaySpec
// FIXME: think of a better name?
class DisplayBlock : public DisplayObj {
  friend class Painter;

public:
  explicit DisplayBlock(int col);
  ~DisplayBlock() override;

  void SetCal(const Calibration &cal) {
    fCal = cal;
    Update();
  };

  double Ch2E(double ch) { return fCal ? fCal.Ch2E(ch) : ch; }
  double E2Ch(double e) { return fCal ? fCal.E2Ch(e) : e; }

  double GetMaxE();
  double GetMinE();
  double GetERange();

  virtual double GetMinCh() { return 0.0; }
  virtual double GetMaxCh() { return 0.0; }

  double GetCenterCh() { return (GetMinCh() + GetMaxCh()) / 2.0; }

  void SetColor(int col);

  void SetNorm(double norm) {
    fNorm = norm;
    Update();
  }

  double GetNorm() { return fNorm; }

protected:
  const TGGC *GetGC() const { return fGC; }

private:
  void InitGC(int col);

  Calibration fCal;
  TGGC *fGC;
  double fNorm; // normalization factor
};

} // end namespace Display
} // end namespace HDTV

#endif
