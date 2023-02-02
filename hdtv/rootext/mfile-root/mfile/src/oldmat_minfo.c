/*
 * oldmat_minfo.c
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
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

// #include "config.h"

#include "getputint.h"
#include "maccess.h"
#include "mat_types.h"
#include "oldmat_getput.h"
#include "oldmat_minfo.h"

#define TESTBUFSIZE (4096 * 4) /* must be a power of 2 */

static void guessdatatype(MFILE *mat, uint32_t pos);
static void guesslinescols(MFILE *mat, uint32_t size);

char MAGIC_OLDMAT[] = "\nMatFmt: ";

static void guessdatatype(mat, pos) MFILE *mat;
uint32_t pos;
{
  unsigned char buf[TESTBUFSIZE];
  int32_t nread;
  int32_t n1 = 0, n2 = 0, n3 = 0, n4 = 0;
  int32_t lf4 = 0, lf8 = 0, hf4 = 0, hf8 = 0, vaxf = 0, vaxg = 0;

  uint32_t i, lim4, lim8;

  pos &= (-8);
  nread = _get(mat->ap, (char *)buf, pos, sizeof(buf));
  nread &= (-8);

  if (nread <= 0)
    return;

  for (i = 0; i < nread; i += 4) {
    uint32_t tli, thi, tvax, e;

    n1 += buf[i];
    n2 += buf[i + 1];
    n3 += buf[i + 2];
    n4 += buf[i + 3];
/* consider floating point32_t number, if within 2^-3 to 2^20 */
#define GETEXP(_n, _bits) (((_n)&0x7fff) >> (15 - (_bits)))
#define MINEXP (-3)
#define MAXEXP (20)
    tli = (buf[i + 3] << 8) + buf[i + 2];
    thi = (buf[i] << 8) + buf[i + 1];
    tvax = (buf[i + 1] << 8) + buf[i];

    e = GETEXP(tli, 8);
    if (127 + MINEXP < e && e < 127 + MAXEXP)
      lf4++;
    e = GETEXP(thi, 8);
    if (127 + MINEXP < e && e < 127 + MAXEXP)
      hf4++;
    e = GETEXP(tvax, 8);
    if (127 + MINEXP < e && e < 127 + MAXEXP)
      vaxf++;

    if (i & 4) {
      e = GETEXP(tli, 11);
      if (1023 + MINEXP < e && e < 1023 + MAXEXP)
        lf8++;
    } else {
      e = GETEXP(thi, 11);
      if (1023 + MINEXP < e && e < 1023 + MAXEXP)
        hf8++;
      e = GETEXP(tvax, 11);
      if (1023 + MINEXP < e && e < 1023 + MAXEXP)
        vaxg++;
    }
#undef GETEXP
#undef MINEXP
#undef MAXEXP
  }

  lim4 = 3 * (nread >> 4);
  lim8 = lim4 >> 1;

  mat->filetype = n1 > n4 << 3 /* looks like low endian ? */
                      ? n3 > n2 << 3                     ? MAT_LE2
                        : n1 > n4 << 12 && n2 >= n3 << 2 ? MAT_LE4
                                                         : MAT_UNKNOWN
                      : n4 > n1 << 3 /* looks like high endian ? */
                            ? n2 > n3 << 3                     ? MAT_HE2
                              : n4 > n1 << 12 && n3 >= n2 << 2 ? MAT_HE4
                                                               : MAT_UNKNOWN
                            : MAT_UNKNOWN;

  if (mat->filetype == MAT_UNKNOWN &&
      (lf4 > lim4) + (hf4 > lim4) + (vaxf > lim4) + (lf8 > lim8) + (hf8 > lim8) + (vaxg > lim8) == 1) {
    mat->filetype = lf4 > lim4    ? MAT_LF4
                    : hf4 > lim4  ? MAT_HF4
                    : vaxf > lim4 ? MAT_VAXF
                    : lf8 > lim8  ? MAT_LF8
                    : hf8 > lim8  ? MAT_HF8
                    : vaxg > lim8 ? MAT_VAXG
                                  : MAT_UNKNOWN;
  }
}

