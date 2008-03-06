#ifndef __MTViewer_h__
#define __MTViewer_h__

#include <TH2.h>
#include <TGFrame.h>
#include <TGStatusBar.h>
#include "MTView.h"

class MTViewer : public TGMainFrame {
  public:
    MTViewer(UInt_t w, UInt_t h, TH2 *mat, const char *title);
    ~MTViewer();
    
    ClassDef(MTViewer, 1)
    
  private:
    MTView *fView;
    TGStatusBar *fStatusBar;
};

#endif
