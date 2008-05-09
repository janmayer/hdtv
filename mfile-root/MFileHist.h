#ifndef __MFILESPEC_H__
#define __MFILESPEC_H__

#ifndef __CINT__
#include <mfile.h>
#else
typedef unsigned int u_int;
#endif

#include <TH1.h>

class MFileHist {
  public:
    MFileHist();
    ~MFileHist();
    
    int Open(char *fname);
    int Close();
    
    inline int GetFileType()   { return fInfo ? fInfo->filetype : MAT_INVALID; }
    inline u_int GetNLevels()  { return fInfo ? fInfo->levels : 0; }
    inline u_int GetNLines()   { return fInfo ? fInfo->lines : 0; }
    inline u_int GetNColumns() { return fInfo ? fInfo->columns : 0; }
    
    template <class histType>
    histType *ToTH1(char *name, char *title, int level, int line);
    
    TH1 *FillTH1(TH1 *hist, int level, int line);
    
    TH1D *ToTH1D(char *name, char *title, int level, int line);
	TH1I *ToTH1I(char *name, char *title, int level, int line);
    
  private:
#ifndef __CINT__
    MFILE *fHist;
    minfo *fInfo;
    
    static const int kSuccess = 0;
    static const int kFailure = -1;
#endif
};

#endif
