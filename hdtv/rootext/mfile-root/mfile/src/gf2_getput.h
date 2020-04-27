/*
 * gf2_getput.h:
 * 
 * Support for Radware gf2 files.
 *
 */
/*
 * Copyright (c) 2003-2008, Nigel Warr <n.warr@ikp.uni-koeln.de>
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

#include <stdint.h>

extern int32_t  gf2_get(MFILE *mat, float *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern int32_t  gf2_put(MFILE *mat, float *buffer, uint32_t level, uint32_t line, uint32_t col, uint32_t num);
extern void gf2_probe(MFILE *mat);
extern void gf2_init(MFILE *mat);
extern int32_t  gf2_uninit(MFILE *mat);
