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
 
#ifndef __Param_h__
#define __Param_h__

#include <TF1.h>

namespace HDTV {
namespace Fit {

class Param {
  public:
    static inline Param Fixed(double val) { return Param(-1, val, false); }
    static inline Param Free(int id, double ival) { return Param(id, ival, true); }
    inline Param() { }
    
    inline bool IsFree() { return fFree; }
    inline double Value(double *p) { return fFree ? p[fId] : fValue; }
    double Value(TF1 *func);
    double Error(TF1 *func);
    int _Id() { return fId; }
    double _Value() { return fValue; }
    
  private:
    Param(int id, double value, bool free);
    bool fFree;
    int fId;
    double fValue;
};

} // end namespace Fit
} // end namespace HDTV

#endif
