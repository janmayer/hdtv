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

#include "MatOp.hh"

#include <iostream>

#include "MFileRoot.hh"
#include "matop/matop_adjust.h"
#include "matop/matop_conv.h"
#include "matop/matop_project.h"

const int MatOp::ERR_SUCCESS = 0;
const int MatOp::ERR_UNKNOWN = 1;
const int MatOp::ERR_SRC_OPEN = 2;
const int MatOp::ERR_PRX_OPEN = 3;
const int MatOp::ERR_PRX_FMT = 4;
const int MatOp::ERR_PRY_OPEN = 5;
const int MatOp::ERR_PRY_FMT = 6;
const int MatOp::ERR_PROJ_FAIL = 7;
const int MatOp::ERR_TRANS_OPEN = 8;
const int MatOp::ERR_TRANS_FMT = 9;
const int MatOp::ERR_TRANS_FAIL = 10;
const int MatOp::MAX_ERR = 10;

const char *MatOp::ErrDesc[] = {
    "Success",                                      // ERR_SUCCESS
    "Unknown error",                                // ERR_UNKNOWN
    "Failed to open input file",                    // ERR_SRC_OPEN
    "Failed to open output file for x projection",  // ERR_PRX_OPEN
    "Incompatible formats in x projection",         // ERR_PRX_FMT
    "Failed to open output file for y projection",  // ERR_PRY_OPEN
    "Incompatible formats in y projection",         // ERR_PRY_FMT
    "Projection failed",                            // ERR_PROJ_FAIL
    "Failed to open output file for transposition", // ERR_TRANS_OPEN
    "Incompatible formats in transposition",        // ERR_TRANS_FMT
    "Transposition failed"                          // ERR_TRANS_FAIL
};

int MatOp::Project(const char *src_fname, const char *prx_fname,
                   const char *pry_fname) {
  if (prx_fname && !(*prx_fname))
    prx_fname = 0;
  if (pry_fname && !(*pry_fname))
    pry_fname = 0;

  MFile in_matrix(src_fname, "r");
  if (in_matrix.IsZombie())
    return ERR_SRC_OPEN;

  // std::cout << "Info: input format is " << mgetfmt(in_matrix, NULL) <<
  // std::endl;

  MFile out_prx(prx_fname, "w");
  if (out_prx.IsZombie())
    return ERR_PRX_OPEN;

  if (!out_prx.IsNull()) {
    if (matop_adjustfmts_prx(out_prx, in_matrix) != 0)
      return ERR_PRX_FMT;
  }

  MFile out_pry(pry_fname, "w");
  if (out_pry.IsZombie())
    return ERR_PRY_OPEN;

  if (!out_pry.IsNull()) {
    if (matop_adjustfmts_pry(out_pry, in_matrix) != 0)
      return ERR_PRY_FMT;
  }

  if (matop_proj(out_prx, out_pry, in_matrix) != 0)
    return ERR_PROJ_FAIL;

  return ERR_SUCCESS;
}

int MatOp::Transpose(const char *src_fname, const char *dst_fname) {
  MFile in_matrix(src_fname, "r");
  if (in_matrix.IsZombie())
    return ERR_SRC_OPEN;

  // std::cout << "Info: input format is " << mgetfmt(in_matrix, NULL) <<
  // std::endl;

  MFile out_matrix(dst_fname, "w");
  if (out_matrix.IsZombie())
    return ERR_TRANS_OPEN;

  if (matop_adjustfmts_trans(out_matrix, in_matrix) != 0)
    return ERR_TRANS_FMT;

  // std::cout << "Info: output format is " << mgetfmt(out_matrix, NULL) <<
  // std::endl;

  if (matop_conv(out_matrix, in_matrix, MAT_TRANS) != 0)
    return ERR_TRANS_FAIL;

  matop_conv_free_cache();

  return ERR_SUCCESS;
}

const char *MatOp::GetErrorString(int error_nr) {
  if (error_nr < 0 || error_nr > MAX_ERR)
    error_nr = ERR_UNKNOWN;

  return ErrDesc[error_nr];
}
