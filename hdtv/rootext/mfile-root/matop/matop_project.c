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

#include "matop_project.h"
#include <stdlib.h>
#include <string.h>

static int mprojint(MFILE *dstx, MFILE *dsty, unsigned int level, MFILE *src);
static int mprojflt(MFILE *dstx, MFILE *dsty, unsigned int level, MFILE *src);
static int mprojdbl(MFILE *dstx, MFILE *dsty, unsigned int level, MFILE *src);
static int matop_proj_single(MFILE *dstx, MFILE *dsty, unsigned int level, MFILE *src);

int matop_proj(MFILE *dstx, MFILE *dsty, MFILE *src) {
  int err;
  minfo info;

  mgetinfo(src, &info);

  if (info.levels > 2)
    return -1;

  err = matop_proj_single(dstx, dsty, 0, src);
  if (err != 0)
    return err;

  if (info.levels > 1)
    err = matop_proj_single(dstx, dsty, 1, src);

  return err;
}

int matop_proj_single(MFILE *dstx, MFILE *dsty, unsigned int level, MFILE *src) {

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
    return mprojint(dstx, dsty, level, src);

  case MAT_LF4:
  case MAT_HF4:
  case MAT_VAXF:
    return mprojflt(dstx, dsty, level, src);

  case MAT_LF8:
  case MAT_HF8:
  case MAT_VAXG:
  case MAT_TXT:
    return mprojdbl(dstx, dsty, level, src);
  }
  return -1;
}

static int mprojint(MFILE *dstx, MFILE *dsty, unsigned int level, MFILE *src) {

  int err = 0;
  int exitstatus = -1;
  minfo info;
  int *lbuf;
  int *prx = NULL;
  int *pry = NULL;

  int columns;
  int lines;

  mgetinfo(src, &info);
  columns = info.columns;
  lines = info.lines;
  if (level >= info.levels)
    goto errexit;

  lbuf = (int *)malloc(columns * sizeof(int));
  if (dstx)
    prx = (int *)malloc(columns * sizeof(int));
  if (dsty)
    pry = (int *)malloc(lines * sizeof(int));

  if (!lbuf || (dstx && !prx) || (dsty && !pry))
    goto errexit;

  {
    int l, c;

    if (prx)
      memset(prx, 0, columns * sizeof(int));
    if (pry)
      memset(pry, 0, lines * sizeof(int));

    for (l = 0; l < lines; l++) {
      if (mgetint(src, lbuf, level, l, 0, columns) != columns)
        goto errexit;

      if (prx) {
        for (c = 0; c < columns; c++) {
          prx[c] += lbuf[c];
        }
      }
      if (pry) {
        int sum = 0;
        for (c = 0; c < columns; c++) {
          sum += lbuf[c];
        }
        pry[l] += sum;
      }
    }
  }

  free(lbuf);

  if (prx) {
    if (mputint(dstx, prx, level, 0, 0, columns) != columns)
      err = -1;
    free(prx);
  }

  if (pry) {
    if (mputint(dsty, pry, level, 0, 0, lines) != lines)
      err = -1;
    free(pry);
  }

  exitstatus = err;

errexit:

  return exitstatus;
}

static int mprojflt(MFILE *dstx, MFILE *dsty, unsigned int level, MFILE *src) {

  int err = 0;
  int exitstatus = -1;
  minfo info;
  float *lbuf;
  float *prx = NULL;
  float *pry = NULL;

  int columns;
  int lines;

  mgetinfo(src, &info);
  columns = info.columns;
  lines = info.lines;
  if (level >= info.levels)
    goto errexit;

  lbuf = (float *)malloc(columns * sizeof(float));
  if (dstx)
    prx = (float *)malloc(columns * sizeof(float));
  if (dsty)
    pry = (float *)malloc(lines * sizeof(float));

  if (!lbuf || (dstx && !prx) || (dsty && !pry))
    goto errexit;

  {
    int l, c;

    if (prx)
      memset(prx, 0, columns * sizeof(float));
    if (pry)
      memset(pry, 0, lines * sizeof(float));

    for (l = 0; l < lines; l++) {
      if (mgetflt(src, lbuf, level, l, 0, columns) != columns)
        goto errexit;

      if (prx) {
        for (c = 0; c < columns; c++) {
          prx[c] += lbuf[c];
        }
      }
      if (pry) {
        float sum = 0;
        for (c = 0; c < columns; c++) {
          sum += lbuf[c];
        }
        pry[l] += sum;
      }
    }
  }

  free(lbuf);

  if (prx) {
    if (mputflt(dstx, prx, level, 0, 0, columns) != columns)
      err = -1;
    free(prx);
  }

  if (pry) {
    if (mputflt(dsty, pry, level, 0, 0, lines) != lines)
      err = -1;
    free(pry);
  }

  exitstatus = err;

errexit:

  return exitstatus;
}

static int mprojdbl(MFILE *dstx, MFILE *dsty, unsigned int level, MFILE *src) {

  int err = 0;
  int exitstatus = -1;
  minfo info;
  double *lbuf;
  double *prx = NULL;
  double *pry = NULL;

  int columns;
  int lines;

  mgetinfo(src, &info);
  columns = info.columns;
  lines = info.lines;
  if (level >= info.levels)
    goto errexit;

  lbuf = (double *)malloc(columns * sizeof(double));
  if (dstx)
    prx = (double *)malloc(columns * sizeof(double));
  if (dsty)
    pry = (double *)malloc(lines * sizeof(double));

  if (!lbuf || (dstx && !prx) || (dsty && !pry))
    goto errexit;

  {
    int l, c;

    if (prx)
      memset(prx, 0, columns * sizeof(double));
    if (pry)
      memset(pry, 0, lines * sizeof(double));

    for (l = 0; l < lines; l++) {
      if (mgetdbl(src, lbuf, level, l, 0, columns) != columns)
        goto errexit;

      if (prx) {
        for (c = 0; c < columns; c++) {
          prx[c] += lbuf[c];
        }
      }
      if (pry) {
        double sum = 0;
        for (c = 0; c < columns; c++) {
          sum += lbuf[c];
        }
        pry[l] += sum;
      }
    }
  }

  free(lbuf);

  if (prx) {
    if (mputdbl(dstx, prx, level, 0, 0, columns) != columns)
      err = -1;
    free(prx);
  }

  if (pry) {
    if (mputdbl(dsty, pry, level, 0, 0, lines) != lines)
      err = -1;
    free(pry);
  }

  exitstatus = err;

errexit:

  return exitstatus;
}
