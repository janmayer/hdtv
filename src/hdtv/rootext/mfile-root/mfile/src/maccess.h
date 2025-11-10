/*
 * maccess.h
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

/* ------------------------------------------------------------------------- */

#define _get(ap, buf, pos, num) ap->get(ap, buf, pos, num)
#define _put(ap, buf, pos, num) ap->put(ap, buf, pos, num)
#define _geta(ap, pos, num) ap->geta(ap, pos, num)
#define _puta(ap, pos, num) ap->puta(ap, pos, num)
#define _flush(ap) ap->flush(ap)
#define _close(ap) ap->close(ap)

/* ------------------------------------------------------------------------- */

typedef uint32_t acc_pos;

/*typedef struct accessmethod *amp;*/

typedef int32_t tryaccessf(amp ap, const char *name, const char *mode);
typedef int32_t flushf(amp ap);
typedef int32_t closef(amp ap);
typedef int32_t getf(amp ap, void *buffer, acc_pos offset, acc_pos nbytes);
typedef int32_t putf(amp ap, void *buffer, acc_pos offset, acc_pos nbytes);
typedef void *getaf(amp ap, acc_pos offset, acc_pos nbytes);
typedef void *putaf(amp ap, acc_pos offset, acc_pos nbytes);

typedef struct accessmethod {
  getf *get;
  putf *put;
  getaf *geta;
  putaf *puta;
  flushf *flush;
  closef *close;
  char *name;
  void *buffer;
  acc_pos size;
  acc_pos rd_offs;
  acc_pos rd_bytes;
  acc_pos wr_offs;
  acc_pos wr_bytes;
  struct {
    int32_t i;
    void *p;
  } specinfo;
} accessmethod;

/* ------------------------------------------------------------------------- */

typedef struct maccessdescr {
  tryaccessf *tryaccess;
  const char *name;
  struct maccessdescr *next;
} maccessdescr;

extern maccessdescr *tryaccess_first;

/* ------------------------------------------------------------------------- */

amp tryaccess(const char *name, const char *mode, char *accessname);
int32_t maddaccess(tryaccessf *taf, char *name);
