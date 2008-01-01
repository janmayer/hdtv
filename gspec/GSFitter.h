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
 
#ifndef __GSFitter_h__
#define __GSFitter_h__

#include <TF1.h>
#include <TH1.h>
#include <list>

class GSFitter {
 public:
  GSFitter(double r1, double r2);
  void AddPeak(double pos);
  void AddBgRegion(double p1, double p2);
  TF1 *Fit(TH1 *hist, TF1 *bgFunc=NULL);
  TF1 *FitBackground(TH1 *hist);
  inline void SetLeftTails(double t) { fLeftTails = t; }
  inline void SetRightTails(double t) { fRightTails = t; }
  
 private:
  double fMin, fMax;
  double fLeftTails, fRightTails;
  std::list<double> fBgRegions;
  std::list<double> fPeaks;
  int fNumPeaks;
};

#endif
  
