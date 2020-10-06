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

#ifndef __EEFitter_h__
#define __EEFitter_h__

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

class EEFitter;

//! Peak shape useful for fitting electron-electron scattering peaks
class EEPeak {
  friend class EEFitter;

public:
  EEPeak() = default;
  EEPeak(const Param &pos, const Param &amp, const Param &sigma1, const Param &sigma2, const Param &eta,
         const Param &gamma);
  EEPeak(const EEPeak &src);
  EEPeak &operator=(const EEPeak &src);

  double Eval(const double *x, const double *p) const;

  double GetPos() { return fPos.Value(fFunc); };
  double GetPosError() { return fPos.Error(fFunc); };

  void RestorePos(double value, double error) { RestoreParam(fPos, value, error); };

  double GetAmp() { return fAmp.Value(fFunc); };
  double GetAmpError() { return fAmp.Error(fFunc); };

  void RestoreAmp(double value, double error) { RestoreParam(fAmp, value, error); };

  double GetSigma1() { return fSigma1.Value(fFunc); };
  double GetSigma1Error() { return fSigma1.Error(fFunc); };

  void RestoreSigma1(double value, double error) { RestoreParam(fSigma1, value, error); };

  double GetSigma2() { return fSigma2.Value(fFunc); };
  double GetSigma2Error() { return fSigma2.Error(fFunc); };

  void RestoreSigma2(double value, double error) { RestoreParam(fSigma2, value, error); };

  double GetEta() { return fEta.Value(fFunc); };
  double GetEtaError() { return fEta.Error(fFunc); };

  void RestoreEta(double value, double error) { RestoreParam(fEta, value, error); };

  double GetGamma() { return fGamma.Value(fFunc); };
  double GetGammaError() { return fGamma.Error(fFunc); };

  void RestoreGamma(double value, double error) { RestoreParam(fGamma, value, error); };

  double GetVol() { return fVol; }
  double GetVolError() { return fVolError; }

  void RestoreVol(double value, double error) {
    fVol = value;
    fVolError = error;
  };

  void SetSumFunc(TF1 *func) { fFunc = func; }

  TF1 *GetPeakFunc();

private:
  void StoreIntegral();

  Param fPos, fAmp, fSigma1, fSigma2, fEta, fGamma;
  double fVol, fVolError;
  TF1 *fFunc;
  std::unique_ptr<TF1> fPeakFunc;

  void RestoreParam(const Param &param, double value, double error);

  static const double DECOMP_FUNC_WIDTH;
};

//! Fitting multiple EEPeaks
class EEFitter : public Fitter {
public:
  EEFitter(double r1, double r2, Option<bool> integrate, Option<std::string> likelihood, bool debugShowInipar = false)
      : Fitter(r1, r2), fIntegrate(integrate), fLikelihood(likelihood), fDebugShowInipar(debugShowInipar) {}

  // Copying the fitter is not supported
  EEFitter(const EEFitter &) = delete;
  EEFitter &operator=(const EEFitter &) = delete;

  void AddPeak(const EEPeak &peak);
  void Fit(TH1 &hist, const Background &bg);
  void Fit(TH1 &hist, int intBgDeg = -1);

  int GetNumPeaks() { return fNumPeaks; }
  const EEPeak &GetPeak(int i) { return fPeaks[i]; }
  TF1 *GetSumFunc() { return fSumFunc.get(); }

  TF1 *GetBgFunc();
  bool Restore(const Background &bg, double ChiSquare);
  bool Restore(const TArrayD &bgPolValues, const TArrayD &bgPolErrors, double ChiSquare);

  // For debugging only
  // double GetVol() { return fInt; }
  // double GetVolError() { return fIntError; }

private:
  double Eval(const double *x, const double *p) const;
  double EvalBg(const double *x, const double *p) const;
  void _Fit(TH1 &hist);
  void _Restore(double ChiSquare);

  std::vector<EEPeak> fPeaks;
  Option<bool> fIntegrate;
  Option<std::string> fLikelihood;
  bool fDebugShowInipar;

  // For debugging only
  // double fInt, fIntError;
  // void StoreIntegral(TF1 *func, double pos, double sigma1);
};

} // end namespace Fit
} // end namespace HDTV

#endif
