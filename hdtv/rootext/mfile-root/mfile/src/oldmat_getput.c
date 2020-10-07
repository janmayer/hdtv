/*
 * oldmat_getput.c
 */
/*
 * Copyright (c) 1992-2008, Stefan Esser <se@ikp.uni-koeln.de>
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 *	* Redistributions of source code must retain the above copyright notice,
 *	  this list of conditions and the following disclaimer.
 * 	* Redistributions in binary form must reproduce the above copyright notice,
 * 	  this list of conditions and the following disclaimer in the documentation
 * 	  and/or other materials provided with the distribution.
 *
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
 * OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */
#include <string.h>

#include "getputint.h"
#include "oldmat_getput.h"

#define fpos(s) (((level * mat->lines + line) * mat->columns + col) * (s))

#define tri_pos(l, c) (((l * (l + 1)) >> 1) + c)

#define fpos_t(s) ((level * tri_pos(mat->lines, 0) + tri_pos(line, col)) * (s))

int32_t le4_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return getle4(mat->ap, buffer, fpos(4), num);
}

int32_t le4_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return putle4(mat->ap, buffer, fpos(4), num);
}

int32_t le2_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return getle2(mat->ap, buffer, fpos(2), num);
}

int32_t le2_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return putle2(mat->ap, buffer, fpos(2), num);
}

int32_t le2s_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return getle2s(mat->ap, buffer, fpos(2), num);
}

int32_t he4_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return gethe4(mat->ap, buffer, fpos(4), num);
}

int32_t he4_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return puthe4(mat->ap, buffer, fpos(4), num);
}

int32_t he2_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return gethe2(mat->ap, buffer, fpos(2), num);
}

int32_t he2s_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return gethe2s(mat->ap, buffer, fpos(2), num);
}

int32_t he2_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return puthe2(mat->ap, buffer, fpos(2), num);
}

/*----------------------------------------------------------------------*/

int32_t le4t_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  int32_t ndata, nzero;
  int32_t res;

  ndata = line + 1 - col;
  if (ndata < 0)
    ndata = 0;
  if (ndata > num)
    ndata = num;
  nzero = num - ndata;

  if ((res = getle4(mat->ap, buffer, fpos_t(4), (unsigned)ndata)) < ndata)
    return res;
  memset(buffer + ndata, 0, nzero * sizeof(*buffer));

  return num;
}

int32_t le4t_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  int32_t ndata;
  int32_t res;
  int32_t i;

  ndata = line + 1 - col;
  if (ndata < 0)
    ndata = 0;
  if (ndata > num)
    ndata = num;

  if ((res = putle4(mat->ap, buffer, fpos_t(4), (unsigned)ndata)) < ndata)
    return res;

  for (i = ndata; i < num; i++) {
    if (*(buffer + i) != 0)
      return i;
  }

  return num;
}

int32_t le2t_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  int32_t ndata, nzero;
  int32_t res;

  ndata = line + 1 - col;
  if (ndata < 0)
    ndata = 0;
  if (ndata > num)
    ndata = num;
  nzero = num - ndata;

  if ((res = getle2(mat->ap, buffer, fpos_t(2), (unsigned)ndata)) < ndata)
    return res;
  memset(buffer + ndata, 0, nzero * sizeof(*buffer));

  return num;
}

int32_t le2t_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  int32_t ndata;
  int32_t res;
  int32_t i;

  ndata = line + 1 - col;
  if (ndata < 0)
    ndata = 0;
  if (ndata > num)
    ndata = num;

  if ((res = putle2(mat->ap, buffer, fpos_t(2), (unsigned)ndata)) < ndata)
    return res;

  for (i = ndata; i < num; i++) {
    if (*(buffer + i) != 0)
      return i;
  }

  return num;
}

int32_t he4t_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  int32_t ndata, nzero;
  int32_t res;

  ndata = line + 1 - col;
  if (ndata < 0)
    ndata = 0;
  if (ndata > num)
    ndata = num;
  nzero = num - ndata;

  if ((res = gethe4(mat->ap, buffer, fpos_t(4), (unsigned)ndata)) < ndata)
    return res;
  memset(buffer + ndata, 0, nzero * sizeof(*buffer));

  return num;
}

int32_t he4t_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  int32_t ndata;
  int32_t res;
  int32_t i;

  ndata = line + 1 - col;
  if (ndata < 0)
    ndata = 0;
  if (ndata > num)
    ndata = num;

  if ((res = puthe4(mat->ap, buffer, fpos_t(4), (unsigned)ndata)) < ndata)
    return res;

  for (i = ndata; i < num; i++) {
    if (*(buffer + i) != 0)
      return i;
  }

  return num;
}

int32_t he2t_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  int32_t ndata, nzero;
  int32_t res;

  ndata = line + 1 - col;
  if (ndata < 0)
    ndata = 0;
  if (ndata > num)
    ndata = num;
  nzero = num - ndata;

  if ((res = gethe2(mat->ap, buffer, fpos_t(2), (unsigned)ndata)) < ndata)
    return res;
  memset(buffer + ndata, 0, nzero * sizeof(*buffer));

  return num;
}

int32_t he2t_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  int32_t ndata;
  int32_t res;
  int32_t i;

  ndata = line + 1 - col;
  if (ndata < 0)
    ndata = 0;
  if (ndata > num)
    ndata = num;

  if ((res = puthe2(mat->ap, buffer, fpos_t(2), (unsigned)ndata)) < ndata)
    return res;

  for (i = ndata; i < num; i++) {
    if (*(buffer + i) != 0)
      return i;
  }

  return num;
}

/*----------------------------------------------------------------------*/

int32_t lf4_get(MFILE *mat, float *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return getle4(mat->ap, (int32_t *)buffer, fpos(4), num);
}

int32_t lf4_put(MFILE *mat, float *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return putle4(mat->ap, (int32_t *)buffer, fpos(4), num);
}

int32_t hf4_get(MFILE *mat, float *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return gethe4(mat->ap, (int32_t *)buffer, fpos(4), num);
}

int32_t hf4_put(MFILE *mat, float *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return puthe4(mat->ap, (int32_t *)buffer, fpos(4), num);
}

/*----------------------------------------------------------------------*/

int32_t lf8_get(MFILE *mat, double *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return getle8(mat->ap, (int32_t *)buffer, fpos(8), num);
}

int32_t lf8_put(MFILE *mat, double *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return putle8(mat->ap, (int32_t *)buffer, fpos(8), num);
}

int32_t hf8_get(MFILE *mat, double *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return gethe8(mat->ap, (int32_t *)buffer, fpos(8), num);
}

int32_t hf8_put(MFILE *mat, double *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  return puthe8(mat->ap, (int32_t *)buffer, fpos(8), num);
}
