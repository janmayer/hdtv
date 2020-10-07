/*
 * callindir.c
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

#include "callindir.h"
#include "converters.h"
#include "mat_types.h"
#include "mopen.h"

#define paramok(mat, buffer, level, line, col, num)                                                                    \
  (mat && buffer && (uint32_t)level < mat->levels && (uint32_t)line < mat->lines && (uint32_t)col < mat->columns &&    \
   (uint32_t)num <= mat->columns && (uint32_t)(col + num) <= mat->columns)

int32_t mgetint(MFILE *mat, int32_t *buffer, int32_t level, int32_t line, int32_t col, int32_t num) {

  int32_t (*f)();

  /* sanity checks */
  if (paramok(mat, buffer, level, line, col, num)) {

    if ((f = mat->mgeti4f))
      return f(mat, buffer, level, line, col, num);
    matproc_init(mat);
    installconverters(mat);
    if ((f = mat->mgeti4f))
      return f(mat, buffer, level, line, col, num);
  }

  return -1;
}

int32_t mputint(MFILE *mat, int32_t *buffer, int32_t level, int32_t line, int32_t col, int32_t num) {

  int32_t (*f)();

  /* sanity checks */
  if (paramok(mat, buffer, level, line, col, num)) {

    mat->status |= (MST_DIRTY | MST_DIMSFIXED);

    if ((f = mat->mputi4f))
      return f(mat, buffer, level, line, col, num);
    if (mat->filetype == MAT_UNKNOWN)
      mat->filetype = MAT_STD_INT;
    matproc_init(mat);
    installconverters(mat);
    if ((f = mat->mputi4f))
      return f(mat, buffer, level, line, col, num);
  }

  return -1;
}

/*------------------------------------------------------------------------*/

int32_t mgetflt(MFILE *mat, float *buffer, int32_t level, int32_t line, int32_t col, int32_t num) {

  int32_t (*f)();

  /* sanity checks */
  if (paramok(mat, buffer, level, line, col, num)) {

    if ((f = mat->mgetf4f))
      return f(mat, buffer, level, line, col, num);
    matproc_init(mat);
    installconverters(mat);
    if ((f = mat->mgetf4f))
      return f(mat, buffer, level, line, col, num);
  }

  return -1;
}

int32_t mputflt(MFILE *mat, float *buffer, int32_t level, int32_t line, int32_t col, int32_t num) {

  int32_t (*f)();

  /* sanity checks */
  if (paramok(mat, buffer, level, line, col, num)) {

    mat->status |= (MST_DIRTY | MST_DIMSFIXED);

    if ((f = mat->mputf4f))
      return f(mat, buffer, level, line, col, num);
    if (mat->filetype == MAT_UNKNOWN)
      mat->filetype = MAT_STD_FLT;
    matproc_init(mat);
    installconverters(mat);
    if ((f = mat->mputf4f))
      return f(mat, buffer, level, line, col, num);
  }

  return -1;
}

/*------------------------------------------------------------------------*/

int32_t mgetdbl(MFILE *mat, double *buffer, int32_t level, int32_t line, int32_t col, int32_t num) {

  int32_t (*f)();

  /* sanity checks */
  if (paramok(mat, buffer, level, line, col, num)) {

    if ((f = mat->mgetf8f))
      return f(mat, buffer, level, line, col, num);
    matproc_init(mat);
    installconverters(mat);
    if ((f = mat->mgetf8f))
      return f(mat, buffer, level, line, col, num);
  }

  return -1;
}

int32_t mputdbl(MFILE *mat, double *buffer, int32_t level, int32_t line, int32_t col, int32_t num) {

  int32_t (*f)();

  /* sanity checks */
  if (paramok(mat, buffer, level, line, col, num)) {

    mat->status |= (MST_DIRTY | MST_DIMSFIXED);

    if ((f = mat->mputf8f))
      return f(mat, buffer, level, line, col, num);
    if (mat->filetype == MAT_UNKNOWN)
      mat->filetype = MAT_STD_DBL;
    matproc_init(mat);
    installconverters(mat);
    if ((f = mat->mputf8f))
      return f(mat, buffer, level, line, col, num);
  }

  return -1;
}
