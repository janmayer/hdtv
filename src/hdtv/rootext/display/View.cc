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

#include "View.hh"

namespace HDTV {
namespace Display {

View::View(const TGWindow *p, UInt_t w, UInt_t h) : TGFrame(p, w, h) {
  AddInput(kPointerMotionMask | kEnterWindowMask | kLeaveWindowMask | kButtonPressMask | kButtonReleaseMask);

  GCValues_t gval;
  gval.fMask = kGCForeground | kGCFunction;
  gval.fFunction = kGXxor;
  gval.fForeground = GetWhitePixel();
  fCursorGC = gClient->GetGCPool()->GetGC(&gval, true);
  fCursorVisible = false;
  fCursorX = 0;
  fCursorY = 0;

  fDragging = false;
}

void View::DrawCursor() {
  gVirtualX->DrawLine(GetId(), fCursorGC->GetGC(), 1, fCursorY, fWidth, fCursorY);
  gVirtualX->DrawLine(GetId(), fCursorGC->GetGC(), fCursorX, 1, fCursorX, fHeight);
  fCursorVisible = !fCursorVisible;
}

} // end namespace Display
} // end namespace HDTV
