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

#include "DisplaySpec.h"
#include <TROOT.h>
#include <Riostream.h>

#include "DisplayStack.h"

namespace HDTV {
namespace Display {

DisplaySpec::DisplaySpec(const TH1 *spec, int col) : DisplayObj(col)
{
  fSpec = (TH1*) spec->Clone();
 
  //cout << "GSDisplaySpec constructor" << endl;

  /* Set invalid values to ensure cache is flushed at the 
	 first call to GetMax_Cached() */
  fCachedB1 = 1;
  fCachedB2 = 0;
}

DisplaySpec::~DisplaySpec(void)
{
  delete fSpec;
  //cout << "GSDisplaySpec destructor" << endl;
}

int DisplaySpec::GetRegionMaxBin(int b1, int b2)
{
  // Find the bin number of the bin between b1 and b2 (inclusive) which
  // contains the most events

  int bin, max_bin;
  double y, max_y;

  if(b1 < 0) b1 = 0;
  if(b2 > fSpec->GetNbinsX() + 1) b2 = fSpec->GetNbinsX() + 1;
  
  max_y = fSpec->GetBinContent(b1);
  max_bin = b1;

  for(bin = b1; bin <= b2; bin ++) {
	y = fSpec->GetBinContent(bin);
	if(y > max_y) {
	  max_y = y;
	  max_bin = bin;
	}
  }
  
  return max_bin;
}

DisplayStack::ObjList& DisplaySpec::GetList(DisplayStack *stack)
{
  // Return the stacks object list where this kind of object should be inserted

  return stack->fSpectra;
}

double DisplaySpec::GetRegionMax(int b1, int b2)
{
  int max_bin = GetRegionMaxBin(b1, b2);

  //return max_bin == -1 ? 0.0 : fSpec->GetBinContent(max_bin);
  return fSpec->GetBinContent(max_bin);
}

/* Gets the maximum count between bin b1 and bin b2, inclusive.
   Employes caching to save time during scrolling operations. 

   NOTE: For the caching to be effective, use this function ONLY for
   scrolling operations.
*/
double DisplaySpec::GetMax_Cached(int b1, int b2)
{
  int bin, newBin;
  double max, newMax=-1.0;

  if(b1 < 0) b1 = 0;
  if(b2 > GetNbinsX() + 1) b2 = GetNbinsX() + 1;

  if(b2 < b1)
	return -1;

  if(fCachedB2 < b1 || fCachedB1 > b2 || fCachedB1 > fCachedB2) {
	fCachedB1 = b1;
	fCachedB2 = b2;
	fCachedMaxBin = GetRegionMaxBin(b1, b2);
	fCachedMax = GetBinContent(fCachedMaxBin);
  } else {
	if(b1 < fCachedB1) {
	  newBin = GetRegionMaxBin(b1, fCachedB1);
	  newMax = GetBinContent(newBin);

	  fCachedB1 = b1;
	}

	if(b2 > fCachedB2) {
	  bin = GetRegionMaxBin(fCachedB2, b2);
	  max = GetBinContent(bin);

	  if(max > newMax) {
		newMax = max;
		newBin = bin;
	  }

	  fCachedB2 = b2;
	}

	if(newMax >= fCachedMax) {
	  fCachedMaxBin = newBin;
	  fCachedMax = newMax;
	} else if(fCachedMaxBin < b1 || fCachedMaxBin > b2) {
	  bin = GetRegionMaxBin(b1 > fCachedB1 ? b1 : fCachedB1,
			         	    b2 < fCachedB2 ? b2 : fCachedB2);

	  max = GetBinContent(bin);

	  if(max > newMax) {
		fCachedMax = max;
		fCachedMaxBin = bin;
	  } else {
		fCachedMax = newMax;
		fCachedMaxBin = newBin;
	  }

	  fCachedB1 = b1;
	  fCachedB2 = b2;
	}
  }

  return fCachedMax;
}

} // end namespace Display
} // end namespace HDTV
