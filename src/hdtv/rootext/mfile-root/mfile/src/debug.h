/* debug.h
 *
 * Macro for enabling some debug output
 */
/*
 * Copyright (c) 2008, Ralf Schulze <ralf.schulze@ikp.uni-koeln.de>
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

#ifndef DEBUG_H_
#define DEBUG_H_

/* Include autoconf 'config.h' */
// #if HAVE_CONFIG_H
// #include "config.h"
// #endif /* HAVE_CONFIG_H */

/* Debugging output macro */
#ifdef DEBUG_OUTPUT

#include <stdio.h>
#define DEBUG(...)                                                                                                     \
  {                                                                                                                    \
    (void)fprintf(stderr, "DEBUG:(%s:%d):\t", __FILE__, __LINE__);                                                     \
    fprintf(stderr, __VA_ARGS__);                                                                                      \
  }
#else /* DEBUG_OUTPUT */
#define DEBUG(...) ((void)0)
#endif /* DEBUG_OUTPUT */

#define PERROR fprintf(stderr, "(%s:%d)\t", __FILE__, __LINE__), perror

#endif /* DEBUG_H_ */
