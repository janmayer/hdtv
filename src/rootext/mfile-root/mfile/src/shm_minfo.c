/*
 * shm_minfo.c
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
#include <stdlib.h>
#include <string.h>

#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/types.h>

#include "getputint.h"
#include "shm_getput.h"
#include "shm_minfo.h"

#ifdef undef
void shm_probe(MFILE *mat) {

  char buf[128], *p;
  int32_t shmid;
  struct shmid_ds shm_stat;
  void *shm_addr;
  int32_t shm_size;

  static char shm_magic[] = "shared memory (shm_alloc)\nid=";

  memset(buf, 0, sizeof(buf));
  if (get(mat->fd, buf, 0, sizeof(buf)) < sizeof(shm_magic))
    return;
  if (strncmp(buf, shm_magic, sizeof(shm_magic) - 1) != 0)
    return;

  p = buf + sizeof(shm_magic) - 1;
  while (isspace(*p))
    p++;
  shmid = 0;
  while (isdigit(*p))
    shmid = shmid * 10 + (*p++ - '0');

  shm_addr = (void *)shmat(shmid, NULL, SHM_RDONLY);
  if ((int32_t)shm_addr == -1)
    return;

  if (shmctl(shmid, IPC_STAT, &shm_stat) != 0)
    return;
  shm_size = shm_stat.shm_segsz;

  mat->status |= MST_DIMSFIXED;
  mat->filetype = MAT_SHM;

  mat->levels = 1;
  mat->lines = 1;
  mat->columns = shm_size / sizeof(int32_t);

  mat->mgeti4f = shm_get;
  mat->mputi4f = NULL;
  mat->muninitf = shm_uninit;

  mat->specinfo.p = shm_addr;
}

void shm_init(MFILE *mat) { mat->filetype = MAT_INVALID; }

int32_t shm_putinfo(MFILE *mat, minfo *info) { return 0; }

int32_t shm_uninit(MFILE *mat) {
  /*
    not yet implemented:
    if shmctl() --> shm_attach == 1:
       try to delete shm segment at close !
       no error, if we don't have permission to do this.
   */
  return shmdt((char *)mat->specinfo.p);
}

#endif /* NO_SHM */
#endif /*undef*/
