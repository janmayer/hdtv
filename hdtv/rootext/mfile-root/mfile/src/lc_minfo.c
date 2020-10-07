/*
 * lc_minfo.c
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
#include <memory.h>
#include <stdlib.h>

#include "getputint.h"
#include "lc_c1.h"
#include "lc_c2.h"
#include "lc_getput.h"
#include "lc_minfo.h"
#include "maccess.h"
#include "sys_endian.h"

static int32_t init_lci(MFILE *mat, uint32_t freepos, uint32_t freelistpos, uint32_t poslentablepos);
/* static int32_t lc_updateheader(MFILE *mat); */
static void free_lci(MFILE *mat);
static int32_t lc_flush(MFILE *mat);

static int32_t init_lci(MFILE *mat, uint32_t freepos, uint32_t freelistpos, uint32_t poslentablepos) {

  uint32_t n = mat->lines * mat->levels;

  lc_minfo *lci = (lc_minfo *)malloc(sizeof(lc_minfo));

  mat->specinfo.p = (void *)lci;

  if (lci) {
    lci->version = mat->version;
    lci->cachedline = -1;
    lci->cachedcomprline = -1;
    lci->comprlinelen = 0;
    lci->cachedlinedirty = 0;
    lci->linebuf = NULL;
    lci->comprlinebuf = NULL;

    switch (lci->version) {

    case LC_C1_VERSION:
      lci->comprf = lc1_compress;
      lci->uncomprf = lc1_uncompress;
      lci->comprlinebuf = (void *)malloc(lc1_comprlinelenmax(mat->columns));
      break;

    case LC_C2_VERSION:
      lci->comprf = lc2_compress;
      lci->uncomprf = lc2_uncompress;
      lci->comprlinebuf = (void *)malloc(lc2_comprlinelenmax(mat->columns));
      break;
    }

    lci->linebuf = (int32_t *)malloc(mat->columns * sizeof(int32_t));
    lci->poslentableptr = (lc_poslen *)malloc(n * sizeof(lc_poslen));

    if (lci->poslentableptr && lci->linebuf && lci->comprlinebuf) {

      if (freepos != 0) {
        lci->poslentablepos = poslentablepos;
        lci->freepos = freepos;
        lci->freelistpos = freelistpos;
        if (getle4(mat->ap, (int32_t *)lci->poslentableptr, poslentablepos, 2 * n) == 2 * n) {
          lc_poslen lpc;
          lpc.len = lci->poslentableptr[0].len;
          lpc.pos = lci->poslentableptr[0].pos;
          if (lpc.len && lpc.pos < sizeof(lc_header) + n * sizeof(lc_poslen))
            return -1;
          return 0;
        }
      } else {
        lci->poslentablepos = sizeof(lc_header);
        lci->freepos = lci->poslentablepos + n * sizeof(lc_poslen);
        lci->freelistpos = 0;
        memset(lci->poslentableptr, 0, n * sizeof(lc_poslen));
        return 0;
      }
    }
  }

  return -1;
}

void lc_probe(MFILE *mat) {

  lc_header lch;

  if (_get(mat->ap, &lch, 0, sizeof(lch)) != sizeof(lch))
    return;

  if (lch.magic != GETLE4((unsigned)MAGIC_LC))
    return;

  mat->status |= MST_DIMSFIXED;
  mat->filetype = MAT_LC;
  mat->version = GETLE4(lch.version);

  mat->levels = GETLE4(lch.levels);
  mat->lines = GETLE4(lch.lines);
  mat->columns = GETLE4(lch.columns);

  mat->mgeti4f = lc_get;
  mat->mputi4f = lc_put;
  mat->mflushf = lc_flush;
  mat->muninitf = lc_uninit;

  if (init_lci(mat, GETLE4(lch.freepos), GETLE4(lch.freelistpos), GETLE4(lch.poslentablepos)) != 0)
    free_lci(mat);
  if (mat->specinfo.p)
    mat->status |= (MST_INITIALIZED | MST_DIMSFIXED);
}

void lc_init(MFILE *mat) {

  if (mat->status & MST_INITIALIZED)
    return;

  if (mat->version == 0) {
    mat->version = LC_STD_VERSION;
  }

  if (init_lci(mat, 0, 0, 0) != 0) {
    free_lci(mat);
    mat->filetype = MAT_INVALID;
    return;
  }

  mat->mgeti4f = lc_get;
  mat->mputi4f = lc_put;
  mat->mflushf = lc_flush;
  mat->muninitf = lc_uninit;
}

#ifdef undef
int32_t lc_putinfo(MFILE *mat, minfo *info) { return 0; }
#endif

int32_t lc_uninit(MFILE *mat) {

  int32_t status;

  status = lc_flush(mat);
  free_lci(mat);

  return status;
}

static int32_t lc_flush(MFILE *mat) {

  if (mat->status & MST_DIRTY) {
    lc_header lch;
    lc_minfo *lci = (lc_minfo *)mat->specinfo.p;
    uint32_t n;

    if (lc_flushcache(mat) != 0)
      return -1;

    lch.magic = GETLE4((unsigned)MAGIC_LC);

    lch.levels = GETLE4(mat->levels);
    lch.lines = GETLE4(mat->lines);
    lch.columns = GETLE4(mat->columns);

    lch.version = GETLE4(lci->version);
    lch.poslentablepos = GETLE4(lci->poslentablepos);
    lch.freepos = GETLE4(lci->freepos);
    lch.freelistpos = GETLE4(lci->freelistpos);
    lch.used = 0; /* not yet implemented */
    lch.free = 0;
    lch.status = 0;

    if (_put(mat->ap, &lch, 0, sizeof(lch)) != sizeof(lch))
      return -1;

    n = mat->levels * mat->lines;
    if (putle4(mat->ap, (int32_t *)lci->poslentableptr, lci->poslentablepos, 2 * n) != 2 * n)
      return -1;
    if (_flush(mat->ap) != 0)
      return -1;
    mat->status &= ~MST_DIRTY;
  }
  return 0;
}

static void free_lci(MFILE *mat) {

  if (mat != NULL) {
    lc_minfo *lci = (lc_minfo *)mat->specinfo.p;
    if (lci->linebuf != NULL)
      free(lci->linebuf);
    if (lci->comprlinebuf != NULL)
      free(lci->comprlinebuf);
    if (lci->poslentableptr != NULL)
      free(lci->poslentableptr);
    free(lci);
  }
  mat->filetype = MAT_INVALID;
}
