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

#include "GSDisplayObj.h"

#include <TMath.h>
#include <TGFrame.h>
#include <TColor.h>
#include <TROOT.h>

#include <Riostream.h>

GSDisplayObj::GSDisplayObj(int col)
{
  // Set a trivial calibration
  SetCal();
  
  // Setup GC for color
  TColor *color = (TColor*) (gROOT->GetListOfColors()->At(col));
  GCValues_t gval;
  gval.fMask = kGCForeground;
  gval.fForeground = color->GetPixel();
  fGC = gClient->GetGCPool()->GetGC(&gval, true);
}

GSDisplayObj::~GSDisplayObj()
{
  gClient->GetGCPool()->FreeGC(fGC); 
  //cout << "GSDisplayObj destructor" << endl;
}

void GSDisplayObj::SetCal(double cal0, double cal1, double cal2, double cal3)
{
  // Set the energy calibration for the spectrum. At the moment,
  // this is limited to a cubic polynomial.

 fCal[0] = cal0;
 fCal[1] = cal1;
 fCal[2] = cal2;
 fCal[3] = cal3;
}

double GSDisplayObj::Ch2E(double ch)
{
  // Convert a channel to an energy, using the chosen energy
  // calibration.

  return fCal[0] + (fCal[1] + fCal[2] + (fCal[3] * ch) * ch) * ch;
}

double GSDisplayObj::E2Ch(double e)
{
  // Convert an energy to a channel, using the chosen energy
  // calibration. For the moment, this can be done analytically.

  // Catch the case of a quadratic calibration
  if(TMath::Abs(fCal[3]) < 1e-50) {
    // Catch the case of a linear calibration
    if(TMath::Abs(fCal[2]) < 1e-50) {
  	  return (e - fCal[0]) / fCal[1];
    }
    
    double k, c1, c2, ctr = GetCenterCh();

    k = TMath::Sqrt(fCal[1]*fCal[1] - 4*fCal[2]*(fCal[0]-e));

    c1 = (k - fCal[1]) / (2 * fCal[2]);
    c2 = (-k - fCal[1]) / (2 * fCal[2]);

    // Return the root which is closer to the center of
    // the spectrums channel range

    return (TMath::Abs(c1 - ctr) < TMath::Abs(c2 - ctr)) ? c1 : c2;
  }
  
  double a, b, c;
  
  if(TMath::RootsCubic(fCal, a, b, c)) {
    // only one real root
    return a;
  } else {
  	// three real roots: return the one which is close to the center
  	// of the spectrums channel range
  
  	double ctr = GetCenterCh();
  	
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

double GSDisplayObj::GetMinE()
{
  // Return the spectrums lower endpoint in energy units

  return TMath::Min(Ch2E((double) GetMinCh()),
					Ch2E((double) GetMaxCh()));
}

double GSDisplayObj::GetMaxE()
{
  // Return the spectrums upper endpoint in energy units

  return TMath::Max(Ch2E((double) GetMinCh()),
					Ch2E((double) GetMaxCh()));
}

double GSDisplayObj::GetERange()
{
  // Returns the width of the spectrum in energy units

  return TMath::Abs(Ch2E((double) GetMinCh())
					- Ch2E((double) GetMaxCh()));
}
