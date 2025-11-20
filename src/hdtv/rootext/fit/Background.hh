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

#ifndef __Background_h__
#define __Background_h__

#include <limits>

class TF1;

namespace HDTV {
namespace Fit {

//! Base class for background fitters
class Background {
public:
  Background() = default;
  virtual ~Background() = default;
  virtual Background *Clone() const { return new Background(); }
  virtual TF1 *GetFunc() { return nullptr; }
  virtual double GetCoeff(int i) const { return 0.; }
  virtual double GetMin() const { return std::numeric_limits<double>::quiet_NaN(); }
  virtual double GetMax() const { return std::numeric_limits<double>::quiet_NaN(); }
  virtual unsigned int GetNparams() const { return 0; };
  virtual double Eval(double /*x*/) const { return std::numeric_limits<double>::quiet_NaN(); }
  virtual double EvalError(double /*x*/) const { return std::numeric_limits<double>::quiet_NaN(); }

private:
  Background(const Background & /*b*/) = default;
};

} // end namespace Fit
} // end namespace HDTV

#endif
