#include "MTViewer.h"

MTViewer::MTViewer(UInt_t w, UInt_t h, TH2 *mat, const char *title)
  : TGMainFrame(gClient->GetRoot(), w, h)
{
  fView = new MTView(this, w-4, h-4, mat);
  AddFrame(fView, new TGLayoutHints(kLHintsExpandX | kLHintsExpandY, 0,0,0,0));
  
  fStatusBar = new TGStatusBar(this, 10, 16);
  AddFrame(fStatusBar, new TGLayoutHints(kLHintsExpandX, 0,0,0,0));
  
  fView->SetStatusBar(fStatusBar);

  SetWindowName(title);
  MapSubwindows();
  Resize(GetDefaultSize());
  MapWindow();
}

MTViewer::~MTViewer()
{
  Cleanup();
}
