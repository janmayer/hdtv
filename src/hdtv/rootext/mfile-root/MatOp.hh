/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2010  The HDTV development team (see file AUTHORS)
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

#ifndef __MatOp_h__
#define __MatOp_h__

class MatOp {
public:
  static int Project(const char *src_fname, const char *prx_fname, const char *pry_fname = nullptr);
  static int Transpose(const char *src_fname, const char *dst_fname);

  static const char *GetErrorString(int error_nr);

  const static int ERR_SUCCESS;
  const static int ERR_UNKNOWN;
  const static int ERR_SRC_OPEN;
  const static int ERR_PRX_OPEN;
  const static int ERR_PRX_FMT;
  const static int ERR_PRY_OPEN;
  const static int ERR_PRY_FMT;
  const static int ERR_PROJ_FAIL;
  const static int ERR_TRANS_OPEN;
  const static int ERR_TRANS_FMT;
  const static int ERR_TRANS_FAIL;
  const static int MAX_ERR;

  const static char *ErrDesc[];
};

#endif
