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

#include "DisplayStack.h"
#include "View1D.h"

#include <iostream>

namespace HDTV {
namespace Display {

DisplayStack::~DisplayStack()
{
  // Destructor
  // Removes all display objects from the stack, and turns all markers
  // into zombies.

  for(ObjList::iterator obj = fSpectra.begin();
      obj != fSpectra.end();
      ++obj) {
    (*obj)->Remove(this);
  }
  
  for(ObjList::iterator obj = fFunctions.begin();
      obj != fFunctions.end();
      ++obj) {
    (*obj)->Remove(this);
  }
  
  for(ObjList::iterator obj = fMisc.begin();
      obj != fMisc.end();
      ++obj) {
    (*obj)->Remove(this);
  }
  
  for(MarkerList::iterator marker = fMarkers.begin();
      marker != fMarkers.end();
      ++marker) {
    (*marker)->MakeZombie();
  }
}

void DisplayStack::Update()
{
  // Call Update() of corresponding view
  
  fView->Update();
}

void DisplayStack::LockUpdate()
{
  // Call LockUpdate() of corresponding view

  fView->LockUpdate();
}

void DisplayStack::UnlockUpdate()
{
  // Call UnlockUpdate() of corresponding view

  fView->UnlockUpdate();
}

inline void DisplayStack::PaintList(ObjList& objects, UInt_t x1, UInt_t x2, Painter& painter)
{
  // Paints all objects in the list given (internal use only)
  
  for(ObjList::iterator obj = objects.begin();
      obj != objects.end();
      ++obj) {
    (*obj)->PaintRegion(x1, x2, painter);
  }
}

void DisplayStack::PaintRegion(UInt_t x1, UInt_t x2, Painter& painter)
{
  // Paints all objects in the stack
  
  PaintList(fSpectra, x1, x2, painter);
  PaintList(fFunctions, x1, x2, painter);
  PaintList(fMisc, x1, x2, painter);
  
  for(MarkerList::iterator marker = fMarkers.begin();
      marker != fMarkers.end();
      ++marker) {
    (*marker)->PaintRegion(x1, x2, painter);
  }
}

} // end namespace Display
} // end namespace HDTV
