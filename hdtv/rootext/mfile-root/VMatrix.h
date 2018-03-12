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

#include <cmath>

#include <list>

#include <TH1.h>
#include <TH2.h>

#include "MFileHist.h"

// VMatrix and RMatrix should be moved to a different module, as they are not
// related to MFile...

/*
  Cut  ^
  Axis |
       |
       |+++++++++++++++++++
       |+++++++++++++++++++
       |+++++++++++++++++++
       |    |    |    |
       |    |    |    |
       |    v    v    v
       +------------------->
               Projection axis
*/
  
//! A ``virtual matrix'', i.e. a matrix that is not necessarily stored in memory  
class VMatrix {
  public:
    VMatrix() : fFail(false) { };
    virtual ~VMatrix() {};
  
    inline void AddCutRegion(int c1, int c2) { AddRegion(fCutRegions, c1, c2); }
    inline void AddBgRegion(int c1, int c2) { AddRegion(fBgRegions, c1, c2); }
    void ResetRegions() { fCutRegions.clear(); fBgRegions.clear(); }
    
    TH1 *Cut(const char *histname, const char *histtitle);
    
    // Cut axis info
    virtual int FindCutBin(double x) = 0;
    virtual int GetCutLowBin() = 0;
    virtual int GetCutHighBin() = 0;
    
    // Projection axis info
    virtual double GetProjXmin() = 0;
    virtual double GetProjXmax() = 0;
    virtual int GetProjXbins() = 0;
    
    virtual void AddLine(TArrayD& dst, int l) = 0;
    
    inline bool Failed() { return fFail; }
  
  private:
    void AddRegion(std::list<int> &reglist, int c1, int c2);
    std::list<int> fCutRegions, fBgRegions;
    
  protected:
    bool fFail;
};

//! ROOT TH2-backed VMatrix
class RMatrix: public VMatrix {
  public:
    enum ProjAxis_t { PROJ_X, PROJ_Y };
  
    RMatrix(TH2* hist, ProjAxis_t paxis);
    virtual ~RMatrix() {};
        
    virtual int FindCutBin(double x)
       { TAxis *a = (fProjAxis == PROJ_X) ? fHist->GetYaxis() : fHist->GetXaxis();
         return a->FindBin(x); }
       
    virtual int GetCutLowBin()  { return 1; }
    virtual int GetCutHighBin()
       { return (fProjAxis == PROJ_X) ? fHist->GetNbinsY() : fHist->GetNbinsX(); }
    
    virtual double GetProjXmin()
       { TAxis *a = (fProjAxis == PROJ_X) ? fHist->GetXaxis() : fHist->GetYaxis();
         return a->GetXmin(); }
         
    virtual double GetProjXmax()
       { TAxis *a = (fProjAxis == PROJ_X) ? fHist->GetXaxis() : fHist->GetYaxis();
         return a->GetXmax(); }
         
    virtual int GetProjXbins()
       { return (fProjAxis == PROJ_X) ? fHist->GetNbinsX() : fHist->GetNbinsY(); }
       
    virtual void AddLine(TArrayD& dst, int l);
    
  private:
    TH2* fHist;
    ProjAxis_t fProjAxis;
};

//! MFile-histogram-backed VMatrix
class MFMatrix: public VMatrix {
  public:
    MFMatrix(MFileHist *mat, unsigned int level);
    virtual ~MFMatrix() {};
    virtual int FindCutBin(double x)  // convert channel to bin number
      { return (int) ceil(x - 0.5); }

    virtual int GetCutLowBin()   { return 0; }
    virtual int GetCutHighBin()  { return fMatrix->GetNLines() - 1; }
    
    virtual double GetProjXmin() { return -0.5; }
    virtual double GetProjXmax() { return fMatrix->GetNColumns() - .5; }
    virtual int GetProjXbins()   { return fMatrix->GetNColumns(); }
    
    virtual void AddLine(TArrayD& dst, int l);

  private:
    MFileHist *fMatrix;
    unsigned int fLevel;
    TArrayD fBuf;
};

#endif
