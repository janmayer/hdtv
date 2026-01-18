/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2026  The HDTV development team (see file AUTHORS)
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

#include <algorithm>
#include <cstdint>
#include <memory>

#include <mfile.h>

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

const char *MatOp::GetErrorString(int error_nr) {
  if (error_nr < 0 || error_nr > MAX_ERR) {
    error_nr = ERR_UNKNOWN;
  }

  return ErrDesc[error_nr];
}

namespace {
template <typename T,
          // Using mget_ & mput_ to distinguish from definitions of mfile.h
          int32_t (*mget_)(MFILE *, T *, int32_t, int32_t, int32_t, int32_t),
          int32_t (*mput_)(MFILE *, T *, int32_t, int32_t, int32_t, int32_t)>
int ProjectGeneric(MFILE *dstx, MFILE *dsty, unsigned int level, MFILE *src) {
  minfo info;
  mgetinfo(src, &info);
  if (level >= info.levels) {
    return MatOp::ERR_PROJ_FAIL;
  }

  auto lbuf = std::make_unique<T[]>(info.columns);
  auto prx = dstx ? std::make_unique<T[]>(info.columns) : nullptr;
  auto pry = dsty ? std::make_unique<T[]>(info.lines) : nullptr;

  for (uint32_t l = 0; l < info.lines; l++) {
    if (static_cast<uint32_t>(mget_(src, lbuf.get(), level, l, 0, info.columns)) != info.columns) {
      return MatOp::ERR_PROJ_FAIL;
    }

    if (prx) {
      for (uint32_t c = 0; prx && c < info.columns; c++) {
        prx[c] += lbuf[c];
      }
    }

    if (pry) {
      T sum = 0;
      for (uint32_t c = 0; c < info.columns; c++) {
        sum += lbuf[c];
      }
      pry[l] += sum;
    }
  }

  int err = MatOp::ERR_SUCCESS;
  if (prx && static_cast<uint32_t>(mput_(dstx, prx.get(), level, 0, 0, info.columns)) != info.columns) {
    err = MatOp::ERR_PROJ_FAIL;
  }

  if (pry && static_cast<uint32_t>(mput_(dsty, pry.get(), level, 0, 0, info.lines)) != info.lines) {
    err = MatOp::ERR_PROJ_FAIL;
  }
  return err;
}
} // namespace

int MatOp::Project(const char *src_fname, const char *prx_fname, const char *pry_fname) {
  int err = ERR_SUCCESS;

  MFILE *src_matrix = nullptr;
  MFILE *prx_matrix = nullptr;
  MFILE *pry_matrix = nullptr;

  src_matrix = mopen(src_fname, "r");
  if (src_matrix == nullptr) {
    err = ERR_SRC_OPEN;
    goto exit;
  }

  minfo src_info;
  mgetinfo(src_matrix, &src_info);
  if (src_info.levels > 2) {
    err = ERR_PROJ_FAIL;
    goto exit;
  }

  if (prx_fname != nullptr && *prx_fname != '\0') {
    prx_matrix = mopen(prx_fname, "w");
    if (prx_matrix == nullptr) {
      err = ERR_PRX_OPEN;
      goto exit;
    }

    minfo prx_info;
    mgetinfo(prx_matrix, &prx_info);

    prx_info.levels = src_info.levels;
    prx_info.lines = 1;
    prx_info.columns = src_info.columns;

    if (msetinfo(prx_matrix, &prx_info)) {
      err = ERR_PRX_FMT;
      goto exit;
    }
  }

  if (pry_fname != nullptr && *pry_fname != '\0') {
    pry_matrix = mopen(pry_fname, "w");
    if (pry_matrix == nullptr) {
      err = ERR_PRY_OPEN;
      goto exit;
    }

    minfo pry_info;
    mgetinfo(pry_matrix, &pry_info);

    pry_info.levels = src_info.levels;
    pry_info.lines = 1;
    pry_info.columns = src_info.lines;

    if (msetinfo(pry_matrix, &pry_info)) {
      err = ERR_PRY_FMT;
      goto exit;
    }
  }

  // Projection of level 0 and 1. src_info.levels is <= 2
  for (uint32_t l = 0; l < src_info.levels; l++) {
    switch (src_matrix->filetype) {
    case MAT_LE2:
    case MAT_LE4:
    case MAT_HE2:
    case MAT_HE4:

    case MAT_LE2T:
    case MAT_LE4T:
    case MAT_HE2T:
    case MAT_HE4T:

    case MAT_SHM:
    case MAT_LC:
    case MAT_MATE:
    case MAT_TRIXI:
      err = ProjectGeneric<int, mgetint, mputint>(prx_matrix, pry_matrix, l, src_matrix);
      break;
    case MAT_LF4:
    case MAT_HF4:
    case MAT_VAXF:
      err = ProjectGeneric<float, mgetflt, mputflt>(prx_matrix, pry_matrix, l, src_matrix);
      break;
    case MAT_LF8:
    case MAT_HF8:
    case MAT_VAXG:
    case MAT_TXT:
      err = ProjectGeneric<double, mgetdbl, mputdbl>(prx_matrix, pry_matrix, l, src_matrix);
      break;
    default:
      err = ERR_PROJ_FAIL;
      goto exit;
    }

    if (err != ERR_SUCCESS) {
      break;
    }
  }

exit:
  // using mclose on a nullptr has no effect
  mclose(src_matrix);
  mclose(prx_matrix);
  mclose(pry_matrix);

  return err;
}

