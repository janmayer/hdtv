/*
 * mat_types.h
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

#include "mfile.h"
#include <stdint.h>

typedef void mprobef(MFILE *mat);
typedef void minitf(MFILE *mat);
typedef int32_t mgetf(MFILE *mat, void *buf, int32_t v, int32_t l, int32_t c, int32_t n);
typedef int32_t mputf(MFILE *mat, void *buf, int32_t v, int32_t l, int32_t c, int32_t n);

void matproc_guessfiletype(MFILE *mat);
void matproc_init(MFILE *mat);
int32_t matproc_filetype(const char *fmtname);
char *matproc_fmtname(int32_t filetype);
int32_t matproc_datatype(int32_t filetype);
mgetf *matproc_getf(int32_t filetype);
mputf *matproc_putf(int32_t filetype);

typedef char fmtnametype[7];

typedef struct {
  int32_t filetype;
  fmtnametype fmtname;
  int32_t datatype;
  mgetf *mget;
  mputf *mput;
  mprobef *mprobe;
  minitf *minit;
} matprocs;
