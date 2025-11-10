/*
 * minfo.c
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
#include <ctype.h>
#include <memory.h>
#include <stddef.h>

#include "mat_types.h"
#include "mfile.h"

static char *putnum(char *p, uint32_t n, int32_t put1);
static char *putfmt(char *p, int32_t filetype);
static char *minfototxt(const char *fmt, minfo *info);

int32_t mgetinfo(MFILE *mat, minfo *info) {

  if (info == NULL)
    return -1;

  if (mat == NULL) {
    info->filetype = MAT_INVALID;
    info->version = 0;
    info->levels = 0;
    info->lines = 0;
    info->columns = 0;
    info->status = 0;
    info->name = NULL;
    info->comment = NULL;
    return -1;
  }

  info->filetype = mat->filetype;
  info->version = mat->version;
  info->levels = mat->levels;
  info->lines = mat->lines;
  info->columns = mat->columns;
  info->status = mat->status;
  info->name = mat->name;
  info->comment = mat->comment;

  return 0;
}

int32_t msetinfo(MFILE *mat, minfo *info) {

  /* check parameters and set filetype = MATINVALID in case of error */
  /* should call 'mat->msetinfof()' for sanity checks ... */

  if (mat == NULL || info == NULL)
    return -1;

  if (mat->status & MST_DIMSFIXED) { /* Dimesions of matrix are fixed */
    if (mat->lines != info->lines || mat->columns != info->columns)
      return -1;
  }

  mat->filetype = info->filetype;
  mat->version = info->version;
  mat->levels = info->levels;
  mat->lines = info->lines;
  mat->columns = info->columns;
  mat->status = (mat->status & MST_INTERN) | (info->status & MST_USER);

  return 0;
}

int32_t mtxttoinfo(char *fmt, minfo *info) {

  int32_t lev = 0;
  int32_t lin = 0;
  int32_t col = 0;
  int32_t typ = MAT_UNKNOWN;
  int32_t ver = 0;

#define skipspace(p)                                                                                                   \
  while (isspace(*p))                                                                                                  \
  (p++)
#define getnum(p, n)                                                                                                   \
  while (isdigit(*p))                                                                                                  \
  n = n * 10 + ((*p++) - '0')

  if (fmt == NULL)
    return 0;
  if (info == NULL)
    return -1;

  skipspace(fmt);

  while (isdigit(*fmt)) {
    if (lev != 0)
      return -1;
    lev = lin;
    lin = col;

    col = 0;
    getnum(fmt, col);
    if (*fmt == 'k') {
      fmt++;
      col *= 1024;
    }
    if (col == 0)
      return -1;

    if (*fmt == '.') {
      fmt++;
    } else {
      break;
    }
  }
  if (isalpha(*fmt)) {
    char fmtname[8];
    char c;
    int32_t i = 0;

    while (i < (sizeof(fmtname) - 1) && (c = *fmt) && c != ':') {
      fmtname[i] = c;
      fmt++;
      i++;
    }
    fmtname[i] = '\0';

    typ = matproc_filetype(fmtname);
    if (typ == MAT_INVALID)
      return -1;

    if (*fmt == ':') {
      fmt++;
      getnum(fmt, ver);
    }
  }
  if (*fmt != '\0' && !isspace(*fmt))
    return -1;

  if (typ != MAT_UNKNOWN) {
    info->filetype = typ;
    info->version = ver;
  }

  /*  if (info->filetype == MAT_UNKNOWN) info->filetype == MAT_STD; */

  if (col != 0) {
    info->levels = lev ? lev : 1;
    info->lines = lin ? lin : 1;
    info->columns = col ? col : 1;
  }
  return 0;
#undef skipspace
#undef getnum
}

static char *putnum(char *p, uint32_t n, int32_t put1) {

  if (n != 1 || put1) {
    char numbuf[32];
    char *revp = numbuf;

    if (n && (n % 1024 == 0)) {
      n /= 1024;
      *revp++ = 'k';
    }

    while (n) {
      char d = n % 10;
      *revp++ = d + '0';
      n /= 10;
    }

    while (revp != numbuf) {
      *p++ = *--revp;
    }
  }
  *p = '\0';

  return p;
}

static char *putfmt(char *p, int32_t filetype) {

  char *cp;

  cp = matproc_fmtname(filetype);
  while (*cp)
    *p++ = *cp++;
  *p = '\0';

  return p;
}

static char *minfototxt(const char *fmt, minfo *info) {

  static char txtbuf[127];
  char *p;

  if (fmt == NULL)
    fmt = txtbuf;
  p = (char *)fmt;

  if (info == NULL) {
    p = putfmt(p, MAT_INVALID);
  } else {
    p = putnum(p, info->levels, 0);
    if (p != fmt)
      *p++ = '.';
    p = putnum(p, info->lines, p != fmt);
    if (p != fmt)
      *p++ = '.';
    p = putnum(p, info->columns, 1);
    if (p != fmt)
      *p++ = '.';

    p = putfmt(p, info->filetype);

    if (info->version) {
      *p++ = ':';
      p = putnum(p, info->version, 1);
    }
  }

  return (char *)fmt;
}

int32_t msetfmt(MFILE *mat, const char *format) {

  minfo info;
  if (mat && format) {
    if (mgetinfo(mat, &info) != 0)
      return -1;
    if (mtxttoinfo((char *)format, &info) != 0)
      return -1;
    return msetinfo(mat, &info);
  } else {
    memset(&info, 0, sizeof(minfo));
    return mtxttoinfo((char *)format, &info);
  }
}

char *mgetfmt(MFILE *mat, char *format) {

  minfo info;

  mgetinfo(mat, &info);
  return minfototxt(format, &info);
}
