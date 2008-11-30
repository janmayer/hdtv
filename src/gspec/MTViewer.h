#ifndef __MTViewer_h__
#define __MTViewer_h__

#include <TH2.h>
#include <TGFrame.h>
#include <TGStatusBar.h>
#include "View2D.h"

class MTViewer : public TGMainFrame {
  public:
    MTViewer(UInt_t w, UInt_t h, TH2 *mat, const char *title);
    ~MTViewer();
    
    ClassDef(MTViewer, 1)
    
  private:
    HDTV::Display::View2D *fView;
    TGStatusBar *fStatusBar;
};

#endif
