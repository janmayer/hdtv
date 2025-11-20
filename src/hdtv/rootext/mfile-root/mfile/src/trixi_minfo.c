/*
 * trixi_minfo.c
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

#include "getputint.h"
#include "maccess.h"
#include "sys_endian.h"
#include "trixi_getput.h"
#include "trixi_minfo.h"

static char trixi_magic[] = "Trixi Save_matrix";

typedef struct {
  char code[40];
  char name[20];
  char date[20];
  int32_t x_res;
  int32_t y_res;
  int32_t bpc;
  int32_t blocksize;
  char comment[416];
} trixi_header;

static void strbcat(char *s1, char *s2, int32_t n) {

  char c;
  char *p = s1 + strlen(s1);
  int32_t i;

  i = strlen(s2);
  if (i > n)
    i = n;

  while (i-- && (c = *s2++) != '\0')
    *p++ = c;
  *p = '\0';

  i = strlen(s1);
  while (i-- && *--p == ' ')
    ;
  *++p = '\0';
}

void trixi_probe(MFILE *mat) {

  trixi_header trixi_h;
  char comment[512];

  if (_get(mat->ap, (char *)&trixi_h, 0, sizeof(trixi_h)) != sizeof(trixi_h))
    return;

  if (strncmp(trixi_h.code, trixi_magic, strlen(trixi_magic)) != 0)
    return;

  /* only short matrizes supported at this time */
  if (GETLE4(trixi_h.bpc) != 2)
    return;

  mat->status |= MST_DIMSFIXED;
  mat->filetype = MAT_TRIXI;
  mat->version = 0;

  mat->levels = 1;
  mat->lines = GETLE4(trixi_h.y_res);
  mat->columns = GETLE4(trixi_h.x_res);

  mat->mgeti4f = trixi_get;
  mat->mputi4f = NULL;
  mat->muninitf = NULL;

  comment[0] = '\0';
  strbcat(comment, trixi_h.name, sizeof(trixi_h.name));
  strcat(comment, " ");
  strbcat(comment, trixi_h.date, sizeof(trixi_h.date));
  strcat(comment, " ");
  strbcat(comment, trixi_h.comment, sizeof(trixi_h.comment));

  mat->comment = (char *)malloc(strlen(comment) + 1);
  strcpy(mat->comment, comment);
}
