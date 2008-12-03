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
 
#include "EEFitter.h"
#include <TMath.h>
#include <math.h>
#include <Riostream.h>

namespace HDTV {
namespace Fit {

EEPeak::EEPeak(const Param& pos, const Param& amp, const Param& sigma1, const Param& sigma2,
               const Param& eta, const Param& gamma)
{
  fPos = pos;
  fAmp = amp;
  fSigma1 = sigma1;
  fSigma2 = sigma2;
  fEta = eta;
  fGamma = gamma;
  
  fFunc = NULL;
}

double EEPeak::Eval(double x, double* p)
{
  double dx = x - fPos.Value(p);
  double sigma1 = fSigma1.Value(p);
  double sigma2 = fSigma2.Value(p);
  double eta = fEta.Value(p);
  double gamma = fGamma.Value(p);
  double _y;
  
  if(dx <= 0) {
    _y = exp(-log(2.) * dx * dx / (sigma1 * sigma1));
  } else if(dx <= (eta * sigma2)) {
	_y = exp(-log(2.) * dx * dx / (sigma2 * sigma2));
  } else {
    double B = (sigma2*gamma - 2.*sigma2*eta*eta*log(2))/(2.*eta*log(2));
	double A = exp(-eta*eta*log(2.)) * exp(gamma * log(sigma2*eta + B));
	_y = A / exp(gamma * log(B + dx));
  }
  
  return fAmp.Value(p) * _y;
}

double EEPeak::GetVol()
{
  double sigma1 = fSigma1.Value(fFunc);
  double sigma2 = fSigma2.Value(fFunc);
  double eta = fEta.Value(fFunc);
  double gamma = fGamma.Value(fFunc);
  double vol; // normalized volume
  
  // Contribution from left half
  vol = 0.5 * sqrt(M_PI/log(2.)) * sigma1;
  
  // Contribution from truncated right half
  vol += 0.5 * sqrt(M_PI/log(2.)) * sigma2 * TMath::Erf(sqrt(log(2.)) * eta);
  
  // Contribution from tail
  double B = (sigma2*gamma - 2.*sigma2*eta*eta*log(2.))/(2.*eta*log(2.));
  double A = exp(-eta*eta*log(2.)) * exp(gamma * log(sigma2*eta + B));
  vol += 1./(gamma - 1.) * A / pow(B + eta*sigma2, gamma - 1.);
  
  // Return real volume
  return fAmp.Value(fFunc) * vol;
}

double EEPeak::GetVolError()
{
  // Not implemented yet...
  return 0.0;
}

/*** EEFitter ***/
EEFitter::EEFitter(double r1, double r2)
{
  fMin = TMath::Min(r1, r2);
  fMax = TMath::Max(r1, r2);
  fBgFunc = NULL;
  
  fNumPeaks = 0;
  fNumParams = 0;
  fIntBgDeg = -1;
}

Param EEFitter::AllocParam(double ival)
{
  return Param::Free(fNumParams++, ival);
}

void EEFitter::AddPeak(const EEPeak& peak)
{
  fPeaks.push_back(peak);
  fNumPeaks++;
}

double EEFitter::Eval(double *x, double *p)
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
  std::vector<EEPeak>::iterator iter;
  for(iter = fPeaks.begin(); iter != fPeaks.end(); iter++) {
    sum += iter->Eval(*x, p);
  }
  
  return sum;
}

TF1 *EEFitter::Fit(TH1 *hist, TF1 *bgFunc)
{
  fBgFunc = bgFunc;
  fIntBgDeg = -1;
  return _Fit(hist);
}

TF1 *EEFitter::Fit(TH1 *hist, int intBgDeg)
{
  fBgFunc = NULL;
  fIntBgDeg = intBgDeg;
  return _Fit(hist);
}

TF1 *EEFitter::_Fit(TH1 *hist)
{
  // Allocate additional parameters for internal polynomial background
  // Note that a polynomial of degree n has n+1 parameters!
  if(fIntBgDeg >= 0) {
    fNumParams += (fIntBgDeg + 1);
  }
  
  // Create fit function
  TF1 *func = new TF1("f", this, &EEFitter::Eval, fMin, fMax,
                      fNumParams, "EEFitter", "Eval");
  
  // Init fit parameters FIXME: this will not work properly for fixed parameters
  std::vector<EEPeak>::iterator iter;
  double amp;
  for(iter = fPeaks.begin(); iter != fPeaks.end(); iter ++) {
    amp = (double) hist->GetBinContent((int) TMath::Ceil(iter->fPos._Value() - 0.5));
	func->SetParameter(iter->fPos._Id(), iter->fPos._Value());
	func->SetParameter(iter->fAmp._Id(), amp);
	func->SetParameter(iter->fSigma1._Id(), 1.0);
	func->SetParameter(iter->fSigma2._Id(), 1.0);
	func->SetParameter(iter->fEta._Id(), 1.0);
	func->SetParameter(iter->fGamma._Id(), 1.0);
	
	iter->SetFunc(func);
  }
  
  // Do the fit
  hist->Fit(func, "RQNM");
     
  return func;
}

} // end namespace Fit
} // end namespace HDTV
