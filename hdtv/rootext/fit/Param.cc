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

#include "Param.hh"

#include <iostream>
#include <limits>

#include <TF1.h>

namespace HDTV {
namespace Fit {

double Param::Value(TF1 *func) const {
  if (fFree) {
    return func ? func->GetParameter(fId) : std::numeric_limits<double>::quiet_NaN();
  } else {
    return fValue;
  }
}

double Param::Error(TF1 *func) const {
  // Fixed parameters do not have a fit error
  if (fFree) {
    return func ? func->GetParError(fId) : std::numeric_limits<double>::quiet_NaN();
  } else {
    return 0.0;
  }
}

std::ostream &operator<<(std::ostream &lhs, const Param &rhs) {
  lhs << "[Id=" << rhs._Id() << ", Free=" << rhs.IsFree() << ", IVal=" << rhs.HasIVal()
      << ", Valid=" << static_cast<bool>(rhs) << ", Value=" << rhs._Value() << ']';
  return lhs;
}

} // end namespace Fit
} // end namespace HDTV
