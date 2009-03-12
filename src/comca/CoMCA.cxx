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
 
#include "CoMCA.h"
#include <comca.h>

namespace CoMCA {

const int Device::RET_SUCCESS = 0;
const int Device::RET_ERR_COMCA = -1;
const int Device::RET_ERR_INVALID = -10;

int Device::StartAcq(int channel)
{
  if(fValid)
    return comca_start_acq(fMCA, channel);
  else
    return RET_ERR_INVALID;
}

int Device::StopAcq(int channel)
{
  if(fValid)
    return comca_stop_acq(fMCA, channel);
  else
    return RET_ERR_INVALID;
}

int Device::ClearSpec(int channel)
{
  if(fValid)
    return comca_start_acq(fMCA, channel);
  else
    return RET_ERR_INVALID;
}   

unsigned int Device::GetSerial()
{
  if(fValid)
    return comca_get_serial(fMCA);
  else
    return RET_ERR_INVALID;
}

unsigned int Device::GetFirmwareVersion()
{
  if(fValid)
    return comca_get_firmware_version(fMCA);
  else
    return RET_ERR_INVALID;
}   

int Device::SetNumBins(int channel, int nbins)
{
  if(fValid)
    return comca_set_num_channels(fMCA, channel, nbins);
  else
    return RET_ERR_INVALID;
}

int Device::GetNumBins(int channel)
{
  if(fValid)
    return comca_get_num_channels(fMCA, channel);
  else
    return RET_ERR_INVALID;
}

} // end namespace CoMCA
