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

#ifndef __DisplayStack_h__
#define __DisplayStack_h__

#include <list>

#include "Painter.hh"

namespace HDTV {
namespace Display {

class DisplayObj;
class View1D;

//! An ordered list of objects being displayed
class DisplayStack {
  friend class DisplayObj;
  friend class View1D;

public:
  using ObjList = std::list<DisplayObj *>;

  explicit DisplayStack(View1D *view) { fView = view; }
  ~DisplayStack();

  void Update();

  inline void LockUpdate();
  inline void UnlockUpdate();

  void PaintRegion(UInt_t x1, UInt_t x2, Painter &painter);

private:
  ObjList fObjects;
  View1D *fView;
};

} // end namespace Display
} // end namespace HDTV

#endif