static void guesslinescols(mat, size) MFILE *mat;
uint32_t size;
{
  int32_t filetype = mat->filetype;

  if (filetype != MAT_INVALID) {
    uint32_t elems, lines, columns;

    switch (filetype) {
    case MAT_LE2:
    case MAT_HE2:
      elems = size >> 1;
      break;

    case MAT_LE4:
    case MAT_HE4:
    case MAT_LF4:
    case MAT_HF4:
    case MAT_VAXF:
      elems = size >> 2;
      break;

    case MAT_LF8:
    case MAT_HF8:
    case MAT_VAXG:
      elems = size >> 3;
      break;

    default:
      elems = 0;
      break;
    }

    columns = 0;
    if (elems == 4096 * 4096) {
      lines = 4096;
      columns = 4096;
    } else {
      lines = 1;
      while (lines <= (2 << 15)) {
        if (elems == ((lines * (lines + 1)) >> 1)) {
          columns = lines;
          switch (filetype) {
          case MAT_LE2: {
            mat->filetype = MAT_LE2T;
            break;
          }
          case MAT_LE4: {
            mat->filetype = MAT_LE4T;
            break;
          }
          case MAT_HE2: {
            mat->filetype = MAT_HE2T;
            break;
          }
          case MAT_HE4: {
            mat->filetype = MAT_HE4T;
            break;
          }
          default: {
            columns = 0;
            break;
          }
          }
          break;
        }
        lines <<= 1;
      }
      if (columns == 0) {
        lines = 1;
        columns = elems;
      }
    }

    mat->lines = lines;
    mat->columns = columns;
    mat->version = OLDMAT_STD_VERSION;
  }
}

static void checkformagic(mat, size) MFILE *mat;
int32_t size;
{
  oldmat_header omh;
  uint32_t s = sizeof(omh);
  uint32_t l = strlen(MAGIC_OLDMAT);

  if (size < s || _get(mat->ap, (char *)omh, size - s, s) != s)
    return;

  if (strncmp(omh, MAGIC_OLDMAT, l) != 0)
    return;
  msetfmt(mat, omh + l);
}

void oldmat_probe(mat) MFILE *mat;
{
  uint32_t size = mat->ap->size;

  checkformagic(mat, size);
  if (mat->filetype != MAT_UNKNOWN)
    return;

  guessdatatype(mat, (size / 3) & -TESTBUFSIZE);
  if (mat->filetype == MAT_INVALID)
    return;

  guesslinescols(mat, size);
}

void oldmat_init(mat) MFILE *mat;
{
  if (0 < mat->columns && mat->columns <= MAT_COLMAX) {
    int32_t filetype = mat->filetype;
    int32_t datatype = matproc_datatype(filetype);
    int32_t elemsize = datatype & MAT_D_SIZE;
    mgetf *getf = matproc_getf(filetype);
    mputf *putf = matproc_putf(filetype);

    mat->specinfo.i = elemsize;
    mat->version = OLDMAT_STD_VERSION;

    switch (datatype) {
    case MAT_D_I2U:
      mat->mgeti4f = getf;
      mat->mputi4f = putf;
      break;
    case MAT_D_I2S:
      mat->mgeti4f = getf;
      mat->mputi4f = putf;
      break;
    case MAT_D_I4S:
      mat->mgeti4f = getf;
      mat->mputi4f = putf;
      break;
    case MAT_D_F4:
      mat->mgetf4f = getf;
      mat->mputf4f = putf;
      mat->version = 2;
      break;
    case MAT_D_F8:
      mat->mgetf8f = getf;
      mat->mputf8f = putf;
      mat->version = 2;
      break;
    default:
      return;
      break;
    }

    mat->muninitf = oldmat_uninit;
  }
}

int32_t oldmat_uninit(mat)
MFILE *mat;
{
  if ((mat->status & MST_DIRTY) == 0)
    return 0;

  if (mat->version == 2) {
    oldmat_header omh;
    uint32_t elemsize = mat->specinfo.i;
    uint32_t matsize = mat->levels * mat->lines * mat->columns * elemsize;

    if (matsize == 0)
      return 0;

    /* Avoid writing uninitialized memory to file */
    memset(omh, 0, sizeof(omh));
#ifdef HAVE_SNPRINTF
    snprintf(omh, sizeof(omh), "%s%s\n", MAGIC_OLDMAT, mgetfmt(mat, NULL));
#else
    sprintf(omh, "%s%s\n", MAGIC_OLDMAT, mgetfmt(mat, NULL));
#endif

    if (_put(mat->ap, (char *)omh, matsize, sizeof(omh)) != sizeof(omh))
      return -1;
  }
  return 0;
}

int32_t oldmat_putinfo(MFILE *mat, minfo *info) { return 0; }
