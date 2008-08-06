/*** Test setup for scrollable matrix display ***/
#ifndef __MTView_h__
#define __MTView_h__

#include <map>
#include <stdint.h>
#include <TGX11.h>
#include <TGFrame.h>
#include <TGStatusBar.h>
#include <TH2.h>
#include <math.h>

class MTView : public TGFrame {
  public:
    MTView(const TGWindow *p, UInt_t w, UInt_t h, TH2 *mat);
    ~MTView();
    Pixmap_t RenderTile(int xoff, int yoff);
    Pixmap_t GetTile(int x, int y);
    void FlushTiles();
    void WeedTiles();
    void DoRedraw();
    void Update();
    void UpdateStatusBar();
    void ZoomFull(Bool_t update=true);
    void ZoomAroundCursor(double f, Bool_t update=true);
    double Log(double x);
    inline void SetStatusBar(TGStatusBar *sb)
      { fStatusBar = sb; }
    
    Bool_t HandleKey(Event_t *ev);
    
    /* Copied from GSViewport: Merge? */
    Bool_t HandleMotion(Event_t *ev);
    Bool_t HandleButton(Event_t *ev);
    Bool_t HandleCrossing(Event_t *ev);
    void DrawCursor(void);
    
    inline int XTileToCh(int x)
       { return (int) ceil(((double) x) / fXZoom - 0.5); }
    inline int YTileToCh(int y)
       { return (int) ceil(((double) y) / fYZoom - 0.5); }
    inline int XScrToTile(int x)
       { return x - fXTileOffset; }
    inline int YScrToTile(int y)
       { return -y + fYTileOffset; }
    inline int XScrToCh(int x)
       { return XTileToCh(XScrToTile(x)); }
    inline int YScrToCh(int y)
       { return YTileToCh(YScrToTile(y)); }
    inline int ZCtsToScr(double z)
       { return (int) (((z - fZOffset) / fZVisibleRegion) * cZColorRange); }
    /* inline void SetXVisibleRegion(double xreg)
       { fXZoom = (double) fWidth / xreg; }
    inline void SetYVisibleRegion(double yreg)
       { fYZoom = (double) fHeight / yreg; } */
    void ShiftOffset(int dX, int dY);
    inline int GetTileId(int pos)
       { return pos < 0 ? (pos / cTileSize) - 1 : pos / cTileSize; }

    void ZtoRGB(int z, int &r, int &g, int &b);
    int GetValueAtPixel(int xs, int ys);
    
  ClassDef(MTView, 1)
  
  protected:
    std::map<uint32_t, Pixmap_t> fTiles;
    double fXZoom, fYZoom;
    double fZVisibleRegion, fZOffset;
    Bool_t fLogScale;
    
    TH2 *fMatrix;
    double fMatrixMax;
    
    int fXTileOffset, fYTileOffset;
    int fXNumTiles, fYNumTiles;
    
    UInt_t fCursorX, fCursorY;
    Bool_t fCursorVisible;
    Bool_t fDragging;
    TGGC *fCursorGC;
    
    TGStatusBar *fStatusBar;
    
    static const int cZColorRange = 5 * 256;
    static const int cTileSize = 128;
};

#endif
