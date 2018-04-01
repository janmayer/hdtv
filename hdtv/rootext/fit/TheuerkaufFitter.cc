/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2009  The HDTV development team (see file AUTHORS)
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

#include "TheuerkaufFitter.hh"

#include <cmath>

#include <algorithm>

#include <Riostream.h>
#include <TError.h>
#include <TF1.h>
#include <TH1.h>

#include "Util.hh"

namespace HDTV {
namespace Fit {

// *** TheuerkaufPeak ***
//! Constructor
//! Note that no tails correspond to tail parameters tl = tr = \infty. However,
//! all  member functions are supposed to check fHasLeftTail and fHasRightTail
//! and then ignore the tail parameters. We only need to have some definite
//! value to not interfere with norm caching.
TheuerkaufPeak::TheuerkaufPeak(const Param &pos, const Param &vol,
                               const Param &sigma, const Param &tl,
                               const Param &tr, const Param &sh,
                               const Param &sw)
    : fPos{pos}, fVol{vol}, fSigma{sigma}, fTL{tl ? tl : Param::Fixed(0.0)},
      fTR{tr ? tr : Param::Fixed(0.0)}, fSH{sh ? sh : Param::Fixed(0.0)},
      fSW{sw ? sw : Param::Fixed(1.0)}, fHasLeftTail{tl},
      fHasRightTail{tr}, fHasStep{sh}, fFunc{nullptr},
      fCachedNorm{std::numeric_limits<double>::quiet_NaN()},
      fCachedSigma{std::numeric_limits<double>::quiet_NaN()},
      fCachedTL{std::numeric_limits<double>::quiet_NaN()},
      fCachedTR{std::numeric_limits<double>::quiet_NaN()} {}

//! Copy constructor
//! Does not copy the fPeakFunc pointer, it will be re-generated when needed.
TheuerkaufPeak::TheuerkaufPeak(const TheuerkaufPeak &src)
    : fPos{src.fPos}, fVol{src.fVol}, fSigma{src.fSigma}, fTL{src.fTL},
      fTR{src.fTR}, fSH{src.fSH}, fSW{src.fSW}, fHasLeftTail{src.fHasLeftTail},
      fHasRightTail{src.fHasRightTail}, fHasStep{src.fHasStep},
      fFunc{src.fFunc}, fCachedNorm{src.fCachedNorm},
      fCachedSigma{src.fCachedSigma}, fCachedTL{src.fCachedTL},
      fCachedTR{src.fCachedTR} {}

//! Assignment operator (handles self-assignment implicitly)
TheuerkaufPeak &TheuerkaufPeak::operator=(const TheuerkaufPeak &src) {
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
  fCachedNorm = src.fCachedNorm;
  fCachedSigma = src.fCachedSigma;
  fCachedTL = src.fCachedTL;
  fCachedTR = src.fCachedTR;

  // Do not copy the fPeakFunc pointer, it will be generated when needed.
  fPeakFunc.reset(nullptr);

  return *this;
}

void TheuerkaufPeak::RestoreParam(const Param &param, double value,
                                  double error) {
  //! Restores parameters and error for fit function.
  //! Warnings:    Restore function of corresponding fitter has to be called
  //!              beforehand!

  if (fFunc) {
    fFunc->SetParameter(param._Id(), value);
    fFunc->SetParError(param._Id(), error);
  }

  if (fPeakFunc) {
    fPeakFunc->SetParameter(param._Id(), value);
    fPeakFunc->SetParError(param._Id(), error);
  }
}

const double TheuerkaufPeak::DECOMP_FUNC_WIDTH = 5.0;

TF1 *TheuerkaufPeak::GetPeakFunc() {
  if (fPeakFunc) {
    return fPeakFunc.get();
  }

  if (!fFunc) {
    return nullptr;
  }

  double min = fPos.Value(fFunc) - DECOMP_FUNC_WIDTH * fSigma.Value(fFunc);
  double max = fPos.Value(fFunc) + DECOMP_FUNC_WIDTH * fSigma.Value(fFunc);
  int numParams = fFunc->GetNpar();

  fPeakFunc.reset(new TF1(GetFuncUniqueName("peak", this).c_str(), this,
                          &TheuerkaufPeak::EvalNoStep, min, max, numParams,
                          "TheuerkaufPeak", "EvalNoStep"));

  for (int i = 0; i < numParams; i++) {
    fPeakFunc->SetParameter(i, fFunc->GetParameter(i));
  }

  return fPeakFunc.get();
}

double TheuerkaufPeak::Eval(double *x, double *p) {
  return EvalNoStep(x, p) + EvalStep(x, p);
}

double TheuerkaufPeak::EvalNoStep(double *x, double *p) {
  double dx = *x - fPos.Value(p);
  double vol = fVol.Value(p);
  double sigma = fSigma.Value(p);
  double tl = fTL.Value(p);
  double tr = fTR.Value(p);
  double norm = GetNorm(sigma, tl, tr);
  double _x;

  // Peak function
  if (dx < -tl && fHasLeftTail) {
    _x = tl / (sigma * sigma) * (dx + tl / 2.0);
  } else if (dx < tr || !fHasRightTail) {
    _x = -dx * dx / (2.0 * sigma * sigma);
  } else {
    _x = -tr / (sigma * sigma) * (dx - tr / 2.0);
  }

  return vol * norm * std::exp(_x);
}

double TheuerkaufPeak::EvalStep(double *x, double *p) {
  //! Step function

  if (fHasStep) {
    double dx = *x - fPos.Value(p);
    double sigma = fSigma.Value(p);
    double sh = fSH.Value(p);
    double sw = fSW.Value(p);

    double vol = fVol.Value(p);
    double norm = GetNorm(sigma, fTL.Value(p), fTR.Value(p));

    return vol * norm * sh *
           (M_PI / 2. + std::atan(sw * dx / (std::sqrt(2.) * sigma)));
  } else {
    return 0.0;
  }
}

double TheuerkaufPeak::GetNorm(double sigma, double tl, double tr) {
  if (fCachedSigma == sigma && fCachedTL == tl && fCachedTR == tr)
    return fCachedNorm;

  double vol;

  // Contribution from left tail + left half of truncated gaussian
  if (fHasLeftTail) {
    vol = (sigma * sigma) / tl * std::exp(-(tl * tl) / (2.0 * sigma * sigma));
    vol +=
        std::sqrt(M_PI / 2.0) * sigma * std::erf(tl / (std::sqrt(2.0) * sigma));
  } else {
    vol = std::sqrt(M_PI / 2.0) * sigma;
  }

  // Contribution from right tail + right half of truncated gaussian
  if (fHasRightTail) {
    vol += (sigma * sigma) / tr * std::exp(-(tr * tr) / (2.0 * sigma * sigma));
    vol +=
        std::sqrt(M_PI / 2.0) * sigma * std::erf(tr / (std::sqrt(2.0) * sigma));
  } else {
    vol += std::sqrt(M_PI / 2.0) * sigma;
  }

  fCachedSigma = sigma;
  fCachedTL = tl;
  fCachedTR = tr;
  fCachedNorm = 1. / vol;

  return fCachedNorm;
}

// *** TheuerkaufFitter ***
void TheuerkaufFitter::AddPeak(const TheuerkaufPeak &peak) {
  //! Adds a peak to the peak list

  if (IsFinal()) {
    return;
  }

  fPeaks.push_back(peak);
  fNumPeaks++;
}

double TheuerkaufFitter::Eval(double *x, double *p) {
  //! Private: evaluation function for fit

  // Evaluate background function, if it has been given
  double sum = fBackground ? fBackground->Eval(*x) : 0.0;

  // Evaluate internal background
  double bg = 0.0;
  for (int i = fNumParams - 1; i >= (fNumParams - fIntBgDeg - 1); i--) {
    bg = bg * *x + p[i];
  }
  sum += bg;

  // Evaluate peaks
  PeakVector_t::iterator iter;
  for (iter = fPeaks.begin(); iter != fPeaks.end(); iter++) {
    sum += iter->Eval(x, p);
  }

  return sum;
}

double TheuerkaufFitter::EvalBg(double *x, double *p) {
  //! Private: evaluation function for background

  // Evaluate background function, if it has been given
  double sum = fBackground ? fBackground->Eval(*x) : 0.0;

  // Evaluate internal background
  double bg = 0.0;
  for (int i = fNumParams - 1; i >= (fNumParams - fIntBgDeg - 1); i--) {
    bg = bg * *x + p[i];
  }
  sum += bg;

  // Evaluate steps in peaks
  PeakVector_t::iterator iter;
  for (iter = fPeaks.begin(); iter != fPeaks.end(); iter++) {
    sum += iter->EvalStep(x, p);
  }

  return sum;
}

//! Return a pointer to a function describing this fits background, including
//! any steps in peaks.
//!
//! The function remains owned by the TheuerkaufFitter and is only valid as
//! long as the TheuerkaufFitter is.
TF1 *TheuerkaufFitter::GetBgFunc() {

  if (fBgFunc != nullptr) {
    return fBgFunc.get();
  }

  if (fSumFunc == nullptr) {
    return nullptr;
  }

  double min, max;
  if (fBackground != nullptr) {
    min = std::min(fMin, fBackground->GetMin());
    max = std::max(fMax, fBackground->GetMax());
  } else {
    min = fMin;
    max = fMax;
  }

  fBgFunc.reset(new TF1(GetFuncUniqueName("fitbg", this).c_str(), this,
                        &TheuerkaufFitter::EvalBg, min, max, fNumParams,
                        "TheuerkaufFitter", "EvalBg"));

  for (int i = 0; i < fNumParams; i++) {
    fBgFunc->SetParameter(i, fSumFunc->GetParameter(i));
    fBgFunc->SetParError(i, fSumFunc->GetParError(i));
  }

  return fBgFunc.get();
}

void TheuerkaufFitter::Fit(TH1 &hist, const Background &bg) {
  //! Do the fit, using the given background function

  // Refuse to fit twice
  if (IsFinal()) {
    return;
  }

  fBackground.reset(bg.Clone());
  fIntBgDeg = -1;
  _Fit(hist);
}

void TheuerkaufFitter::Fit(TH1 &hist, int intBgDeg) {
  //! Do the fit, fitting a polynomial of degree intBgDeg for the background
  //! at the same time. Set intBgDeg to -1 to disable background completely.

  // Refuse to fit twice
  if (IsFinal()) {
    return;
  }

  fBackground.reset();
  fIntBgDeg = intBgDeg;
  _Fit(hist);
}

void TheuerkaufFitter::_Fit(TH1 &hist) {
  //! Private: worker function to actually do the fit

  // Allocate additional parameters for internal polynomial background
  // Note that a polynomial of degree n has n+1 parameters!
  if (fIntBgDeg >= 0) {
    fNumParams += (fIntBgDeg + 1);
  }

  // Create fit function
  fSumFunc.reset(new TF1(GetFuncUniqueName("f", this).c_str(), this,
                         &TheuerkaufFitter::Eval, fMin, fMax, fNumParams,
                         "TheuerkaufFitter", "Eval"));

  PeakVector_t::const_iterator citer;

  // *** Initial parameter estimation ***
  int b1 = hist.FindBin(fMin);
  int b2 = hist.FindBin(fMax);

  // Check if any of the peaks contain steps
  bool steps = false;
  for (citer = fPeaks.begin(); citer != fPeaks.end(); citer++) {
    if (citer->HasStep())
      steps = true;
  }

  // If there is internal background, we need to estimate it first. We will
  // estimate that the background is constant at the level of the bin with the
  // lowest content if there are no steps, or constant at the level of the
  // leftmost bin in the fit region otherwise (both after substraction of
  // possible external background).
  // NOTE: we generally assume that the step width is positive, so the step
  // function goes to zero at the far left side of the peak. This seems
  // reasonable, as the step width is usually fixed at 1.0.
  double intBg0 = 0.0;
  if (fIntBgDeg >= 0) {
    if (steps) {
      intBg0 = hist.GetBinContent(b1);
      if (fBackground != nullptr) {
        intBg0 -= fBackground->Eval(hist.GetBinCenter(b1));
      }
    } else {
      intBg0 = std::numeric_limits<double>::infinity();

      if (fBackground != nullptr) {
        for (int b = b1; b <= b2; ++b) {
          double bc =
              hist.GetBinContent(b) - fBackground->Eval(hist.GetBinCenter(b));
          if (bc < intBg0) {
            intBg0 = bc;
          }
        }
      } else {
        for (int b = b1; b <= b2; ++b) {
          double bc = hist.GetBinContent(b);
          if (bc < intBg0) {
            intBg0 = bc;
          }
        }
      }
    }

    // Set background parameters of sum function
    fSumFunc->SetParameter(fNumParams - fIntBgDeg - 1, intBg0);
    if (fIntBgDeg >= 1) {
      for (int i = fNumParams - fIntBgDeg; i < fNumParams; ++i) {
        fSumFunc->SetParameter(i, 0.0);
      }
    }
  }

  // Next, we must estimate possible steps in the background. We estimate the
  // sum of all step heights as the difference between the first and the last
  // bin in the region (with background substracted). From this, we substract
  // all step heights that have been fixed, and evenly distribute the difference
  // among the others.
  // For the rest of the initial parameter estimation process, we will generally
  // assume the steps to be sharp (step width zero). This is because the step
  // width depends on the peak width, which will only be estimated in the end.
  double avgFreeStep = 0.0;
  if (steps) {
    double sumFixedStep = 0.;
    int nStepFree = 0;
    for (citer = fPeaks.begin(); citer != fPeaks.end(); ++citer) {
      if (citer->fSH) {
        if (citer->fSH.IsFree())
          ++nStepFree;
        else
          sumFixedStep += citer->fSH._Value();
      }
    }
    double sumStep = hist.GetBinContent(b2) - hist.GetBinContent(b1);
    if (nStepFree != 0)
      avgFreeStep = (sumStep - sumFixedStep) / nStepFree;
  }

  // Estimate peak amplitudes:
  // We assume that the peak positions provided are already a good estimate of
  // the peak centers. The peak amplitude is then estimated as the bin content
  // at the center, with possible external and internal background, and a
  // possible step, substracted. Note that our estimate gets bad if peaks
  // overlap a lot, but it seems hard to do something about this, because we do
  // not know the peak width yet.
  std::vector<double> amps;
  amps.reserve(fPeaks.size());
  double sumAmp = 0.0;

  // First: no steps
  for (citer = fPeaks.begin(); citer != fPeaks.end(); ++citer) {
    double pos = citer->fPos._Value();
    double amp = hist.GetBinContent(hist.FindBin(pos)) - intBg0;
    if (fBackground.get() != 0)
      amp -= fBackground->Eval(pos);
    amps.push_back(amp);
    sumAmp += amp;
  }

  // Second: include steps
  if (steps) {
    double sumStep = 0.0;
    double curStep;

    // Generate a list of peak IDs sorted by position
    PeakID_t nPeaks = fPeaks.size();
    CmpPeakPos cmp(fPeaks);
    std::vector<PeakID_t> sortedPeakIDs;
    sortedPeakIDs.reserve(nPeaks);
    for (PeakID_t i = 0; i < nPeaks; ++i)
      sortedPeakIDs.push_back(i);
    std::sort(sortedPeakIDs.begin(), sortedPeakIDs.end(), cmp);

    std::vector<PeakID_t>::const_iterator IDIter;
    for (IDIter = sortedPeakIDs.begin(); IDIter != sortedPeakIDs.end();
         ++IDIter) {
      const TheuerkaufPeak &peak = fPeaks[*IDIter];
      if (peak.HasStep()) {
        if (peak.fSH.IsFree())
          curStep = avgFreeStep;
        else
          curStep = peak.fSH._Value();
      } else {
        curStep = 0.0;
      }
      amps[*IDIter] -= sumStep + curStep / 2.0;
      sumAmp -= sumStep + curStep / 2.0;

      sumStep += curStep;
    }
  }

  // Estimate peak parameters
  //
  // Assuming that all peaks in the fit have the same width, their volume is
  // proportional to their amplitude. We thus calculate the total volume as a
  // sum over bin contents (with background substracted) and distribute it among
  // the peaks according to their amplitude. Last, we can estimate the common
  // width from the total volume and the sum of the amplitudes.
  //
  // NOTE: This assumes that the peaks are purely Gaussian, i.e. that there are
  // no tails.

  // First: calculate total volume
  double sumVol = 0.0;
  for (int b = b1; b <= b2; ++b) {
    sumVol += hist.GetBinContent(b);
  }
  sumVol -= intBg0 * (b2 - b1 + 1.);
  if (fBackground != nullptr) {
    for (int b = b1; b <= b2; ++b) {
      sumVol -= fBackground->Eval(hist.GetBinCenter(b));
    }
  }

  if (steps) {
    for (citer = fPeaks.begin(); citer != fPeaks.end(); ++citer) {
      if (citer->HasStep()) {
        double curStep;
        if (citer->fSH.IsFree())
          curStep = avgFreeStep;
        else
          curStep = citer->fSH._Value();
        int b = hist.FindBin(citer->fPos._Value());
        sumVol -= curStep * (b2 - std::min(b, b2) + 0.5);
      }
    }
  }

  // Second: calculate average peak width (sigma)
  double avgSigma = sumVol / (sumAmp * std::sqrt(2. * M_PI));

  // Third: calculate sum of free volumes and amplitudes
  double sumFreeAmp = sumAmp;
  double sumFreeVol = sumVol;
  std::vector<double>::const_iterator ampIter;
  ampIter = amps.begin();
  for (citer = fPeaks.begin(); citer != fPeaks.end(); ++citer) {
    if (!citer->fVol.IsFree()) {
      sumFreeAmp -= *(ampIter++);
      sumFreeVol -= citer->fVol._Value();
    }
  }

  // Init fit parameters for peaks
  ampIter = amps.begin();
  PeakVector_t::iterator iter;
  for (iter = fPeaks.begin(); iter != fPeaks.end(); iter++) {
    double amp = *(ampIter++);
    SetParameter(*fSumFunc, iter->fPos);
    SetParameter(*fSumFunc, iter->fVol, sumFreeVol * amp / sumFreeAmp);
    SetParameter(*fSumFunc, iter->fSigma, avgSigma);
    SetParameter(*fSumFunc, iter->fTL, 10.0);
    SetParameter(*fSumFunc, iter->fTR, 10.0);
    SetParameter(*fSumFunc, iter->fSH, avgFreeStep / (amp * M_PI));
    SetParameter(*fSumFunc, iter->fSW, 1.0);

    iter->SetSumFunc(fSumFunc.get());
  }

  if (!fDebugShowInipar) {
    // Now, do the fit
    hist.Fit(fSumFunc.get(), "RQNM");

    // Store Chi^2
    fChisquare = fSumFunc->GetChisquare();
  }

  // Finalize fitter
  fFinal = true;
}

TheuerkaufFitter::CmpPeakPos::CmpPeakPos(const PeakVector_t &peaks) {
  PeakVector_t::const_iterator citer;
  fPos.reserve(peaks.size());
  for (citer = peaks.begin(); citer != peaks.end(); ++citer) {
    fPos.push_back(citer->fPos._Value());
  }
}

//! Restore the fit, using the given background function
bool TheuerkaufFitter::Restore(const Background &bg, double ChiSquare) {
  fBackground.reset(bg.Clone());
  fIntBgDeg = -1;
  _Restore(ChiSquare);
  return true;
}

//! Restore the fit, using the given internal background polynomial
bool TheuerkaufFitter::Restore(const TArrayD &bgPolValues,
                               const TArrayD &bgPolErrors, double ChiSquare) {
  fBackground.reset();

  if (bgPolValues.GetSize() != bgPolErrors.GetSize()) {
    Warning(
        "HDTV::TheuerkaufFitter::Restore",
        "sizes of value and error arrays for internal background do no match.");
    return false;
  }

  fIntBgDeg = bgPolValues.GetSize() - 1;

  // Allocate additional parameters for internal polynomial background
  // Note that a polynomial of degree n has n+1 parameters!
  if (fIntBgDeg >= 0) {
    fNumParams += (fIntBgDeg + 1);
  }

  _Restore(ChiSquare);

  int bgOffset = fNumParams - fIntBgDeg - 1;
  // Set background parameters of sum function
  for (int i = 0; i <= fIntBgDeg; ++i) {
    fSumFunc->SetParameter(i + bgOffset, bgPolValues[i]);
    fSumFunc->SetParError(i + bgOffset, bgPolErrors[i]);
  }
  return true;
}

//! Internal worker function to restore the fit
void TheuerkaufFitter::_Restore(double ChiSquare) {
  // Create fit function
  fSumFunc.reset(new TF1(GetFuncUniqueName("f", this).c_str(), this,
                         &TheuerkaufFitter::Eval, fMin, fMax, fNumParams,
                         "TheuerkaufFitter", "Eval"));

  PeakVector_t::iterator iter;
  for (iter = fPeaks.begin(); iter != fPeaks.end(); iter++) {
    iter->SetSumFunc(fSumFunc.get());
  }

  // Store Chi^2
  fChisquare = ChiSquare;
  fSumFunc->SetChisquare(ChiSquare);

  // Finalize fitter
  fFinal = true;
}

} // end namespace Fit
} // end namespace HDTV
