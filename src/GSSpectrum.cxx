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

/*
 * A note about the bin contents in the ROOT spectrum classes:
 * Bin 0: underflow bin
 * Bin 1...nbinsx: actual spectrum
 * Bin nbinxs+1: overflow bin
 *
 * GetBinContent(x) returns the content of the underflow bin for
 * x < 0 and the content of the overflow bin for x > nbinsx.
 * 
 */

#include "GSSpectrum.h"
#include <Riostream.h>

GSSpectrum::GSSpectrum(TH1 *spec) 
{
  fSpec = spec;

  // Start with a trivial calibration
  fA = 0.0;
  fB = 1.0;
  fC = 0.0;
}

GSSpectrum::~GSSpectrum(void) { 
	cout << "GSSpectrum destructor" << endl;
}


