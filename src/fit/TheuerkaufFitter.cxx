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
#include "Util.h"
#include <TMath.h>
#include <Riostream.h>

namespace HDTV {
namespace Fit {

// *** TheuerkaufPeak ***
TheuerkaufPeak::TheuerkaufPeak(const Param& pos, const Param& vol, const Param& sigma, const Param& tl, const Param& tr, const Param& sh, const Param& sw)
{
  // Constructor

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

TheuerkaufPeak::TheuerkaufPeak(const TheuerkaufPeak& src)
  : fPos(src.fPos),
    fVol(src.fVol),
    fSigma(src.fSigma),
    fTL(src.fTL),
    fTR(src.fTR),
    fSH(src.fSH),
    fSW(src.fSW),
    fHasLeftTail(src.fHasLeftTail),
    fHasRightTail(src.fHasRightTail),
    fHasStep(src.fHasStep),
    fFunc(src.fFunc),
    fPeakFunc(0)   // Do not copy the fPeakFunc pointer, it will be generated when needed.
{
  // Copy constructor
}

TheuerkaufPeak& TheuerkaufPeak::operator= (const TheuerkaufPeak& src)
{
  // Assignment operator (handles self-assignment implicitly)

  fPos = src.fPos;
  fVol = src.fVol;
  fSigma = src.fSigma;
  fTL = src.fTL;
  fTR = src.fTR;
  fSH = src.fSH;
  fSW = src.fSW;
  fHasLeftTail = src.fHasLeftTail;
  fHasRightTail = src.fHasRightTail;
  fHasStep = src.fHasStep;
  fFunc = src.fFunc;
  
  // Do not copy the fPeakFunc pointer, it will be generated when needed.
  fPeakFunc.reset(0);
  
  return *this;
}

const double TheuerkaufPeak::DECOMP_FUNC_WIDTH = 5.0;

TF1 *TheuerkaufPeak::GetPeakFunc()
{
  if(fPeakFunc.get() != 0)
    return fPeakFunc.get();
    
  if(fFunc == NULL)
    return NULL;
    
  double min = fPos.Value(fFunc) - DECOMP_FUNC_WIDTH * fSigma.Value(fFunc);
  double max = fPos.Value(fFunc) + DECOMP_FUNC_WIDTH * fSigma.Value(fFunc);
  int numParams = fFunc->GetNpar();
    
  fPeakFunc.reset(new TF1(GetFuncUniqueName("peak", this).c_str(),
                          this, &TheuerkaufPeak::EvalNoStep, min, max,
                          numParams, "TheuerkaufPeak", "EvalNoStep"));
                          
  for(int i=0; i<numParams; i++) {
    fPeakFunc->SetParameter(i, fFunc->GetParameter(i));
  }
  
  return fPeakFunc.get();
}

double TheuerkaufPeak::Eval(double *x, double *p)
{
  return EvalNoStep(x, p) + EvalStep(x, p);
}

double TheuerkaufPeak::EvalNoStep(double *x, double *p)
{
  double dx = *x - fPos.Value(p);
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
  
  return vol * norm * exp(_x);
}
  
double TheuerkaufPeak::EvalStep(double *x, double *p)
{
  // Step function
  double stepval = 0.0;

  if(fHasStep) {
    double dx = *x - fPos.Value(p);
    double sigma = fSigma.Value(p);
    double sh = fSH.Value(p);
    double sw = fSW.Value(p);
    
    stepval = sh * (M_PI/2. + atan(sw * dx / (sqrt(2.) * sigma)));
  }
  
  return stepval;
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
  // Constructor

  fMin = TMath::Min(r1, r2);
  fMax = TMath::Max(r1, r2);
  
  fNumPeaks = 0;
  fIntBgDeg = -1;
  
  fChisquare = std::numeric_limits<double>::quiet_NaN();
}

void TheuerkaufFitter::AddPeak(const TheuerkaufPeak& peak)
{
  // Adds a peak to the peak list
  
  if(IsFinal())
    return;

  fPeaks.push_back(peak);
  fNumPeaks++;
}

double TheuerkaufFitter::Eval(double *x, double *p)
{
  // Private: evaluation function for fit
  
  double sum = 0.0;
  
  // Evaluate background function, if it has been given
  if(fBackground.get() != 0)
    sum = fBackground->Eval(*x);
    
  // Evaluate internal background
  double bg = 0.0;
  for(int i=fNumParams-1; i >= (fNumParams-fIntBgDeg-1); i--) {
    bg = bg * *x + p[i];
  }
  sum += bg;
  
  // Evaluate peaks
  std::vector<TheuerkaufPeak>::iterator iter;
  for(iter = fPeaks.begin(); iter != fPeaks.end(); iter++) {
    sum += iter->Eval(x, p);
  }
  
  return sum;
}

double TheuerkaufFitter::EvalBg(double *x, double *p)
{
  // Private: evaluation function for background
  
  double sum = 0.0;
  
  // Evaluate background function, if it has been given
  if(fBackground.get() != 0)
    sum = fBackground->Eval(*x);
    
  // Evaluate internal background
  double bg = 0.0;
  for(int i=fNumParams-1; i >= (fNumParams-fIntBgDeg-1); i--) {
    bg = bg * *x + p[i];
  }
  sum += bg;
  
  // Evaluate steps in peaks
  std::vector<TheuerkaufPeak>::iterator iter;
  for(iter = fPeaks.begin(); iter != fPeaks.end(); iter++) {
    sum += iter->EvalStep(x, p);
  }
  
  return sum;
}

TF1* TheuerkaufFitter::GetBgFunc()
{
  // Return a pointer to a function describing this fits background, including
  // any steps in peaks.
  // The function remains owned by the TheuerkaufFitter and is only valid as long
  // as the TheuerkaufFitter is.
  
  if(fBgFunc.get() != 0)
    return fBgFunc.get();
    
  if(fSumFunc.get() == 0)
    return 0;
    
  double min, max;
  if(fBackground.get() != 0) {
    min = TMath::Min(fMin, fBackground->GetMin());
    max = TMath::Max(fMax, fBackground->GetMax());
  } else {
    min = fMin;
    max = fMax;
  }
    
  fBgFunc.reset(new TF1(GetFuncUniqueName("fitbg", this).c_str(),
                        this, &TheuerkaufFitter::EvalBg, min, max,
                        fNumParams, "TheuerkaufFitter", "EvalBg"));
                        
  for(int i=0; i<fNumParams; i++) {
    fBgFunc->SetParameter(i, fSumFunc->GetParameter(i));
    fBgFunc->SetParError(i, fSumFunc->GetParError(i));
  }
                         
  return fBgFunc.get();
}

void TheuerkaufFitter::Fit(TH1& hist, const Background& bg)
{
  // Do the fit, using the given background function
  
  // Refuse to fit twice
  if(IsFinal())
    return;

  fBackground.reset(bg.Clone());
  fIntBgDeg = -1;
  _Fit(hist);
}

void TheuerkaufFitter::Fit(TH1& hist, int intBgDeg)
{
  // Do the fit, fitting a polynomial of degree intBgDeg for the background
  // at the same time. Set intBgDeg to -1 to disable background completely.
  
  // Refuse to fit twice
  if(IsFinal())
    return;

  fBackground.reset();
  fIntBgDeg = intBgDeg;
  _Fit(hist);
}

void TheuerkaufFitter::_Fit(TH1& hist)
{
  // Private: worker function to actually do the fit
  
  // Allocate additional parameters for internal polynomial background
  // Note that a polynomial of degree n has n+1 parameters!
  if(fIntBgDeg >= 0) {
    fNumParams += (fIntBgDeg + 1);
  }
  
  // Create fit function
  fSumFunc.reset(new TF1(GetFuncUniqueName("f", this).c_str(),
                         this, &TheuerkaufFitter::Eval, fMin, fMax,
                         fNumParams, "TheuerkaufFitter", "Eval"));
  
  // Check if there are any peaks with tails.
  //   If so, we do a preliminary fit with all tails fixed.
  bool needPreFit = false;
  std::vector<TheuerkaufPeak>::iterator iter;
  
  for(iter = fPeaks.begin(); iter != fPeaks.end(); iter ++) {
    if (iter->fTL.IsFree() || iter->fTR.IsFree())
      needPreFit = true;
  }
  
  // FIXME
  double avgVol = 1e3;
  
  // Init fit parameters
  for(iter = fPeaks.begin(); iter != fPeaks.end(); iter ++) {
	SetParameter(*fSumFunc, iter->fPos);
	SetParameter(*fSumFunc, iter->fVol, avgVol);
	SetParameter(*fSumFunc, iter->fSigma, 1.0);
	SetParameter(*fSumFunc, iter->fSH, 1.0);
	SetParameter(*fSumFunc, iter->fSW, 1.0);
	if(iter->fTL.IsFree()) {
	  fSumFunc->FixParameter(iter->fTL._Id(), 10.0);
	  needPreFit = true;
	}
	if(iter->fTR.IsFree()) {
	  fSumFunc->FixParameter(iter->fTR._Id(), 10.0);
	  needPreFit = true;
	}
	
	iter->SetSumFunc(fSumFunc.get());
  }
  
  if(needPreFit) {
    // Do the preliminary fit
    hist.Fit(fSumFunc.get(), "RQN");
    
    // Release tail parameters
    for(iter = fPeaks.begin(); iter != fPeaks.end(); iter ++) {
	  if(iter->fTL.IsFree())
	    fSumFunc->ReleaseParameter(iter->fTL._Id());
      if(iter->fTR.IsFree())
	    fSumFunc->ReleaseParameter(iter->fTR._Id());
  	}
  }

  // Now, do the ''real'' fit
  hist.Fit(fSumFunc.get(), "RQNM");
  
  // Store Chi^2
  fChisquare = fSumFunc->GetChisquare();
  
  // Finalize fitter
  fFinal = true;
}

} // end namespace Fit
} // end namespace HDTV

