#ifndef __VMATRIX_H__
#define __VMATRIX_H__

#include "MFileHist.h"
#include <TH1.h>

class VMatrix {
  public:
    VMatrix(MFileHist *hist, int level);
    ~VMatrix();
  
    inline void AddCutRegion(int c1, int c2) { AddRegion(fCutRegions, c1, c2); }
    inline void AddBgRegion(int c1, int c2) { AddRegion(fBgRegions, c1, c2); }
    void ResetRegions() { fCutRegions.clear(); fBgRegions.clear(); }
  
    TH1 *Cut();
  
  private:
    void AddRegion(list<int> reglist, int c1, int c2)
 
    MFileHist *fMatrix;
    list<int} fCutRegions, fBgRegions;
}

#endif
