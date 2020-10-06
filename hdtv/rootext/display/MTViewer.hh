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

#ifndef __MTViewer_h__
#define __MTViewer_h__

#include <memory>

#include <TGFrame.h>

#include "View2D.hh"

class TCutG;
class TGStatusBar;
class TH2;
class THnSparse;

namespace HDTV {
namespace Display {

//! Class implementing a window (ROOT TGMainFrame) containing a View2D widget
//! and a statusbar.
class MTViewer : public TGMainFrame {
public:
  MTViewer(UInt_t w, UInt_t h, TH2 *mat, const char *title, bool copy = false);
  MTViewer(UInt_t w, UInt_t h, THnSparse *mat, const char *title);
  ~MTViewer() override;

  void AddCut(const TCutG &cut, bool invertAxes = false) { fView->AddCut(cut, invertAxes); }

  void DeleteAllCuts() { fView->DeleteAllCuts(); }

private:
  void Init(UInt_t w, UInt_t h, TH2 *mat, const char *title);

  HDTV::Display::View2D *fView;
  TGStatusBar *fStatusBar;
  std::unique_ptr<TH2> fMatCopy;

  ClassDefOverride(MTViewer, 1) // NOLINT
};

} // end namespace Display
} // end namespace HDTV

#endif
