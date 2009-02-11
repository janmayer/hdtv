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

#ifndef __DisplaySpec_h__
#define __DisplaySpec_h__

#include <TH1.h>
#include <memory>
#include "DisplayBlock.h"

namespace HDTV {
namespace Display {

class DisplaySpec : public DisplayBlock {
 public:
   DisplaySpec(const TH1 *hist, int col = DEFAULT_COLOR);
  
   void SetHist(const TH1* hist);
   inline TH1* GetHist()  { return fHist.get(); }

   int GetRegionMaxBin(int b1, int b2);
   double GetRegionMax(int b1, int b2);

   inline double GetMinCh(void) { return 0.0; }
   inline double GetMaxCh(void) { return (double) fHist->GetNbinsX(); }
   inline double GetBinContent(Int_t bin) { return fHist->GetBinContent(bin); }
   inline Int_t GetNbinsX(void) { return fHist->GetNbinsX(); }
   double GetMax_Cached(int b1, int b2);
   
   // HDTV::Display:: required for CINT
   virtual std::list<HDTV::Display::DisplayObj *>& GetList(DisplayStack *stack);
   
   virtual void PaintRegion(UInt_t x1, UInt_t x2, Painter& painter)
      { if (IsVisible()) painter.DrawSpectrum(this, x1, x2); }

 private:
   std::auto_ptr<TH1> fHist;
   
   int fCachedB1, fCachedB2, fCachedMaxBin;
   double fCachedMax;
};

} // end namespace Display
} // end namespace HDTV

#endif