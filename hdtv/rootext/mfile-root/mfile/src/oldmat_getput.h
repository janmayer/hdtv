/*
 * oldmat_getput.h
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

extern int32_t le4_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t le4_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t le2_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t le2_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t he4_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t he4_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t he2_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t he2_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t le2s_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t he2s_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);

extern int32_t le4t_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t le4t_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t le2t_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t le2t_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t he4t_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t he4t_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t he2t_get(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t he2t_put(MFILE *mat, int32_t *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);

extern int32_t lf4_get(MFILE *mat, float *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t lf4_put(MFILE *mat, float *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t hf4_get(MFILE *mat, float *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t hf4_put(MFILE *mat, float *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t lf8_get(MFILE *mat, double *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t lf8_put(MFILE *mat, double *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t hf8_get(MFILE *mat, double *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t hf8_put(MFILE *mat, double *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
