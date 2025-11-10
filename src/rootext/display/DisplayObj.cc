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

#include "DisplayObj.hh"

#include <algorithm>
#include <iostream>

#include "DisplayStack.hh"
#include "View1D.hh"

namespace HDTV {
namespace Display {

const int DisplayObj::DEFAULT_COLOR = 3;

//! Destructor
DisplayObj::~DisplayObj() {
  // Remove object from all display stacks
  Remove();
}

//! Update all display stacks that the object is presently on
void DisplayObj::Update(bool force) {
  if (!IsVisible() && !force) {
    return;
  }

  for (auto &stack : fStacks) {
    stack->Update();
  }
}

//! Add the object to view s display stack
void DisplayObj::Draw(View1D *view) {
  if (!view) {
    std::cout << "Error: Draw to NULL view: no action taken." << std::endl;
    return;
  }

  Draw(view->GetDisplayStack());
}

//! Remove the object from view s display stack
void DisplayObj::Remove(View1D *view) { Remove(view->GetDisplayStack()); }

//! Add the object to the display stack
void DisplayObj::Draw(DisplayStack *stack) {
  auto &objects = stack->fObjects;
  auto zindex = GetZIndex();
  auto pos = std::find_if(objects.begin(), objects.end(),
                          [&zindex](const DisplayObj *obj) { return obj->GetZIndex() > zindex; });
  objects.insert(pos, this);
  fStacks.insert(fStacks.begin(), stack);
  stack->Update();
}

//! Remove the object from the display stack
void DisplayObj::Remove(DisplayStack *stack) {
  stack->fObjects.remove(this);
  stack->Update();
  fStacks.remove(stack);
}

//! Remove the object from all display stacks it appears in
void DisplayObj::Remove() {
  // Note that we cannot use an iterator to traverse a changing list
  while (!fStacks.empty()) {
    Remove(*fStacks.begin());
  }
}

//! Move the object to the top of its list in view s display stack
void DisplayObj::ToTop(View1D *view) { ToTop(view->GetDisplayStack()); }

//! Move the object to the bottom of its list in view s display stack
void DisplayObj::ToBottom(View1D *view) { ToBottom(view->GetDisplayStack()); }

//! Move the object to the top of all objects with lower or equal z-index in the
//! display stack.
void DisplayObj::ToTop(DisplayStack *stack) {
  auto &objects = stack->fObjects;
  auto zindex = GetZIndex();
  auto pos = std::find_if(objects.begin(), objects.end(),
                          [&zindex](const DisplayObj *obj) { return obj->GetZIndex() > zindex; });
  if (pos != objects.end() && *pos == this) {
    return;
  }

  objects.remove(this);
  objects.insert(pos, this);
  stack->Update();
}

//! Move the object to the top of all objects with lower or equal z-index in all
//! display stacks it appears in.
void DisplayObj::ToTop() {
  for (auto &stack : fStacks) {
    ToTop(stack);
  }
}

//! Move the object to the bottom of all objects with higher or equal z-index in
//! the display stack.
void DisplayObj::ToBottom(DisplayStack *stack) {

  auto &objects = stack->fObjects;
  auto zindex = GetZIndex();
  auto pos = std::find_if(objects.begin(), objects.end(),
                          [&zindex](const DisplayObj *obj) { return !(obj->GetZIndex() < zindex); });
  if (pos != objects.end() && *pos == this) {
    return;
  }

  objects.remove(this);
  objects.insert(objects.begin(), this);

  stack->Update();
}

//! Move the object to the bottom of all objects with higher or equal z-index in
//! all display stacks it appears in.
void DisplayObj::ToBottom() {
  for (auto &stack : fStacks) {
    ToBottom(stack);
  }
}

} // end namespace Display
} // end namespace HDTV
