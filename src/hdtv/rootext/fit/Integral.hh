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
#include <stdexcept>

#include "Background.hh"

namespace HDTV {
namespace Fit {

//! Helper class template wrapping a cached value
template <typename T> class CachedValue {
  T value_;
  bool valid_;

public:
  CachedValue() : valid_{false} {}
  explicit CachedValue(const T &value) : value_{value}, valid_{true} {}

  explicit operator bool() const { return valid_; }

  CachedValue<T> &operator=(const T &value) {
    value_ = value;
    valid_ = true;
    return *this;
  }

  CachedValue<T> &operator=(T &&value) {
    value_ = std::move(value);
    valid_ = true;
    return *this;
  }

  T &get() {
    if (!valid_) {
      throw std::runtime_error("trying to access uncached value");
    }
    return value_;
  }

  const T &get() const {
    if (!valid_) {
      throw std::runtime_error("trying to access uncached value");
    }
    return value_;
  }

  template <typename CalcFn> T &get_or_eval(CalcFn calc) {
    if (!valid_) {
      value_ = calc();
      valid_ = true;
    }
    return value_;
  }
};

//! Helper class to calculate various statistical moments (integral, mean, ...)
//! of a histogram
class Integral {
public:
  /*! Constructor
   * \param b1 First bin in sum (inclusive)
   * \param b2 Last bin in sum (inclusive)
   */
  Integral(int b1, int b2) : fB1(b1), fB2(b2) {}
  virtual ~Integral() = default;

  //! Cached version of CalcIntegral()
  double GetIntegral() {
    return fCIntegral.get_or_eval([&]() { return CalcIntegral(); });
  }

  //! Cached version of CalcIntegralError()
  double GetIntegralError() {
    return fCIntegralError.get_or_eval([&]() { return CalcIntegralError(); });
  }

  //! Cached version of CalcMean()
  double GetMean() {
    return fCMean.get_or_eval([&]() { return CalcMean(); });
  }

  //! Cached version of CalcMeanError()
  double GetMeanError() {
    return fCMeanError.get_or_eval([&]() { return CalcMeanError(); });
  }

  //! Cached version of CalcVariance()
  double GetVariance() {
    return fCVariance.get_or_eval([&]() { return CalcVariance(); });
  }

  //! Cached version of CalcVarianceError()
  double GetVarianceError() {
    return fCVarianceError.get_or_eval([&]() { return CalcVarianceError(); });
  }

  //! Cached version of CalcRawSkewness()
  double GetRawSkewness() {
    return fCRawSkewness.get_or_eval([&]() { return CalcRawSkewness(); });
  }

  //! Cached version of CalcRawSkewnessError()
  double GetRawSkewnessError() {
    return fCRawSkewnessError.get_or_eval([&]() { return CalcRawSkewnessError(); });
  }

  //! Cached version of CalcSkewness()
  double GetSkewness() {
    return fCSkewness.get_or_eval([&]() { return CalcSkewness(); });
  }

  //! Cached version of CalcSkewnessError()
  double GetSkewnessError() {
    return fCSkewnessError.get_or_eval([&]() { return CalcSkewnessError(); });
  }

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

  CachedValue<double> fCIntegral, fCIntegralError;
  CachedValue<double> fCMean, fCMeanError;
  CachedValue<double> fCVariance, fCVarianceError;
  CachedValue<double> fCRawSkewness, fCRawSkewnessError;
  CachedValue<double> fCSkewness, fCSkewnessError;

  // ClassDef(HDTV::Fit::Integral, 0)
};

//! Calculate moments of a TH1 histogram
class TH1Integral : public Integral {
public:
  TH1Integral(TH1 *hist, double r1, double r2);

protected:
  double GetBinContent(int bin) override { return fHist->GetBinContent(bin); }

  double GetBinError2(int bin) override {
    double e = fHist->GetBinError(bin);
    return e * e;
  }

  double GetBinCenter(int bin) override { return fHist->GetBinCenter(bin); }

  const TH1 *fHist;
};

//! Calculate moments of a background function (using a user-specified binning)
class BgIntegral : public Integral {
public:
  BgIntegral(const Background *background, double r1, double r2, TAxis *axis);

protected:
  double GetBinContent(int bin) override { return fBackground->Eval(GetBinCenter(bin)); }

  double GetBinError2(int bin) override {
    double e = fBackground->EvalError(GetBinCenter(bin));
    return e * e;
  }

  double GetBinCenter(int bin) override { return fAxis->GetBinCenter(bin); }

  const Background *fBackground;
  const TAxis *fAxis;
};

//! Calculate moments of a background-substracted TH1 histogram
class TH1BgsubIntegral : public Integral {
public:
  TH1BgsubIntegral(TH1 *hist, const Background *background, double r1, double r2);

protected:
  double GetBinContent(int bin) override;
  double GetBinError2(int bin) override;
  double GetBinCenter(int bin) override { return fHist->GetBinCenter(bin); }

  const TH1 *fHist;
  const Background *fBackground;
};

} // end namespace Fit
} // end namespace HDTV

#endif
