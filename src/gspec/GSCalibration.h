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

#include <vector>
#include <TAxis.h>

class GSCalibration {
  public:
   	GSCalibration(double cal0)
  	  { SetCal(cal0); }

   	GSCalibration(double cal0, double cal1)
  	  { SetCal(cal0, cal1); }

   	GSCalibration(double cal0, double cal1, double cal2)
  	  { SetCal(cal0, cal1, cal2); }

  	GSCalibration(double cal0, double cal1, double cal2, double cal3)
  	  { SetCal(cal0, cal1, cal2, cal3); }

  	GSCalibration(std::vector<double> cal)
  	  { SetCal(cal); }
  	
	void SetCal(double cal0);
	void SetCal(double cal0, double cal1);
	void SetCal(double cal0, double cal1, double cal2);
	void SetCal(double cal0, double cal1, double cal2, double cal3);
	void SetCal(std::vector<double> cal);
	
    double Ch2E(double ch);
    double dEdCh(double ch);
    double E2Ch(double e);
    
    void Apply(TAxis *axis, int nbins);
    
  private:
    std::vector<double> fCal;
    std::vector<double> fCalDeriv;
    void UpdateDerivative();
};

#endif

