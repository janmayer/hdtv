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
 
#ifndef __CoMCA_h__
#define __CoMCA_h__

namespace CoMCA {

class Device {
  public:
    Device();
    ~Device();
    
    int StartAcq(int channel);
    int StopAcq(int channel);
    
    // ReadSpec
    int ClearSpec(int channel);
    
    unsigned int GetSerial();
    unsigned int GetFirmwareVersion();
    
    int SetNumBins(int channel, int nbins);
    int GetNumBins(int channel);
    
    static const int RET_SUCCESS;     // Success
    static const int RET_ERR_COMCA;   // libCoMCA error (unspecified)
    static const int RET_ERR_INVALID; // Device is invalid
  
  private:
    ComcaDev *fMCA;
    bool fValid;
}

} // end namespace CoMCA
