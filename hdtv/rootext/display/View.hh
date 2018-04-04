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

#ifndef __View_h__
#define __View_h__

#include <TGFrame.h>
#include <TGX11.h>

namespace HDTV {
namespace Display {

//! Code shared between View1D and View2D
/** Presently, this implements mostly the XOR cursor. */
class View : public TGFrame {
public:
  View(const TGWindow *p, UInt_t w, UInt_t h);

protected:
  void DrawCursor();

protected:
  TGGC *fCursorGC;
  UInt_t fCursorX, fCursorY;
  Bool_t fCursorVisible;
  Bool_t fDragging;

  ClassDefOverride(View, 1) // NOLINT
};

} // end namespace Display
} // end namespace HDTV

#endif
