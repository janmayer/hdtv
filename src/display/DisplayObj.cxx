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

#include "DisplayObj.h"
#include "DisplayStack.h"
#include "View1D.h"

#include <Riostream.h>

namespace HDTV {
namespace Display {

const int DisplayObj::DEFAULT_COLOR = 3;

DisplayObj::~DisplayObj()
{
  // Destructor

  Remove();  // Remove object from all display stacks
}

DisplayStack::ObjList& DisplayObj::GetList(DisplayStack *stack)
{
  // Return the stacks object list where this kind of object should be inserted

  return stack->fMisc;
}

void DisplayObj::Update(bool force)
{
  // Update all display stacks that the object is presently on

  if(!IsVisible() && !force)
    return;
  
  for(std::list<DisplayStack*>::iterator stack = fStacks.begin();
      stack != fStacks.end();
      stack++)
  {
    (*stack)->Update();
  }
}

void DisplayObj::Draw(View1D *view)
{
  // Add the object to view s display stack

  if(!view) {
    cout << "Error: Draw to NULL view: no action taken." << endl;
    return;
  }

  Draw(view->GetDisplayStack());
}

void DisplayObj::Remove(View1D *view)
{
  // Remove the object from view s display stack

  Remove(view->GetDisplayStack());
}

void DisplayObj::Draw(DisplayStack *stack)
{
  // Add the object to the display stack

  DisplayStack::ObjList& list = GetList(stack);
  list.insert(list.end(), this);
  
  fStacks.insert(fStacks.begin(), stack);
  
  stack->Update();
}

void DisplayObj::Remove(DisplayStack *stack)
{
  // Remove the object from the display stack

  GetList(stack).remove(this);
  stack->Update();
}

void DisplayObj::Remove()
{
  // Remove the object from all display stacks it appears in

  for(std::list<DisplayStack*>::iterator stack = fStacks.begin();
      stack != fStacks.end();
      ++stack) {
    Remove(*stack);
  }
}

} // end namespace Display
} // end namespace HDTV
