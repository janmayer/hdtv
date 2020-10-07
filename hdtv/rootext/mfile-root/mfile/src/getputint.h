/*
 * getputint.h
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

/* signed low endian 8 byte matrix file */
uint32_t getle8(amp ap, int32_t *buffer, uint32_t pos, uint32_t num);
uint32_t putle8(amp ap, int32_t *buffer, uint32_t pos, uint32_t num);

/* signed high endian 8 byte matrix file */
uint32_t gethe8(amp ap, int32_t *buffer, uint32_t pos, uint32_t num);
uint32_t puthe8(amp ap, int32_t *buffer, uint32_t pos, uint32_t num);

/* signed low endian 4 byte matrix file */
uint32_t getle4(amp ap, int32_t *buffer, uint32_t pos, uint32_t num);
uint32_t putle4(amp ap, int32_t *buffer, uint32_t pos, uint32_t num);

/* signed high endian 4 byte matrix file */
uint32_t gethe4(amp ap, int32_t *buffer, uint32_t pos, uint32_t num);
uint32_t puthe4(amp ap, int32_t *buffer, uint32_t pos, uint32_t num);

/* unsigned low endian 2 byte matrix file */
uint32_t getle2(amp ap, int32_t *buffer, uint32_t pos, uint32_t num);
uint32_t putle2(amp ap, int32_t *buffer, uint32_t pos, uint32_t num);

/* unsigned high endian 2 byte matrix file */
uint32_t gethe2(amp ap, int32_t *buffer, uint32_t pos, uint32_t num);
uint32_t puthe2(amp ap, int32_t *buffer, uint32_t pos, uint32_t num);

/* signed low endian 2 byte matrix file */
uint32_t getle2s(amp ap, int32_t *buffer, uint32_t pos, uint32_t num);

/* signed high endian 2 byte matrix file */
uint32_t gethe2s(amp ap, int32_t *buffer, uint32_t pos, uint32_t num);
