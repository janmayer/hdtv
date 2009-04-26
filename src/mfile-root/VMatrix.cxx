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

#include <TArrayD.h>
#include "VMatrix.h"

VMatrix::VMatrix(MFileHist *hist, int level)
{
  fMatrix = hist;
  fLevel = level;
}

void VMatrix::AddRegion(std::list<int> &reglist, int l1, int l2)
{
  std::list<int>::iterator iter, next;
  bool inside = false;
  int min, max;
  
  min = TMath::Min(l1, l2);
  max = TMath::Max(l1, l2);
  
  // Perform clipping
  if(max < 0 || min >= fMatrix->GetNColumns() || fMatrix->GetNColumns() == 0)
    return;
  min = TMath::Max(min, 0);
  max = TMath::Min(max, (int) fMatrix->GetNColumns() - 1);

  iter = reglist.begin();
  while(iter != reglist.end() && *iter < min) {
    inside = !inside;
    iter++;
  }
  
  if(!inside) {
    iter = reglist.insert(iter, min);
    iter++;
  }
  
  while(iter != reglist.end() && *iter < max) {
    inside = !inside;
    next = iter; next++;
    reglist.erase(iter);
    iter = next;
  }
  
  if(!inside) {
    reglist.insert(iter, max);
  }
}

class MFileReadException { };

TH1 *VMatrix::Cut(const char *histname, const char *histtitle)
{
  int l, l1, l2;   // lines
  int c, cols = fMatrix->GetNColumns();   // columns
  std::list<int>::iterator iter;
  int nCut=0, nBg=0;   // total number of cut and background lines
  

  // Sanity checks
  if(fLevel < 0 || fLevel >= fMatrix->GetNLevels())
  	return NULL;
  	
  if(fCutRegions.empty())
    return NULL;
  
  // Temporary buffer
  TArrayD buf(cols);
  
  // Sum of cut lines
  TArrayD sum(cols);
  sum.Reset(0.0);
  
  // Sum of background lines
  TArrayD bg(cols);
  bg.Reset(0.0);
  
  try {
    // Add up all cut lines
    iter = fCutRegions.begin();
    while(iter != fCutRegions.end()) {
      l1 = *iter++;
      l2 = *iter++;
      for(l=l1; l<=l2; l++) {
        if(!fMatrix->FillBuf1D(buf.GetArray(), fLevel, l))
          throw MFileReadException();

        for(c=0; c<cols; c++) {
          // Bad for speed; overloaded operator[] checks array bounds
          sum[c] += buf[c];
        }
      
        nCut++;
      }
    }
     
    // Add up all background lines
    iter = fBgRegions.begin();
    while(iter != fBgRegions.end()) {
      l1 = *iter++;
      l2 = *iter++;
      for(l=l1; l<=l2; l++) {
        if(!fMatrix->FillBuf1D(buf.GetArray(), fLevel, l))
          throw MFileReadException();

        for(c=0; c<cols; c++) {
          // Bad for speed; overloaded operator[] checks array bounds
          bg[c] += buf[c];
        }
      
        nBg++;
      }
    }
  }
  catch(MFileReadException&) {
    return NULL;
  }
  
  double bgFac = (double) nCut / nBg;
  TH1D *hist = new TH1D(histname, histtitle, cols, -0.5, (double) cols - 0.5);
  for(c=0; c<cols; c++) {
    hist->SetBinContent(c+1, sum[c] - bg[c] * bgFac);
  }
  
  return hist;
}
