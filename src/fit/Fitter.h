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
 
#ifndef __Fitter_h__
#define __Fitter_h__

#include "Param.h"

namespace HDTV {
namespace Fit {

// Common base class for all different fitters
// Right now, it only handles parameter management
class Fitter {
  public:
    Fitter();
    Param AllocParam();
    Param AllocParam(double ival);
    inline bool IsFinal() { return fFinal; }
    
  protected:
    int fNumParams;
    bool fFinal;
    
    void SetParameter(TF1& func, Param& param, double ival=0.0);
};

} // end namespace Fit
} // end namespace HDTV

#endif
