/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2020  The HDTV development team (see file AUTHORS)
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

#ifndef __Option_h__
#define __Option_h__

namespace HDTV {
namespace Fit {

//! Description of a fit option
template <typename T> class Option {
public:
  Option() = default;
  Option(T val) : val_(val) {}

  T GetValue() const { return val_; }
  void SetValue(T val) { val_ = val; }

private:
  T val_;
};

// std::ostream &operator <<(std::ostream &lhs, const Option &rhs);

} // end namespace Fit
} // end namespace HDTV

#endif
