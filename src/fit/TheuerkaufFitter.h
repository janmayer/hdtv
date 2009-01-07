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

#include "Param.h"
#include "Fitter.h"

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

    double Eval(double x, double *p);
    
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
                                            
    inline void SetFunc(TF1 *func) { fFunc = func; }

  private:
    double GetNorm(double sigma, double tl, double tr);
    
    Param fPos, fVol, fSigma, fTL, fTR, fSH, fSW;
    bool fHasLeftTail, fHasRightTail, fHasStep;
    TF1 *fFunc;
    
    double fCachedNorm;
    double fCachedSigma, fCachedTL, fCachedTR;
};

class TheuerkaufFitter : public Fitter {
  public:
    TheuerkaufFitter(double r1, double r2);
    void AddPeak(const TheuerkaufPeak& peak);
    TF1* Fit(TH1 *hist, TF1 *bgFunc);
    TF1* Fit(TH1 *hist, int intBgDeg=-1);
    inline int GetNumPeaks() { return fNumPeaks; }
    inline const TheuerkaufPeak& GetPeak(int i) { return fPeaks[i]; }
    inline double GetChisquare() { return fChisquare; }
    
  private:
    double Eval(double *x, double *p);
    TF1* _Fit(TH1 *hist);

    int fIntBgDeg;
    double fMin, fMax;
    std::vector<TheuerkaufPeak> fPeaks;
    TF1 *fBgFunc;
    int fNumPeaks;
    double fChisquare;
};

} // end namespace Fit
} // end namespace HDTV

#endif
