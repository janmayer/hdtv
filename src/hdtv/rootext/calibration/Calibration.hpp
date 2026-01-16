/*
 * SPDX-License-Identifier: GPL-2.0-or-later
 *
 * This file is part of HDTV - A ROOT-based spectrum analysis software
 *   Copyright (C) 2006-2026  The HDTV development team (see file AUTHORS)
 */

#pragma once

#include <algorithm>
#include <cmath>
#include <iostream>
#include <iterator>
#include <memory>
#include <numeric>
#include <vector>

#include <TArrayD.h>
#include <TAxis.h>

namespace HDTV {
//! A calibration (channel-energy relationship) with a polynomial of an
//! arbitrary degree
/** It should be noted that this class knows nothing about the binning of the
 *  histogram it might belong to. In hdtv, a Calibration is used to convert an
 *  energy to a channel, and the ROOT TAxis object of the respective histogram
 *  is used to convert the channel to a bin.
 *
 *  For compatibility with the original TV program, functions that read spectra
 *  from files where no information on the binning is recorded usually place
 *  the center of the first visible bin (bin number 1 in ROOT) at channel 0.0.
 *  This then corresponds to an energy E = cal0. However, this needs not be
 *  true for spectra read e.g. from ROOT files.
 */
class Calibration {
public:
  Calibration() = default;

  explicit Calibration(const std::vector<double> &cal) { SetCal(cal); }
  explicit Calibration(const TArrayD &cal) { SetCal(cal); }
  explicit Calibration(double cal0) { SetCal(cal0); }

  Calibration(double cal0, double cal1) { SetCal(cal0, cal1); }
  Calibration(double cal0, double cal1, double cal2) { SetCal(cal0, cal1, cal2); }
  Calibration(double cal0, double cal1, double cal2, double cal3) { SetCal(cal0, cal1, cal2, cal3); }

  void SetCal(const std::vector<double> &cal) {
    fCal = cal;
    UpdateDerivative();
  }
  void SetCal(double cal0) { SetCal(std::vector{cal0}); }
  void SetCal(double cal0, double cal1) { SetCal(std::vector{cal0, cal1}); }
  void SetCal(double cal0, double cal1, double cal2) { SetCal(std::vector{cal0, cal1, cal2}); }
  void SetCal(double cal0, double cal1, double cal2, double cal3) { SetCal(std::vector{cal0, cal1, cal2, cal3}); }
  void SetCal(const TArrayD &cal) { SetCal(std::vector(cal.GetArray(), cal.GetArray() + cal.GetSize())); }

  bool operator==(const Calibration &rhs) const { return this->fCal == rhs.fCal; }
  bool operator!=(const Calibration &rhs) const { return !(*this == rhs); }

  explicit operator bool() const { return !IsTrivial(); }

  bool IsTrivial() const { return fCal.empty(); }
  const std::vector<double> &GetCoeffs() const { return fCal; }
  int GetDegree() const { return fCal.size() - 1; }

  //! Convert a channel to an energy, using the chosen energy calibration.
  double Ch2E(double ch) const {
    // Catch special case of a trivial calibration
    if (fCal.empty()) {
      return ch;
    }

    return std::accumulate(fCal.rbegin(), fCal.rend(), 0.0, [ch](double E, double coeff) { return (E * ch) + coeff; });
  }

  //! Calculate the slope of the calibration function \frac{dE}{dCh}, at position ch
  double dEdCh(double ch) const {
    // Catch special case of a trivial calibration
    if (fCal.empty()) {
      return 1.0;
    }

    return std::accumulate(fCalDeriv.rbegin(), fCalDeriv.rend(), 0.0,
                           [ch](double slope, double coeff) { return (slope * ch) + coeff; });
  }

  //! Convert an energy to a channel, using the chosen energy calibration.
  //! TODO: Deal with slope == 0.0
  double E2Ch(double e) const {
    // Catch special case of a trivial calibration
    if (fCal.empty()) {
      return e;
    }

    double ch = 1.0;
    double de = Ch2E(ch) - e;
    const double _e = std::max(std::abs(e), 1.0);

    for (int i = 0; i < 10 && std::abs(de / _e) > 1e-10; i++) {
      // Calculate the slope
      const double slope = std::accumulate(fCalDeriv.rbegin(), fCalDeriv.rend(), 0.0,
                                           [ch](double slope, double coeff) { return (slope * ch) + coeff; });
      ch -= de / slope;
      de = Ch2E(ch) - e;
    }

    if (std::abs(de / _e) > 1e-10) {
      std::cout << "Warning: Solver failed to converge in Calibration::E2Ch()." << std::endl;
    }

    return ch;
  }

  void Rebin(const unsigned int nBins) {
    const unsigned int size = fCal.size();
    for (unsigned int i = 0; i < size; i++) {
      fCal[i] *= std::pow(nBins, i);
    }
    UpdateDerivative();
  }

  void Apply(TAxis *axis, int nbins) const {
    auto centers = std::make_unique<double[]>(nbins);

    for (int i = 0; i < nbins; i++) {
      centers[i] = Ch2E(i);
    }

    axis->Set(nbins, centers.get());
  }

private:
  std::vector<double> fCal;
  std::vector<double> fCalDeriv;

  void UpdateDerivative() {
    // Update the coefficients of the derivative polynomial
    fCalDeriv.clear();
    if (!fCal.empty()) {
      double a = 1.0;
      std::transform(fCal.begin() + 1, fCal.end(), std::back_inserter(fCalDeriv),
                     [&](double coeff) { return coeff * a++; });
    };
  }
};
} // end namespace HDTV
