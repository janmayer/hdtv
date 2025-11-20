/*
 * mate_minfo.c
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
/* #include <memory.h>*/

#include "getputint.h"
#include "maccess.h"
#include "mate_getput.h"
#include "mate_minfo.h"
#include "sys_endian.h"

static int32_t match(const char *str, const char *pattern);

typedef struct {
  char dummy1[7];
  char name[15];
  char date[12];
  char time[12];
  char dummy2[210];
  char dummy3[10];
  int16_t channels;
} mate_header;

static int32_t match(const char *str, const char *pattern) {

  char p;

  while ((p = *pattern++)) {
    char c = *str++;
    switch (p) {
    case '\0':
      return 0;
    case ' ':
    case ':':
      if (c != p)
        return -1;
      break;
    case '9':
      if ((c < '0' || c > '9') && c != ' ')
        return -1;
      break;
    case 'Z':
      if (c < 'A' || c > 'Z')
        return -1;
      break;
    case '?':
      break;
    default:
      return -1;
      break;
    }
  }
  return 0;
}

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

void mate_probe(MFILE *mat) {

  mate_header mate_h;
  char comment[128];

  if (_get(mat->ap, (char *)&mate_h, 0, sizeof(mate_h)) != sizeof(mate_h))
    return;

  if (match(mate_h.date, "ZZZ 99 9999") != 0)
    return;
  if (match(mate_h.time, "99:99:99 ZZ") != 0)
    return;

  mat->status |= MST_DIMSFIXED;
  mat->filetype = MAT_MATE;
  mat->version = 0;

  mat->levels = 1;
  mat->lines = 1;
  mat->columns = GETLE2(mate_h.channels);

  mat->mgeti4f = mate_get;
  mat->mputi4f = NULL;
  mat->muninitf = NULL;

  comment[0] = '\0';
  strbcat(comment, mate_h.name, sizeof(mate_h.name));
  strcat(comment, " ");
  strbcat(comment, mate_h.date, sizeof(mate_h.date));
  strcat(comment, " ");
  strbcat(comment, mate_h.time, sizeof(mate_h.time));

  mat->comment = (char *)malloc(strlen(comment) + 1);
  strcpy(mat->comment, comment);
}
