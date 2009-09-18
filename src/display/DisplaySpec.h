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

//! Wrapper around a ROOT TH1 object being displayed
class DisplaySpec : public DisplayBlock {
 public:
   DisplaySpec(const TH1 *hist, int col = DEFAULT_COLOR);
  
   void SetHist(const TH1* hist);
   inline TH1* GetHist()  { return fHist.get(); }

   int GetRegionMaxBin(int b1, int b2);
   double GetRegionMax(int b1, int b2);
   
   inline void SetID(int ID)  { fID = ID; }
   inline int GetID() const   { return fID; }

   // Convenience functions to access the underlying histogram object and its x axis
   inline double GetBinContent(Int_t bin) { return fHist->GetBinContent(bin); }
   inline double GetBinCenter(Int_t bin) { return fHist->GetXaxis()->GetBinCenter(bin); }
   inline Int_t FindBin(double x) { return fHist->GetXaxis()->FindBin(x); }
   inline Int_t GetNbinsX(void) { return fHist->GetNbinsX(); }
   
   inline void SetDrawUnderflowBin(bool x)  { fDrawUnderflowBin = x; }
   inline void SetDrawOverflowBin(bool x)   { fDrawOverflowBin = x; }
   inline bool GetDrawUnderflowBin() { return fDrawUnderflowBin; }
   inline bool GetDrawOverflowBin()  { return fDrawOverflowBin; }
   
   inline double GetMinCh(void) { return (double) fHist->GetXaxis()->GetXmin(); }
   inline double GetMaxCh(void) { return (double) fHist->GetXaxis()->GetXmax(); }
   
   inline Int_t ClipBin(Int_t bin) {
     if(fDrawUnderflowBin) {
       if(bin < 0) bin = 0;
     } else {
       if(bin < 1) bin = 1;
     }
       
     if(fDrawOverflowBin) {
       if(bin > GetNbinsX()+1) bin = GetNbinsX()+1;
     } else {
       if(bin > GetNbinsX()) bin = GetNbinsX();
     }
     
     return bin;
   }
   
   inline double GetClippedBinContent(Int_t bin) {
     return GetBinContent(ClipBin(bin));
   }
   
   double GetMax_Cached(int b1, int b2);
   
   virtual void PaintRegion(UInt_t x1, UInt_t x2, Painter& painter)
      { if (IsVisible()) painter.DrawSpectrum(this, x1, x2); }
      
   virtual int GetZIndex() { return Z_INDEX_SPEC; }

 private:
   std::auto_ptr<TH1> fHist;
   
   int fCachedB1, fCachedB2, fCachedMaxBin;
   double fCachedMax;
   bool fDrawUnderflowBin, fDrawOverflowBin;
   int fID;  // ID for use by higher-level structures
};

} // end namespace Display
} // end namespace HDTV

#endif
