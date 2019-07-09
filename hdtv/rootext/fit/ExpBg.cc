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

#include "ExpBg.hh"

#include <cmath>

#include <iostream>

#include <TError.h>
#include <TF1.h>
#include <TH1.h>
#include <TVirtualFitter.h>
#include <ROOT/RMakeUnique.hxx>

#include "Util.hh"

namespace HDTV {
namespace Fit {

ExpBg::ExpBg(int bgdeg) {
  //! Constructor

  fBgDeg = bgdeg;
  fChisquare = std::numeric_limits<double>::quiet_NaN();
}

ExpBg::ExpBg(const ExpBg &src)
    : fBgRegions(src.fBgRegions), fBgDeg(src.fBgDeg),
      fChisquare(src.fChisquare), fCovar(src.fCovar) {
  //! Copy constructor

  if (src.fFunc != nullptr) {
    fFunc = std::make_unique<TF1>(GetFuncUniqueName("b", this).c_str(), this,
                                   &ExpBg::_Eval, src.fFunc->GetXmin(),
                                   src.fFunc->GetXmax(), fBgDeg + 1, "ExpBg",
                                   "_Eval");

    for (int i = 0; i <= fBgDeg; i++) {
      fFunc->SetParameter(i, src.fFunc->GetParameter(i));
      fFunc->SetParError(i, src.fFunc->GetParError(i));
    }
  }
}

ExpBg &ExpBg::operator=(const ExpBg &src) {
  //! Assignment operator

  // Handle self assignment
  if (this == &src) {
    return *this;
  }

  fBgRegions = src.fBgRegions;
  fBgDeg = src.fBgDeg;
  fChisquare = src.fChisquare;
  fCovar = src.fCovar;

  fFunc = std::make_unique<TF1>(GetFuncUniqueName("b", this).c_str(), this,
                                 &ExpBg::_Eval, src.fFunc->GetXmin(),
                                 src.fFunc->GetXmax(), fBgDeg + 1, "ExpBg",
                                 "_Eval");

  for (int i = 0; i <= fBgDeg; i++) {
    fFunc->SetParameter(i, src.fFunc->GetParameter(i));
    fFunc->SetParError(i, src.fFunc->GetParError(i));
  }

  return *this;
}

void ExpBg::Fit(TH1 &hist) {
  //! Fit the background function to the histogram hist

  if (fBgDeg < 0) { // Degenerate case, no free parameters in fit
    return;
  }

  // Create function to be used for fitting
  // Note that a polynomial of degree N has N+1 parameters
  TF1 fitFunc(GetFuncUniqueName("b_fit", this).c_str(), this,
              &ExpBg::_EvalRegion, GetMin(), GetMax(), fBgDeg + 1, "ExpBg",
              "_EvalRegion");

  for (int i = 0; i <= fBgDeg; i++) {
    fitFunc.SetParameter(i, 0.0);
  }

  // Fit
  hist.Fit(&fitFunc, "RQNM");

  // Copy chisquare
  fChisquare = fitFunc.GetChisquare();

  // Copy covariance matrix (needed for error evaluation)
  TVirtualFitter *fitter = TVirtualFitter::GetFitter();
  if (fitter == nullptr) {
    Error("ExpBg::Fit", "No existing fitter after fit");
  } else {
    fCovar = std::vector<std::vector<double>>(fBgDeg + 1,
                                              std::vector<double>(fBgDeg + 1));
    for (int i = 0; i <= fBgDeg; i++) {
      for (int j = 0; j <= fBgDeg; j++) {
        fCovar[i][j] = fitter->GetCovarianceMatrixElement(i, j);
      }
    }
  }

  // Copy parameters to new function
  fFunc = std::make_unique<TF1>(GetFuncUniqueName("b", this).c_str(), this,
                                 &ExpBg::_Eval, GetMin(), GetMax(), fBgDeg + 1,
                                 "ExpBg", "_Eval");

  for (int i = 0; i <= fBgDeg; i++) {
    fFunc->SetParameter(i, fitFunc.GetParameter(i));
    fFunc->SetParError(i, fitFunc.GetParError(i));
  }
}

bool ExpBg::Restore(const TArrayD &values, const TArrayD &errors,
                     double ChiSquare) {
  //! Restore state of a ExpBg object from saved values.
  //! NOTE: The covariance matrix is currently NOT restored, so EvalError()
  //! will always return NaN.

  if (values.GetSize() != fBgDeg + 1 || errors.GetSize() != fBgDeg + 1) {
    Warning("HDTV::ExpBg::Restore",
            "size of vector does not match degree of background.");
    return false;
  }

  // Copy parameters to new function
  fFunc = std::make_unique<TF1>(GetFuncUniqueName("b", this).c_str(), this,
                                 &ExpBg::_Eval, GetMin(), GetMax(), fBgDeg + 1,
                                 "ExpBg", "_Eval");

  for (int i = 0; i <= fBgDeg; i++) {
    fFunc->SetParameter(i, values[i]);
    fFunc->SetParError(i, errors[i]);
  }

  // Copy chisquare
  fChisquare = ChiSquare;
  fFunc->SetChisquare(ChiSquare);

  // Clear covariance matrix
  fCovar.clear();

  return true;
}

void ExpBg::AddRegion(double p1, double p2) {
  //! Adds a histogram region to be considered while fitting the
  //! background. If regions overlap, the values covered by two or
  //! more regions are still only considered once in the fit.

  std::list<double>::iterator iter, next;
  bool inside = false;
  double min, max;

  min = std::min(p1, p2);
  max = std::max(p1, p2);

  iter = fBgRegions.begin();
  while (iter != fBgRegions.end() && *iter < min) {
    inside = !inside;
    iter++;
  }

  if (!inside) {
    iter = fBgRegions.insert(iter, min);
    iter++;
  }

  while (iter != fBgRegions.end() && *iter < max) {
    inside = !inside;
    next = iter;
    next++;
    fBgRegions.erase(iter);
    iter = next;
  }

  if (!inside) {
    fBgRegions.insert(iter, max);
  }
}

double ExpBg::_EvalRegion(double *x, double *p) {
  //! Evaluate background function at position x, calling TH1::RejectPoint()
  //! if x lies outside the defined background region

  std::list<double>::iterator iter;

  bool reject = true;
  for (iter = fBgRegions.begin(); iter != fBgRegions.end() && *iter < x[0];
       iter++) {
    reject = !reject;
  }

  if (reject) {
    TF1::RejectPoint();
    return 0.0;
  } else {
    double bg;
    bg = p[fBgDeg];
    for (int i = fBgDeg - 1; i >= 0; i--) {
      bg = bg * x[0] + p[i];
    }
    return exp(bg);
  }
}

double ExpBg::_Eval(double *x, double *p) {
  //! Evaluate background function at position x

  double bg = p[fBgDeg];
  for (int i = fBgDeg - 1; i >= 0; i--) {
    bg = bg * x[0] + p[i];
  }

  return exp(bg);
}

double ExpBg::EvalError(double x) const {
  // Returns the error of the value of the background function at position x

  if (fCovar.empty()) { // No covariance matrix available
    return std::numeric_limits<double>::quiet_NaN();
  }

  // Evaluate \sum_{i=0}^{fBgDeg} \sum_{j=0}^{fBgDeg} cov(c_i, c_j) x^i x^j
  // via a dual Horner scheme
  std::vector<std::vector<double>>::const_reverse_iterator cov_i;
  double errsq = 0.0;
  for (cov_i = fCovar.rbegin(); cov_i != fCovar.rend(); ++cov_i) {
    std::vector<double>::const_reverse_iterator cov_ij;
    double errsq_i = 0.0;
    for (cov_ij = (*cov_i).rbegin(); cov_ij != (*cov_i).rend(); ++cov_ij) {
      errsq_i = errsq_i * x + *cov_ij;
    }
    errsq = errsq * x + errsq_i;
  }

  return sqrt(errsq);
}

} // end namespace Fit
} // end namespace HDTV
