/*
 * txt_getput.c
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

#include "maccess.h"
#include "txt_getput.h"
#include "txt_minfo.h"

int32_t txt_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {

  double *dblp = (double *)mat->specinfo.p;

  /*  if (dblp == NULL) return -1; */

  int32_t idx = ((level * mat->lines) + line) * mat->columns + col;

  memcpy(buffer, dblp + idx, num * sizeof(double));

  return num;
}

int32_t txt_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num) {
  double *dblp = (double *)mat->specinfo.p;

  /*  if (dblp == NULL) return -1; */

  int32_t idx = ((level * mat->lines) + line) * mat->columns + col;

  memcpy(dblp + idx, buffer, num * sizeof(double));

  return num;
}

int32_t txt_flush(MFILE *mat) {

  if ((mat->status & MST_DIRTY) != 0) {
    double *dblp = (double *)mat->specinfo.p;
    int32_t maxnum = mat->levels * mat->lines * mat->columns;
    int32_t i;
    /* PROVISORISCH !!! */
    FILE *outf = (FILE *)mat->ap->specinfo.p;

    if (mat->version == 1) {
      fprintf(outf, "%s%s\n", TXT_MAGIC, mgetfmt(mat, NULL));
    }
    for (i = 0; i < maxnum; i++) {
      if (fprintf(outf, "%G\n", *dblp++) < 0)
        return -1;
    }
    if (fflush(outf) != 0)
      return -1;
    mat->status &= ~MST_DIRTY;
  }
  return 0;
}
