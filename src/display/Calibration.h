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

#ifndef __Calibration_h__
#define __Calibration_h__

#include <vector>
#include <TAxis.h>

namespace HDTV {

class Calibration {
  public:
    Calibration() { }
  
   	Calibration(double cal0)
  	  { SetCal(cal0); }

   	Calibration(double cal0, double cal1)
  	  { SetCal(cal0, cal1); }

   	Calibration(double cal0, double cal1, double cal2)
  	  { SetCal(cal0, cal1, cal2); }

  	Calibration(double cal0, double cal1, double cal2, double cal3)
  	  { SetCal(cal0, cal1, cal2, cal3); }

  	Calibration(const std::vector<double>& cal)
  	  { SetCal(cal); }
  	  
  	Calibration(const TArrayD& cal)
  	  { SetCal(cal); }
  	
	void SetCal(double cal0);
	void SetCal(double cal0, double cal1);
	void SetCal(double cal0, double cal1, double cal2);
	void SetCal(double cal0, double cal1, double cal2, double cal3);
	void SetCal(const std::vector<double>& cal);
	void SetCal(const TArrayD& cal);
	
    inline operator bool() const { return !fCal.empty(); }
	inline const std::vector<double>& GetCoeffs() const { return fCal; }
	
    double Ch2E(double ch) const;
    double dEdCh(double ch) const;
    double E2Ch(double e) const;
    
    void Apply(TAxis *axis, int nbins);
    
  private:
    std::vector<double> fCal;
    std::vector<double> fCalDeriv;
    void UpdateDerivative();
};

} // end namespace HDTV

#endif
