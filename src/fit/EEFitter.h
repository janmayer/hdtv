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
 
#ifndef __EEFitter_h__
#define __EEFitter_h__

#include <TF1.h>
#include <TH1.h>
#include <list>
#include <vector>
#include <iostream>

#include "Param.h"
#include "Fitter.h"

namespace HDTV {
namespace Fit {

class EEFitter;

class EEPeak {
  friend class EEFitter;
  public:
    EEPeak(const Param& pos, const Param& amp, const Param& sigma1, const Param& sigma2,
           const Param& eta, const Param& gamma);
  
    double Eval(double x, double *p);
    
    inline double GetPos()          { return fPos.Value(fFunc); };
    inline double GetPosError()     { return fPos.Error(fFunc); };
    inline double GetAmp()          { return fAmp.Value(fFunc); };
    inline double GetAmpError()     { return fAmp.Error(fFunc); };
    inline double GetSigma1()       { return fSigma1.Value(fFunc); };
    inline double GetSigma1Error()  { return fSigma1.Error(fFunc); };
    inline double GetSigma2()       { return fSigma2.Value(fFunc); };
    inline double GetSigma2Error()  { return fSigma2.Error(fFunc); };
    inline double GetEta()          { return fEta.Value(fFunc); };
    inline double GetEtaError()     { return fEta.Error(fFunc); };
    inline double GetGamma()        { return fGamma.Value(fFunc); };
    inline double GetGammaError()   { return fGamma.Error(fFunc); };
    
    inline double GetVol()          { return fVol; }
    inline double GetVolError()     { return fVolError; }
                                                
    inline void SetFunc(TF1 *func) { fFunc = func; }

  private:
    void StoreIntegral();
    double fVol, fVolError;
  
    Param fPos, fAmp, fSigma1, fSigma2, fEta, fGamma;
    TF1 *fFunc;
};

class EEFitter : public Fitter {
  public:
    EEFitter(double r1, double r2);
    void AddPeak(const EEPeak& peak);
    TF1* Fit(TH1 *hist, TF1 *bgFunc);
    TF1* Fit(TH1 *hist, int intBgDeg=-1);
    inline int GetNumPeaks() { return fNumPeaks; }
    inline const EEPeak& GetPeak(int i) { return fPeaks[i]; }
    
    // For debugging only
    //inline double GetVol()          { return fInt; }
    //inline double GetVolError()     { return fIntError; }
    
  private:
    double Eval(double *x, double *p);
    TF1* _Fit(TH1 *hist);
  
    int fIntBgDeg;
    double fMin, fMax;
    std::vector<EEPeak> fPeaks;
    TF1 *fBgFunc;
    int fNumPeaks;
    
    // For debugging only
    //double fInt, fIntError;
    //void StoreIntegral(TF1 *func, double pos, double sigma1);
};

} // end namespace Fit
} // end namespace HDTV

#endif
