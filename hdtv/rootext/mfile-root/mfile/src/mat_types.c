/*
 * mat_types.c
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
#include "gf2_getput.h"
#include "gf2_minfo.h"
#include "lc_getput.h"
#include "lc_minfo.h"
#include "mate_getput.h"
#include "mate_minfo.h"
#include "oldmat_getput.h"
#include "oldmat_minfo.h"
#include "trixi_getput.h"
#include "trixi_minfo.h"
#include "txt_getput.h"
#include "txt_minfo.h"
#ifdef undef
#ifndef NO_SHM
#include "shm_getput.h"
#include "shm_minfo.h"
#endif /* NO_SHM */
#endif
#include "mat_types.h"

#include <string.h>

static matprocs matproc[] = {
    /* formats that are easily recognized (eg. by magic number) first	     */
    {MAT_LC, "lc", MAT_D_I4S, (mgetf *)lc_get, (mputf *)lc_put, lc_probe, lc_init},
#ifdef undef
#ifndef NO_SHM
    {MAT_SHM, "shm", MAT_D_I4S, (mgetf *)shm_get, NULL, shm_probe, NULL},
#endif /* NO_SHM */
#endif
    {MAT_MATE, "mate", MAT_D_I4S, (mgetf *)mate_get, NULL, mate_probe, NULL},
    {MAT_TRIXI, "trixi", MAT_D_I2U, (mgetf *)trixi_get, NULL, trixi_probe, NULL},
    {MAT_GF2, "gf2", MAT_D_F4, (mgetf *)gf2_get, (mputf *)gf2_put, gf2_probe, gf2_init},
    {MAT_HGF2, "hgf2", MAT_D_F4, (mgetf *)gf2_get, (mputf *)gf2_put, gf2_probe, gf2_init},

    /* formats that may need guessing ...					     */
    {MAT_LE4, "le4", MAT_D_I4S, (mgetf *)le4_get, (mputf *)le4_put, oldmat_probe, oldmat_init},
    {MAT_HE4, "he4", MAT_D_I4S, (mgetf *)he4_get, (mputf *)he4_put, NULL, oldmat_init},

    {MAT_LE2, "le2", MAT_D_I2U, (mgetf *)le2_get, (mputf *)le2_put, NULL, oldmat_init},
    {MAT_HE2, "he2", MAT_D_I2U, (mgetf *)he2_get, (mputf *)he2_put, NULL, oldmat_init},

    {MAT_LE2S, "le2s", MAT_D_I2S, (mgetf *)le2s_get, (mputf *)le2_put, NULL, oldmat_init},
    {MAT_HE2S, "he2s", MAT_D_I2S, (mgetf *)he2s_get, (mputf *)he2_put, NULL, oldmat_init},

    {MAT_LE4T, "le4t", MAT_D_I4S, (mgetf *)le4t_get, (mputf *)le4t_put, NULL, oldmat_init},
    {MAT_HE4T, "he4t", MAT_D_I4S, (mgetf *)he4t_get, (mputf *)he4t_put, NULL, oldmat_init},

    {MAT_LE2T, "le2t", MAT_D_I2U, (mgetf *)le2t_get, (mputf *)le2t_put, NULL, oldmat_init},
    {MAT_HE2T, "he2t", MAT_D_I2U, (mgetf *)he2t_get, (mputf *)he2t_put, NULL, oldmat_init},

    {MAT_LF4, "lf4", MAT_D_F4, (mgetf *)lf4_get, (mputf *)lf4_put, NULL, oldmat_init},
    {MAT_HF4, "hf4", MAT_D_F4, (mgetf *)hf4_get, (mputf *)hf4_put, NULL, oldmat_init},

    {MAT_LF8, "lf8", MAT_D_F8, (mgetf *)lf8_get, (mputf *)lf8_put, NULL, oldmat_init},
    {MAT_HF8, "hf8", MAT_D_F8, (mgetf *)hf8_get, (mputf *)hf8_put, NULL, oldmat_init},

    /*
      { MAT_VAXF, "vaxf", MAT_D_F4,  vaxf_get, vaxf_put,NULL,	  oldmat_init},
      { MAT_VAXG, "vaxg", MAT_D_F8,  vaxg_get, vaxg_put,NULL,	  oldmat_init},
    */
    {MAT_TXT, "txt", MAT_D_F8, (mgetf *)txt_get, (mputf *)txt_put, txt_probe, txt_init},

    /* MAT_INVALID must be the last entry (used internally !)		     */
    {MAT_INVALID, "???", MAT_D_INV, NULL, NULL, NULL, NULL},
};

void matproc_guessfiletype(MFILE *mat) {

  matprocs *p = matproc;

  while (p->filetype != MAT_INVALID) {
    mprobef *f = p->mprobe;
    if (f) {
      f(mat);
      if (mat->filetype != MAT_UNKNOWN)
        return;
    }
    p++;
  }
}

void matproc_init(MFILE *mat) {

  matprocs *p = matproc;
  int32_t mft = mat->filetype;
  int32_t pft;

  while ((pft = p->filetype) != MAT_INVALID) {
    if (pft == mft) {
      minitf *f = p->minit;
      if (f)
        f(mat);
      return;
    }
    p++;
  }
}

char *matproc_fmtname(int32_t mft) {

  matprocs *p = matproc;
  int32_t pft;

  while ((pft = p->filetype) != MAT_INVALID) {
    if (pft == mft) {
      return p->fmtname;
    }
    p++;
  }
  return "???";
}

int32_t matproc_filetype(const char *fmt) {

  matprocs *p = matproc;

  while (p->filetype != MAT_INVALID) {
    if (strcmp(p->fmtname, fmt) == 0) {
      return p->filetype;
    }
    p++;
  }
  return MAT_INVALID;
}

int32_t matproc_datatype(int32_t mft) {

  matprocs *p = matproc;
  int32_t pft;

  while ((pft = p->filetype) != MAT_INVALID) {
    if (pft == mft) {
      return p->datatype;
    }
    p++;
  }
  return MAT_D_INV;
}

mgetf *matproc_getf(int32_t mft) {

  matprocs *p = matproc;
  int32_t pft;

  while ((pft = p->filetype) != MAT_INVALID) {
    if (pft == mft) {
      return p->mget;
    }
    p++;
  }

  return (mgetf *)NULL;
}

mputf *matproc_putf(int32_t mft) {

  matprocs *p = matproc;
  int32_t pft;

  while ((pft = p->filetype) != MAT_INVALID) {
    if (pft == mft) {
      return p->mput;
    }
    p++;
  }

  return (mputf *)NULL;
}
