/*
 * Copyright (c) 1992-2008, Stefan Esser <se@ikp.uni-koeln.de>
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *      * Redistributions of source code must retain the above copyright notice,
 *        this list of conditions and the following disclaimer.
 *      * Redistributions in binary form must reproduce the above copyright
 *        notice, this list of conditions and the following disclaimer in the
 *        documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.
 * IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/*
 * This code was derived from the matop package, the license of which is
 * reproduced above.
 *
 * Adapted for HDTV by Norbert Braun, 2010.
 */

/*
 * matop_conv: Copyright by
 *      Stefan Esser
 *      Institute for Nuclear Physics
 *      University of Cologne, Germany
 *
 */

/* Description:
 *
 * program to convert between different matrix file formats without
 * changing the contents of the file (except rounding, depending on
 * the precision and range of the data representations)
 */

#include "matop_conv.h"
#include <stdlib.h>
#include <string.h>

static int mcopyint(MFILE *dst, MFILE *src, int op);
static int mcopyflt(MFILE *dst, MFILE *src, int op);
static int mcopydbl(MFILE *dst, MFILE *src, int op);

struct cache_int_t {
  int *buf;
  int size, lines, columns;
  int level, col, cachecols;
  MFILE *mat;
};
struct cache_int_t cache_int = {NULL};

static int mgetint_col(MFILE *mat, int *buf, int level, int line, int col, int num) {
  if (mat != cache_int.mat) {
    int size;
    int columns = mat->columns;
    int lines = mat->lines;
    int cachecols = (int)(MBUFSIZE / (lines * sizeof(*cache_int.buf)));
    if (cachecols < 1)
      cachecols = 1;
    if (cachecols > columns)
      cachecols = columns;

    size = lines * cachecols;

    if (size > cache_int.size) {
      cache_int.size = 0;
      if (cache_int.buf)
        free(cache_int.buf);
      cache_int.buf = (int *)malloc(size * sizeof(*cache_int.buf));
      if (cache_int.buf)
        cache_int.size = size;
    }
    cache_int.mat = mat;
    cache_int.cachecols = cachecols;
    cache_int.level = -1;
    cache_int.lines = lines;
    cache_int.columns = columns;
  }

  if (level != cache_int.level || col < cache_int.col || col >= cache_int.col + cache_int.cachecols) {

    int n;
    int l;
    int *p = cache_int.buf;

    cache_int.level = -1;
    n = cache_int.cachecols;
    if (col + n > cache_int.columns)
      n = cache_int.columns - col;

    for (l = 0; l < cache_int.lines; l++) {
      int nread;
      nread = mgetint(mat, p, level, l, col, n);
      if (nread != n)
        return -1;
      p += cache_int.cachecols;
    }
    cache_int.level = level;
    cache_int.col = col;
  }
  {
    int i;
    int *p = cache_int.buf + (line * cache_int.cachecols + col - cache_int.col);

    for (i = 0; i < num; i++) {
      *buf++ = *p;
      p += cache_int.cachecols;
    }
  }
  return num;
}

/* ======================================================================== */
struct cache_flt_t {
  float *buf;
  int size, lines, columns;
  int level, col, cachecols;
  MFILE *mat;
};
struct cache_flt_t cache_flt = {NULL};

static int mgetflt_col(MFILE *mat, float *buf, int level, int line, int col, int num) {
  if (mat != cache_flt.mat) {
    int size;
    int columns = mat->columns;
    int lines = mat->lines;
    int cachecols = (int)(MBUFSIZE / (lines * sizeof(*cache_flt.buf)));
    if (cachecols < 1)
      cachecols = 1;
    if (cachecols > columns)
      cachecols = columns;

    size = lines * cachecols;

    if (size > cache_flt.size) {
      cache_flt.size = 0;
      if (cache_flt.buf)
        free(cache_flt.buf);
      cache_flt.buf = (float *)malloc(size * sizeof(*cache_flt.buf));
      if (cache_flt.buf)
        cache_flt.size = size;
    }
    cache_flt.mat = mat;
    cache_flt.cachecols = cachecols;
    cache_flt.level = -1;
    cache_flt.lines = lines;
    cache_flt.columns = columns;
  }

  if (level != cache_flt.level || col < cache_flt.col || col >= cache_flt.col + cache_flt.cachecols) {

    int n;
    int l;
    float *p = cache_flt.buf;

    cache_flt.level = -1;
    n = cache_flt.cachecols;
    if (col + n > cache_flt.columns)
      n = cache_flt.columns - col;

    for (l = 0; l < cache_flt.lines; l++) {
      int nread;
      nread = mgetflt(mat, p, level, l, col, n);
      if (nread != n)
        return -1;
      p += cache_flt.cachecols;
    }
    cache_flt.level = level;
    cache_flt.col = col;
  }
  {
    int i;
    float *p = cache_flt.buf + (line * cache_flt.cachecols + col - cache_flt.col);

    for (i = 0; i < num; i++) {
      *buf++ = *p;
      p += cache_flt.cachecols;
    }
  }
  return num;
}

