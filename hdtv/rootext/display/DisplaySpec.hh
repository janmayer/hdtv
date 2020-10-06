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

#include <memory>
#include <sstream>

#include <TH1.h>

#include "DisplayBlock.hh"

namespace HDTV {
namespace Display {

//! Wrapper around a ROOT TH1 object being displayed
class DisplaySpec : public DisplayBlock {
public:
  explicit DisplaySpec(const TH1 *hist, int col = DEFAULT_COLOR);

  void SetHist(const TH1 *hist);

  TH1 *GetHist() { return fHist.get(); }

  int GetRegionMaxBin(int b1, int b2);
  double GetRegionMax(int b1, int b2);

  void SetID(int ID) {
    fID = std::to_string(ID);
    Update();
  }

  void SetID(const std::string *ID) {
    if (ID) {
      fID = *ID;
    } else {
      fID = "";
    }
    Update();
  }

  void SetID(const char *ID) {
    if (ID) {
      fID = ID;
    } else {
      fID = "";
    }
    Update();
  }

  std::string GetID() const { return fID; }

  // Convenience functions to access the underlying histogram object and its x
  // axis
  double GetBinContent(Int_t bin) { return fHist->GetBinContent(bin); }

  double GetBinCenter(Int_t bin) { return fHist->GetXaxis()->GetBinCenter(bin); }

  Int_t FindBin(double x) { return fHist->GetXaxis()->FindBin(x); }
  Int_t GetNbinsX() { return fHist->GetNbinsX(); }

  void SetDrawUnderflowBin(bool x) { fDrawUnderflowBin = x; }
  void SetDrawOverflowBin(bool x) { fDrawOverflowBin = x; }
  bool GetDrawUnderflowBin() { return fDrawUnderflowBin; }
  bool GetDrawOverflowBin() { return fDrawOverflowBin; }

  double GetMinCh() override { return fHist->GetXaxis()->GetXmin(); }
  double GetMaxCh() override { return fHist->GetXaxis()->GetXmax(); }

  Int_t ClipBin(Int_t bin) {
    return std::min(std::max(bin, fDrawOverflowBin ? 0 : 1), fDrawOverflowBin ? GetNbinsX() + 1 : GetNbinsX());
  }

  double GetClippedBinContent(Int_t bin) { return GetBinContent(ClipBin(bin)); }

  double GetMax_Cached(int b1, int b2);

  void PaintRegion(UInt_t x1, UInt_t x2, Painter &painter) override {
    if (IsVisible()) {
      painter.DrawSpectrum(this, x1, x2);
    }
  }

  int GetZIndex() const override { return Z_INDEX_SPEC; }

private:
  std::unique_ptr<TH1> fHist;

  int fCachedB1, fCachedB2, fCachedMaxBin;
  double fCachedMax;
  bool fDrawUnderflowBin, fDrawOverflowBin;
  std::string fID; // ID for use by higher-level structures
};

} // end namespace Display
} // end namespace HDTV

#endif
