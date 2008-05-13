#ifndef __MFILESPEC_H__
#define __MFILESPEC_H__

#ifndef __CINT__
#include <mfile.h>
#else
typedef unsigned int u_int;
#endif

#include <TH1.h>
#include <TH2.h>

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
    
    double *FillBuf1D(double *buf, int level, int line);
    
    template <class histType>
    histType *ToTH1(const char *name, const char *title, int level, int line);
    
    TH1 *FillTH1(TH1 *hist, int level, int line);
    
    TH1D *ToTH1D(const char *name, const char *title, int level, int line);
	TH1I *ToTH1I(const char *name, const char *title, int level, int line);
	
	template <class histType>
    histType *ToTH2(const char *name, const char *title, int level);
    
    TH2 *FillTH2(TH2 *hist, int level);
    
    TH2D *ToTH2D(const char *name, const char *title, int level);
	TH2I *ToTH2I(const char *name, const char *title, int level);
    
  private:
#ifndef __CINT__
    MFILE *fHist;
    minfo *fInfo;
    
    static const int kSuccess = 0;
    static const int kFailure = -1;
#endif
};

#endif
