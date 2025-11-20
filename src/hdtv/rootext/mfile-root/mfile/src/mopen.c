/*
 * mopen.c
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
/*#include <sys/file.h>*/
/*#include <sys/stat.h>*/

#include "maccess.h"
#include "mat_types.h"
#include "mopen.h"
#include "sys_endian.h"

/*static void guessfiletype(MFILE *mat);*/
static void setmatdefaults(MFILE *mat);
static void openmatfile(MFILE *mat, const char *name, const char *mode);

/* include header files for all known format check routines */
#include "lc_minfo.h"
/*#include "oldmat_minfo.h"*/

static void setmatdefaults(MFILE *mat) {

  mat->ap = NULL;
  mat->name = NULL;
  mat->comment = NULL;
  mat->version = 0;
  mat->status = 0;

  mat->filetype = MAT_UNKNOWN;

  mat->levels = 1;
  mat->lines = 1;
  mat->columns = 0;

  mat->mflushf = NULL;
  mat->muninitf = NULL;
  mat->mgeti4f = NULL;
  mat->mgetf4f = NULL;
  mat->mgetf8f = NULL;
  mat->mputi4f = NULL;
  mat->mputf4f = NULL;
  mat->mputf8f = NULL;

  mat->specinfo.p = NULL;
}

static void openmatfile(MFILE *mat, const char *name, const char *mode) {

  char *accessmode = NULL;

  /* PROVISORISCH !!!
   *  Test auf (_accessmode_) in Name und Mode noch einrichten !!!
   */

  mat->name = malloc(strlen(name) + 1);
  if (mat->name)
    strcpy(mat->name, name);

  mat->ap = tryaccess(name, mode, accessmode);

  if (!mat->ap)
    mat->filetype = MAT_INVALID;
}

MFILE *mopen(const char *name, const char *mode) {

  MFILE *mat;
  char *fmt;

  if (name == NULL || mode == NULL)
    return NULL;

  mat = (MFILE *)malloc(sizeof(*mat));
  if (mat == NULL)
    return NULL;

  setmatdefaults(mat);
  openmatfile(mat, name, mode);

  if (mat->filetype != MAT_INVALID) {
    mat->filetype = MAT_UNKNOWN;

    if (mat->ap->size != 0)
      matproc_guessfiletype(mat);
  }

  fmt = strchr(mode, ',');
  if (fmt)
    msetfmt(mat, fmt + 1);

  if (mat->filetype == MAT_INVALID) {
    mclose(mat);
    mat = NULL;
  }

  return (mat);
}

int32_t mclose(MFILE *mat) {

  int32_t status = 0;

  if (mat) {
    if (mat->muninitf)
      status = mat->muninitf(mat);
    if (mat->ap) {
      if (_close(mat->ap) != 0)
        status = -1;
      free(mat->ap->name);
      free(mat->ap);
    }

    if (mat->name)
      free(mat->name);
    free(mat);
  }

  return status;
}

int32_t mflush(MFILE *mat) {

  int32_t status = 0;

  if (mat && mat->mflushf)
    status = mat->mflushf(mat);
  if (mat->ap) {
    if (_flush(mat->ap) != 0)
      status = -1;
  }

  return status;
}
