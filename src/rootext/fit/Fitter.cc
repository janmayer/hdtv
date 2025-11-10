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

#include "Fitter.hh"

#include <cmath>

#include <TF1.h>

namespace HDTV {
namespace Fit {

Fitter::Fitter(double r1, double r2) noexcept
    : fNumParams{0}, fFinal{false}, fMin{std::min(r1, r2)}, fMax{std::max(r1, r2)}, fNumPeaks{0}, fIntBgDeg{0},
      fIntNParams{-1}, fChisquare{std::numeric_limits<double>::quiet_NaN()} {}

Param Fitter::AllocParam() { return Param::Free(fNumParams++); }

Param Fitter::AllocParam(double ival) { return Param::Free(fNumParams++, ival); }

void Fitter::SetParameter(TF1 &func, Param &param, double ival, bool useLimits, double lowerLimit, double upperLimit) {
  if (useLimits && param.IsFree()) {
    ival = ival < lowerLimit ? lowerLimit : ival > upperLimit ? upperLimit : ival;
  }
  if (!param.HasIVal()) {
    param.SetValue(ival);
  }

  if (param.IsFree()) {
    if (useLimits) {
      func.SetParameter(param._Id(), param._Value());
      func.SetParLimits(param._Id(), lowerLimit, upperLimit);
    } else {
      func.SetParameter(param._Id(), param._Value());
    }
  }
}

double Fitter::GetIntBgCoeff(int i) const {
  if (fSumFunc == nullptr || i < 0 || i > fIntBgDeg) {
    return std::numeric_limits<double>::quiet_NaN();
  } else {
    return fSumFunc->GetParameter(fNumParams - fIntBgDeg - 1 + i);
  }
}

double Fitter::GetIntBgCoeffError(int i) const {
  if (fSumFunc == nullptr || i < 0 || i > fIntBgDeg) {
    return std::numeric_limits<double>::quiet_NaN();
  } else {
    return fSumFunc->GetParError(fNumParams - fIntBgDeg - 1 + i);
  }
}

} // end namespace Fit
} // end namespace HDTV
