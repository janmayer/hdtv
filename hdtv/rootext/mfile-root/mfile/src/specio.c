/*
 * specio.c
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

int32_t load_spec(const char *name, uint32_t *buf, int32_t num) {

  int32_t n;
  MFILE *mat;

  mat = mopen((char *)name, "r");
  n = mget(mat, (void *)buf, 0, 0, 0, num);
  if (mclose(mat) != 0)
    return -1;

  return n;
}

int32_t save_spec(const char *name, uint32_t *buf, int32_t num) {

  int32_t n;
  MFILE *mat;
  minfo info;

  mat = mopen((char *)name, "w");

  mgetinfo(mat, &info);
  info.filetype = MAT_LC;
  info.levels = 1;
  info.lines = 1;
  info.columns = num;
  msetinfo(mat, &info);

  n = mput(mat, (void *)buf, 0, 0, 0, num);
  if (mclose(mat) != 0)
    return -1;

  return n;
}
