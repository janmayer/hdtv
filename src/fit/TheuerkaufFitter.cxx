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
 
#include "TheuerkaufFitter.h"
#include <TMath.h>
#include <iostream>

namespace HDTV {
namespace Fit {

// *** TheuerkaufPeak ***
TheuerkaufPeak::TheuerkaufPeak(const Param& pos, const Param& vol, const Param& sigma, const Param& tl, const Param& tr, const Param& sh, const Param& sw)
{
  fPos = pos;
  fVol = vol;
  fSigma = sigma;
  
  // Note that no tails correspond to tail parameters tl = tr = \infty. However, all
  // member functions are supposed to check fHasLeftTail and fHasRightTail and
  // then ignore the tail parameters. We only need to have some definite value to
  // not interfere with norm caching.
  if(!tl) {
    fTL = Param::Fixed(0.0);
    fHasLeftTail = false;
  } else {
    fTL = tl;
    fHasLeftTail = true;
  }
  
  if(!tr) {
    fTR = Param::Fixed(0.0);
    fHasRightTail = false;
  } else {
    fTR = tr;
    fHasRightTail = true;
  }
  
  if(!sh) {
    fSH = Param::Fixed(0.0);
    fHasStep = false;
  } else {
    fSH = sh;
    fHasStep = true;
  }
  
  if(!sw) {
    fSW = Param::Fixed(1.0);
  } else {
    fSW = sw;
  }
  
  fFunc = NULL;
}

double TheuerkaufPeak::Eval(double x, double *p)
{
  double dx = x - fPos.Value(p);
  double vol = fVol.Value(p);
  double sigma = fSigma.Value(p);
  double tl = fTL.Value(p);
  double tr = fTR.Value(p);
  double norm = GetNorm(sigma, tl, tr);
  double _x;
  
  // Peak function
  if(dx < -tl && fHasLeftTail) {
    _x = tl / (sigma * sigma) * (dx + tl / 2.0);
  } else if(dx < tr || !fHasRightTail) {
    _x = - dx * dx / (2.0 * sigma * sigma);
  } else {
    _x = - tr / (sigma * sigma) * (dx - tr / 2.0);
  }
  
  // Step function
  double stepval = 0.0;
  if(fHasStep) {
    double sh = fSH.Value(p);
    double sw = fSW.Value(p);
    
    stepval = sh * (M_PI/2. + atan(sw * dx / (sqrt(2.) * sigma)));
  }
  
  return vol * norm * exp(_x) + stepval;
}

double TheuerkaufPeak::GetNorm(double sigma, double tl, double tr)
{
  if(fCachedSigma == sigma && fCachedTL == tl && fCachedTR == tr)
    return fCachedNorm;

  double vol;
  
  // Contribution from left tail + left half of truncated gaussian
  if(fHasLeftTail) {
    vol = (sigma * sigma) / tl * exp(-(tl*tl)/(2.0*sigma*sigma));
    vol += sqrt(M_PI / 2.0) * sigma * TMath::Erf(tl / (sqrt(2.0)*sigma));
  } else {
    vol = sqrt(M_PI / 2.0) * sigma;
  }
  
  // Contribution from right tail + right half of truncated gaussian
  if(fHasRightTail) {
    vol += (sigma * sigma) / tr * exp(-(tr*tr)/(2.0*sigma*sigma));
    vol += sqrt(M_PI / 2.0) * sigma * TMath::Erf(tr / (sqrt(2.0)*sigma));
  } else {
    vol += sqrt(M_PI / 2.0) * sigma;
  }
  
  fCachedSigma = sigma;
  fCachedTL = tl;
  fCachedTR = tr;
  fCachedNorm = 1./vol;
 
  return fCachedNorm;
}

// *** TheuerkaufFitter ***
TheuerkaufFitter::TheuerkaufFitter(double r1, double r2)
 : Fitter()
{
  fMin = TMath::Min(r1, r2);
  fMax = TMath::Max(r1, r2);
  fBgFunc = NULL;
  
  fNumPeaks = 0;
  fIntBgDeg = -1;
}

void TheuerkaufFitter::AddPeak(const TheuerkaufPeak& peak)
{
  fPeaks.push_back(peak);
  fNumPeaks++;
}

double TheuerkaufFitter::Eval(double *x, double *p)
{
  double sum = 0.0;
  
  // Evaluate background function, if it has been given
  if(fBgFunc)
    sum = fBgFunc->Eval(*x);
    
  // Evaluate internal background
  double bg = 0.0;
  for(int i=fNumParams-1; i >= (fNumParams-fIntBgDeg-1); i--) {
    bg = bg * *x + p[i];
  }
  sum += bg;
  
  // Evaluate peaks
  std::vector<TheuerkaufPeak>::iterator iter;
  for(iter = fPeaks.begin(); iter != fPeaks.end(); iter++) {
    sum += iter->Eval(*x, p);
  }
  
  return sum;
}

TF1 *TheuerkaufFitter::Fit(TH1 *hist, TF1 *bgFunc)
{
  fBgFunc = bgFunc;
  fIntBgDeg = -1;
  return _Fit(hist);
}

TF1 *TheuerkaufFitter::Fit(TH1 *hist, int intBgDeg)
{
  fBgFunc = NULL;
  fIntBgDeg = intBgDeg;
  return _Fit(hist);
}

TF1 *TheuerkaufFitter::_Fit(TH1 *hist)
{
  // Allocate additional parameters for internal polynomial background
  // Note that a polynomial of degree n has n+1 parameters!
  if(fIntBgDeg >= 0) {
    fNumParams += (fIntBgDeg + 1);
  }
  
  // Create fit function
  TF1 *func = new TF1("f", this, &TheuerkaufFitter::Eval, fMin, fMax,
                      fNumParams, "TheuerkaufFitter", "Eval");
  
  // Check if there are any peaks with tails.
  //   If so, we do a preliminary fit with all tails fixed.
  bool needPreFit = false;
  std::vector<TheuerkaufPeak>::iterator iter;
  
  for(iter = fPeaks.begin(); iter != fPeaks.end(); iter ++) {
    if (iter->fTL.IsFree() || iter->fTR.IsFree())
      needPreFit = true;
  }
  
  // FIXME
  double avgVol = 1e2;
  
  // Init fit parameters
  for(iter = fPeaks.begin(); iter != fPeaks.end(); iter ++) {
	SetParameter(func, iter->fPos);
	SetParameter(func, iter->fVol, avgVol);
	SetParameter(func, iter->fSigma, 1.0);
	SetParameter(func, iter->fSH, 1.0);
	SetParameter(func, iter->fSW, 1.0);
	if(iter->fTL.IsFree()) {
	  func->FixParameter(iter->fTL._Id(), 10.0);
	  needPreFit = true;
	}
	if(iter->fTR.IsFree()) {
	  func->FixParameter(iter->fTR._Id(), 10.0);
	  needPreFit = true;
	}
	
	iter->SetFunc(func);
  }
  
  if(needPreFit) {
    // Do the preliminary fit
    hist->Fit(func, "RQN");
    
    // Release tail parameters
    for(iter = fPeaks.begin(); iter != fPeaks.end(); iter ++) {
	  if(iter->fTL.IsFree())
	    func->ReleaseParameter(iter->fTL._Id());
      if(iter->fTR.IsFree())
	    func->ReleaseParameter(iter->fTR._Id());
  	}
  }

  // Now, do the ''real'' fit
  hist->Fit(func, "RQNM");
  
  // Store Chi^2
  fChisquare = func->GetChisquare();
     
  return func;
}

} // end namespace Fit
} // end namespace HDTV

