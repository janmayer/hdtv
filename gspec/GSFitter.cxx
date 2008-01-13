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
 
#include "GSFitter.h"
#include <TMath.h>
#include <math.h>
#include <Riostream.h>

/* As of version 5.15, ROOT does not allow a fitting function
   to access parameters inside a class. The only way to pass
   parameters is via the p[] array. This forces a certain
   uglyness here: some parameters are passed via global
   variables, which means that the function can only be used
   once, and some are passed via abuse of the p[] array.  */

list<double> *gBgRegions;

/* Only on instance of TF1 may use this
   function at any given time, since it
   relies on global variables for parameter
   passing. */
double LinearBgForFit(double *x, double *p)
{
  list<double>::iterator iter;

  bool reject = true;
  for(iter = gBgRegions->begin(); iter != gBgRegions->end() && *iter < x[0]; iter++)
    reject = !reject;
    
  if(reject) {
    TF1::RejectPoint();
    return 0.0;
  } else {
    return p[0] + p[1] * x[0];
  }
}

double LinearBg(double *x, double *p)
{
  return p[0] + p[1] * x[0];
}

double PeakFunc(double *x, double *p)
{
  double dx = x[0] - p[1];
  double sigma = p[2];
  double tl = p[3], tr = p[4];
  double _x;
  
  if(dx < -tl) {
    _x = tl / (sigma * sigma) * (dx + tl / 2.0);
  } else if(dx < tr) {
    _x = - dx * dx / (2.0 * sigma * sigma);
  } else {
    _x = - tr / (sigma * sigma) * (dx - tr / 2.0);
  }
  
  return p[0] * exp(_x);
}

/* Function used for fitting.
   The number of peaks is passed via abuse of the p[0]
   parameter, which has to be FIXED. */
   
/* p[1], p[2]: linear background
   p[3], ...: 5 parameters per peak */
double FitFunc(double *x, double *p)
{
  double sum;
  int numPeaks = (int) p[0];
  
  sum = p[1] + x[0] * p[2];

  for(int i=0; i<numPeaks; i++) {
    sum += PeakFunc(x, p + 5*i + 3);
  }
  
  return sum;
}

GSFitter::GSFitter(double r1, double r2)
{
  fMin = TMath::Min(r1, r2);
  fMax = TMath::Max(r1, r2);
  fNumPeaks = 0;
  
  /* Disable left and right tails */
  fLeftTails = 100000.0;
  fRightTails = 100000.0;
}

void GSFitter::AddPeak(double pos)
{
  list<double>::iterator iter = fPeaks.begin();
  while(iter != fPeaks.end() && *iter < pos)
    iter++;
  fPeaks.insert(iter, pos);
  fNumPeaks++;  
}

void GSFitter::AddBgRegion(double p1, double p2)
{
  list<double>::iterator iter, next;
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

TF1 *GSFitter::FitBackground(TH1 *hist)
{
  TF1 *fitFunc = new TF1("b_fit", &LinearBgForFit, *(fBgRegions.begin()), *(fBgRegions.rbegin()), 2);
  TF1 *func = new TF1("b", &LinearBg, *(fBgRegions.begin()), *(fBgRegions.rbegin()), 2);

  /* Setup global variables used for parameter passing (UGLY!!!) */
  gBgRegions = &fBgRegions;
  
  fitFunc->SetParameter(0, 0.0);
  fitFunc->SetParameter(1, 0.0);
  hist->Fit(fitFunc, "RQN");
  
  /* Copy parameters */
  func->SetParameter(0, fitFunc->GetParameter(0));
  func->SetParameter(1, fitFunc->GetParameter(1));
  
  delete fitFunc;
  
  return func;
}

TF1 *GSFitter::Fit(TH1 *hist, TF1 *bgFunc)
{
  list<double>::iterator iter;
  int i;
  TF1 *func = new TF1("f", &FitFunc, fMin, fMax, fNumPeaks * 5 + 3);

  func->FixParameter(0, (double)fNumPeaks);
  
  if(bgFunc) {
    func->FixParameter(1, bgFunc->GetParameter(0));
    func->FixParameter(2, bgFunc->GetParameter(1));
  }
  
  for(i=0, iter = fPeaks.begin(); iter != fPeaks.end(); i++, iter++) {
    double val;
  
    val = (double) hist->GetBinContent((int) TMath::Ceil(*iter - 0.5));
    func->SetParameter(5*i + 0 + 3, val);
    func->SetParameter(5*i + 1 + 3, *iter);
    func->SetParameter(5*i + 2 + 3, 1.0);
    /* Negative values for the tails means to fit them */
    if(fLeftTails < 0) {
    	func->SetParameter(5*i + 3 + 3, 10.0);
    } else {
        func->FixParameter(5*i + 3 + 3, fLeftTails);
    }
    if(fRightTails < 0) {
    	func->SetParameter(5*i + 4 + 3, 10.0);
    } else {
        func->FixParameter(5*i + 4 + 3, fRightTails);
    }
  }
  
  hist->Fit(func, "RQNM");
  
  /* Now, do the ''real'' fit */
  /* for(i=0, iter = fPeaks.begin(); iter != fPeaks.end(); i++, iter++) {
    if(fLeftTails < 0)
      func->SetParameter(5*i + 3 + 3, 6.0); //func->GetParameter(5*i + 2 + 3));
    if(fRightTails < 0)
      func->SetParameter(5*i + 4 + 3, func->GetParameter(5*i + 2 + 3));
  }
   
  hist->Fit(func, "RQNM"); */
     
  return func;
}

double GSFitter::GetPeakPos(TF1 *func, int id)
{
  if(id < 0 || id > int(func->GetParameter(0)))
     return 0.0;
     
  return func->GetParameter(5*id + 1 + 3);
}

double GSFitter::GetPeakVol(TF1 *func, int id)
{
  if(id < 0 || id > int(func->GetParameter(0)))
     return 0.0;
     
  double sigma = func->GetParameter(5*id + 2 + 3);
  double tl = func->GetParameter(5*id + 3 + 3);
  double tr = func->GetParameter(5*id + 4 + 3);
  double vol = 0.0;
  
  // Contribution from left tail
  vol += (sigma * sigma) / tl * exp(-(tl*tl)/(2.0*sigma*sigma));
  
  // Contribution from truncated gaussian
  vol += sqrt(M_PI / 2.0) * sigma * (TMath::Erf(tl / (sqrt(2.0)*sigma)) + TMath::Erf(tr / (sqrt(2.0)*sigma)));
  
  // Contribution from right tail
  vol += (sigma * sigma) / tr * exp(-(tr*tr)/(2.0*sigma*sigma));
  
  // Multiply by scaling factor A
  return func->GetParameter(5*id + 0 + 3) * vol;
}

double GSFitter::GetPeakFWHM(TF1 *func, int id)
{
  if(id < 0 || id > int(func->GetParameter(0)))
     return 0.0;
     
  return 2.0 * sqrt(2.0 * log(2.0)) * func->GetParameter(5*id + 2 + 3);
}

double GSFitter::GetPeakLT(TF1 *func, int id)
{
  if(id < 0 || id > int(func->GetParameter(0)))
     return 0.0;
     
  return func->GetParameter(5*id + 3 + 3);
}

double GSFitter::GetPeakRT(TF1 *func, int id)
{
  if(id < 0 || id > int(func->GetParameter(0)))
     return 0.0;
     
  return func->GetParameter(5*id + 4 + 3);
}