/* ======================================================================== */
struct cache_dbl_t {
  double *buf;
  int size, lines, columns;
  int level, col, cachecols;
  MFILE *mat;
};
struct cache_dbl_t cache_dbl = {NULL};

static int mgetdbl_col(MFILE *mat, double *buf, int level, int line, int col, int num) {
  if (mat != cache_dbl.mat) {
    int size;
    int columns = mat->columns;
    int lines = mat->lines;
    int cachecols = (int)(MBUFSIZE / (lines * sizeof(*cache_dbl.buf)));
    if (cachecols < 1)
      cachecols = 1;
    if (cachecols > columns)
      cachecols = columns;

    size = lines * cachecols;

    if (size > cache_dbl.size) {
      cache_dbl.size = 0;
      if (cache_dbl.buf)
        free(cache_dbl.buf);
      cache_dbl.buf = (double *)malloc(size * sizeof(*cache_dbl.buf));
      if (cache_dbl.buf)
        cache_dbl.size = size;
    }
    cache_dbl.mat = mat;
    cache_dbl.cachecols = cachecols;
    cache_dbl.level = -1;
    cache_dbl.lines = lines;
    cache_dbl.columns = columns;
  }

  if (level != cache_dbl.level || col < cache_dbl.col || col >= cache_dbl.col + cache_dbl.cachecols) {

    int n;
    int l;
    double *p = cache_dbl.buf;

    cache_dbl.level = -1;
    n = cache_dbl.cachecols;
    if (col + n > cache_dbl.columns)
      n = cache_dbl.columns - col;

    for (l = 0; l < cache_dbl.lines; l++) {
      int nread;
      nread = mgetdbl(mat, p, level, l, col, n);
      if (nread != n)
        return -1;
      p += cache_dbl.cachecols;
    }
    cache_dbl.level = level;
    cache_dbl.col = col;
  }
  {
    int i;
    double *p = cache_dbl.buf + (line * cache_dbl.cachecols + col - cache_dbl.col);

    for (i = 0; i < num; i++) {
      *buf++ = *p;
      p += cache_dbl.cachecols;
    }
  }
  return num;
}

/* ======================================================================== */

int matop_conv(MFILE *dst, MFILE *src, int op) {

  switch (src->filetype) {
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
    return mcopyint(dst, src, op);

  case MAT_LF4:
  case MAT_HF4:
  case MAT_VAXF:
    return mcopyflt(dst, src, op);

  case MAT_LF8:
  case MAT_HF8:
  case MAT_VAXG:
  case MAT_TXT:
    return mcopydbl(dst, src, op);
  }
  return -1;
}

void matop_conv_free_cache(void) {
  if (cache_int.buf)
    free(cache_int.buf);
  memset(&cache_int, 0, sizeof(cache_int));

  if (cache_flt.buf)
    free(cache_flt.buf);
  memset(&cache_flt, 0, sizeof(cache_flt));

  if (cache_dbl.buf)
    free(cache_dbl.buf);
  memset(&cache_dbl, 0, sizeof(cache_dbl));
}

