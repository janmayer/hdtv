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

#ifndef __TheuerkaufFitter_h__
#define __TheuerkaufFitter_h__

#include <limits>
#include <memory>
#include <string>
#include <vector>

#include "Fitter.hh"
#include "Option.hh"
#include "Param.hh"

class TArrayD;
class TF1;
class TH1;

namespace HDTV {
namespace Fit {

class TheuerkaufFitter;

//! ``Theuerkauf'' peak shape, useful for fitting peaks from HPGe detectors
/** This is the ``standard'' peak shape used by the original ``TV'' program.
 * It is described in appendix B of
 * Jürgen Theuerkauf: Die Analyse von zwei- und mehrdimensionalen
 * γγ-Koinzidenzspektren an Beispielen aus Hochspinexperimenten in der
 * Massengegend um 146Gd (PhD thesis, IKP Cologne, 1994).
 */
class TheuerkaufPeak {
  friend class TheuerkaufFitter;

public:
  TheuerkaufPeak() = default;
  TheuerkaufPeak(const Param &pos, const Param &vol, const Param &sigma, const Param &tl = Param::Empty(),
                 const Param &tr = Param::Empty(), const Param &sh = Param::Empty(), const Param &sw = Param::Empty());
  TheuerkaufPeak(const TheuerkaufPeak &src);
  TheuerkaufPeak &operator=(const TheuerkaufPeak &src);

  double Eval(const double *x, const double *p) const;
  double EvalNoStep(const double *x, const double *p) const;
  double EvalStep(const double *x, const double *p) const;

  double GetPos() const { return fPos.Value(fFunc); }
  double GetPosError() const { return fPos.Error(fFunc); }
  bool PosIsFree() const { return fPos.IsFree(); }

  void RestorePos(double value, double error) { RestoreParam(fPos, value, error); }

  double GetVol() const { return fVol.Value(fFunc); }
  double GetVolError() const { return fVol.Error(fFunc); }
  bool VolIsFree() const { return fVol.IsFree(); }

  void RestoreVol(double value, double error) { RestoreParam(fVol, value, error); }

  double GetSigma() const { return fSigma.Value(fFunc); }
  double GetSigmaError() const { return fSigma.Error(fFunc); }
  bool SigmaIsFree() const { return fSigma.IsFree(); }
  void RestoreSigma(double value, double error) { RestoreParam(fSigma, value, error); }

  bool HasLeftTail() const { return fHasLeftTail; }

  double GetLeftTail() const { return fHasLeftTail ? fTL.Value(fFunc) : std::numeric_limits<double>::infinity(); }

  double GetLeftTailError() const { return fHasLeftTail ? fTL.Error(fFunc) : std::numeric_limits<double>::quiet_NaN(); }

  bool LeftTailIsFree() const { return fHasLeftTail ? fTL.IsFree() : false; }

  void RestoreLeftTail(double value, double error) { RestoreParam(fTL, value, error); }

  bool HasRightTail() const { return fHasRightTail; }

  double GetRightTail() const { return fHasRightTail ? fTR.Value(fFunc) : std::numeric_limits<double>::infinity(); }

  double GetRightTailError() const {
    return fHasRightTail ? fTR.Error(fFunc) : std::numeric_limits<double>::quiet_NaN();
  }

  bool RightTailIsFree() const { return fHasRightTail ? fTR.IsFree() : false; }

  void RestoreRightTail(double value, double error) { RestoreParam(fTR, value, error); }

  bool HasStep() const { return fHasStep; }
  double GetStepHeight() const { return fHasStep ? fSH.Value(fFunc) : 0.0; }

  double GetStepHeightError() const { return fHasStep ? fSH.Error(fFunc) : std::numeric_limits<double>::quiet_NaN(); }

  bool StepHeightIsFree() const { return fHasStep ? fSH.IsFree() : false; }

  void RestoreStepHeight(double value, double error) { RestoreParam(fSH, value, error); }

  double GetStepWidth() const { return fHasStep ? fSW.Value(fFunc) : std::numeric_limits<double>::quiet_NaN(); }

  double GetStepWidthError() const { return fHasStep ? fSW.Error(fFunc) : std::numeric_limits<double>::quiet_NaN(); }

  bool StepWidthIsFree() const { return fHasStep ? fSW.IsFree() : false; }

  void RestoreStepWidth(double value, double error) { RestoreParam(fSW, value, error); }

  void SetSumFunc(TF1 *func) { fFunc = func; }

  TF1 *GetPeakFunc();

private:
  double GetNorm(double sigma, double tl, double tr) const;

  Param fPos, fVol, fSigma, fTL, fTR, fSH, fSW;
  bool fHasLeftTail, fHasRightTail, fHasStep;
  TF1 *fFunc;
  std::unique_ptr<TF1> fPeakFunc;

  mutable double fCachedNorm, fCachedSigma, fCachedTL, fCachedTR;

  void RestoreParam(const Param &param, double value, double error);

  static const double DECOMP_FUNC_WIDTH;
};

//! Fitting multiple TheuerkaufPeaks
class TheuerkaufFitter : public Fitter {
public:
  TheuerkaufFitter(double r1, double r2, Option<bool> integrate, Option<std::string> likelihood,
                   Option<bool> onlypositivepeaks, bool debugShowInipar = false)
      : Fitter(r1, r2), fIntegrate(integrate), fLikelihood(likelihood), fOnlypositivepeaks(onlypositivepeaks),
        fDebugShowInipar(debugShowInipar) {}

  // Copying the fitter is not supported
  TheuerkaufFitter(const TheuerkaufFitter &) = delete;
  TheuerkaufFitter &operator=(const TheuerkaufFitter &) = delete;

  void AddPeak(const TheuerkaufPeak &peak);
  void Fit(TH1 &hist, const Background &bg);
  void Fit(TH1 &hist, int intNParams = -1);

  int GetNumPeaks() { return fNumPeaks; }
  const TheuerkaufPeak &GetPeak(int i) { return fPeaks[i]; }
  TF1 *GetSumFunc() { return fSumFunc.get(); }

  TF1 *GetBgFunc();
  bool Restore(const Background &bg, double ChiSquare);
  bool Restore(const TArrayD &bgPolValues, const TArrayD &bgPolErrors, double ChiSquare);

private:
  using PeakVector_t = std::vector<TheuerkaufPeak>;
  using PeakID_t = PeakVector_t::size_type;

  double Eval(const double *x, const double *p) const;
  double EvalBg(const double *x, const double *p) const;
  void _Fit(TH1 &hist);
  void _Restore(double ChiSquare);

  std::vector<TheuerkaufPeak> fPeaks;
  Option<bool> fIntegrate;
  Option<std::string> fLikelihood;
  Option<bool> fOnlypositivepeaks;
  bool fDebugShowInipar;
};

} // end namespace Fit
} // end namespace HDTV

#endif
