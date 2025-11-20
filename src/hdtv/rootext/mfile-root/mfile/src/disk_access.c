/*
 * disc_access.c
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

#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
// #include <sys/file.h>
#include <sys/stat.h>

#include "debug.h"
#include "disk_access.h"
#include "maccess.h"

/* ------------------------------------------------------------------------- */

int32_t disk_get(amp ap, void *buffer, acc_pos offset, acc_pos nbytes) {

  FILE *f = (FILE *)ap->specinfo.p;
  if (fseek(f, (long)offset, SEEK_SET) != 0) {
    PERROR("fseek");
    return -1;
  }

  return fread(buffer, 1, nbytes, f);
}

int32_t disk_put(amp ap, void *buffer, acc_pos offset, acc_pos nbytes) {

  FILE *f = (FILE *)ap->specinfo.p;

  if (fseek(f, (long)offset, SEEK_SET) != 0) {
    PERROR("fseek");
    return -1;
  }

  return fwrite(buffer, 1, nbytes, f);
}

/* ------------------------------------------------------------------------- */

int32_t disk_flush(amp ap) {

  FILE *f = (FILE *)ap->specinfo.p;

  return fflush(f);
}

int32_t disk_close(amp ap) {

  FILE *f = (FILE *)ap->specinfo.p;

  return fclose(f);
}

/* ------------------------------------------------------------------------- */

int32_t disk_tryaccess(amp ap, const char *name, const char *mode) {

  FILE *f;
  struct stat stat_buf;

  // Always open in binary mode
  char *b = "b";
  size_t len = strlen(mode);
  size_t spn = strcspn(mode, b);
  if (spn == len) {
    char *bmode = malloc(len + 2);
    strcpy(bmode, mode);
    bmode[len] = b[0];
    bmode[len + 1] = '\0';
    f = fopen(name, bmode);
    free(bmode);
  } else {
    f = fopen(name, mode);
  }

  if (!f) {
    PERROR("fopen");
    return -1;
  }
  ap->specinfo.p = (void *)f;
  ap->get = disk_get;
  ap->put = disk_put;
  ap->close = disk_close;
  ap->flush = disk_flush;

  if (fstat(fileno(f), &stat_buf) == 0) {
    ap->size = stat_buf.st_size;
  }

  return 0;
}

/* ------------------------------------------------------------------------- */
