/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2008  Norbert Braun <n.braun@ikp.uni-koeln.de>
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
 
#include "PolyBg.h"
#include <iostream>
 
namespace HDTV {
namespace Fit {

PolyBg::PolyBg(int bgdeg)
{
  fBgDeg = bgdeg;
}

TF1 *PolyBg::Fit(TH1 *hist)
{
  // Create function to be used for fitting
  // Note that a polynomial of degree N has N+1 parameters
  TF1 *fitFunc = new TF1("b_fit", this, &PolyBg::EvalRegion,
                         *(fBgRegions.begin()), *(fBgRegions.rbegin()),
                         fBgDeg+1, "PolyBg", "EvalRegion");
  
  for(int i=0; i<=fBgDeg; i++)
    fitFunc->SetParameter(i, 0.0);
  
  // Fit
  hist->Fit(fitFunc, "RQN");
  
  // Copy parameters to new function
  TF1 *func = new TF1("b", this, &PolyBg::Eval,
                      *(fBgRegions.begin()), *(fBgRegions.rbegin()),
                      fBgDeg+1, "PolyBg", "Eval");
  for(int i=0; i<=fBgDeg; i++)
    func->SetParameter(i, fitFunc->GetParameter(i));
  
  delete fitFunc;

  return func;
}

// Adds a histogram region to be considered while fitting the
// background. If regions overlap, the values covered by two or
// more regions are still only considered once in the fit.
void PolyBg::AddRegion(double p1, double p2)
{
  std::list<double>::iterator iter, next;
  bool inside = false;
  double min, max;
  
  min = TMath::Min(p1, p2);
  max = TMath::Max(p1, p2);

  iter = fBgRegions.begin();
  while(iter != fBgRegions.end() && *iter < min) {
    inside = !inside;
    iter++;
  }
  
  if(!inside) {
    iter = fBgRegions.insert(iter, min);
    iter++;
  }
  
  while(iter != fBgRegions.end() && *iter < max) {
    inside = !inside;
    next = iter; next++;
    fBgRegions.erase(iter);
    iter = next;
  }
  
  if(!inside) {
    fBgRegions.insert(iter, max);
  }
}

// Evaluate background function at position x, calling TH1::RejectPoint()
// if x lies outside the defined background region
double PolyBg::EvalRegion(double *x, double *p)
{
  std::list<double>::iterator iter;

  bool reject = true;
  for(iter = fBgRegions.begin(); iter != fBgRegions.end() && *iter < x[0]; iter++)
    reject = !reject;
    
  if(reject) {
    TF1::RejectPoint();
    return 0.0;
  } else {
    double bg;
    bg = p[fBgDeg];
    for(int i=fBgDeg-1; i>=0; i--)
      bg = bg * x[0] + p[i];
    return bg;
  }
}

// Evaluate background function at position x
double PolyBg::Eval(double *x, double *p)
{
  double bg;
  
  bg = p[fBgDeg];
  for(int i=fBgDeg-1; i>=0; i--)
    bg = bg * x[0] + p[i];
    
  return bg;
}


} // end namespace Fit
} // end namespace HDTV
