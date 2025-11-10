/*
 * lc_getput.c
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
#include <errno.h>
#include <memory.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

#include "getputint.h"
#include "lc_c1.h"
#include "lc_c2.h"
#include "lc_getput.h"
#include "lc_minfo.h"
#include "maccess.h"

/* static int32_t lc_alloc(MFILE *mat, int32_t n)); */
static int32_t readline(MFILE *mat, int32_t *buffer, uint32_t line);
static int32_t writeline(MFILE *mat, int32_t *buffer, uint32_t line);
static void trycacheline(MFILE *mat, uint32_t line);

#ifdef VERIFY_COMPRESSION
static void verifycompr(lc_minfo *lci, int32_t *line, int32_t num) {

  static int32_t uncline[MAT_COLMAX];

  if (num > MAT_COLMAX)
    return;

  uncline[num - 1] = line[num - 1] - 1;

  if ((lci->uncomprf(uncline, lci->comprlinebuf, num) != num) || (memcmp(uncline, line, num * sizeof(int32_t)) != 0)) {
    uint32_t c;
    for (c = 0; c < num; c++) {
      if (uncline[c] != line[c]) {
        fprintf(stderr, "\ncompression error, aborting !!!\ncol = %d,  %d (correct %d)\n", c, uncline[c], line[c]);
        abort();
      }
    }
  }
}
#endif /* VERIFY_COMPRESSION */

static int32_t readline(MFILE *mat, int32_t *buffer, uint32_t line) {

  lc_minfo *lci = (lc_minfo *)mat->specinfo.p;

  if (lci->cachedcomprline != line) {
    amp ap = mat->ap;
    lc_poslen *poslentable = lci->poslentableptr;

    uint32_t l = poslentable[line].len;
    uint32_t p = poslentable[line].pos;

    if (l == 0)
      return 0;

    if (_get(ap, (void *)lci->comprlinebuf, p, l) == l) {
      lci->comprlinelen = l;
      lci->cachedcomprline = line;
    }
  }
  if (lci->cachedcomprline == line) {
    return lci->uncomprf(buffer, lci->comprlinebuf, mat->columns);
  }

  return -1;
}

static int32_t writeline(MFILE *mat, int32_t *buffer, uint32_t line) {

  amp ap = mat->ap;
  lc_minfo *lci = (lc_minfo *)mat->specinfo.p;

  lc_poslen *poslentable = lci->poslentableptr;

  uint32_t p = poslentable[line].pos;
  uint32_t l = poslentable[line].len;

  uint32_t fp = lci->freepos;
  uint32_t nl = lci->comprf(lci->comprlinebuf, buffer, mat->columns);
#ifdef VERIFY_COMPRESSION
  verifycompr(lci, buffer, mat->columns);
#endif
  if (nl > 0) {
    if (l + p == fp) {
      fp = p;
      l = 0;
    }
    if (l < nl) {
      l = nl;
      p = fp;
      fp += l;
    }

    if (_put(ap, (void *)lci->comprlinebuf, p, l) == l) {
      lci->freepos = fp;
      poslentable[line].len = l;
      poslentable[line].pos = p;
      return mat->columns;
    }
  }

  return -1;
}

static void trycacheline(MFILE *mat, uint32_t line) {

  lc_minfo *lci = (lc_minfo *)mat->specinfo.p;

  if (lci->cachedline != line) {
    if (lci->cachedlinedirty && writeline(mat, lci->linebuf, lci->cachedline) == mat->columns) {
      lci->cachedlinedirty = 0;
    }
    if (!lci->cachedlinedirty && readline(mat, lci->linebuf, line) == mat->columns) {
      lci->cachedline = line;
    }
  }
}

int32_t lc_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  lc_minfo *lci = (lc_minfo *)mat->specinfo.p;

  line += level * mat->lines;

  if (num != mat->columns) {
    trycacheline(mat, line);
  }

  if (line == lci->cachedline) {
    memcpy(buffer, lci->linebuf + col, num * sizeof(int));
    return num;
  }
  if (num == mat->columns) {
    return readline(mat, buffer, line);
  }

  return -1;
}

int32_t lc_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  lc_minfo *lci = (lc_minfo *)mat->specinfo.p;

  line += level * mat->lines;

  if (num == mat->columns) {
    return writeline(mat, buffer, line);
  }
  if (lci->cachedline != line) {
    trycacheline(mat, line);
    if (lci->cachedline != line && !lci->cachedlinedirty) {
      memset(lci->linebuf, 0, mat->columns * sizeof(int32_t));
      lci->cachedline = line;
    }
  }
  if (lci->cachedline == line) {
    lci->cachedlinedirty = 1;
    memcpy(lci->linebuf + col, buffer, num * sizeof(int32_t));
    return num;
  }

  return -1;
}

int32_t lc_flushcache(MFILE *mat) {

  lc_minfo *lci = (lc_minfo *)mat->specinfo.p;

  if (lci->cachedlinedirty && writeline(mat, lci->linebuf, lci->cachedline) != mat->columns) {
    return -1;
  }
  lci->cachedlinedirty = 0;
  return 0;
}
