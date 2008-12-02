/*
 * gSpec - a viewer for gamma spectra
 *  Copyright (C) 2006  Norbert Braun <n.braun@ikp.uni-koeln.de>
 *
 * This file is part of gSpec.
 *
 * gSpec is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * gSpec is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
 * for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with gSpec; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
 * 
 */
 
/*
 * For compatibility with the original TV program, the GSCalibration class uses
 * a different bin numbering convention than ROOT: the center of the first visible
 * bin (bin number 1 in ROOT) is assumed to lie at E(0.0) = cal0.
 */

#include "GSCalibration.h"
#include <TMath.h>
#include <Riostream.h>

void GSCalibration::SetCal(std::vector<double> cal)
{
  fCal = cal;
  UpdateDerivative();
}

void GSCalibration::SetCal(double cal0)
{
  fCal.clear();
  fCal.push_back(cal0);
  UpdateDerivative();
}

void GSCalibration::SetCal(double cal0, double cal1)
{
  fCal.clear();
  fCal.push_back(cal0);
  fCal.push_back(cal1);
  UpdateDerivative();
}

void GSCalibration::SetCal(double cal0, double cal1, double cal2)
{
  fCal.clear();
  fCal.push_back(cal0);
  fCal.push_back(cal1);
  fCal.push_back(cal2);
  UpdateDerivative();
}

void GSCalibration::SetCal(double cal0, double cal1, double cal2, double cal3)
{
  fCal.clear();
  fCal.push_back(cal0);
  fCal.push_back(cal1);
  fCal.push_back(cal2);
  fCal.push_back(cal3);
  UpdateDerivative();
}

void GSCalibration::UpdateDerivative()
{
  std::vector<double>::iterator c = fCal.begin();
  c++;
  double a = 1.0;
  
  fCalDeriv.clear();
  while(c != fCal.end()) {
    fCalDeriv.push_back(a * *c++);
    a += 1.;
  }
}

double GSCalibration::Ch2E(double ch)
{
  // Convert a channel to an energy, using the chosen energy
  // calibration.
  std::vector<double>::reverse_iterator c = fCal.rbegin();
  double E = *c++;
  
  while(c != fCal.rend())
    E = E * ch + *c++;

  return E;
}

double GSCalibration::dEdCh(double ch)
{
  std::vector<double>::reverse_iterator c = fCalDeriv.rbegin();
  double slope = *c++;
  
  while(c != fCalDeriv.rend())
    slope = slope * ch + *c++;

  return slope;
}

// Convert an energy to a channel, using the chosen energy
// calibration.
// TODO: deal with slope == 0.0
double GSCalibration::E2Ch(double e)
{
  double ch = 1.0;
  double de = Ch2E(ch) - e;
  double slope;
  double _e = TMath::Abs(e);
  std::vector<double>::reverse_iterator c;
  
  if(_e < 1.0) _e = 1.0;
  
  for(int i=0; i<10 && TMath::Abs(de / _e) > 1e-10; i++) {
    /* Calculate slope */
    c = fCalDeriv.rbegin();
    slope = *c++;
    while(c != fCalDeriv.rend()) {
      slope = slope * ch + *c++;
    }
  
  	ch -= de / slope;
  	de = Ch2E(ch) - e;
  }
  
  if(TMath::Abs(de / _e) > 1e-10) {
    cout << "Warning: Solver failed to converge in GSCalibration::E2Ch()." << endl;
  } 
  
  return ch;
}

void GSCalibration::Apply(TAxis *axis, int nbins)
{
  double *centers = new double[nbins];
  
  for(int i=0; i<nbins; i++) {
    centers[i] = Ch2E((double)i);
  }
  
  axis->Set(nbins, centers);
  
  delete[] centers;
}
