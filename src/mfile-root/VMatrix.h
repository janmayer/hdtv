#ifndef __VMATRIX_H__
#define __VMATRIX_H__

#include "MFileHist.h"
#include <list>
#include <TH1.h>

class VMatrix {
  public:
    VMatrix(MFileHist *hist, int level);
  
    inline void AddCutRegion(int c1, int c2) { AddRegion(fCutRegions, c1, c2); }
    inline void AddBgRegion(int c1, int c2) { AddRegion(fBgRegions, c1, c2); }
    void ResetRegions() { fCutRegions.clear(); fBgRegions.clear(); }
  
    TH1 *Cut(const char *histname, const char *histtitle);
  
  private:
    void AddRegion(std::list<int> &reglist, int c1, int c2);
 
    MFileHist *fMatrix;
    int fLevel;
    std::list<int> fCutRegions, fBgRegions;
};

#endif
