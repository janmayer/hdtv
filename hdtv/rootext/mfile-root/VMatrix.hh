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

#ifndef __VMatrix_h__
#define __VMatrix_h__

#include <list>

#include <TH1.h>
#include <TH2.h>

#include "MFileHist.hh"

// VMatrix and RMatrix should be moved to a different module, as they are not
// related to MFile...

/*
  Cut  ^
  Axis |
       |
       |+++++++++++++++++++
       |+++++++++++++++++++
       |+++++++++++++++++++
       |    |    |    |
       |    |    |    |
       |    v    v    v
       +------------------->
               Projection axis
*/

//! A ``virtual matrix'', i.e. a matrix that is not necessarily stored in memory
class VMatrix {
public:
  VMatrix() : fFail(false){};
  virtual ~VMatrix() = default;

  void AddCutRegion(int c1, int c2) { AddRegion(fCutRegions, c1, c2); }
  void AddBgRegion(int c1, int c2) { AddRegion(fBgRegions, c1, c2); }
  void ResetRegions() {
    fCutRegions.clear();
    fBgRegions.clear();
  }

  TH1 *Cut(const char *histname, const char *histtitle);

  // Cut axis info
  virtual int FindCutBin(double x) = 0;
  virtual int GetCutLowBin() = 0;
  virtual int GetCutHighBin() = 0;

  // Projection axis info
  virtual double GetProjXmin() = 0;
  virtual double GetProjXmax() = 0;
  virtual int GetProjXbins() = 0;

  virtual void AddLine(TArrayD &dst, int l) = 0;

  bool Failed() { return fFail; }

private:
  void AddRegion(std::list<int> &reglist, int c1, int c2);
  std::list<int> fCutRegions, fBgRegions;

protected:
  bool fFail;
};

//! ROOT TH2-backed VMatrix
class RMatrix : public VMatrix {
public:
  enum ProjAxis_t { PROJ_X, PROJ_Y };

  RMatrix(TH2 *hist, ProjAxis_t paxis);
  ~RMatrix() override = default;

  int FindCutBin(double x) override {
    TAxis *a = (fProjAxis == PROJ_X) ? fHist->GetYaxis() : fHist->GetXaxis();
    return a->FindBin(x);
  }

  int GetCutLowBin() override { return 1; }
  int GetCutHighBin() override { return (fProjAxis == PROJ_X) ? fHist->GetNbinsY() : fHist->GetNbinsX(); }

  double GetProjXmin() override {
    TAxis *a = (fProjAxis == PROJ_X) ? fHist->GetXaxis() : fHist->GetYaxis();
    return a->GetXmin();
  }

  double GetProjXmax() override {
    TAxis *a = (fProjAxis == PROJ_X) ? fHist->GetXaxis() : fHist->GetYaxis();
    return a->GetXmax();
  }

  int GetProjXbins() override { return (fProjAxis == PROJ_X) ? fHist->GetNbinsX() : fHist->GetNbinsY(); }

  void AddLine(TArrayD &dst, int l) override;

private:
  TH2 *fHist;
  ProjAxis_t fProjAxis;
};

//! MFile-histogram-backed VMatrix
class MFMatrix : public VMatrix {
public:
  MFMatrix(MFileHist *mat, unsigned int level);
  ~MFMatrix() override = default;

  int FindCutBin(double x) override // convert channel to bin number
  {
    return std::ceil(x - 0.5);
  }

  int GetCutLowBin() override { return 0; }
  int GetCutHighBin() override { return fMatrix->GetNLines() - 1; }

  double GetProjXmin() override { return -0.5; }
  double GetProjXmax() override { return fMatrix->GetNColumns() - .5; }
  int GetProjXbins() override { return fMatrix->GetNColumns(); }

  void AddLine(TArrayD &dst, int l) override;

private:
  MFileHist *fMatrix;
  unsigned int fLevel;
  TArrayD fBuf;
};

#endif
