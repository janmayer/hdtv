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

#include "VMatrix.hh"

#include <cmath>

#include <TArrayD.h>

void VMatrix::AddRegion(std::list<int> &reglist, int l1, int l2) {
  std::list<int>::iterator iter, next;
  bool inside = false;
  int min = std::min(l1, l2);
  int max = std::max(l1, l2);

  // Perform clipping
  if (max < GetCutLowBin() || min > GetCutHighBin()) {
    return;
  }
  min = std::max(min, GetCutLowBin());
  max = std::min(max, GetCutHighBin());

  iter = reglist.begin();
  while (iter != reglist.end() && *iter < min) {
    inside = !inside;
    iter++;
  }

  if (!inside) {
    iter = reglist.insert(iter, min);
    iter++;
  }

  while (iter != reglist.end() && *iter < max) {
    inside = !inside;
    next = iter;
    next++;
    reglist.erase(iter);
    iter = next;
  }

  if (!inside) {
    reglist.insert(iter, max);
  }
}

class ReadException {};

TH1 *VMatrix::Cut(const char *histname, const char *histtitle) {
  int l, l1, l2; // lines
  std::list<int>::iterator iter;
  int nCut = 0, nBg = 0; // total number of cut and background lines
  int pbins = GetProjXbins();

  if (Failed()) {
    return nullptr;
  }

  if (fCutRegions.empty()) {
    return nullptr;
  }

  // Sum of cut lines
  TArrayD sum(pbins);
  sum.Reset(0.0);

  // Sum of background lines
  TArrayD bg(pbins);
  bg.Reset(0.0);

  try {
    // Add up all cut lines
    iter = fCutRegions.begin();
    while (iter != fCutRegions.end()) {
      l1 = *iter++;
      l2 = *iter++;
      for (l = l1; l <= l2; l++) {
        AddLine(sum, l);
        nCut++;
      }
    }

    // Add up all background lines
    iter = fBgRegions.begin();
    while (iter != fBgRegions.end()) {
      l1 = *iter++;
      l2 = *iter++;
      for (l = l1; l <= l2; l++) {
        AddLine(bg, l);
        nBg++;
      }
    }
  } catch (ReadException &) {
    return nullptr;
  }

  double bgFac = (nBg == 0) ? 0.0 : static_cast<double>(nCut) / nBg;
  auto hist = new TH1D(histname, histtitle, GetProjXbins(), GetProjXmin(), GetProjXmax());
  // cols, -0.5, (double) cols - 0.5);
  for (int c = 0; c < pbins; c++) {
    hist->SetBinContent(c + 1, sum[c] - bg[c] * bgFac);
  }

  return hist;
}

RMatrix::RMatrix(TH2 *hist, ProjAxis_t paxis) : VMatrix(), fHist(hist), fProjAxis(paxis) {}

void RMatrix::AddLine(TArrayD &dst, int l) {
  if (fProjAxis == PROJ_X) {
    int cols = fHist->GetNbinsX();

    for (int c = 1; c <= cols; ++c) {
      // Bad for speed; overloaded operator[] checks array bounds
      dst[c - 1] += fHist->GetBinContent(c, l);
    }
  } else {
    int cols = fHist->GetNbinsY();

    for (int c = 1; c <= cols; ++c) {
      // Bad for speed; overloaded operator[] checks array bounds
      dst[c - 1] += fHist->GetBinContent(l, c);
    }
  }
}

MFMatrix::MFMatrix(MFileHist *mat, unsigned int level) : VMatrix(), fMatrix(mat), fLevel(level), fBuf() {
  // Sanity checks
  if (fLevel >= fMatrix->GetNLevels()) {
    fFail = true;
  } else {
    fBuf.Set(fMatrix->GetNColumns());
  }
}

void MFMatrix::AddLine(TArrayD &dst, int l) {
  if (!fMatrix->FillBuf1D(fBuf.GetArray(), fLevel, l)) {
    throw ReadException();
  }

  int cols = fMatrix->GetNColumns();

  for (int c = 0; c < cols; ++c) {
    // Bad for speed; overloaded operator[] checks array bounds
    dst[c] += fBuf[c];
  }
}
