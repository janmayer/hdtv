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

#ifndef __VMatrix_h__
#define __VMatrix_h__

#include "MFileHist.h"
#include <list>
#include <TH1.h>
#include <cmath>

class VMatrix {
  public:
    VMatrix(MFileHist *hist, int level);
  
    inline void AddCutRegion(int c1, int c2) { AddRegion(fCutRegions, c1, c2); }
    inline void AddBgRegion(int c1, int c2) { AddRegion(fBgRegions, c1, c2); }
    void ResetRegions() { fCutRegions.clear(); fBgRegions.clear(); }
    inline int Ch2Bin(double ch)  // convert channel to bin number
      { return (int) ceil(ch - 0.5); }

    TH1 *Cut(const char *histname, const char *histtitle);
  
  private:
    void AddRegion(std::list<int> &reglist, int c1, int c2);
 
    MFileHist *fMatrix;
    int fLevel;
    std::list<int> fCutRegions, fBgRegions;
};

#endif
