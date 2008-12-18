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
#include <TVirtualFitter.h>
#include <TError.h>
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

// Initialize fVol and fVolError
// The volume is the integral from -\infty to x_0 + 5 * \sigma_1
//  (see email from Oleksiy Burda <burda@ikp.tu-darmstadt.de>, 2008-12-05)
void EEPeak::StoreIntegral()
{
  // Get fitter
  TVirtualFitter* fitter = TVirtualFitter::GetFitter();
  if (fitter == 0) {
    Error("EEPeak::StoreIntegral", "No existing fitter");
    return;
  }

  double sigma1 = fSigma1.Value(fFunc);
  double sigma2 = fSigma2.Value(fFunc);
  double eta = fEta.Value(fFunc);
  double gamma = fGamma.Value(fFunc);
  
  double vol; // normalized volume
  double dVdSigma1;
  double dVdSigma2 = 0.0, dVdEta = 0.0, dVdGamma = 0.0;
  
  // Contribution from left half
  vol = 0.5 * sqrt(M_PI/log(2.)) * sigma1;
  dVdSigma1 = 0.5 * sqrt(M_PI/log(2.));
  
  // See if radiative tail needs to be included in integral
  if(5.*sigma1 > eta*sigma2) {
    // Contribution from tail
    double B = (sigma2*gamma - 2.*sigma2*eta*eta*log(2.))/(2.*eta*log(2.));
    double A = exp(-eta*eta*log(2.)) * exp(gamma * log(sigma2*eta + B));
    
    double dBdSigma2 = B / sigma2;
    double dBdEta = -(2.*sigma2 + B/eta);
    double dBdGamma = sigma2 / (2.*eta*log(2));

    double dAdSigma2 = (gamma*gamma)/(2.*eta*log(2)) * A/(sigma2*eta+B);
    double dAdEta = -(2.*log(2)*eta + gamma/eta) * A;
    double dAdGamma = A * (log(sigma2*eta + B) + gamma/(sigma2*eta + B) * dBdGamma);
    
    double Vt = A/(1. - gamma) * (pow(B + 5.*sigma1, 1.-gamma) - pow(B + eta*sigma2, 1.-gamma));
    
    double dVtdA = Vt/A;
    double dVtdB = A*(pow(B+5.*sigma1, -gamma) - pow(B+eta*sigma2, -gamma));
   
    double dVtdSigma1 = 5.*A * pow(B+5.*sigma1, -gamma);
    double dVtdSigma2 = dVtdA*dAdSigma2 + dVtdB*dBdSigma2
              - A * pow(B+eta*sigma2, -gamma) * eta;
    double dVtdEta = dVtdA*dAdEta + dVtdB*dBdEta
              - A * pow(B+eta*sigma2, -gamma) * sigma2;
    double dVtdGamma = dVtdA*dAdGamma + dVtdB*dBdGamma
              + Vt/(1.-gamma)
              - A/(1.-gamma) * (log(B+5.*sigma1) * pow(B+5.*sigma1, 1.-gamma)
                                 - log(B+eta*sigma2) * pow(B+eta*sigma2, 1.-gamma));
    
    vol += Vt;
    
    dVdSigma1 += dVtdSigma1;
    dVdSigma2 += dVtdSigma2;
    dVdEta += dVtdEta;
    dVdGamma += dVtdGamma;
    
    // Contribution from truncated right half
    double Vr = 0.5 * sqrt(M_PI/log(2.)) * sigma2 * TMath::Erf(sqrt(log(2.)) * eta);
    double dVrdSigma2 = Vr / sigma2;
    double dVrdEta = sigma2 * exp(-log(2)*eta*eta);
    
    vol += Vr;
    dVdSigma2 += dVrdSigma2;
    dVdEta += dVrdEta;
  } else {
    // Contribution from truncated right half
    double Vr = 0.5 * sqrt(M_PI/log(2.)) * sigma2 * TMath::Erf(5. * sqrt(log(2.)) * sigma1/sigma2);
    double dVrdSigma1 = 5.*exp(-25.*log(2)*(sigma1*sigma1)/(sigma2*sigma2));
    double dVrdSigma2 = Vr / sigma2 
           - 5.*exp(-25.*log(2)*(sigma1*sigma1)/(sigma2*sigma2))
               * sigma1 / sigma2;
  
    vol += Vr;
    dVdSigma1 += dVrdSigma1;
    dVdSigma2 += dVrdSigma2;
  }
  
  // Peak amplitude
  // Note: so far, we have been dealing with the normalized volume
  double amp = fAmp.Value(fFunc);
  
  // Process covariance matrix
  // Note: V = amp * vol  =>  dVdAmp = vol
  double errsq = 0.0;
  double deriv[5] = { vol, amp*dVdSigma1, amp*dVdSigma2, amp*dVdEta, amp*dVdGamma };
  int id[5] = { fAmp._Id(), fSigma1._Id(), fSigma2._Id(), fEta._Id(), fGamma._Id() };
  
  for(int i=0; i<5; i++) {
    for(int j=0; j<5; j++) {
      double covar;
    
      // Fixed parameters do not have covariances
      if(id[i]<0 || id[j]<0)
        covar = 0.0;
      else
        covar = fitter->GetCovarianceMatrixElement(id[i], id[j]);
        
      errsq += deriv[i] * deriv[j] * covar;
    }
  }
  
  fVol = amp * vol;
  fVolError = sqrt(errsq);
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

Param EEFitter::AllocParam()
{
  return Param::Free(fNumParams++);
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
  
  // Init fit parameters
  // Note: this may set parameters several times, but that should not matter
  std::vector<EEPeak>::iterator iter;
  double amp;
  for(iter = fPeaks.begin(); iter != fPeaks.end(); iter ++) {
    amp = (double) hist->GetBinContent((int) TMath::Ceil(iter->fPos._Value() - 0.5));
	SetParameter(func, iter->fPos);
	SetParameter(func, iter->fAmp, amp);
	SetParameter(func, iter->fSigma1, 1.0);
	SetParameter(func, iter->fSigma2, 1.0);
	SetParameter(func, iter->fEta, 1.0);
	SetParameter(func, iter->fGamma, 1.0);
	
	iter->SetFunc(func);
  }
  
  // Do the fit
  hist->Fit(func, "RQNM");
  
  // Calculate the peak volumes while the covariance matrix is still available
  for(iter = fPeaks.begin(); iter != fPeaks.end(); iter ++)
    iter->StoreIntegral();
  
  // For debugging only
  /* if(fPeaks.size() > 0) {
    StoreIntegral(func, fPeaks[0].GetPos(), fPeaks[0].GetSigma1());
  } else {
    fInt = fIntError = std::numeric_limits<double>::quiet_NaN();
    fIntError = fIntError = std::numeric_limits<double>::quiet_NaN();
  } */
     
  return func;
}

void EEFitter::SetParameter(TF1 *func, const Param& param, double ival)
{
  if(!param.IsFree())
    return;
    
  if(param.HasIVal())
    func->SetParameter(param._Id(), param._Value());
  else
    func->SetParameter(param._Id(), ival);
}

/* void EEFitter::StoreIntegral(TF1 *func, double pos, double sigma1)
{
  fInt = func->Integral(pos - 10. * sigma1, pos + 5. * sigma1);
  fIntError = func->IntegralError(pos - 10. * sigma1, pos + 5. * sigma1);
} */

} // end namespace Fit
} // end namespace HDTV
