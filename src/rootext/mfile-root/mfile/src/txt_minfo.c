/*
 * txt_minfo.c
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

#include <ctype.h>
#include <memory.h>
#include <stdlib.h>
#include <string.h>

#include "getputint.h"
#include "maccess.h"
#include "txt_getput.h"
#include "txt_minfo.h"

static int32_t txt_load(MFILE *mat);
static int32_t txt_alloc(MFILE *mat);
static void txt_free(MFILE *mat);

#define PROBESIZE 8192

#define GETBUF (nleft = _get(mat->ap, buffer, fpos, sizeof(buffer)), fpos += nleft, nleft--)

#define NEXTCHAR (nleft-- ? *++p : (GETBUF > 0 ? (p = buffer, buffer[0]) : '\0'))

#define SKIPTOEOL                                                                                                      \
  {                                                                                                                    \
    do                                                                                                                 \
      c = NEXTCHAR;                                                                                                    \
    while (c && c != '\n');                                                                                            \
  }

#define SKIPSPACE                                                                                                      \
  {                                                                                                                    \
    while (c && isspace(c))                                                                                            \
      c = NEXTCHAR;                                                                                                    \
  }

#define SKIPCOMMENT                                                                                                    \
  {                                                                                                                    \
    if (c && (c == '#' /*|| c == '!'*/)) {                                                                             \
      SKIPTOEOL;                                                                                                       \
      continue;                                                                                                        \
    }                                                                                                                  \
  }

#define GETSIGN(PUTC)                                                                                                  \
  {                                                                                                                    \
    if (c == '-' || c == '+') {                                                                                        \
      PUTC;                                                                                                            \
      c = NEXTCHAR;                                                                                                    \
    }                                                                                                                  \
  }

#define GETDOT(PUTC)                                                                                                   \
  {                                                                                                                    \
    if (c == '.') {                                                                                                    \
      PUTC;                                                                                                            \
      c = NEXTCHAR;                                                                                                    \
    }                                                                                                                  \
  }

#define GETE(PUTC)                                                                                                     \
  {                                                                                                                    \
    if (c == 'e' || c == 'E') {                                                                                        \
      PUTC;                                                                                                            \
      c = NEXTCHAR;                                                                                                    \
    }                                                                                                                  \
  }

#define GETINT(PUTC)                                                                                                   \
  {                                                                                                                    \
    while (isdigit(c)) {                                                                                               \
      PUTC;                                                                                                            \
      c = NEXTCHAR;                                                                                                    \
    }                                                                                                                  \
  }

#define GETNUMBER(PUTC)                                                                                                \
  {                                                                                                                    \
    GETSIGN(PUTC);                                                                                                     \
    GETINT(PUTC);                                                                                                      \
    GETDOT(PUTC);                                                                                                      \
    GETINT(PUTC);                                                                                                      \
    GETE(PUTC);                                                                                                        \
    GETSIGN(PUTC);                                                                                                     \
    GETINT(PUTC);                                                                                                      \
  }

void txt_probe(MFILE *mat) {

  char buffer[PROBESIZE];
  char *p = buffer;
  uint32_t fpos = 0;
  int32_t nleft = 0;

  int32_t numbers = 0;
  char c = NEXTCHAR;

  if (nleft > sizeof(TXT_MAGIC) && strncmp(buffer, TXT_MAGIC, sizeof(TXT_MAGIC) - 1) == 0) {
    msetfmt(mat, buffer + sizeof(TXT_MAGIC) - 1);
    return;
  }

  for (;;) {
    SKIPSPACE;
    SKIPCOMMENT;
    if (c == '\0')
      break;
    if (c != '-' && c != '+' && !isdigit(c))
      return;
    GETNUMBER({});
    numbers++;
  }
  if (numbers) {
    mat->filetype = MAT_TXT;
    mat->columns = numbers;
    mat->lines = 1;
    mat->levels = 1;
  }
}

static int32_t txt_load(MFILE *mat) {

  char buffer[PROBESIZE];
  char *p = buffer;
  uint32_t fpos = 0;
  int32_t nleft = 0;
  int32_t maxnum = mat->levels * mat->lines * mat->columns;
  int32_t n;

  char c = NEXTCHAR;

  double *dblp = (double *)mat->specinfo.p;
  if (dblp == NULL)
    return -1;

  n = 0;
  while (n < maxnum) {
    char buf[40];
    int32_t i = 0;

    SKIPSPACE;
    SKIPCOMMENT;
    if (c == '\0')
      break;
    if (c != '-' && c != '+' && !isdigit(c))
      return -1;

    GETNUMBER({
      if (i < sizeof(buf))
        buf[i++] = c;
    });

    buf[i] = '\0';
    *dblp++ = atof(buf);
    n++;
  }
  return n;
}

static int32_t txt_alloc(MFILE *mat) {

  unsigned arrsize = mat->levels * mat->lines * mat->columns * sizeof(double);
  mat->specinfo.p = (void *)malloc(arrsize);
  if (mat->specinfo.p == NULL)
    return -1;
  memset(mat->specinfo.p, 0, arrsize);

  return 0;
}

static void txt_free(MFILE *mat) {

  double *dblp = (double *)mat->specinfo.p;
  if (dblp)
    free(dblp);
  mat->specinfo.p = NULL;
}

void txt_init(MFILE *mat) {

  if (mat->status & MST_INITIALIZED)
    return;

  if (mat->version == 0) {
    mat->version = TXT_STD_VERSION;
  }

  if (txt_alloc(mat) == 0 && txt_load(mat) >= 0) {
    mat->mgetf8f = txt_get;
    mat->mputf8f = txt_put;
    mat->mflushf = txt_flush;
    mat->muninitf = txt_uninit;
  } else {
    txt_free(mat);
  }
}

int32_t txt_uninit(MFILE *mat) {

  int32_t status;

  status = txt_flush(mat);
  txt_free(mat);

  return status;
}
