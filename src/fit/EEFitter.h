/*
 * gSpec - a viewer for gamma spectra
 *  Copyright (C) 2006  Norbert Braun <n.braun@ikp.uni-koeln.de>
 *
 * This file is part of gSpec.
 *
 * gSpec is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * gSpec is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
 * for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with gSpec; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
 * 
 */
 
#ifndef __EEFitter_h__
#define __EEFitter_h__

#include <TF1.h>
#include <TH1.h>
#include <list>

#include "Param.h"

namespace HDTV {
namespace Fit {

class EEFitter;

class EEPeak {
  friend class EEFitter;
  public:
    EEPeak(const Param& pos, const Param& amp, const Param& sigma1, const Param& sigma2,
           const Param& eta, const Param& gamma);
  
    double Eval(double x, double *p);
    
    inline double GetPos()       { return fPos.Value(fFunc); };
    inline double GetPosError()  { return fPos.Error(fFunc); };
                                                
    inline double SetFunc(TF1 *func) { fFunc = func; }

  private:
    Param fPos, fAmp, fSigma1, fSigma2, fEta, fGamma;
    TF1 *fFunc;
};

class EEFitter {
  public:
    EEFitter(double r1, double r2);
    Param AllocParam(double ival=0.0);
    void AddPeak(EEPeak peak);
    TF1* Fit(TH1 *hist, TF1 *bgFunc);
    TF1* Fit(TH1 *hist, int intBgDeg=-1);
  private:
    double Eval(double *x, double *p);
    TF1* _Fit(TH1 *hist);
  
    int fNumParams;
    int fIntBgDeg;
    double fMin, fMax;
    std::list<EEPeak> fPeaks;
    TF1 *fBgFunc;
    int fNumPeaks;
};

} // end namespace Fit
} // end namespace HDTV

#endif
