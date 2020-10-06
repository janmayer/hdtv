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

#include "DisplaySpec.hh"

#include <utility>

#include <TH1.h>
#include <TROOT.h>

#include "DisplayStack.hh"

namespace HDTV {
namespace Display {

//! Constructor
DisplaySpec::DisplaySpec(const TH1 *hist, int col)
    : DisplayBlock(col), fCachedMaxBin{0}, fCachedMax{0.0}, fDrawUnderflowBin(false), fDrawOverflowBin(false) {

  fHist.reset(dynamic_cast<TH1 *>(hist->Clone()));

  // cout << "GSDisplaySpec constructor" << endl;

  /* Set invalid values to ensure cache is flushed at the
         first call to GetMax_Cached() */
  fCachedB1 = 1;
  fCachedB2 = 0;
}

void DisplaySpec::SetHist(const TH1 *hist) {
  //! Set the histogram owned by this object to a copy of hist

  fHist.reset(dynamic_cast<TH1 *>(hist->Clone()));
  Update();
}

int DisplaySpec::GetRegionMaxBin(int b1, int b2) {
  //! Find the bin number of the bin between b1 and b2 (inclusive) which
  //! contains the most events
  //! b1 and b2 are raw bin numbers
  //! The region is clipped according to fDrawUnderflowBin and fDrawOverflowBin

  int bin, max_bin;
  double y, max_y;

  b1 = ClipBin(b1);
  b2 = ClipBin(b2);

  max_y = fHist->GetBinContent(b1);
  max_bin = b1;

  for (bin = b1; bin <= b2; bin++) {
    y = fHist->GetBinContent(bin);
    if (y > max_y) {
      max_y = y;
      max_bin = bin;
    }
  }

  return max_bin;
}

double DisplaySpec::GetRegionMax(int b1, int b2) {
  //! Get the maximum counts in the region between bin b1 and bin b2 (inclusive)
  //! b1 and b2 are raw bin numbers

  int max_bin = GetRegionMaxBin(b1, b2);

  // return max_bin == -1 ? 0.0 : fHist->GetBinContent(max_bin);
  return fHist->GetBinContent(max_bin);
}

double DisplaySpec::GetMax_Cached(int b1, int b2) {
  //! Gets the maximum count between bin b1 and bin b2, inclusive.
  //! Employes caching to save time during scrolling operations.
  //!
  //! NOTE: For the caching to be effective, use this function ONLY for
  //! scrolling operations.

  int bin = 0;
  int newBin = 0;
  double max, newMax = -1.0;

  b1 = std::max(b1, 0);
  b2 = std::min(b2, GetNbinsX() + 1);

  if (b2 < b1) {
    std::swap(b1, b2);
  }

  if (fCachedB2 < b1 || fCachedB1 > b2 || fCachedB1 > fCachedB2) {
    fCachedB1 = b1;
    fCachedB2 = b2;
    fCachedMaxBin = GetRegionMaxBin(b1, b2);
    fCachedMax = GetBinContent(fCachedMaxBin);
  } else {
    if (b1 < fCachedB1) {
      newBin = GetRegionMaxBin(b1, fCachedB1);
      newMax = GetBinContent(newBin);

      fCachedB1 = b1;
    }

    if (b2 > fCachedB2) {
      bin = GetRegionMaxBin(fCachedB2, b2);
      max = GetBinContent(bin);

      if (max > newMax) {
        newMax = max;
        newBin = bin;
      }

      fCachedB2 = b2;
    }

    if (newMax >= fCachedMax) {
      fCachedMaxBin = newBin;
      fCachedMax = newMax;
    } else if (fCachedMaxBin < b1 || fCachedMaxBin > b2) {
      bin = GetRegionMaxBin(b1 > fCachedB1 ? b1 : fCachedB1, b2 < fCachedB2 ? b2 : fCachedB2);

      max = GetBinContent(bin);

      if (max > newMax) {
        fCachedMax = max;
        fCachedMaxBin = bin;
      } else {
        fCachedMax = newMax;
        fCachedMaxBin = newBin;
      }

      fCachedB1 = b1;
      fCachedB2 = b2;
    }
  }

  return fCachedMax;
}

} // end namespace Display
} // end namespace HDTV
