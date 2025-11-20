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

#ifndef __InterpolationBg_h__
#define __InterpolationBg_h__

#include <limits>
#include <list>
#include <memory>
#include <vector>

#include "Math/Interpolator.h"
#include "Math/Polynomial.h"
#include <TF1.h>

#include "Background.hh"

class TArrayD;
class TH1;

namespace HDTV {
namespace Fit {

// Interpolating background fitter
//
// Given N_bg - potentially overlapping - unsorted background regions with
// lower and upper limits l_i and u_i (0 <= i < N_bg), the continous
// background fit is determined in the following way:
// 1. 	Determine the region centers c_i = 0.5*(l_i + u_i), i.e. the mean
// 	values of the limits.
// 2.	Sort the background regions by their centers.
// 3.	Interpolate the tuples (c_i, m_i), where c_i are the region centers,
// 	and the m_i are the uncertainty-weighted mean values of all
// 	bin contents within the interval [floor(l_i), ceil(u_i)].

// Structure to contain a background region which is identified by
// four quantities:
// - 	the lower limit l_i
// - 	the upper limit u_i
// - 	the center, defined as 0.5*(u_i + l_i)
// - 	the uncertainty-weighted mean value of the bin contents within the interval
// 	[l_i, u_i]
// The lower and upper limit are store in a std::pair container
struct BgReg {
  std::pair<double, double> limit;
  double center;
  double weighted_mean;
  double weighted_mean_uncertainty;
};

// Auxiliary class to be able to hand over a ROOT::Math::Interpolator
// to a TF1 object
class InterpolationWrapper {
public:
  InterpolationWrapper(ROOT::Math::Interpolation::Type type) : inter(0, ROOT::Math::Interpolation::kCSPLINE) {}
  InterpolationWrapper(std::vector<double> xx, std::vector<double> yy, ROOT::Math::Interpolation::Type type)
      : inter(xx, yy, ROOT::Math::Interpolation::kCSPLINE) {}

  void SetData(std::vector<double> xx, std::vector<double> yy) {
    x = xx;
    y = yy;
    inter.SetData(x, y);
  }

  InterpolationWrapper(const InterpolationWrapper &iw) : inter(0, ROOT::Math::Interpolation::kCSPLINE) {
    std::vector<double> xx;
    std::vector<double> yy;
    for (unsigned int i = 0; i < iw.GetX().size(); ++i) {
      xx.push_back(iw.GetX()[i]);
      yy.push_back(iw.GetY()[i]);
    }
    inter.SetData(xx, yy);
  }
  InterpolationWrapper &operator=(const InterpolationWrapper &iw) {
    if (this == &iw)
      return *this;
    inter.SetData(iw.GetX(), iw.GetY());
    return *this;
  }

  double operator()(double v) const { return inter.Eval(v); }
  // This is the call operator needed by TF1
  double operator()(double *v, double *p) { return inter.Eval(v[0]); }

  std::vector<double> GetX() const { return x; };
  std::vector<double> GetY() const { return y; };

private:
  ROOT::Math::Interpolator inter;
  std::vector<double> x;
  std::vector<double> y;
};

class InterpolationBg : public Background {
public:
  explicit InterpolationBg(int nParams = 0);
  InterpolationBg(const InterpolationBg &src);
  InterpolationBg &operator=(const InterpolationBg &src);

  double GetCoeff(int i) const override {
    return fFunc ? fFunc->GetParameter(i) : std::numeric_limits<double>::quiet_NaN();
  }

  double GetCoeffError(int i) { return fFunc ? fFunc->GetParError(i) : std::numeric_limits<double>::quiet_NaN(); }

  double GetChisquare() { return fChisquare; }
  double GetMin() const override { return (*fBgRegions.begin()).limit.first; }
  double GetMax() const override { return (*(--fBgRegions.end())).limit.second; }
  unsigned int GetNparams() const override { return fnParams; }

  void Fit(TH1 &hist);
  bool Restore(const TArrayD &values, const TArrayD &errors, double ChiSquare);
  void AddRegion(double p1, double p2);

  InterpolationBg *Clone() const override { return new InterpolationBg(*this); }
  TF1 *GetFunc() override { return fFunc.get(); }

  double Eval(double x) const override {
    if (x <= fFunc->GetXmin() || x >= fFunc->GetXmax())
      return 0.;
    return fInter(x);
  }

  double EvalError(double x) const override;

private:
  double _Eval(double *x, double *p);

  std::list<BgReg> fBgRegions;
  int fnParams;

  std::unique_ptr<TF1> fFunc;
  InterpolationWrapper fInter;
  double fChisquare;
  std::vector<std::vector<double>> fCovar;
};

} // end namespace Fit
} // end namespace HDTV

#endif
