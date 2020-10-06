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

#ifndef __Calibration_h__
#define __Calibration_h__

#include <vector>

class TAxis;
class TArrayD;

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

  explicit Calibration(double cal0) { SetCal(cal0); }

  Calibration(double cal0, double cal1) { SetCal(cal0, cal1); }

  Calibration(double cal0, double cal1, double cal2) { SetCal(cal0, cal1, cal2); }

  Calibration(double cal0, double cal1, double cal2, double cal3) { SetCal(cal0, cal1, cal2, cal3); }

  explicit Calibration(const std::vector<double> &cal) { SetCal(cal); }

  explicit Calibration(const TArrayD &cal) { SetCal(cal); }

  void SetCal(double cal0);
  void SetCal(double cal0, double cal1);
  void SetCal(double cal0, double cal1, double cal2);
  void SetCal(double cal0, double cal1, double cal2, double cal3);
  void SetCal(const std::vector<double> &cal);
  void SetCal(const TArrayD &cal);

  bool operator==(const Calibration &rhs) { return this->fCal == rhs.fCal; }
  bool operator!=(const Calibration &rhs) { return !(*this == rhs); }

  explicit operator bool() const { return !IsTrivial(); }
  bool IsTrivial() const { return fCal.empty(); }
  const std::vector<double> &GetCoeffs() const { return fCal; }
  int GetDegree() const { return fCal.size() - 1; }

  double Ch2E(double ch) const;
  double dEdCh(double ch) const;
  double E2Ch(double e) const;

  void Rebin(const unsigned int nBins);
  void Apply(TAxis *axis, int nbins);

private:
  std::vector<double> fCal;
  std::vector<double> fCalDeriv;
  void UpdateDerivative();
};

} // end namespace HDTV

#endif
