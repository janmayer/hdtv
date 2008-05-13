/*
 * gSpec - a viewer for gamma spectra
 *  Copyright (C) 2006  Norbert Braun <n.braun@ikp.uni-koeln.de>
 *
 * This file is part of gSpec.
 *
 * gSpec is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * gSpec is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
 * for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with gSpec; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
 * 
 */

#ifndef __GSViewer_h__
#define __GSViewer_h__

#include <TApplication.h>
#include <TGFrame.h>
#include <TGScrollBar.h>
#include <TGStatusBar.h>
#include <KeySymbols.h>
#include "GSViewport.h"

#include <iostream>

#include <RQ_OBJECT.h>

class GSViewer : public TGMainFrame {
  RQ_OBJECT("GSViewer")
 public:
  GSViewer(UInt_t w=800, UInt_t h=400, const char *title = "gSpec");
  ~GSViewer(void);
  inline const GSViewport *GetViewport(void) { return fViewport; }
  void KeyPressed() {   Emit("KeyPressed()"); }  // *SIGNAL*
  
  UInt_t fKeySym; // temporary hack
  
  ClassDef(GSViewer, 1)

 protected:
  void UpdateScrollbar(void);
  Bool_t ProcessMessage(Long_t msg, Long_t parm1, Long_t);
  Bool_t HandleKey(Event_t *ev);

 protected:
  GSViewport *fViewport;
  TGHScrollBar *fScrollbar;
  TGStatusBar *fStatusBar;
};

#endif
