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

#include "InterpolationBg.hh"

#include <cmath>

#include <iostream>

#include <TError.h>
#include <TF1.h>
#include <TH1.h>
#include <TVirtualFitter.h>

#include "Math/Polynomial.h"
#include "Math/Interpolator.h"

#include "Util.hh"

namespace HDTV {
namespace Fit {

InterpolationBg::InterpolationBg(int bgdeg) 
	:fInter(ROOT::Math::Interpolation::kCSPLINE){
  fBgDeg = bgdeg;
  fChisquare = std::numeric_limits<double>::quiet_NaN();
}

InterpolationBg::InterpolationBg(const InterpolationBg &src)
    : 	fBgRegions(src.fBgRegions), fBgDeg(src.fBgDeg),
	fInter(ROOT::Math::Interpolation::kCSPLINE),
      	fChisquare(src.fChisquare), fCovar(src.fCovar)
{
  //! Copy constructor
  if (src.fFunc != nullptr) {
    fFunc = std::make_unique<TF1>(GetFuncUniqueName("b", this).c_str(), this,
                                   &InterpolationBg::_Eval, src.fFunc->GetXmin(),
                                   src.fFunc->GetXmax(), fBgDeg + 1, "InterpolationBg",
                                   "_Eval");

    for (int i = 0; i <= fBgDeg; i++) {
      fFunc->SetParameter(i, src.fFunc->GetParameter(i));
      fFunc->SetParError(i, src.fFunc->GetParError(i));
    }
  }
}

InterpolationBg &InterpolationBg::operator=(const InterpolationBg &src) {
  //! Assignment operator

  // Handle self assignment
  if (this == &src) {
    return *this;
  }

  fBgRegions = src.fBgRegions;
  fBgDeg = src.fBgDeg;
  fChisquare = src.fChisquare;
  fCovar = src.fCovar;
  fInter = src.fInter;

  fFunc = std::make_unique<TF1>(GetFuncUniqueName("b", this).c_str(), this,
                                 &InterpolationBg::_Eval, src.fFunc->GetXmin(),
                                 src.fFunc->GetXmax(), fBgDeg + 1, "InterpolationBg",
                                 "_Eval");

  for (int i = 0; i <= fBgDeg; i++) {
    fFunc->SetParameter(i, src.fFunc->GetParameter(i));
    fFunc->SetParError(i, src.fFunc->GetParError(i));
  }

  return *this;
}

void InterpolationBg::Fit(TH1 &hist) {

  // Need to cast background region centers and mean values into 
  // std::vector or array to be able to call ROOT::Math:Interpolator.
  // It would be more efficient to store the background regions like
  // this from the beginning, but it was decided to follow the convention
  // of the PolyBg class.
  std::vector<double> x;
  x.reserve(fBgRegions.size());
  std::vector<double> y;
  y.reserve(fBgRegions.size());

  for(auto &bgReg : fBgRegions){
	double denominator = 0.;
	double numerator = 0.;
	double weight = 0.;
	
	// TH1 bins start at 1. Bin 0 is reserved as an underflow bin.
	// This is in contrast to the conventions of C++.
	// However, since the background regions are determined elsewhere
	// in the code using a TH1 histogram, the following code assumes
	// that this has been taken care of.
	for(int i = floor(bgReg.limit.first); i < ceil(bgReg.limit.second); ++i){
		weight = 1./pow(hist.GetBinError(i), 2);
		numerator += hist.GetBinContent(i)*weight;
		denominator += weight;
	}
	bgReg.weighted_mean = numerator/denominator;
	bgReg.weighted_mean_uncertainty = 1./sqrt(denominator);
	x.push_back(bgReg.center);
	y.push_back(bgReg.weighted_mean);
  }

  // Interpolate the background regions
  fInter.SetData(x, y);
  fFunc = std::make_unique<TF1>(GetFuncUniqueName("b", this).c_str(), this,
		                 &InterpolationBg::_Eval,
				 x[0], x[fBgRegions.size()-1],
				 2*fBgDeg, "InterpolationBg", "_Eval");

  fFunc->SetChisquare(0.);
  unsigned int index = 0;
  for(auto bgReg : fBgRegions){
    fFunc->SetParameter(2*index, bgReg.center);
    fFunc->SetParError(2*index, hist.GetBinWidth(hist.GetBin(bgReg.center)));
    fFunc->SetParameter(2*index+1, bgReg.weighted_mean);
    fFunc->SetParError(2*index+1, bgReg.weighted_mean_uncertainty);
    ++index;
  }
}

bool InterpolationBg::Restore(const TArrayD &values, const TArrayD &errors,
                     double ChiSquare) {
  return true;
}

void InterpolationBg::AddRegion(double p1, double p2) {

  //  In contrast to the polynomial fits, overlapping background
  //  regions are treated separately.

  BgReg bgRegion = {std::minmax(p1, p2), 0.5*(p1+p2), 0.};

  if(!fBgRegions.size()){
	fBgRegions.push_back(bgRegion);
  } else{
	std::list<BgReg>::iterator iter;	
	iter = fBgRegions.begin();
	while(iter != fBgRegions.end()){
		if(bgRegion.center < (*iter).center){
			fBgRegions.insert(iter, bgRegion);
			break;
		}
		++iter;
		if(iter==fBgRegions.end()){
			fBgRegions.push_back(bgRegion);
		}
	}
  }
}

double InterpolationBg::_Eval(double *x, double *p) {
	// Even if the TF1 object is only defined on a finite interval,
	// HDTV sometimes tries to call it with values outside of this interval
	// (for example when the displayed function is updated),
	// which causes an input domain error by ROOT::Math::GSLInterpolator::Eval().
	// It is not exactly clear why this happens, maybe due to rounding errors,
	// but the following if-branch prevents these errors in a straightforward way.
	if(x[0] <= fFunc->GetXmin() || x[0] >= fFunc->GetXmax())
		return 0.;
  	return fInter(x, p);
}

double InterpolationBg::EvalError(double x) const {
  return 0.;
}

} // end namespace Fit
} // end namespace HDTV
