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

#include "DisplayStack.hh"

#include <iostream>

#include "DisplayObj.hh"
#include "View1D.hh"

namespace HDTV {
namespace Display {

DisplayStack::~DisplayStack() {
  // Destructor
  // Removes all display objects from the stack

  // Note that we cannot use an iterator to traverse a changing list
  while (!fObjects.empty()) {
    (*fObjects.begin())->Remove(this);
  }
}

void DisplayStack::Update() {
  //! Call Update() of corresponding view

  fView->Update(true);
}

void DisplayStack::LockUpdate() {
  //! Call LockUpdate() of corresponding view

  fView->LockUpdate();
}

void DisplayStack::UnlockUpdate() {
  //! Call UnlockUpdate() of corresponding view

  fView->UnlockUpdate();
}

void DisplayStack::PaintRegion(UInt_t x1, UInt_t x2, Painter &painter) {
  //! Paints all objects in the stack

  for (auto &obj : fObjects) {
    obj->PaintRegion(x1, x2, painter);
  }
}

} // end namespace Display
} // end namespace HDTV
