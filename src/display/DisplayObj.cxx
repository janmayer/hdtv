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

#include "DisplayObj.h"
#include "DisplayStack.h"
#include "View1D.h"

#include <TMath.h>
#include <TGFrame.h>
#include <TColor.h>
#include <TROOT.h>

#include <Riostream.h>

#include "DisplayStack.h"
#include "View1D.h"

namespace HDTV {
namespace Display {

const int DisplayObj::DEFAULT_COLOR = 3;

DisplayObj::DisplayObj(int col)
  : fCal(),
    fVisible(true)
{
  // Constructor
  
  InitGC(col);
}

inline void DisplayObj::InitGC(int col)
{
  // Setup GC for requested color
  TColor *color = dynamic_cast<TColor*>(gROOT->GetListOfColors()->At(col));
  GCValues_t gval;
  gval.fMask = kGCForeground;
  gval.fForeground = color->GetPixel();
  fGC = gClient->GetGCPool()->GetGC(&gval, true);
}

void DisplayObj::SetColor(int col)
{
  // Free old GC
  gClient->GetGCPool()->FreeGC(fGC);
  
  // Setup GC for color
  InitGC(col);
  
  Update();
}

DisplayObj::~DisplayObj()
{
  // Destructor

  Remove();  // Remove object from all display stacks
  gClient->GetGCPool()->FreeGC(fGC);
}

DisplayStack::ObjList& DisplayObj::GetList(DisplayStack *stack)
{
  // Return the stacks object list where this kind of object should be inserted

  return stack->fMisc;
}

void DisplayObj::Update()
{
  // Update all display stacks that the object is presently on

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

void DisplayObj::ToTop(View1D *view)
{
  // Move the object to the top of its list in view s display stack

  ToTop(view->GetDisplayStack());
}

void DisplayObj::ToBottom(View1D *view)
{
  // Move the object to the bottom of its list in view s display stack
  
  ToBottom(view->GetDisplayStack());
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

void DisplayObj::ToTop(DisplayStack *stack)
{
  // Move the object to the top of its list in the display stack

  DisplayStack::ObjList& list = GetList(stack);
  if(*list.rbegin() == this)
    return;
  
  list.remove(this);
  list.insert(list.end(), this);
  
  stack->Update();
}

void DisplayObj::ToTop()
{
  // Move the object to the top of its list in all display stacks it appears in

  for(std::list<DisplayStack*>::iterator stack = fStacks.begin();
      stack != fStacks.end();
      ++stack) {
    ToTop(*stack);
  }
}

void DisplayObj::ToBottom(DisplayStack *stack)
{
  // Move the object to the bottom of its list in the display stack

  DisplayStack::ObjList& list = GetList(stack);
  if(*list.begin() == this)
    return;
  
  list.remove(this);
  list.insert(list.begin(), this);
  
  stack->Update();
}

void DisplayObj::ToBottom()
{
  // Move the object to the bottom of its list in all display stacks it appears in

  for(std::list<DisplayStack*>::iterator stack = fStacks.begin();
      stack != fStacks.end();
      ++stack) {
    ToBottom(*stack);    
  }
}

double DisplayObj::GetMinE()
{
  // Return the spectrums lower endpoint in energy units

  return TMath::Min(Ch2E((double) GetMinCh()),
					Ch2E((double) GetMaxCh()));
}

double DisplayObj::GetMaxE()
{
  // Return the spectrums upper endpoint in energy units

  return TMath::Max(Ch2E((double) GetMinCh()),
					Ch2E((double) GetMaxCh()));
}

double DisplayObj::GetERange()
{
  // Returns the width of the spectrum in energy units

  return TMath::Abs(Ch2E((double) GetMinCh())
					- Ch2E((double) GetMaxCh()));
}

} // end namespace Display
} // end namespace HDTV
