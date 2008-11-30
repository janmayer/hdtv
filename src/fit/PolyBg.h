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
 
/* Polynomial background fitter
 * Supports fitting the background in several non-connected regions.
 */
 
#ifndef __PolyBg_h__
#define __PolyBg_h__

#include <TF1.h>
#include <TH1.h>
#include <list>

namespace HDTV {
namespace Fit {

class PolyBg {
  public:
    PolyBg();
    TF1 *Fit(TH1 *hist);
    void AddRegion(double p1, double p2);
    double EvalRegion(double *x, double *p);
    double Eval(double *x, double *p);

  private:
    std::list<double> fBgRegions;
    int fBgDeg;
};

} // end namespace Fit
} // end namespace HDTV

#endif