static int mcopyint(MFILE *dst, MFILE *src, int op) {

  int sc = src->columns;
  int dc = dst->columns;

  int *sbuf = NULL;
  int *dbuf = NULL;

  int err = 0;

  dbuf = (int *)malloc(dc * sizeof(*dbuf));

  if (op == MAT_SYMM) {
    sbuf = (int *)malloc(sc * sizeof(*sbuf));
  } else {
    sbuf = dbuf;
  }

  if (sbuf && dbuf) {
    int v, l;
    int vmax = src->levels;
    int lmax = src->lines;

    /* For asymmetric matrices, columns and rows are exchanged */
    if (op == MAT_TRANS) {
      lmax = src->columns;
    }

    for (v = 0; !err && v < vmax; v++) {
      for (l = 0; !err && l < lmax; l++) {

        if (op == MAT_CONV || op == MAT_SYMM) {
          if (mgetint(src, sbuf, v, l, 0, sc) != sc)
            err = -1;
        }

        if (op == MAT_TRANS || op == MAT_SYMM) {
          if (mgetint_col(src, dbuf, v, 0, l, dc) != dc)
            err = -1;
        }

        if (op == MAT_SYMM) {
          int c;
          for (c = 0; c < sc; c++)
            dbuf[c] += sbuf[c];
        }

        if (!err && mputint(dst, dbuf, v, l, 0, dc) != dc)
          err = -1;
      }
    }
  } else {
    err = -1;
  }

  if (mflush(dst) != 0)
    err = -1;

  if (dbuf)
    free(dbuf);
  if (op == MAT_SYMM && sbuf)
    free(sbuf);

  return err;
}

static int mcopyflt(MFILE *dst, MFILE *src, int op) {

  int sc = src->columns;
  int dc = dst->columns;

  float *sbuf = NULL;
  float *dbuf = NULL;

  int err = 0;

  dbuf = (float *)malloc(dc * sizeof(*dbuf));

  if (op == MAT_SYMM) {
    sbuf = (float *)malloc(sc * sizeof(*sbuf));
  } else {
    sbuf = dbuf;
  }

  if (sbuf && dbuf) {
    int v, l;
    int vmax = src->levels;
    int lmax = src->lines;

    for (v = 0; !err && v < vmax; v++) {
      for (l = 0; !err && l < lmax; l++) {

        if (op == MAT_CONV || op == MAT_SYMM) {
          if (mgetflt(src, sbuf, v, l, 0, sc) != sc)
            err = -1;
        }

        if (op == MAT_TRANS || op == MAT_SYMM) {
          if (mgetflt_col(src, dbuf, v, 0, l, dc) != dc)
            err = -1;
        }

        if (op == MAT_SYMM) {
          int c;
          for (c = 0; c < sc; c++)
            dbuf[c] += sbuf[c];
        }

        if (mputflt(dst, dbuf, v, l, 0, dc) != dc)
          err = -1;
      }
    }
  } else {
    err = -1;
  }

  if (mflush(dst) != 0)
    err = -1;

  if (dbuf)
    free(dbuf);
  if (op == MAT_SYMM && sbuf)
    free(sbuf);

  return err;
}

static int mcopydbl(MFILE *dst, MFILE *src, int op) {

  int sc = src->columns;
  int dc = dst->columns;

  double *sbuf = NULL;
  double *dbuf = NULL;

  int err = 0;

  dbuf = (double *)malloc(dc * sizeof(*dbuf));

  if (op == MAT_SYMM) {
    sbuf = (double *)malloc(sc * sizeof(*sbuf));
  } else {
    sbuf = dbuf;
  }

  if (sbuf && dbuf) {
    int v, l;
    int vmax = src->levels;
    int lmax = src->lines;

    for (v = 0; !err && v < vmax; v++) {
      for (l = 0; !err && l < lmax; l++) {

        if (op == MAT_CONV || op == MAT_SYMM) {
          if (mgetdbl(src, sbuf, v, l, 0, sc) != sc)
            err = -1;
        }

        if (op == MAT_TRANS || op == MAT_SYMM) {
          if (mgetdbl_col(src, dbuf, v, 0, l, dc) != dc)
            err = -1;
        }

        if (op == MAT_SYMM) {
          int c;
          for (c = 0; c < sc; c++)
            dbuf[c] += sbuf[c];
        }

        if (mputdbl(dst, dbuf, v, l, 0, dc) != dc)
          err = -1;
      }
    }
  } else {
    err = -1;
  }

  if (mflush(dst) != 0)
    err = -1;

  if (dbuf)
    free(dbuf);
  if (op == MAT_SYMM && sbuf)
    free(sbuf);

  return err;
}
