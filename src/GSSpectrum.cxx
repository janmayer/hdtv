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
 * A note about the bin contents in the ROOT spectrum classes:
 * Bin 0: underflow bin
 * Bin 1...nbinsx: actual spectrum
 * Bin nbinxs+1: overflow bin
 *
 * GetBinContent(x) returns the content of the underflow bin for
 * x < 0 and the content of the overflow bin for x > nbinsx.
 * 
 */

#include "GSSpectrum.h"

GSSpectrum::GSSpectrum(const char *name, const char *title, Int_t nbinsx) 
  : TH1I(name, title, nbinsx, 0.0, (Double_t) nbinsx)
{
  // Constructor

  // Start with a trivial calibration
  fA = 0.0;
  fB = 1.0;
  fC = 0.0;
}

GSSpectrum::~GSSpectrum(void) { }


void GSSpectrum::SetCal(double a, double b, double c)
{
  // Set the energy calibration for the spectrum. At the moment,
  // this is limited to a quadratic polynomial.

  fA = a;
  fB = b;
  fC = c;
}

double GSSpectrum::Channel2Energy(double ch)
{
  // Convert a channel to an energy, using the chosen energy
  // calibration.

  return fA + (fB + fC * ch) * ch;
}

double GSSpectrum::Energy2Channel(double e)
{
  // Convert an energy to a channel, using the chosen energy
  // calibration. For the moment, this can be done analytically.

  double k, c1, c2, ctr;

  // Catch the case of a linear calibration
  if(fC == 0) {
	return (e - fA) / fB;
  }

  k = TMath::Sqrt(fB*fB - 4*fC*(fA-e));

  c1 = (k - fB) / (2 * fC);
  c2 = (-k - fB) / (2 * fC);

  // Return the solution which is closer to the center of
  // the spectrums channel range
  ctr = ((double) GetMaxChannel() - GetMinChannel()) / 2.0;

  return (TMath::Abs(c1 - ctr) < TMath::Abs(c2 - ctr)) ? c1 : c2;
}

int GSSpectrum::GetRegionMaxCh_ch(int c1, int c2)
{
  // Calculate the maximum count found between channel c1
  // and channel c2, inclusive

  int n, y, max_y = -1, max_n = -1;

  if(c1 < 0) c1 = 0;
  if(c2 > GetNbinsX() + 1) c2 = GetNbinsX() + 1;

  for(n = c1; n <= c2; n ++) {
	y = (int) GetBinContent(n);
	if(y > max_y) {
	  max_y = y;
	  max_n = n;
	}
  }
  
  return max_n;
}

int GSSpectrum::GetRegionMaxCh_ch(double c1, double c2)
{
  // Calculate the maximum count found between channel c1
  // and channel c2, where c1 and c2 may be non-integer
  
  int n1, n2;

  if(c1 < c2) {
	n1 = (int) TMath::Ceil(c1 - 0.5);
	n2 = (int) TMath::Ceil(c2 - 1.5);
  } else {
	n1 = (int) TMath::Ceil(c2 - 0.5);
	n2 = (int) TMath::Ceil(c1 - 1.5);
  }

  if(n2 < n1)
	n2 = n1;

  return GetRegionMaxCh_ch(n1, n2);
}

int GSSpectrum::GetRegionMaxCh_e(double e1, double e2)
{
  // Calculate the maximum count found between energy e1
  // and energy e2

  double c1 = Energy2Channel(e1);
  double c2 = Energy2Channel(e2);

  return GetRegionMaxCh_ch(c1, c2);
}

int GSSpectrum::GetRegionMax_e(double e1, double e2) {
  int maxCh = GetRegionMaxCh_e(e1, e2);
  
  return maxCh < 0 ? -1 : (int) GetBinContent(maxCh);
}

double GSSpectrum::GetMinEnergy(void)
{
  // Return the spectrums lower endpoint in energy units

  return TMath::Min(Channel2Energy((double) GetMinChannel()),
					Channel2Energy((double) GetMaxChannel()));
}

double GSSpectrum::GetMaxEnergy(void)
{
  // Return the spectrums upper endpoint in energy units

  return TMath::Max(Channel2Energy((double) GetMinChannel()),
					Channel2Energy((double) GetMaxChannel()));
}

double GSSpectrum::GetEnergyRange(void)
{
  // Returns the width of the spectrum in energy units

  return TMath::Abs(Channel2Energy((double) GetMinChannel())
					- Channel2Energy((double) GetMaxChannel()));
}
