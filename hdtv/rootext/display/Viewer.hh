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

#ifndef __Viewer_h__
#define __Viewer_h__

#include <TGFrame.h>

// see below...
// #include <RQ_OBJECT.h>

class TGHScrollBar;
class TGStatusBar;

namespace HDTV {
namespace Display {

class View1D;

//! Class implementing a window (ROOT TGMainFrame) containing a View1D widget
//! and a statusbar
class Viewer : public TGMainFrame {
  // FIXME: uncommenting the following line causes the inherited CloseWindow()
  //  signal to stop working. The reason is not presently understood, however,
  //  the line does not seem to be needed.
  // RQ_OBJECT("HDTV::Display::Viewer")
public:
  explicit Viewer(UInt_t w = 800, UInt_t h = 400, const char *title = "hdtv");
  ~Viewer() override;

  // FIXME: should be called GetView
  const View1D *GetViewport() { return fView; }

  void KeyPressed() { Emit("KeyPressed()"); } // *SIGNAL*

  UInt_t fKeySym;   // Key symbol
  char fKeyStr[16]; // Key string
  UInt_t fKeyState; // Key mask

protected:
  void UpdateScrollbar();
  Bool_t ProcessMessage(Long_t msg, Long_t parm1, Long_t) override;
  Bool_t HandleKey(Event_t *ev) override;

protected:
  View1D *fView;
  TGHScrollBar *fScrollbar;
  TGStatusBar *fStatusBar;

  ClassDefOverride(Viewer, 1) // NOLINT
};

} // end namespace Display
} // end namespace HDTV

#endif
