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
 
/* Base class for background fitters
 */
 
#ifndef __Background_h__
#define __Background_h__

#include <TF1.h>

namespace HDTV {
namespace Fit {

class Background
{
  public:
    Background()  { }
    virtual ~Background()  { }
    virtual Background* Clone() const
      { return new Background(); }
    virtual double Eval(double x)
      { return 0.0; }
    virtual TF1* GetFunc()
      { return NULL; }
    virtual double GetMin()
      { return std::numeric_limits<double>::quiet_NaN(); }
    virtual double GetMax()
      { return std::numeric_limits<double>::quiet_NaN(); }
    
  private:
    Background(const Background& b) { }
};

} // end namespace Fit
} // end namespace HDTV

#endif
