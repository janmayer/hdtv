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
 
#include "Param.h"
 
namespace HDTV {
namespace Fit {

Param::Param(int id, double value, bool free)
{
  fId = id;
  fValue = value;
  fFree = free;
}

double Param::Value(TF1 *func)
{
  if(fFree)
    return func ? func->GetParameter(fId) : std::numeric_limits<double>::quiet_NaN();
  else
  	return fValue;
}

double Param::Error(TF1 *func)
{
  // Fixed parameters do not have a fit error
  if(fFree)
    return func ? func->GetParError(fId) : std::numeric_limits<double>::quiet_NaN();
  else
  	return 0.0;
}

} // end namespace Fit
} // end namespace HDTV
