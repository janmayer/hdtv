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

#ifndef __Param_h__
#define __Param_h__

#include <iosfwd>

class TF1;

namespace HDTV {
namespace Fit {

//! Description of a fit parameter
class Param {
public:
  Param() = default;

  static Param Fixed(double val) { return Param(-1, val, false, true, true); }
  static Param Fixed() { return Param(-1, 0.0, false, false, true); }
  static Param Free(int id) { return Param(id, 0.0, true, false, true); }
  static Param Free(int id, double ival) { return Param(id, ival, true, true, true); }
  static Param Empty() { return Param(-1, 0.0, false, false, false); }

  bool IsFree() const { return fFree; }
  bool HasIVal() const { return fHasIVal; }
  explicit operator bool() const { return fValid; }
  double Value(const double *p) const { return fFree ? p[fId] : fValue; }
  void SetValue(double val) { fValue = val; }

  double Value(TF1 *func) const;
  double Error(TF1 *func) const;
  int _Id() const { return fId; }
  double _Value() const { return fValue; }

private:
  Param(int id, double value, bool free, bool hasIVal, bool valid) noexcept
      : fFree{free}, fHasIVal{hasIVal}, fValid{valid}, fId{id}, fValue{value} {}

  bool fFree, fHasIVal, fValid;
  int fId;
  double fValue;
};

std::ostream &operator<<(std::ostream &lhs, const Param &rhs);

} // end namespace Fit
} // end namespace HDTV

#endif
