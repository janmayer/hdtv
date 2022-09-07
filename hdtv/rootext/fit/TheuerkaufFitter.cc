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
#include <memory>
#include <numeric>

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
TheuerkaufPeak::TheuerkaufPeak(const Param &pos, const Param &vol, const Param &sigma, const Param &tl, const Param &tr,
                               const Param &sh, const Param &sw)
    : fPos{pos}, fVol{vol}, fSigma{sigma}, fTL{tl ? tl : Param::Fixed(0.0)}, fTR{tr ? tr : Param::Fixed(0.0)},
      fSH{sh ? sh : Param::Fixed(0.0)}, fSW{sw ? sw : Param::Fixed(1.0)}, fHasLeftTail{tl},
      fHasRightTail{tr}, fHasStep{sh}, fFunc{nullptr}, fCachedNorm{std::numeric_limits<double>::quiet_NaN()},
      fCachedSigma{std::numeric_limits<double>::quiet_NaN()}, fCachedTL{std::numeric_limits<double>::quiet_NaN()},
      fCachedTR{std::numeric_limits<double>::quiet_NaN()} {}

//! Copy constructor
//! Does not copy the fPeakFunc pointer, it will be re-generated when needed.
TheuerkaufPeak::TheuerkaufPeak(const TheuerkaufPeak &src)
    : fPos{src.fPos}, fVol{src.fVol}, fSigma{src.fSigma}, fTL{src.fTL}, fTR{src.fTR}, fSH{src.fSH}, fSW{src.fSW},
      fHasLeftTail{src.fHasLeftTail}, fHasRightTail{src.fHasRightTail}, fHasStep{src.fHasStep}, fFunc{src.fFunc},
      fCachedNorm{src.fCachedNorm}, fCachedSigma{src.fCachedSigma}, fCachedTL{src.fCachedTL}, fCachedTR{src.fCachedTR} {
}

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

//! Restores parameters and error for fit function.
//! Warnings:    Restore function of corresponding fitter has to be called
//!              beforehand!
void TheuerkaufPeak::RestoreParam(const Param &param, double value, double error) {
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

  fPeakFunc = std::make_unique<TF1>(GetFuncUniqueName("peak", this).c_str(), this, &TheuerkaufPeak::EvalNoStep, min,
                                    max, numParams, "TheuerkaufPeak", "EvalNoStep");

  for (int i = 0; i < numParams; i++) {
    fPeakFunc->SetParameter(i, fFunc->GetParameter(i));
  }

  return fPeakFunc.get();
}

double TheuerkaufPeak::Eval(const double *x, const double *p) const { return EvalNoStep(x, p) + EvalStep(x, p); }

