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

#include "Calibration.hh"

#include <cmath>

#include <algorithm>
#include <iostream>
#include <memory>
#include <numeric>

#include <TAxis.h>

namespace HDTV {

void Calibration::SetCal(const std::vector<double> &cal) {
  fCal = cal;
  UpdateDerivative();
}

void Calibration::SetCal(const TArrayD &cal) {
  fCal.clear();
  fCal.reserve(cal.GetSize());
  std::copy(cal.GetArray(), cal.GetArray() + cal.GetSize(), std::back_inserter(fCal));
  UpdateDerivative();
}

void Calibration::SetCal(double cal0) {
  fCal.clear();
  fCal.push_back(cal0);
  UpdateDerivative();
}

void Calibration::SetCal(double cal0, double cal1) {
  fCal.clear();
  fCal.push_back(cal0);
  fCal.push_back(cal1);
  UpdateDerivative();
}

void Calibration::SetCal(double cal0, double cal1, double cal2) {
  fCal.clear();
  fCal.push_back(cal0);
  fCal.push_back(cal1);
  fCal.push_back(cal2);
  UpdateDerivative();
}

void Calibration::SetCal(double cal0, double cal1, double cal2, double cal3) {
  fCal.clear();
  fCal.push_back(cal0);
  fCal.push_back(cal1);
  fCal.push_back(cal2);
  fCal.push_back(cal3);
  UpdateDerivative();
}

void Calibration::UpdateDerivative() {
  // Update the coefficients of the derivative polynomial.
  // (Internal use only.)

  fCalDeriv.clear();
  if (fCal.empty()) {
    return;
  }

  double a = 1.0;

  std::transform(fCal.begin() + 1, fCal.end(), std::back_inserter(fCalDeriv),
                 [&](double coeff) { return coeff * a++; });
}

//! Convert a channel to an energy, using the chosen energy
//! calibration.
double Calibration::Ch2E(double ch) const {
  // Catch special case of a trivial calibration
  if (fCal.empty()) {
    return ch;
  }

  return std::accumulate(fCal.rbegin(), fCal.rend(), 0.0, [ch](double E, double coeff) { return E * ch + coeff; });
}

//! Calculate the slope of the calibration function, \frac{dE}{dCh},
//! at position ch .
double Calibration::dEdCh(double ch) const {
  // Catch special case of a trivial calibration
  if (fCal.empty()) {
    return 1.0;
  }
  return std::accumulate(fCalDeriv.rbegin(), fCalDeriv.rend(), 0.0,
                         [ch](double slope, double coeff) { return slope * ch + coeff; });
}

double Calibration::E2Ch(double e) const {
  //! Convert an energy to a channel, using the chosen energy
  //! calibration.
  //! TODO: deal with slope == 0.0

  // Catch special case of a trivial calibration
  if (fCal.empty()) {
    return e;
  }

  double ch = 1.0;
  double de = Ch2E(ch) - e;
  double slope;
  double _e = std::abs(e);
  std::vector<double>::const_reverse_iterator c;

  if (_e < 1.0) {
    _e = 1.0;
  }

  for (int i = 0; i < 10 && std::abs(de / _e) > 1e-10; i++) {
    // Calculate slope
    slope = std::accumulate(fCalDeriv.rbegin(), fCalDeriv.rend(), 0.0,
                            [ch](double slope, double coeff) { return slope * ch + coeff; });

    ch -= de / slope;
    de = Ch2E(ch) - e;
  }

  if (std::abs(de / _e) > 1e-10) {
    std::cout << "Warning: Solver failed to converge in Calibration::E2Ch()." << std::endl;
  }

  return ch;
}

void Calibration::Apply(TAxis *axis, int nbins) {
  auto centers = std::make_unique<double[]>(nbins);

  for (int i = 0; i < nbins; i++) {
    centers[i] = Ch2E(i);
  }

  axis->Set(nbins, centers.get());
}

void Calibration::Rebin(const unsigned int nBins) {
  const unsigned int size = fCal.size();
  for (unsigned int i = 0; i < size; i++) {
    fCal[i] *= std::pow(nBins, i);
  }
  UpdateDerivative();
}

} // end namespace HDTV
