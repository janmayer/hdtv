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

#include "GSDisplaySpec.h"
#include <TROOT.h>
#include <Riostream.h>

GSDisplaySpec::GSDisplaySpec(const TH1I *spec)
{
  fSpec = new TH1I(*spec);
  
  // Set trivial calibration
  SetCal();

  TColor *color = (TColor*) (gROOT->GetListOfColors()->At(3));
  GCValues_t gval;
  gval.fMask = kGCForeground;
  gval.fForeground = color->GetPixel();
  fSpecGC = gClient->GetGCPool()->GetGC(&gval, true);

  //cout << "GSDisplaySpec constructor" << endl;

  /* Set invalid values to ensure cache is flushed at the 
	 first call to GetMax_Cached() */
  fCachedB1 = 1;
  fCachedB2 = 0;
}

GSDisplaySpec::~GSDisplaySpec(void)
{
  gClient->GetGCPool()->FreeGC(fSpecGC);
  delete fSpec;
  cout << "GSDisplaySpec destructor" << endl;
}

void GSDisplaySpec::SetCal(double cal0, double cal1, double cal2, double cal3)
{
  // Set the energy calibration for the spectrum. At the moment,
  // this is limited to a cubic polynomial.

 fCal[0] = cal0;
 fCal[1] = cal1;
 fCal[2] = cal2;
 fCal[3] = cal3;
}

double GSDisplaySpec::Ch2E(double ch)
{
  // Convert a channel to an energy, using the chosen energy
  // calibration.

  return fCal[0] + (fCal[1] + fCal[2] + (fCal[3] * ch) * ch) * ch;
}

double GSDisplaySpec::E2Ch(double e)
{
  // Convert an energy to a channel, using the chosen energy
  // calibration. For the moment, this can be done analytically.

  // Catch the case of a quadratic calibration
  if(TMath::Abs(fCal[3]) < 1e-50) {
    // Catch the case of a linear calibration
    if(TMath::Abs(fCal[2]) < 1e-50) {
  	  return (e - fCal[0]) / fCal[1];
    }
    
    double k, c1, c2, ctr;

    k = TMath::Sqrt(fCal[1]*fCal[1] - 4*fCal[2]*(fCal[0]-e));

    c1 = (k - fCal[1]) / (2 * fCal[2]);
    c2 = (-k - fCal[1]) / (2 * fCal[2]);

    // Return the root which is closer to the center of
    // the spectrums channel range
    ctr = ((double) GetMaxChannel() - GetMinChannel()) / 2.0;

    return (TMath::Abs(c1 - ctr) < TMath::Abs(c2 - ctr)) ? c1 : c2;
  }
  
  double a, b, c;
  
  if(TMath::RootsCubic(fCal, a, b, c)) {
    // only one real root
    return a;
  } else {
  	// three real roots: return the one which is close to the center
  	// of the spectrums channel range
  
  	double ctr = ((double) GetMaxChannel() - GetMinChannel()) / 2.0;
  	
  	if(TMath::Abs(a - ctr) < TMath::Abs(b - ctr)) {
  		if(TMath::Abs(c - ctr) < TMath::Abs(a - ctr)) {
  			return c;
  		} else {
  			return a;
  		}
  	} else {
  		if(TMath::Abs(c - ctr) < TMath::Abs(b - ctr)) {
  			return c;
  		} else {
  			return b;
  		}
  	}
  }
}

/* Find the bin number of the bin between b1 and b2 (inclusive) which
   contains the most events */
int GSDisplaySpec::GetRegionMaxBin(int b1, int b2)
{
  int bin, y, max_bin = -1, max_y = -1;

  if(b1 < 0) b1 = 0;
  if(b2 > fSpec->GetNbinsX() + 1) b2 = fSpec->GetNbinsX() + 1;

  for(bin = b1; bin <= b2; bin ++) {
	y = (int) fSpec->GetBinContent(bin);
	if(y > max_y) {
	  max_y = y;
	  max_bin = bin;
	}
  }
  
  return max_bin;
}

int GSDisplaySpec::GetRegionMax(int b1, int b2)
{
  int max_bin = GetRegionMaxBin(b1, b2);

  return max_bin == -1 ? -1 : (int) fSpec->GetBinContent(max_bin);
}

double GSDisplaySpec::GetMinEnergy(void)
{
  // Return the spectrums lower endpoint in energy units

  return TMath::Min(Ch2E((double) GetMinChannel()),
					Ch2E((double) GetMaxChannel()));
}

double GSDisplaySpec::GetMaxEnergy(void)
{
  // Return the spectrums upper endpoint in energy units

  return TMath::Max(Ch2E((double) GetMinChannel()),
					Ch2E((double) GetMaxChannel()));
}

double GSDisplaySpec::GetEnergyRange(void)
{
  // Returns the width of the spectrum in energy units

  return TMath::Abs(Ch2E((double) GetMinChannel())
					- Ch2E((double) GetMaxChannel()));
}

/* Gets the maximum count between bin b1 and bin b2, inclusive.
   Employes caching to save time during scrolling operations. 

   NOTE: For the caching to be effective, use this function ONLY for
   scrolling operations.
*/
int GSDisplaySpec::GetMax_Cached(int b1, int b2)
{
  int max, bin;
  int newMax=-1, newBin;

  if(b1 < 0) b1 = 0;
  if(b2 > GetNbinsX() + 1) b2 = GetNbinsX() + 1;

  if(b2 < b1)
	return -1;

  if(fCachedB2 < b1 || fCachedB1 > b2) {
	fCachedB1 = b1;
	fCachedB2 = b2;
	fCachedMaxBin = GetRegionMaxBin(b1, b2);
	fCachedMax = (int) GetBinContent(fCachedMaxBin);
  } else {
	if(b1 < fCachedB1) {
	  newBin = GetRegionMaxBin(b1, fCachedB1);
	  newMax = (int) GetBinContent(newBin);

	  fCachedB1 = b1;
	}

	if(b2 > fCachedB2) {
	  bin = GetRegionMaxBin(fCachedB2, b2);
	  max = (int) GetBinContent(bin);

	  if(max > newMax) {
		newMax = max;
		newBin = bin;
	  }

	  fCachedB2 = b2;
	}

	if(newMax >= fCachedMax) {
	  fCachedMaxBin = newBin;
	  fCachedMax = newMax;
	} else if(fCachedMaxBin < b1 || fCachedMaxBin > b2) {
	  bin = GetRegionMaxBin(b1 > fCachedB1 ? b1 : fCachedB1,
			         	    b2 < fCachedB2 ? b2 : fCachedB2);

	  max = (int) GetBinContent(bin);

	  if(max > newMax) {
		fCachedMax = max;
		fCachedMaxBin = bin;
	  } else {
		fCachedMax = newMax;
		fCachedMaxBin = newBin;
	  }

	  fCachedB1 = b1;
	  fCachedB2 = b2;
	}
  }

  return fCachedMax;
}
