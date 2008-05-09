/*
 * gSpec - a viewer for gamma spectra
 *  Copyright (C) 2006  Norbert Braun <n.braun@ikp.uni-koeln.de>
 *
 * This file is part of gSpec.
 *
 * gSpec is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * gSpec is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
 * for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with gSpec; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
 * 
 */

#ifndef __GSDisplayFunc_h__
#define __GSDisplayFunc_h__

#include <TF1.h>
#include "GSDisplayObj.h"

class GSDisplayFunc : public GSDisplayObj {
  public:
  	GSDisplayFunc(const TF1 *func, int col = defaultColor);
  	~GSDisplayFunc();
  	
  	inline TF1 *GetFunc()  { return fFunc; }
  	inline double Eval(double x)  { return fFunc->Eval(x); }
  	
  	inline double GetMinCh(void) { double min, max; fFunc->GetRange(min, max); return min; }
    inline double GetMaxCh(void) { double min, max; fFunc->GetRange(min, max); return max; }
  	
  private:
  	TF1 *fFunc;
};

#endif


