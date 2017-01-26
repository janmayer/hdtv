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
 
#ifndef __PolyBg_h__
#define __PolyBg_h__

#include <TF1.h>
#include <TH1.h>
#include <list>
#include <vector>
#include <memory>
#include <Riostream.h>

#include "Background.h"

namespace HDTV {
namespace Fit {

//! Polynomial background fitter
/** Supports fitting the background in several non-connected regions. */

class PolyBg: public Background {
  public:
    PolyBg(int bgDeg=0);
    PolyBg(const PolyBg& src);
    PolyBg& operator= (const PolyBg& src);
    
    double GetCoeff(int i)
      { return fFunc.get() != 0 ? fFunc->GetParameter(i) :
              std::numeric_limits<double>::quiet_NaN(); }
    double GetCoeffError(int i)
      { return fFunc.get() != 0 ? fFunc->GetParError(i) :
              std::numeric_limits<double>::quiet_NaN(); }
    inline int GetDegree()        { return fBgDeg; }
    inline double GetChisquare()  { return fChisquare; }
    virtual double GetMin() const
      { return fBgRegions.empty() ? std::numeric_limits<double>::quiet_NaN() :
                  *(fBgRegions.begin()); }
    virtual double GetMax() const
      { return fBgRegions.empty() ? std::numeric_limits<double>::quiet_NaN() :
                  *(fBgRegions.rbegin()); }
    
    void Fit(TH1& hist);
    bool Restore(const TArrayD& values, const TArrayD& errors, double ChiSquare);
    void AddRegion(double p1, double p2);
    virtual PolyBg* Clone() const
      { return new PolyBg(*this); }    
    virtual TF1* GetFunc()
      { return fFunc.get(); }
    virtual double Eval(double x) const
      { return fFunc.get() != 0 ? fFunc->Eval(x) : std::numeric_limits<double>::quiet_NaN(); }
    virtual double EvalError(double x) const;

  private:
    double _EvalRegion(double *x, double *p);
    double _Eval(double *x, double *p);
  
    std::list<double> fBgRegions;
    int fBgDeg;
    
    std::unique_ptr<TF1> fFunc;
    double fChisquare;
    std::vector<std::vector<double> > fCovar;
};

} // end namespace Fit
} // end namespace HDTV

#endif
