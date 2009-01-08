/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2009  Norbert Braun <n.braun@ikp.uni-koeln.de>
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

#ifndef __DisplayObj_h__
#define __DisplayObj_h__

#include <TGGC.h>
#include "Calibration.h"

namespace HDTV {
namespace Display {

class DisplayObj {
  public:
  	DisplayObj(int col);
  	~DisplayObj();
  	
    inline TGGC *GetGC() { return fGC; }
  	
	void SetCal(Calibration *cal) { fCal = cal; };
    inline double Ch2E(double ch) { return fCal ? fCal->Ch2E(ch) : ch; }
    inline double E2Ch(double e) { return fCal ? fCal->E2Ch(e) : e; }
    
    double GetMaxE();
    double GetMinE();
    double GetERange();
    virtual inline double GetMinCh() { return 0.0; }
    virtual inline double GetMaxCh() { return 0.0; }
    inline double GetCenterCh() { return (GetMinCh() + GetMaxCh()) / 2.0; }
    
    static const int DEFAULT_COLOR;
  	
  private:
    Calibration *fCal;
    TGGC *fGC;   
};

} // end namespace Display
} // end namespace HDTV

#endif