namespace {
// This function is implemented in this way because the default matrix type of libmfile is MAT_LC,
// which is a line-compressed format. This format does not allow writes to random positions.
// Only (sequential) writes of full lines are possible. Otherwise the matrix file will contain garbage.
template <typename T,
          // Using mget_ & mput_ to distinguish from definitions of mfile.h
          int32_t (*mget_)(MFILE *, T *, int32_t, int32_t, int32_t, int32_t),
          int32_t (*mput_)(MFILE *, T *, int32_t, int32_t, int32_t, int32_t)>
int TransposeGeneric(MFILE *dst_matrix, MFILE *src_matrix) {
  minfo info;
  mgetinfo(src_matrix, &info);

  constexpr int32_t MAX_BUFFER_ELEMENTS = 16 * 1024 * 1024 / sizeof(T);

  int32_t buffered_dst_columns = std::max(1, MAX_BUFFER_ELEMENTS / static_cast<int32_t>(info.lines));
  auto src_buffer = std::make_unique<T[]>(buffered_dst_columns);
  auto dst_buffer = std::make_unique<T[]>(buffered_dst_columns * info.lines);

  for (int32_t level = 0; level < static_cast<int32_t>(info.levels); level++) {
    for (int32_t column = 0; column < static_cast<int32_t>(info.columns); column += buffered_dst_columns) {

      int32_t cc = std::min(buffered_dst_columns, static_cast<int32_t>(info.columns) - column);

      for (int32_t line = 0; line < static_cast<int32_t>(info.lines); line++) {
        if (mget_(src_matrix, &src_buffer[0], level, line, column, cc) != cc) {
          return MatOp::ERR_TRANS_FAIL;
        }
        for (auto c = 0; c < buffered_dst_columns; c++) {
          dst_buffer[(c * info.lines) + line] = src_buffer[c];
        }
      }

      for (auto c = 0; c < cc; c++) {
        if (mput_(dst_matrix, &dst_buffer[c * info.lines], level, column + c, 0, info.lines) !=
            static_cast<int32_t>(info.lines)) {
          return MatOp::ERR_TRANS_FAIL;
        }
      }
    }
  }

  return MatOp::ERR_SUCCESS;
}
} // namespace

int MatOp::Transpose(const char *src_fname, const char *dst_fname) {
  int err = ERR_SUCCESS;

  // All MFILE* are initialized to have defined behavior when exiting early
  MFILE *src_matrix = nullptr;
  MFILE *dst_matrix = nullptr;

  src_matrix = mopen(src_fname, "r");
  if (src_matrix == nullptr) {
    err = ERR_SRC_OPEN;
    goto exit;
  }

  dst_matrix = mopen(dst_fname, "w");
  if (dst_matrix == nullptr) {
    err = ERR_TRANS_OPEN;
    goto exit;
  }

  minfo src_info;
  minfo dst_info;

  mgetinfo(src_matrix, &src_info);
  mgetinfo(dst_matrix, &dst_info);

  dst_info.levels = src_info.levels;
  dst_info.lines = src_info.columns;
  dst_info.columns = src_info.lines;
  if (msetinfo(dst_matrix, &dst_info)) {
    err = ERR_TRANS_FMT;
    goto exit;
  }

  switch (src_matrix->filetype) {
  case MAT_LE2:
  case MAT_LE4:
  case MAT_HE2:
  case MAT_HE4:

  case MAT_LE2T:
  case MAT_LE4T:
  case MAT_HE2T:
  case MAT_HE4T:

  case MAT_SHM:
  case MAT_LC:
  case MAT_MATE:
  case MAT_TRIXI:
    err = TransposeGeneric<int, mgetint, mputint>(dst_matrix, src_matrix);
    break;
  case MAT_LF4:
  case MAT_HF4:
  case MAT_VAXF:
    err = TransposeGeneric<float, mgetflt, mputflt>(dst_matrix, src_matrix);
    break;
  case MAT_LF8:
  case MAT_HF8:
  case MAT_VAXG:
  case MAT_TXT:
    err = TransposeGeneric<double, mgetdbl, mputdbl>(dst_matrix, src_matrix);
    break;
  default:
    err = ERR_TRANS_FAIL;
  }

exit:
  // using mclose on a nullpointer has no effect
  mclose(src_matrix);
  mclose(dst_matrix);

  return err;
}
