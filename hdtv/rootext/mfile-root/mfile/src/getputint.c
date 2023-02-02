/*
 * getputint.c
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

#include "getputint.h"
#include "maccess.h"
#include "sys_endian.h"
#include <errno.h>
// #include "config.h"

#ifdef undef
int32_t get(int32_t fd, void *adr, uint32_t pos, uint32_t num) {

  int32_t w;
  int32_t done = 0;
  char *buffer = adr;

  errno = 0;

  if (lseek(fd, pos, SEEK_SET) != pos) {
    PERROR("lseek");
    return -1;
  }

  do {
    w = read(fd, buffer, num);
    if (w > 0) {
      done += w;
      buffer += w;
      num -= w;
    } else {
#ifndef OSK
      if (errno && errno != EINTR) {
#else
      if (errno) {
#endif
#ifdef undef
        int32_t saveerrno = errno;
        (void)close(fd);
        errno = saveerrno;
        PERROR("get"); /* ERROR ABORT */
        exit(1);
#endif
        return -1;
      } else {
        num = 0;
      }
    }
  } while (num > 0);

  return done;
}

int32_t put(int32_t fd, void *adr, uint32_t pos, uint32_t num) {

  int32_t w;
  int32_t done = 0;
  char *buffer = adr;

  errno = 0;

  if (lseek(fd, pos, SEEK_SET) != pos) {
    PERROR("lseek");
    return -1;
  }

  do {
    w = write(fd, buffer, num);
    if (w > 0) {
      done += w;
      buffer += w;
      num -= w;
    } else {
#ifndef OSK
      if (errno && errno != EINTR) {
#else
      if (errno) {
#endif
#ifdef undef
        int32_t saveerrno = errno;
        (void)close(fd);
        errno = saveerrno;
        PERROR("get"); /* ERROR ABORT */
        exit(1);
#endif
        return -1;
      } else {
        num = 0;
      }
    }
  } while (num > 0);

  return done;
}
#endif /* undef */

uint32_t getle8(amp ap, int32_t *buffer, uint32_t pos, uint32_t num) {

#ifdef LOWENDIAN
  int32_t *iobuf = buffer;
#else
  uint32_t iobuf[2 * MAT_COLMAX], *p;
#endif

  uint32_t n = num << 3;
  if (_get(ap, (char *)iobuf, pos, n) != n)
    return 0;
#ifndef LOWENDIAN
  p = iobuf;
  for (n = num; n; n--) {
    register int32_t t1 = *(p++);
    register int32_t t2 = *(p++);
    *(buffer++) = GETLE4(t2);
    *(buffer++) = GETLE4(t1);
  }
#endif

  return num;
}

uint32_t putle8(amp ap, int32_t *buffer, uint32_t pos, uint32_t num) {

  uint32_t n;
#ifdef LOWENDIAN
  int32_t *iobuf = buffer;
#else
  uint32_t iobuf[2 * MAT_COLMAX], *p = iobuf;

  for (n = num; n; n--) {
    register int32_t t1 = *(buffer++);
    register int32_t t2 = *(buffer++);
    *(p++) = GETLE4(t2);
    *(p++) = GETLE4(t1);
  }
#endif
  n = num << 3;
  if (_put(ap, (char *)iobuf, pos, n) != n)
    return 0;
  return num;
}

uint32_t gethe8(amp ap, int32_t *buffer, uint32_t pos, uint32_t num) {

#ifndef LOWENDIAN
  int32_t *iobuf = buffer;
#else
  uint32_t iobuf[2 * MAT_COLMAX], *p;
#endif

  uint32_t n = num << 3;
  if (_get(ap, (char *)iobuf, pos, n) != n)
    return 0;
#ifdef LOWENDIAN
  p = iobuf;
  for (n = num; n; n--) {
    register int32_t t1 = *(p++);
    register int32_t t2 = *(p++);
    *(buffer++) = GETHE4(t2);
    *(buffer++) = GETHE4(t1);
  }
#endif

  return num;
}

uint32_t puthe8(amp ap, int32_t *buffer, uint32_t pos, uint32_t num) {

  uint32_t n;
#ifndef LOWENDIAN
  int32_t *iobuf = buffer;
#else
  uint32_t iobuf[2 * MAT_COLMAX], *p = iobuf;

  for (n = num; n; n--) {
    register int32_t t1 = *(buffer++);
    register int32_t t2 = *(buffer++);
    *(p++) = GETHE4(t2);
    *(p++) = GETHE4(t1);
  }
#endif
  n = num << 3;
  if (_put(ap, (char *)iobuf, pos, n) != n)
    return 0;
  return num;
}

uint32_t getle4(amp ap, int32_t *buffer, uint32_t pos, uint32_t num) {

#ifdef LOWENDIAN
  int32_t *iobuf = buffer;
#else
  uint32_t iobuf[MAT_COLMAX], *p;
#endif

  uint32_t n = num << 2;
  if (_get(ap, (char *)iobuf, pos, n) != n)
    return 0;
#ifndef LOWENDIAN
  for (p = iobuf, n = num; n; n--) {
    register int32_t t = *(p++);
    *(buffer++) = GETLE4(t);
  }
#endif

  return num;
}

uint32_t putle4(amp ap, int32_t *buffer, uint32_t pos, uint32_t num) {

  uint32_t n;
#ifdef LOWENDIAN
  int32_t *iobuf = buffer;
#else
  uint32_t iobuf[MAT_COLMAX], *p;

  for (p = iobuf, n = num; n; n--) {
    register int32_t t = *(buffer++);
    *(p++) = GETLE4(t);
  }
#endif
  n = num << 2;
  if (_put(ap, (char *)iobuf, pos, n) != n)
    return 0;

  return num;
}

uint32_t gethe4(amp ap, int32_t *buffer, uint32_t pos, uint32_t num) {

#ifndef LOWENDIAN
  int32_t *iobuf = buffer;
#else
  uint32_t iobuf[MAT_COLMAX], *p;
#endif

  uint32_t n = num << 2;
  if (_get(ap, (char *)iobuf, pos, n) != n)
    return 0;
#ifdef LOWENDIAN
  for (p = iobuf, n = num; n; n--) {
    register int32_t t = *(p++);
    *(buffer++) = GETHE4(t);
  }
#endif
  return num;
}

uint32_t puthe4(amp ap, int32_t *buffer, uint32_t pos, uint32_t num) {

  uint32_t n;
#ifndef LOWENDIAN
  int32_t *iobuf = buffer;
#else
  uint32_t iobuf[MAT_COLMAX], *p;

  for (p = iobuf, n = num; n; n--) {
    register int32_t t = *(buffer++);
    *(p++) = GETHE4(t);
  }
#endif
  n = num << 2;
  if (_put(ap, (char *)iobuf, pos, n) != n)
    return 0;
  return num;
}

uint32_t getle2(amp ap, int32_t *buffer, uint32_t pos, uint32_t num) {

  uint16_t iobuf[MAT_COLMAX], *p;
  uint32_t n = num << 1;

  if (_get(ap, (char *)iobuf, pos, n) != n)
    return 0;
  for (p = iobuf, n = num; n; n--) {
    register int32_t t = *(p++);
    *(buffer++) = (uint16_t)GETLE2(t);
  }

  return num;
}

uint32_t putle2(amp ap, int32_t *buffer, uint32_t pos, uint32_t num) {

  uint16_t iobuf[MAT_COLMAX], *p;
  uint32_t n;

  for (p = iobuf, n = num; n; n--) {
    register uint32_t t = *(buffer++);
    *(p++) = GETLE2(t);
  }
  n = num << 1;
  if (_put(ap, (char *)iobuf, pos, n) != n)
    return 0;

  return num;
}

uint32_t gethe2(amp ap, int32_t *buffer, uint32_t pos, uint32_t num) {

  uint16_t iobuf[MAT_COLMAX], *p;
  uint32_t n = num << 1;

  if (_get(ap, (char *)iobuf, pos, n) != n)
    return 0;
  for (p = iobuf, n = num; n; n--) {
    register int32_t t = *(p++);
    *(buffer++) = (uint16_t)GETHE2(t);
  }

  return num;
}

uint32_t puthe2(amp ap, int32_t *buffer, uint32_t pos, uint32_t num) {

  uint16_t iobuf[MAT_COLMAX], *p;
  uint32_t n;

  for (p = iobuf, n = num; n; n--) {
    register uint32_t t = *(buffer++);
    *(p++) = GETHE2(t);
  }
  n = num << 1;
  if (_put(ap, (char *)iobuf, pos, n) != n)
    return 0;

  return num;
}

uint32_t getle2s(amp ap, int32_t *buffer, uint32_t pos, uint32_t num) {

  int16_t iobuf[MAT_COLMAX], *p;
  uint32_t n = num << 1;

  if (_get(ap, (char *)iobuf, pos, n) != n)
    return 0;
  for (p = iobuf, n = num; n; n--) {
    register int32_t t = *(p++);
    *(buffer++) = (int16_t)GETLE2(t);
  }

  return num;
}

uint32_t gethe2s(amp ap, int32_t *buffer, uint32_t pos, uint32_t num) {

  uint16_t iobuf[MAT_COLMAX], *p;
  uint32_t n = num << 1;

  if (_get(ap, (char *)iobuf, pos, n) != n)
    return 0;
  for (p = iobuf, n = num; n; n--) {
    register int32_t t = *(p++);
    *(buffer++) = (int16_t)GETHE2(t);
  }

  return num;
}