double TheuerkaufPeak::EvalNoStep(const double *x, const double *p) const {
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

double TheuerkaufPeak::EvalStep(const double *x, const double *p) const {
  //! Step function

  if (fHasStep) {
    double dx = *x - fPos.Value(p);
    double sigma = fSigma.Value(p);
    double sh = fSH.Value(p);
    double sw = fSW.Value(p);

    double vol = fVol.Value(p);
    double norm = GetNorm(sigma, fTL.Value(p), fTR.Value(p));

    return vol * norm * sh * (M_PI / 2. + std::atan(sw * dx / (std::sqrt(2.) * sigma)));
  } else {
    return 0.0;
  }
}

double TheuerkaufPeak::GetNorm(double sigma, double tl, double tr) const {
  if (fCachedSigma == sigma && fCachedTL == tl && fCachedTR == tr) {
    return fCachedNorm;
  }

  double vol;

  // Contribution from left tail + left half of truncated gaussian
  if (fHasLeftTail) {
    vol = (sigma * sigma) / tl * std::exp(-(tl * tl) / (2.0 * sigma * sigma));
    vol += std::sqrt(M_PI / 2.0) * sigma * std::erf(tl / (std::sqrt(2.0) * sigma));
  } else {
    vol = std::sqrt(M_PI / 2.0) * sigma;
  }

  // Contribution from right tail + right half of truncated gaussian
  if (fHasRightTail) {
    vol += (sigma * sigma) / tr * std::exp(-(tr * tr) / (2.0 * sigma * sigma));
    vol += std::sqrt(M_PI / 2.0) * sigma * std::erf(tr / (std::sqrt(2.0) * sigma));
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

double TheuerkaufFitter::Eval(const double *x, const double *p) const {
  //! Private: evaluation function for fit

  // Evaluate background function, if it has been given
  double sum = fBackground ? fBackground->Eval(*x) : 0.0;

  // Evaluate internal background
  sum += std::accumulate(std::reverse_iterator<const double *>(p + fNumParams),
                         std::reverse_iterator<const double *>(p + fNumParams - fIntNParams), 0.0,
                         [&x](double bg, double param) { return bg * *x + param; });

  // Evaluate peaks
  return std::accumulate(fPeaks.begin(), fPeaks.end(), sum,
                         [x, p](double sum, const TheuerkaufPeak &peak) { return sum + peak.Eval(x, p); });
}

double TheuerkaufFitter::EvalBg(const double *x, const double *p) const {
  //! Private: evaluation function for background

  // Evaluate background function, if it has been given
  double sum = fBackground ? fBackground->Eval(*x) : 0.0;

  // Evaluate internal background
  sum += std::accumulate(std::reverse_iterator<const double *>(p + fNumParams),
                         std::reverse_iterator<const double *>(p + fNumParams - fIntNParams), 0.0,
                         [&x](double bg, double param) { return bg * *x + param; });

  // Evaluate steps in peaks
  return std::accumulate(fPeaks.begin(), fPeaks.end(), sum,
                         [x, p](double sum, const TheuerkaufPeak &peak) { return sum + peak.EvalStep(x, p); });
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

  fBgFunc = std::make_unique<TF1>(GetFuncUniqueName("fitbg", this).c_str(), this, &TheuerkaufFitter::EvalBg, min, max,
                                  fNumParams, "TheuerkaufFitter", "EvalBg");

  for (int i = 0; i < fNumParams; i++) {
    fBgFunc->SetParameter(i, fSumFunc->GetParameter(i));
    fBgFunc->SetParError(i, fSumFunc->GetParError(i));
  }

  return fBgFunc.get();
}

//! Do the fit, using the given background function
void TheuerkaufFitter::Fit(TH1 &hist, const Background &bg) {
  // Refuse to fit twice
  if (IsFinal()) {
    return;
  }

  fBackground.reset(bg.Clone());
  fIntNParams = 0;
  _Fit(hist);
}

//! Do the fit, fitting a polynomial of degree intBgDeg for the background at
//! the same time. Set intNParams to 0 to disable background completely.
void TheuerkaufFitter::Fit(TH1 &hist, int intNParams) {
  // Refuse to fit twice
  if (IsFinal()) {
    return;
  }

  fBackground.reset();
  fIntNParams = intNParams;
  _Fit(hist);
}

//! Private: worker function to actually do the fit
void TheuerkaufFitter::_Fit(TH1 &hist) {
  // Allocate additional parameters for internal polynomial background
  // Note that a polynomial of degree n has n+1 parameters!
  if (fIntNParams >= 1) {
    fNumParams += fIntNParams;
  }

  // Create fit function
  fSumFunc = std::make_unique<TF1>(GetFuncUniqueName("f", this).c_str(), this, &TheuerkaufFitter::Eval, fMin, fMax,
                                   fNumParams, "TheuerkaufFitter", "Eval");

  // *** Initial parameter estimation ***
  int b1 = hist.FindBin(fMin);
  int b2 = hist.FindBin(fMax);

  // Check if any of the peaks contain steps
  bool steps = std::find_if(fPeaks.begin(), fPeaks.end(), [](const TheuerkaufPeak &peak) { return peak.HasStep(); }) !=
               fPeaks.end();

  // If there is internal background, we need to estimate it first. We will
  // estimate that the background is constant at the level of the bin with the
  // lowest content if there are no steps, or constant at the level of the
  // leftmost bin in the fit region otherwise (both after substraction of
  // possible external background).
  // NOTE: we generally assume that the step width is positive, so the step
  // function goes to zero at the far left side of the peak. This seems
  // reasonable, as the step width is usually fixed at 1.0.

  double intBg0 = 0.0;
  if (fIntNParams >= 1) {
    if (steps) {
      intBg0 = hist.GetBinContent(b1);
      if (fBackground != nullptr) {
        intBg0 -= fBackground->Eval(hist.GetBinCenter(b1));
      }
    } else {
      intBg0 = std::numeric_limits<double>::infinity();

      if (fBackground != nullptr) {
        for (int b = b1; b <= b2; ++b) {
          double bc = hist.GetBinContent(b) - fBackground->Eval(hist.GetBinCenter(b));
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
    fSumFunc->SetParameter(fNumParams - fIntNParams, intBg0);
    if (fIntNParams >= 2) {
      for (int i = fNumParams - fIntNParams + 1; i < fNumParams; ++i) {
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
    struct Result {
      int nStepFree;
      double sumFixedStep;
    };

    auto result =
        std::accumulate(fPeaks.begin(), fPeaks.end(), Result{0, 0.0}, [](Result result, const TheuerkaufPeak &peak) {
          if (peak.fSH) {
            if (peak.fSH.IsFree()) {
              ++result.nStepFree;
            } else {
              result.sumFixedStep += peak.fSH._Value();
            }
          }
          return result;
        });

    double sumStep = hist.GetBinContent(b2) - hist.GetBinContent(b1);
    if (result.nStepFree != 0) {
      avgFreeStep = (sumStep - result.sumFixedStep) / result.nStepFree;
    }
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
  std::transform(fPeaks.begin(), fPeaks.end(), std::back_inserter(amps), [&](const TheuerkaufPeak &peak) {
    double pos = peak.fPos._Value();
    double amp = hist.GetBinContent(hist.FindBin(pos)) - intBg0;
    if (fBackground) {
      amp -= fBackground->Eval(pos);
    }
    sumAmp += amp;
    return amp;
  });

  // Second: include steps
  if (steps) {
    // Generate a list of peak IDs sorted by position
    std::vector<PeakID_t> sortedPeakIDs(fPeaks.size());
    std::iota(sortedPeakIDs.begin(), sortedPeakIDs.end(), 0);
    std::sort(sortedPeakIDs.begin(), sortedPeakIDs.end(), [&](const PeakID_t &lhs, const PeakID_t &rhs) {
      return fPeaks[lhs].fPos._Value() < fPeaks[rhs].fPos._Value();
    });

    struct Sums {
      double step, amp;
    };
    auto sums =
        std::accumulate(sortedPeakIDs.begin(), sortedPeakIDs.end(), Sums{0.0, 0.0}, [&](Sums sums, PeakID_t id) {
          auto &peak = fPeaks[id];
          double curStep = 0.0;
          if (peak.HasStep()) {
            curStep = peak.fSH.IsFree() ? peak.fSH._Value() : avgFreeStep;
          }
          amps[id] -= sums.step + curStep / 2.0;
          sums.amp -= sums.step + curStep / 2.0;
          sums.step += curStep;
          return sums;
        });
    sumAmp -= sums.amp;
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
    sumVol -= std::accumulate(fPeaks.begin(), fPeaks.end(), 0.0, [&](double sum, const TheuerkaufPeak &peak) {
      if (peak.HasStep()) {
        double curStep = peak.fSH.IsFree() ? avgFreeStep : peak.fSH._Value();
        int b = hist.FindBin(peak.fPos._Value());
        sum -= curStep * (b2 - std::min(b, b2) + 0.5);
      }
      return sum;
    });
  }

  // Second: calculate average peak width (sigma)
  double avgSigma = std::abs(sumVol / (sumAmp * std::sqrt(2. * M_PI)));

  // Third: calculate sum of free volumes and amplitudes
  double sumFreeAmp = sumAmp;
  double sumFreeVol = sumVol;
  auto ampIter = amps.begin();
  for (auto &peak : fPeaks) {
    if (!peak.fVol.IsFree()) {
      sumFreeAmp -= *(ampIter++);
      sumFreeVol -= peak.fVol._Value();
    }
  }

  // Init fit parameters for peaks
  ampIter = amps.begin();
  for (auto &peak : fPeaks) {
    double amp = *(ampIter++);
    SetParameter(*fSumFunc, peak.fPos);
    if (fOnlypositivepeaks.GetValue()) {
      // The root fit algorithm produces strange results when fitting with extreme limits/boundary conditions, hence set
      // some sane upper limits
      SetParameter(*fSumFunc, peak.fVol, std::max(sumFreeVol * amp / sumFreeAmp, 1.), true, 0.,
                   std::max(100. * sumVol, 0.) + 1e9);
      SetParameter(*fSumFunc, peak.fSigma, avgSigma, true, 0., 10 * (fMax - fMin) + 1e3);
    } else {
      SetParameter(*fSumFunc, peak.fVol, sumFreeVol * amp / sumFreeAmp);
      SetParameter(*fSumFunc, peak.fSigma, avgSigma);
    }
    SetParameter(*fSumFunc, peak.fTL, 10.0);
    SetParameter(*fSumFunc, peak.fTR, 10.0);
    SetParameter(*fSumFunc, peak.fSH, avgFreeStep / (amp * M_PI));
    SetParameter(*fSumFunc, peak.fSW, 1.0);

    peak.SetSumFunc(fSumFunc.get());
  }

  if (!fDebugShowInipar) {
    // Now, do the fit
    char options[7];
    sprintf(options, "RQNM%s%s", fIntegrate.GetValue() ? "I" : "", fLikelihood.GetValue() == "poisson" ? "L" : "");
    hist.Fit(fSumFunc.get(), options);

    // Store Chi^2
    fChisquare = fSumFunc->GetChisquare();
  }

  // Finalize fitter
  fFinal = true;
}

//! Restore the fit, using the given background function
bool TheuerkaufFitter::Restore(const Background &bg, double ChiSquare) {
  fBackground.reset(bg.Clone());
  fIntNParams = 0;
  _Restore(ChiSquare);
  return true;
}

//! Restore the fit, using the given internal background polynomial
bool TheuerkaufFitter::Restore(const TArrayD &bgPolValues, const TArrayD &bgPolErrors, double ChiSquare) {
  fBackground.reset();

  if (bgPolValues.GetSize() != bgPolErrors.GetSize()) {
    Warning("HDTV::TheuerkaufFitter::Restore", "sizes of value and error arrays for internal background do no match.");
    return false;
  }

  fIntNParams = bgPolValues.GetSize();

  // Allocate additional parameters for internal polynomial background
  // Note that a polynomial of degree n has n+1 parameters!
  if (fIntNParams >= 1) {
    fNumParams += fIntNParams;
  }

  _Restore(ChiSquare);

  int bgOffset = fNumParams - fIntNParams;
  // Set background parameters of sum function
  for (int i = 0; i < fIntNParams; ++i) {
    fSumFunc->SetParameter(i + bgOffset, bgPolValues[i]);
    fSumFunc->SetParError(i + bgOffset, bgPolErrors[i]);
  }
  return true;
}

//! Internal worker function to restore the fit
void TheuerkaufFitter::_Restore(double ChiSquare) {
  // Create fit function
  fSumFunc = std::make_unique<TF1>(GetFuncUniqueName("f", this).c_str(), this, &TheuerkaufFitter::Eval, fMin, fMax,
                                   fNumParams, "TheuerkaufFitter", "Eval");

  for (auto &peak : fPeaks) {
    peak.SetSumFunc(fSumFunc.get());
  }

  // Store Chi^2
  fChisquare = ChiSquare;
  fSumFunc->SetChisquare(ChiSquare);

  // Finalize fitter
  fFinal = true;
}

} // end namespace Fit
} // end namespace HDTV
