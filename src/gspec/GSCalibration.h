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

#ifndef __GSCalibration_h__
#define __GSCalibration_h__

class GSCalibration {
  public:
  	GSCalibration(double cal0 = 0.0, double cal1 = 1.0, double cal2 = 0.0, double cal3 = 0.0);
  	  	
	void SetCal(double cal0 = 0.0, double cal1 = 1.0, double cal2 = 0.0, double cal3 = 0.0);
    double Ch2E(double ch);
    double E2Ch(double e);
    
    inline void SetCenterCh(double ch)  { fCenterCh = ch; }
    inline double GetCenterCh()  { return fCenterCh; }
    
  private:
    double fCal[4];
    double fCenterCh;
};

#endif

