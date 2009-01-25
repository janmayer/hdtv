/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2009  Norbert Braun <n.braun@ikp.uni-koeln.de>
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

#ifndef __DisplayObj_h__
#define __DisplayObj_h__

#include <list>
#include <TGGC.h>
#include "Calibration.h"
#include "Painter.h"

namespace HDTV {
namespace Display {

class DisplayStack;
class View1D;

class DisplayObj {
  friend class Painter;

  public:
  	DisplayObj(int col);
  	virtual ~DisplayObj();
  	
	void SetCal(const Calibration& cal) { fCal = cal; Update(); };
    inline double Ch2E(double ch) { return fCal ? fCal.Ch2E(ch) : ch; }
    inline double E2Ch(double e) { return fCal ? fCal.E2Ch(e) : e; }
    
    double GetMaxE();
    double GetMinE();
    double GetERange();
    virtual inline double GetMinCh() { return 0.0; }
    virtual inline double GetMaxCh() { return 0.0; }
    inline double GetCenterCh() { return (GetMinCh() + GetMaxCh()) / 2.0; }
    
    inline bool IsVisible() { return fVisible; }
    inline void Show() { fVisible = true; Update(); }
    inline void Hide() { fVisible = false; Update(); }
    
    void SetColor(int col);
    
    /* Management functions */
    void Draw(View1D *view);
    void Remove(View1D *view);
    void ToTop(View1D *view);
    void ToBottom(View1D *view);
    
    void Draw(DisplayStack *stack);
    void Remove(DisplayStack *stack);
    void ToTop(DisplayStack *stack);
    void ToBottom(DisplayStack *stack);

    void Remove();
    void ToTop();
    void ToBottom();
    
    virtual void PaintRegion(UInt_t x1, UInt_t x2, Painter& painter) { }
    
    // HDTV::Display:: required for CINT
    virtual std::list<HDTV::Display::DisplayObj *>& GetList(DisplayStack *stack);
    
    static const int DEFAULT_COLOR;
    
  protected:
    inline TGGC *GetGC() { return fGC; }
    void Update();
  	
  private:
    void InitGC(int col);
  
    Calibration fCal;
    TGGC *fGC;
    std::list<DisplayStack*> fStacks;
    bool fVisible;
};

} // end namespace Display
} // end namespace HDTV

#endif
