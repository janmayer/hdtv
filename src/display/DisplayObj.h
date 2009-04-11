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

#ifndef __DisplayObj_h__
#define __DisplayObj_h__

#include <list>
#include "Painter.h"

namespace HDTV {
namespace Display {

class DisplayStack;
class View1D;

class DisplayObj {
  public:
    DisplayObj() : fVisible(true) { }
    virtual ~DisplayObj();
  	
    inline bool IsVisible() { return fVisible; }
    inline void Show() { fVisible = true; Update(true); }
    inline void Hide() { fVisible = false; Update(true); }
    
    /* Management functions */
    void Draw(View1D *view);
    void Remove(View1D *view);
    
    void Draw(DisplayStack *stack);
    void Remove(DisplayStack *stack);

    void Remove();
    
    virtual void PaintRegion(UInt_t x1, UInt_t x2, Painter& painter) { }
    
    // HDTV::Display:: required for CINT
    virtual std::list<HDTV::Display::DisplayObj *>& GetList(DisplayStack *stack);
    
    static const int DEFAULT_COLOR;
    
  protected:
    void Update(bool force=false);
    std::list<DisplayStack*> fStacks;
  	
  private:
    bool fVisible;
};

} // end namespace Display
} // end namespace HDTV

#endif
