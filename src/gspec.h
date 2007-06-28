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

#ifndef __gspec_h__
#define __gspec_h__

#include <TQObject.h>
#include <RQ_OBJECT.h>
#include <TApplication.h>
#include <TGClient.h>
#include <TCanvas.h>
#include <TGButton.h>
#include <TGFrame.h>
#include <TGScrollBar.h>
#include <TH1.h>

#include "GSTextSpectrumReader.h"
#include "GSViewer.h"
#include "GSSpectrum.h"

class GSMainFrame {
  RQ_OBJECT("GSMainFrame")
 private:
  TGMainFrame         *fMain;
  GSViewer            *fViewer;
  GSSpectrum *fSpec;

 public:
  GSMainFrame(const TGWindow *p,UInt_t w,UInt_t h);
  virtual ~GSMainFrame();
};

#endif
