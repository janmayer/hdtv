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
#include "DisplayObj.h"
#include "Marker.h"
#include "Painter.h"

namespace HDTV {
namespace Display {

class View1D;

class DisplayStack {
  public:
    DisplayStack(View1D *view) { fView = view; }
    ~DisplayStack();
    void Update();
    inline void LockUpdate();
    inline void UnlockUpdate();
    void PaintRegion(UInt_t x1, UInt_t x2, Painter& painter);
    
    typedef std::list<DisplayObj *> ObjList;
    
    ObjList fSpectra;
    ObjList fFunctions;
    ObjList fMarkers;
    ObjList fMisc;   // junk drawer
    
    View1D* fView;
    
  private:
    void RemoveList(ObjList& objects);
    void PaintList(ObjList& objects, UInt_t x1, UInt_t x2, Painter& painter);
};

} // end namespace Display
} // end namespace HDTV

#endif
