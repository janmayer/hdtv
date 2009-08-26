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

#include "Calibration.h"
#include <TMath.h>
#include <Riostream.h>

namespace HDTV {

void Calibration::SetCal(const std::vector<double>& cal)
{
  fCal = cal;
  UpdateDerivative();
}

void Calibration::SetCal(const TArrayD& cal)
{
  fCal.clear();
  for(int i=0; i<cal.GetSize(); i++)
    fCal.push_back(cal[i]);
  
  UpdateDerivative();
}

void Calibration::SetCal(double cal0)
{
  fCal.clear();
  fCal.push_back(cal0);
  UpdateDerivative();
}

void Calibration::SetCal(double cal0, double cal1)
{
  fCal.clear();
  fCal.push_back(cal0);
  fCal.push_back(cal1);
  UpdateDerivative();
}

void Calibration::SetCal(double cal0, double cal1, double cal2)
{
  fCal.clear();
  fCal.push_back(cal0);
  fCal.push_back(cal1);
  fCal.push_back(cal2);
  UpdateDerivative();
}

void Calibration::SetCal(double cal0, double cal1, double cal2, double cal3)
{
  fCal.clear();
  fCal.push_back(cal0);
  fCal.push_back(cal1);
  fCal.push_back(cal2);
  fCal.push_back(cal3);
  UpdateDerivative();
}

void Calibration::UpdateDerivative()
{
  // Update the coefficients of the derivative polynomial.
  // (Internal use only.)

  std::vector<double>::iterator c = fCal.begin();
  double a = 1.0;
  
  fCalDeriv.clear();
  
  if(c != fCal.end())
    ++c;
  
  while(c != fCal.end()) {
    fCalDeriv.push_back(a * *c++);
    a += 1.;
  }
}

double Calibration::Ch2E(double ch) const
{
  //! Convert a channel to an energy, using the chosen energy
  //! calibration.
  
  // Catch special case of a trivial calibration
  if(fCal.empty())
    return ch;
  
  std::vector<double>::const_reverse_iterator c = fCal.rbegin();
  double E = *c++;
  
  while(c != fCal.rend())
    E = E * ch + *c++;

  return E;
}

double Calibration::dEdCh(double ch) const
{
  //! Calculate the slope of the calibration function, \frac{dE}{dCh},
  //! at position ch .

  // Catch special case of a trivial calibration
  if(fCal.empty())
    return 1.0;

  std::vector<double>::const_reverse_iterator c = fCalDeriv.rbegin();
  double slope = *c++;
  
  while(c != fCalDeriv.rend())
    slope = slope * ch + *c++;

  return slope;
}

double Calibration::E2Ch(double e) const
{
  //! Convert an energy to a channel, using the chosen energy
  //! calibration.
  //! TODO: deal with slope == 0.0
  
  // Catch special case of a trivial calibration
  if(fCal.empty())
    return e;

  double ch = 1.0;
  double de = Ch2E(ch) - e;
  double slope;
  double _e = TMath::Abs(e);
  std::vector<double>::const_reverse_iterator c;
  
  if(_e < 1.0) _e = 1.0;
  
  for(int i=0; i<10 && TMath::Abs(de / _e) > 1e-10; i++) {
    // Calculate slope
    c = fCalDeriv.rbegin();
    slope = *c++;
    while(c != fCalDeriv.rend()) {
      slope = slope * ch + *c++;
    }
  
  	ch -= de / slope;
  	de = Ch2E(ch) - e;
  }
  
  if(TMath::Abs(de / _e) > 1e-10) {
    cout << "Warning: Solver failed to converge in Calibration::E2Ch()." << endl;
  } 
  
  return ch;
}

void Calibration::Apply(TAxis *axis, int nbins)
{
  double *centers = new double[nbins];
  
  for(int i=0; i<nbins; i++) {
    centers[i] = Ch2E((double)i);
  }
  
  axis->Set(nbins, centers);
  
  delete[] centers;
}

} // end namespace HDTV
