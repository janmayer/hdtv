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

#ifndef __Integral_h__
#define __Integral_h__

#include <TH1.h>

#include "Background.hh"

namespace HDTV {
namespace Fit {

//! Helper class wrapping a cached double
class Cached {
  public:
    Cached() { fHasCached = false; }
    inline operator bool() const { return fHasCached; }
    inline double operator()() const { return fCachedValue; }
    inline double operator()(double x) { fHasCached = true; fCachedValue = x; return x; }

  private:
    bool fHasCached;
    double fCachedValue;
};

//! Helper class to calculate various statistical moments (integral, mean, ...) of a histogram
class Integral {
  public:
    //! Constructor
    /*!
      \param b1 First bin in sum (inclusive)
      \param b2 Last bin in sum (inclusive)
    */
    Integral(int b1, int b2)
     : fB1(b1), fB2(b2) { }
    virtual ~Integral()  { }

    //! Cached version of CalcIntegral()
    double GetIntegral()
      { return fCIntegral ? fCIntegral() : fCIntegral(CalcIntegral()); }

    //! Cached version of CalcIntegralError()
    double GetIntegralError()
      { return fCIntegralError ? fCIntegralError() : fCIntegralError(CalcIntegralError()); }

    //! Cached version of CalcMean()
    double GetMean()
      { return fCMean ? fCMean() : fCMean(CalcMean()); }

    //! Cached version of CalcMeanError()
    double GetMeanError()
      { return fCMeanError ? fCMeanError() : fCMeanError(CalcMeanError()); }

    //! Cached version of CalcVariance()
    double GetVariance()
      { return fCVariance ? fCVariance() : fCVariance(CalcVariance()); }

    //! Cached version of CalcVarianceError()
    double GetVarianceError()
      { return fCVarianceError ? fCVarianceError() : fCVarianceError(CalcVarianceError()); }

    //! Cached version of CalcRawSkewness()
    double GetRawSkewness()
      { return fCRawSkewness ? fCRawSkewness() : fCRawSkewness(CalcRawSkewness()); }

    //! Cached version of CalcRawSkewnessError()
    double GetRawSkewnessError()
      { return fCRawSkewnessError ? fCRawSkewnessError() : fCRawSkewnessError(CalcRawSkewnessError()); }

    //! Cached version of CalcSkewness()
    double GetSkewness()
      { return fCSkewness ? fCSkewness() : fCSkewness(CalcSkewness()); }

    //! Cached version of CalcSkewnessError()
    double GetSkewnessError()
      { return fCSkewnessError ? fCSkewnessError() : fCSkewnessError(CalcSkewnessError()); }

    double GetStdDev();
    double GetStdDevError();
    double GetWidth();
    double GetWidthError();

  protected:
    double CalcIntegral();
    double CalcIntegralError();
    double CalcMean();
    double CalcMeanError();
    double CalcVariance();
    double CalcVarianceError();
    double CalcRawSkewness();
    double CalcRawSkewnessError();
    double CalcSkewness();
    double CalcSkewnessError();

    //! Get content of bin
    virtual double GetBinContent(int bin) = 0;
    //! Get squared error of bin
    virtual double GetBinError2(int bin) = 0;
    //! Get center position of bin
    virtual double GetBinCenter(int bin) = 0;

    int fB1, fB2;

    Cached fCIntegral, fCIntegralError;
    Cached fCMean, fCMeanError;
    Cached fCVariance, fCVarianceError;
    Cached fCRawSkewness, fCRawSkewnessError;
    Cached fCSkewness, fCSkewnessError;

    // ClassDef(HDTV::Fit::Integral, 0)
};

//! Calculate moments of a TH1 histogram
class TH1Integral: public Integral {
  public:
    TH1Integral(TH1 *hist, double r1, double r2);

  protected:
    virtual double GetBinContent(int bin)
      { return fHist->GetBinContent(bin); }
    virtual double GetBinError2(int bin)
      { double e = fHist->GetBinError(bin); return e*e; }
    virtual double GetBinCenter(int bin)
      { return fHist->GetBinCenter(bin); }

    const TH1* fHist;
};

//! Calculate moments of a background function (using a user-specified binning)
class BgIntegral: public Integral {
  public:
    BgIntegral(const Background* background, double r1, double r2, TAxis* axis);

  protected:
    virtual double GetBinContent(int bin)
      { return fBackground->Eval(GetBinCenter(bin)); }
    virtual double GetBinError2(int bin)
      { double e = fBackground->EvalError(GetBinCenter(bin)); return e*e; }
    virtual double GetBinCenter(int bin)
      { return fAxis->GetBinCenter(bin); }

    const Background* fBackground;
    const TAxis* fAxis;
};

//! Calculate moments of a background-substracted TH1 histogram
class TH1BgsubIntegral: public Integral {
  public:
    TH1BgsubIntegral(TH1* hist, const Background* background, double r1, double r2);

  protected:
    virtual double GetBinContent(int bin);
    virtual double GetBinError2(int bin);
    virtual double GetBinCenter(int bin)
      { return fHist->GetBinCenter(bin); }

    const TH1* fHist;
    const Background* fBackground;
};

} // end namespace Fit
} // end namespace HDTV

#endif
