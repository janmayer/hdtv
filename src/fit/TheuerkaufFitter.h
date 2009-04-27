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
 
/*
 * This is the ``standard'' peak shape used by the original ``TV'' program.
 * It is described in appendix B of 
 * Jürgen Theuerkauf: Die Analyse von zwei- und mehrdimensionalen
 * γγ-Koinzidenzspektren an Beispielen aus Hochspinexperimenten in der
 * Massengegend um 146Gd (PhD thesis, IKP Cologne, 1994).
 *
 */

#ifndef __TheuerkaufFitter_h__
#define __TheuerkaufFitter_h__

#include <TF1.h>
#include <TH1.h>

#include <math.h>
#include <limits>
#include <vector>
#include <memory>

#include "Param.h"
#include "Fitter.h"
#include "Background.h"

#include <Riostream.h>

namespace HDTV {
namespace Fit {

class TheuerkaufFitter;

class TheuerkaufPeak {
  friend class TheuerkaufFitter;
  public:
    TheuerkaufPeak(const Param& pos, const Param& vol, const Param& sigma,
                   const Param& tl = Param::None(),
                   const Param& tr = Param::None(),
                   const Param& sh = Param::None(),
                   const Param& sw = Param::None());
    TheuerkaufPeak(const TheuerkaufPeak& src);
    TheuerkaufPeak& operator=(const TheuerkaufPeak& src);

    double Eval(double *x, double *p);
    double EvalNoStep(double *x, double *p);
    double EvalStep(double *x, double *p);
    
    inline double GetPos() const        { return fPos.Value(fFunc); }
    inline double GetPosError() const   { return fPos.Error(fFunc); }
    inline bool   PosIsFree() const     { return fPos.IsFree(); }
    inline double GetVol() const        { return fVol.Value(fFunc); }
    inline double GetVolError() const   { return fVol.Error(fFunc); }
    inline bool   VolIsFree() const     { return fVol.IsFree(); }
    inline double GetSigma() const      { return fSigma.Value(fFunc); }
    inline double GetSigmaError() const { return fSigma.Error(fFunc); }
    inline bool   SigmaIsFree() const     { return fSigma.IsFree(); }
    
    inline bool HasLeftTail() const        { return fHasLeftTail; }
    inline double GetLeftTail() const      { return fHasLeftTail ? fTL.Value(fFunc) : 
                                               std::numeric_limits<double>::infinity(); }
    inline double GetLeftTailError() const { return fHasLeftTail ? fTL.Error(fFunc) :
                                               std::numeric_limits<double>::quiet_NaN(); }
    inline bool LeftTailIsFree() const     { return fHasLeftTail ? fTL.IsFree() : false; }

    inline bool HasRightTail() const        { return fHasRightTail; }
    inline double GetRightTail() const      { return fHasRightTail ? fTR.Value(fFunc) : 
                                                std::numeric_limits<double>::infinity(); }
    inline double GetRightTailError() const { return fHasRightTail ? fTR.Error(fFunc) :
                                                std::numeric_limits<double>::quiet_NaN(); }
    inline bool RightTailIsFree() const     { return fHasRightTail ? fTR.IsFree() : false; }
                                            
    inline bool HasStep() const              { return fHasStep; }
    inline double GetStepHeight() const      { return fHasStep ? fSH.Value(fFunc) : 0.0; }
    inline double GetStepHeightError() const { return fHasStep ? fSH.Error(fFunc) :
                                                std::numeric_limits<double>::quiet_NaN(); }
    inline bool StepHeightIsFree() const     { return fHasStep ? fSH.IsFree() : false; }
    inline double GetStepWidth() const       { return fHasStep ? fSW.Value(fFunc) : 
                                                std::numeric_limits<double>::quiet_NaN(); }
    inline double GetStepWidthError() const  { return fHasStep ? fSW.Error(fFunc) :
                                                std::numeric_limits<double>::quiet_NaN(); }
    inline bool StepWidthIsFree() const      { return fHasStep ? fSW.IsFree() : false; }
                                            
    inline void SetSumFunc(TF1 *func) { fFunc = func; }
    
    TF1* GetPeakFunc();

  private:
    double GetNorm(double sigma, double tl, double tr);
    
    Param fPos, fVol, fSigma, fTL, fTR, fSH, fSW;
    bool fHasLeftTail, fHasRightTail, fHasStep;
    TF1 *fFunc;
    std::auto_ptr<TF1> fPeakFunc;
    
    double fCachedNorm;
    double fCachedSigma, fCachedTL, fCachedTR;
    
    static const double DECOMP_FUNC_WIDTH;
};

class TheuerkaufFitter : public Fitter {
  public:
    TheuerkaufFitter(double r1, double r2);

    void AddPeak(const TheuerkaufPeak& peak);
    void Fit(TH1& hist, const Background& bg);
    void Fit(TH1& hist, int intBgDeg=-1);
    inline int GetNumPeaks() { return fNumPeaks; }
    inline const TheuerkaufPeak& GetPeak(int i) { return fPeaks[i]; }
    inline double GetChisquare() { return fChisquare; }
    inline TF1* GetSumFunc() { return fSumFunc.get(); }
    TF1* GetBgFunc();
    
  private:
    // Copying the fitter is not supported
    TheuerkaufFitter(const TheuerkaufFitter& src) { }
    TheuerkaufFitter& operator=(const TheuerkaufFitter& src) { return *this; }
  
    double Eval(double *x, double *p);
    double EvalBg(double *x, double *p);
    void _Fit(TH1& hist);

    int fIntBgDeg;
    double fMin, fMax;
    std::vector<TheuerkaufPeak> fPeaks;
    std::auto_ptr<Background> fBackground;
    std::auto_ptr<TF1> fSumFunc;
    std::auto_ptr<TF1> fBgFunc;
    int fNumPeaks;
    double fChisquare;
};

} // end namespace Fit
} // end namespace HDTV

#endif
