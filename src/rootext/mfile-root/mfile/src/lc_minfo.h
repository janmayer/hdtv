/*
 * lc_minfo.h
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

#define MAGIC_LC 0x80FFFF10

#define LC_C1_VERSION (1)
#define LC_C2_VERSION (2)

#define LC_MAX_VERSION LC_C2_VERSION

#define LC_STD_VERSION LC_C2_VERSION

typedef struct {
  uint32_t magic;
  uint32_t version;
  uint32_t levels, lines, columns;
  uint32_t poslentablepos;
  uint32_t freepos, freelistpos;
  uint32_t used, free;
  uint32_t status;
} lc_header;

typedef struct {
  uint32_t pos, len;
} lc_poslen;

typedef struct {
  int32_t version;
  uint32_t freepos, freelistpos;
  int32_t *linebuf;
  void *comprlinebuf;
  uint32_t cachedlinedirty;
  uint32_t cachedline;
  uint32_t cachedcomprline;
  uint32_t comprlinelen;
  uint32_t poslentablepos;
  lc_poslen *poslentableptr;
  int32_t (*comprf)();
  int32_t (*uncomprf)();
} lc_minfo;

void lc_probe(MFILE *mat);
void lc_init(MFILE *mat);
int32_t lc_putinfo(MFILE *mat, minfo *info);
int32_t lc_uninit(MFILE *mat);
