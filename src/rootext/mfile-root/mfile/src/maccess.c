/*
 * maccess.c
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
#include "maccess.h"
#include "disk_access.h"
#include "sys_endian.h"
#ifndef NO_SHM
#include "shm_access.h"
#endif

#include <errno.h>
#include <stdlib.h>
#include <string.h>

/* ------------------------------------------------------------------------- */

static amp newaccessmethod();
static amp initaccessmethod(amp ap, const char *name);
static void *dummy_geta(amp ap, acc_pos offset, acc_pos nbytes);
static void *dummy_puta(amp ap, acc_pos offset, acc_pos nbytes);
static int32_t dummy_flush(amp ap);
static int32_t dummy_close(amp ap);
static int32_t get_via_geta(amp ap, void *buffer, acc_pos offset, acc_pos nbytes);
static int32_t put_via_puta(amp ap, void *buffer, acc_pos offset, acc_pos nbytes);
static void *geta_via_get(amp ap, acc_pos offset, acc_pos nbytes);
static void *puta_via_put(amp ap, acc_pos offset, acc_pos nbytes);

/* ------------------------------------------------------------------------- */

#ifdef NO_SHM
static maccessdescr disk_access = {disk_tryaccess, NULL, NULL};
maccessdescr *tryaccess_first = &disk_access;
#else
static maccessdescr disk_access = {disk_tryaccess, NULL, NULL};
static maccessdescr shm_access = {shm_tryaccess, "shm", &disk_access};
maccessdescr *tryaccess_first = &shm_access;
#endif

/* ------------------------------------------------------------------------- */

static int32_t dummy_flush(amp ap) { return 0; }

static int32_t dummy_close(amp ap) { return 0; }

static void *dummy_geta(amp ap, acc_pos offset, acc_pos nbytes) { return (void *)NULL; }

static void *dummy_puta(amp ap, acc_pos offset, acc_pos nbytes) { return (void *)NULL; }

/* ------------------------------------------------------------------------- */

static int32_t get_via_geta(amp ap, void *buffer, acc_pos offset, acc_pos nbytes) {

  void *src = _geta(ap, offset, nbytes);
  if (src) {
    memcpy(buffer, src, nbytes);
    return nbytes;
  }

  return 0;
}

static int32_t put_via_puta(amp ap, void *buffer, acc_pos offset, acc_pos nbytes) {

  void *dest = _puta(ap, offset, nbytes);
  if (dest) {
    memcpy(dest, buffer, nbytes);
    return nbytes;
  }

  return 0;
}

/* ------------------------------------------------------------------------- */
/* PROVISORISCH !!! noch nicht implementiert */

static void *geta_via_get(amp ap, acc_pos offset, acc_pos nbytes) { return (void *)NULL; }

static void *puta_via_put(amp ap, acc_pos offset, acc_pos nbytes) { return (void *)NULL; }

/* ------------------------------------------------------------------------- */

int32_t maddaccess(tryaccessf *tryaccess, char *name) {

  maccessdescr *p = (maccessdescr *)malloc(sizeof(maccessdescr));
  if (p) {
    p->tryaccess = tryaccess;
    p->name = name;
    p->next = tryaccess_first;
    tryaccess_first = p;
    return 0;
  }

  return -1;
}

/* ------------------------------------------------------------------------- */

static amp newaccessmethod() {
  amp ap = (amp)malloc(sizeof(accessmethod));
  if (ap)
    memset(ap, 0, sizeof(*ap));
  return ap;
}

static amp initaccessmethod(amp ap, const char *name) {

  if (name) {
    ap->name = malloc(strlen(name) + 1);
    if (ap->name)
      strcpy(ap->name, name);
  }

  if (!ap->geta)
    ap->geta = ap->get ? geta_via_get : dummy_geta;
  if (!ap->get)
    ap->get = get_via_geta;

  if (!ap->puta)
    ap->puta = ap->put ? puta_via_put : dummy_puta;
  if (!ap->put)
    ap->put = put_via_puta;

  if (!ap->flush)
    ap->flush = dummy_flush;
  if (!ap->close)
    ap->close = dummy_close;

  return ap;
}

amp tryaccess(const char *name, const char *mode, char *accessname) {

  amp ap = newaccessmethod();

  if (ap) {
    maccessdescr *p = tryaccess_first;

    if (accessname && !*accessname)
      accessname = NULL;
    while (p) {
      if (!accessname || (p->name && p->name[0] && (strcmp(accessname, p->name) == 0))) {
        if (p->tryaccess(ap, name, mode) == 0)
          return initaccessmethod(ap, name);
      }
      p = p->next;
    }
  }
  free(ap);

  return NULL;
}
