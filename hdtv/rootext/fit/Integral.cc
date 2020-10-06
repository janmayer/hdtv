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

#include "Integral.hh"

#include <cmath>

// ClassImp(HDTV::Fit::Integral)

namespace HDTV {
namespace Fit {

double Integral::GetStdDev() {
  //! Returns the standard deviation
  //! \f[ \sigma = \sqrt{\sigma^{2}} \f]

  return std::sqrt(GetVariance());
}

double Integral::GetStdDevError() {
  //! Returns the error of the standard deviation,
  //! \f[ \Delta \sigma = \frac{\Delta \sigma^{2}}{2 \sigma} \f]
  //! calculated from the error of the variance (see CalcVarianceError())

  return GetVarianceError() / (2. * GetStdDev());
}

double Integral::GetWidth() {
  //! Returns the width,
  //! \f[ w = 2 \sqrt{2 \ln(2)} \sigma \f]
  //! For a Gaussian distribution, this corresponds to the full width at half
  //! maximum (FWHM).

  return 2. * std::sqrt(2. * std::log(2.)) * GetStdDev();
}

double Integral::GetWidthError() {
  //! Returns the error of the width,
  //! \f[ \Delta w = 2 \sqrt{2 \ln(2)} \Delta \sigma \f]

  return 2. * std::sqrt(2. * std::log(2.)) * GetStdDevError();
}

// Worker functions
double Integral::CalcIntegral() {
  //! Returns the integral
  //! \f[  N = \sum_{i=b_{1}}^{b_{2}} n_{i} \f]

  double sum = 0.0;
  for (int b = fB1; b <= fB2; b++) {
    sum += GetBinContent(b);
  }
  return sum;
}

double Integral::CalcIntegralError() {
  //! Returns the error of the integral,
  //! \f[ \Delta N = \sqrt{\sum_{i=b_{1}}^{b_{2}} (\Delta n_{i})^{2}} \f]
  //! calculated from the bin errors by Gaussian error propagation

  double sum = 0.0;
  for (int b = fB1; b <= fB2; b++) {
    sum += GetBinError2(b);
  }
  return sqrt(sum);
}

double Integral::CalcMean() {
  //! Returns the mean
  //! \f[ \bar{x} = \frac{1}{N} \sum_{i=b_{1}}^{b_{2}} x_{i} n_{i} \f]

  double sum = 0.0;
  for (int b = fB1; b <= fB2; b++) {
    double x = GetBinCenter(b);
    sum += x * GetBinContent(b);
  }
  return sum / GetIntegral();
}

double Integral::CalcMeanError() {
  //! Returns the error of the mean,
  //! \f[ \Delta \bar{x} = \frac{1}{N}   \sqrt{\sum_{i=b_{1}}^{b_{2}} (x_{i} -
  //! \bar{x})^{2} (\Delta n_{i})^{2}} \f]
  //! calculated from the bin errors by Gaussian error propagation

  double mean = GetMean();
  double sum = 0.0;
  for (int b = fB1; b <= fB2; b++) {
    double x = GetBinCenter(b);
    sum += (x - mean) * (x - mean) * GetBinError2(b);
  }
  return sqrt(sum) / GetIntegral();
}

double Integral::CalcVariance() {
  //! Returns the variance
  //! \f[ \sigma^{2} = \frac{1}{N} \sum_{i=b_{1}}^{b_{2}} (x_{i} - \bar{x})^{2}
  //! n_{i} \f]

  double mean = GetMean();

  double sum = 0.0;
  for (int b = fB1; b <= fB2; b++) {
    double x = GetBinCenter(b);
    sum += (x - mean) * (x - mean) * GetBinContent(b);
  }
  return sum / GetIntegral();
}

double Integral::CalcVarianceError() {
  //! Returns the error of the variance,
  //! \f[  \Delta \sigma^{2} = \frac{1}{N}   \sqrt{\sum_{i=b_{1}}^{b_{2}}
  //! [(x_{i} - \bar{x})^{2} - \sigma^{2}]^{2} (\Delta n_{i})^{2} } \f]
  //! calculated from the bin errors by Gaussian error propagation

  double mean = GetMean();
  double variance = GetVariance();

  double sum = 0.0;
  for (int b = fB1; b <= fB2; b++) {
    double xm = GetBinCenter(b) - mean;
    double s = xm * xm - variance;
    sum += s * s * GetBinError2(b);
  }
  return sqrt(sum) / GetIntegral();
}

double Integral::CalcRawSkewness() {
  //! Returns the "raw" skewness (i.e. the (non-standardized) third central
  //! moment)
  //! \f[ \mu_{3} = \frac{1}{N} \sum_{i=b_{1}}^{b_{2}} (x_{i} - \bar{x})^{3}
  //! n_{i} \f]

  double mean = GetMean();

  double sum = 0.0;
  for (int b = fB1; b <= fB2; b++) {
    double xm = GetBinCenter(b) - mean;
    sum += xm * xm * xm * GetBinContent(b);
  }
  return sum / GetIntegral();
}

double Integral::CalcRawSkewnessError() {
  //! Returns the error of the "raw" skewness,
  //! \f[ \Delta \mu_{3} = \frac{1}{N}   \sqrt{\sum_{i=b_{1}}^{b_{2}} [(x_{i} -
  //! \bar{x})^{3} - 3 \sigma^{2} (x_{i} - \bar{x}) - \mu_{3}]^{2} (\Delta
  //! n_{i})^{2}} \f]
  //! calculated from the bin errors by Gaussian error propagation

  double mean = GetMean();
  double variance = GetVariance();
  double rawSkewness = GetRawSkewness();

  double sum = 0.0;
  for (int b = fB1; b <= fB2; b++) {
    double xm = GetBinCenter(b) - mean;
    double s = xm * xm * xm - 3. * variance * xm - rawSkewness;
    sum += s * s * GetBinError2(b);
  }
  return sqrt(sum) / GetIntegral();
}

double Integral::CalcSkewness() {
  //! Returns the skewness (i.e. the third standardized moment)
  //! \f[ \gamma = \frac{\mu_{3}}{\sigma^{3}} \f]

  return GetRawSkewness() / pow(GetVariance(), 1.5);
}

double Integral::CalcSkewnessError() {
  //! Returns the error of the skewness,
  //! \f[ \Delta \gamma = \frac{1}{N}   \sqrt{ \sum_{i=b_{1}}^{b_{2}} \left[
  //! \frac{(x_{i} - \bar{x})^{3}}{\sigma^{3}} - 3 \frac{x_{i} -
  //! \bar{x}}{\sigma} - \frac{3}{2} \gamma \frac{(x_{i} -
  //! \bar{x})^{2}}{\sigma^{2}} - \frac{1}{2} \gamma \right]^{2} (\Delta
  //! n_{i})^{2} } \f]
  //! calculated from the bin errors by Gaussian error propagation

  double mean = GetMean();
  double skewness = GetSkewness();
  double sigma = GetStdDev();
  double sigma2 = sigma * sigma;
  double sigma3 = sigma2 * sigma;

  double sum = 0.0;
  for (int b = fB1; b <= fB2; b++) {
    double xm = GetBinCenter(b) - mean;
    double s;
    s = xm * xm * xm / sigma3;
    s -= 3. * xm / sigma;
    s -= 1.5 * skewness * xm * xm / sigma2;
    s -= 0.5 * skewness;
    sum += s * s * GetBinError2(b);
  }
  return sqrt(sum) / GetIntegral();
}

TH1Integral::TH1Integral(TH1 *hist, double r1, double r2)
    : Integral(hist->FindBin(r1), hist->FindBin(r2)), fHist(hist) {
  //! Integrate TH1 object in the region [r1, r2]. The integral is performed as
  //! a sum over histogram bins. The sum starts at the bin containing r1 and
  //! ends at the bin containing r2; these bins are included in the sum with a
  //! weight of 1.
}

BgIntegral::BgIntegral(const Background *background, double r1, double r2, TAxis *axis)
    : Integral(axis->FindBin(r1), axis->FindBin(r2)), fBackground(background), fAxis(axis) {
  //! Integrate background in the region [r1, r2]. The integral is performed as
  //! a sum over histogram bins as specified by the axis parameter. The sum
  //! starts at the bin containing r1 and ends at the bin containing r2; these
  //! bins are included in the sum with a weight of 1.
}

TH1BgsubIntegral::TH1BgsubIntegral(TH1 *hist, const Background *background, double r1, double r2)
    : Integral(hist->FindBin(r1), hist->FindBin(r2)), fHist(hist), fBackground(background) {
  //! Integrate difference between TH1 object and background  in the region
  //! [r1, r2]. The integral is performed as a sum over bins, with a binning
  //! as given by the histogram. The sum starts at the bin containing r1 and
  //! ends at the bin containing r2; these bins are included in the sum with a
  //! weight of 1.
}

double TH1BgsubIntegral::GetBinContent(int bin) {
  double xh = fHist->GetBinContent(bin);
  double xb = fBackground->Eval(fHist->GetBinCenter(bin));
  return xh - xb;
}

double TH1BgsubIntegral::GetBinError2(int bin) {
  double eh = fHist->GetBinError(bin);
  double eb = fBackground->EvalError(fHist->GetBinCenter(bin));
  return eh * eh + eb * eb;
}

} // end namespace Fit
} // end namespace HDTV
