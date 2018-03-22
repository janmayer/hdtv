/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2010  The HDTV development team (see file AUTHORS)
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

#include "DisplayCut.h"

#include <TCutG.h>
#include <TMath.h>

namespace HDTV {
namespace Display {

DisplayCut::DisplayCut(const TCutG& cut, bool invertAxes)
{
    if(invertAxes)
        Init(cut.GetN(), cut.GetY(), cut.GetX());
    else
        Init(cut.GetN(), cut.GetX(), cut.GetY());
}

void DisplayCut::Init(int n, const double* x, const double* y)
{
    if(n <= 0) return;
    
    fPoints.reserve(n);
    
    fPoints.push_back(CutPoint(x[0], y[0]));
    fX1 = fX2 = x[0]; 
    fY1 = fY2 = y[0];
    
    for(int i=1; i<n; ++i) {
        fPoints.push_back(CutPoint(x[i], y[i]));
        fX1 = TMath::Min(fX1, x[i]);
        fX2 = TMath::Max(fX2, x[i]);
        fY1 = TMath::Min(fY1, y[i]);
        fY2 = TMath::Max(fY2, y[i]);
    }
}

} // end namespace Display
} // end namespace HDTV
