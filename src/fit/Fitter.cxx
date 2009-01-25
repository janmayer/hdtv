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
 
#include "Fitter.h"

namespace HDTV {
namespace Fit {

Fitter::Fitter()
{
  fNumParams = 0;
  fFinal = false;
}

Param Fitter::AllocParam()
{
  return Param::Free(fNumParams++);
}

Param Fitter::AllocParam(double ival)
{
  return Param::Free(fNumParams++, ival);
}

void Fitter::SetParameter(TF1& func, Param& param, double ival)
{
  if(!param.HasIVal())
    param.SetValue(ival);
  
  if(param.IsFree())
    func.SetParameter(param._Id(), param._Value());
}

} // end namespace Fit
} // end namespace HDTV
