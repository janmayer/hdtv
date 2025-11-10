/*
 * shm_access.c
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
#ifndef NO_SHM

#include <ctype.h>
#include <errno.h>
#include <memory.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/types.h>

#include "maccess.h"
#include "shm_access.h"

/* ------------------------------------------------------------------------- */

static void *shm_geta(amp ap, acc_pos offset, acc_pos nbytes) {

  char *p = (char *)ap->specinfo.p;

  if (offset + nbytes > ap->size)
    return NULL;
  return p + offset;
}

static int32_t shm_close(amp ap) {
  /*
    not yet implemented:
    if shmctl() --> shm_attach == 1:
       try to delete shm segment at close !
       no error, if we don't have permission to do this.
   */
  return shmdt((char *)ap->specinfo.p);
}

/* ------------------------------------------------------------------------- */

int32_t shm_tryaccess(amp ap, const char *name, const char *mode) {

  FILE *f;
  char buf[128], *p;
  int32_t shmid;
  struct shmid_ds shm_stat;
  void *shm_addr;
  int32_t shm_size;

  static char shm_magic[] = "shared memory (shm_alloc)\nid=";

  memset(buf, 0, sizeof(buf));

  f = fopen(name, "r");
  if (!f)
    return -1;

  if (fread(buf, 1, sizeof(buf), f) < sizeof(shm_magic)) {
    fclose(f);
    return -1;
  }

  if (strncmp(buf, shm_magic, sizeof(shm_magic) - 1) != 0) {
    fclose(f);
    return -1;
  }

  p = buf + sizeof(shm_magic) - 1;
  while (isspace(*p))
    p++;
  shmid = 0;
  while (isdigit(*p))
    shmid = shmid * 10 + (*p++ - '0');

  shm_addr = shmat(shmid, NULL, SHM_RDONLY);
  if (shm_addr == (void *)-1) {
    fclose(f);
    return -1;
  }

  if (shmctl(shmid, IPC_STAT, &shm_stat) != 0) {
    fclose(f);
    return -1;
  }

  shm_size = shm_stat.shm_segsz;

  ap->size = shm_size;
  ap->specinfo.p = shm_addr;

  ap->geta = shm_geta;
  /*  ap->puta		= shm_puta;*/

  ap->close = shm_close;

  return 0;
}

#endif /* NO_SHM */
