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

#include <Riostream.h>

#include "DisplayStack.hh"
#include "View1D.hh"

namespace HDTV {
namespace Display {

const int DisplayObj::DEFAULT_COLOR = 3;

DisplayObj::~DisplayObj() {
  //! Destructor

  Remove(); // Remove object from all display stacks
}

void DisplayObj::Update(bool force) {
  //! Update all display stacks that the object is presently on

  if (!IsVisible() && !force)
    return;

  for (std::list<DisplayStack *>::iterator stack = fStacks.begin();
       stack != fStacks.end(); stack++) {
    (*stack)->Update();
  }
}

void DisplayObj::Draw(View1D *view) {
  //! Add the object to view s display stack

  if (!view) {
    std::cout << "Error: Draw to NULL view: no action taken." << std::endl;
    return;
  }

  Draw(view->GetDisplayStack());
}

void DisplayObj::Remove(View1D *view) {
  //! Remove the object from view s display stack

  Remove(view->GetDisplayStack());
}

void DisplayObj::Draw(DisplayStack *stack) {
  //! Add the object to the display stack

  DisplayStack::ObjList &list = stack->fObjects;

  DisplayStack::ObjList::iterator pos = list.begin();
  while (pos != list.end() && (*pos)->GetZIndex() <= GetZIndex()) {
    ++pos;
  }
  list.insert(pos, this);

  fStacks.insert(fStacks.begin(), stack);

  stack->Update();
}

void DisplayObj::Remove(DisplayStack *stack) {
  //! Remove the object from the display stack

  stack->fObjects.remove(this);
  stack->Update();
  fStacks.remove(stack);
}

void DisplayObj::Remove() {
  //! Remove the object from all display stacks it appears in

  // Note that we cannot use an iterator to traverse a changing list
  while (!fStacks.empty()) {
    Remove(*fStacks.begin());
  }
}

void DisplayObj::ToTop(View1D *view) {
  //! Move the object to the top of its list in view s display stack

  ToTop(view->GetDisplayStack());
}

void DisplayObj::ToBottom(View1D *view) {
  //! Move the object to the bottom of its list in view s display stack

  ToBottom(view->GetDisplayStack());
}

void DisplayObj::ToTop(DisplayStack *stack) {
  //! Move the object to the top of all objects with lower or equal z-index in
  //! the display stack.

  DisplayStack::ObjList &list = stack->fObjects;

  DisplayStack::ObjList::iterator pos = list.begin();
  while (pos != list.end() && (*pos)->GetZIndex() <= GetZIndex()) {
    ++pos;
  }

  if (pos != list.end() && *pos == this)
    return;

  list.remove(this);
  list.insert(pos, this);

  stack->Update();
}

void DisplayObj::ToTop() {
  //! Move the object to the top of all objects with lower or equal z-index in
  //! all display stacks it appears in.

  for (std::list<DisplayStack *>::iterator stack = fStacks.begin();
       stack != fStacks.end(); ++stack) {
    ToTop(*stack);
  }
}

void DisplayObj::ToBottom(DisplayStack *stack) {
  //! Move the object to the bottom of all objects with higher or equal z-index
  //! in the display stack.

  DisplayStack::ObjList &list = stack->fObjects;

  DisplayStack::ObjList::iterator pos = list.begin();
  while (pos != list.end() && (*pos)->GetZIndex() < GetZIndex()) {
    ++pos;
  }

  if (pos != list.end() && *pos == this)
    return;

  list.remove(this);
  list.insert(list.begin(), this);

  stack->Update();
}

void DisplayObj::ToBottom() {
  //! Move the object to the bottom of all objects with higher or equal z-index
  //! in all display stacks it appears in.

  for (std::list<DisplayStack *>::iterator stack = fStacks.begin();
       stack != fStacks.end(); ++stack) {
    ToBottom(*stack);
  }
}

} // end namespace Display
} // end namespace HDTV
