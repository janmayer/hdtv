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

#ifndef __PolyBg_h__
#define __PolyBg_h__

#include <limits>
#include <list>
#include <memory>
#include <string>
#include <vector>

#include <TF1.h>

#include "Background.hh"
#include "Option.hh"

class TArrayD;
class TH1;

namespace HDTV {
namespace Fit {

//! Polynomial background fitter
/** Supports fitting the background in several non-connected regions. */

class PolyBg : public Background {
public:
  explicit PolyBg(int nParams = 2, Option<bool> integrate = Option<bool>{false},
                  Option<std::string> likelihood = Option<std::string>{"normal"});
  PolyBg(const PolyBg &src);
  PolyBg &operator=(const PolyBg &src);

  double GetCoeff(int i) const override {
    return fFunc ? fFunc->GetParameter(i) : std::numeric_limits<double>::quiet_NaN();
  }

  double GetCoeffError(int i) { return fFunc ? fFunc->GetParError(i) : std::numeric_limits<double>::quiet_NaN(); }

  double GetChisquare() { return fChisquare; }
  double GetMin() const override {
    return fBgRegions.empty() ? std::numeric_limits<double>::quiet_NaN() : *(fBgRegions.begin());
  }
  double GetMax() const override {
    return fBgRegions.empty() ? std::numeric_limits<double>::quiet_NaN() : *(fBgRegions.rbegin());
  }
  unsigned int GetNparams() const override { return fnParams; };

  void Fit(TH1 &hist);
  bool Restore(const TArrayD &values, const TArrayD &errors, double ChiSquare);
  void AddRegion(double p1, double p2);

  PolyBg *Clone() const override { return new PolyBg(*this); }
  TF1 *GetFunc() override { return fFunc.get(); }

  double Eval(double x) const override { return fFunc ? fFunc->Eval(x) : std::numeric_limits<double>::quiet_NaN(); }

  double EvalError(double x) const override;

private:
  double _EvalRegion(double *x, double *p);
  double _Eval(double *x, double *p);

  std::list<double> fBgRegions;
  int fnParams;
  Option<bool> fIntegrate;
  Option<std::string> fLikelihood;

  std::unique_ptr<TF1> fFunc;
  double fChisquare;
  std::vector<std::vector<double>> fCovar;
};

} // end namespace Fit
} // end namespace HDTV

#endif
