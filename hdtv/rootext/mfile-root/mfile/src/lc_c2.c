/*
 * lc_c2.c
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
#include "lc_c2.h"

#define encode(i) ((encodetmp = i) >= 0 ? (encodetmp << 1) : ~(encodetmp << 1))

#define fitsinto(i, n) (((i) >> n) == 0)

#define put_3_2(a, b, c) (*dest++ = (a) + ((b) << 2) + ((c) << 4))

#define put_2_3(a, b) (*dest++ = 0x40 + (a) + ((b) << 3))

#define put_tag_n(T, a)                                                                                                \
  do {                                                                                                                 \
    uint32_t t = a;                                                                                                    \
    if (t <= 59) {                                                                                                     \
      *dest++ = T + t;                                                                                                 \
    } else {                                                                                                           \
      char *tag = dest++;                                                                                              \
      int32_t bytes = 0;                                                                                               \
      t -= 60;                                                                                                         \
      *dest++ = (char)t;                                                                                               \
      while ((t = t >> 8)) {                                                                                           \
        *dest++ = (char)--t;                                                                                           \
        bytes++;                                                                                                       \
      }                                                                                                                \
      *tag = T + 60 + bytes;                                                                                           \
    }                                                                                                                  \
  } while (0)

#define put_1_n(a) put_tag_n(0x80, a)

#define put_same_diff(s, d) put_tag_n(0xc0, (s << 1) + d)

/* liefert Anzahl Bytes nach Kompression oder -1 bei Fehler */

int32_t lc2_compress(char *dest, int32_t *src, int32_t num) {

  int32_t last = 0;
  char *p = dest;

  while (num) {
    uint32_t d = *src - last;
    int32_t same = 0;
    int32_t i = 1;

    if (d < 2) {
      while (i < num && *(src + i) == last)
        i++;
    }
    same = i - 1;

    if (same >= 3) {

      put_same_diff((same - 3), d);
      src += i;
      num -= i;

    } else {

      int32_t encodetmp;
      uint32_t a;
      int32_t s0 = *src;

      a = encode(s0 - last);

      if (fitsinto(a, 3) && (num >= 2)) {
        int32_t s1 = *(src + 1);
        uint32_t b = encode(s1 - last);

        if (fitsinto(a | b, 2) && (num >= 3)) {
          int32_t s2 = *(src + 2);
          uint32_t c = encode(s2 - last);

          if (fitsinto(/*a|b|*/ c, 2)) {
            put_3_2(a, b, c);
            src += 3;
            num -= 3;
            last = s2;
            continue;
          }
        }
        if (fitsinto(/*a|*/ b, 3)) {
          put_2_3(a, b);
          src += 2;
          num -= 2;
          last = s1;
          continue;
        }
      }
      put_1_n(a);
      src++;
      num--;
      last = s0;
      continue;
    }
  }

  return (dest - p);
}

#define decode(i) (((i)&1) ? ~((uint32_t)(i) >> 1) : ((uint32_t)(i) >> 1))

#define bitextract(i, p, l) (((i) >> p) & ((1 << (l)) - 1))

int32_t lc2_uncompress(int32_t *dest, char *src, int32_t num) {

  int32_t last = 0;
  int32_t nleft = num;

  while (nleft) {
    int32_t i;
    unsigned char t = *src++;

    if (t & 0x80) {

      int32_t n = t & 0x3f;
      if (n > 59) {
        int32_t bytes = n - 59;

        n = 59;
        for (i = 0; i < bytes; i++) {
          unsigned char b = *src++;
          int32_t s = i << 3;
          n += (b + 1) << s;
        }
      }
      if (t & 0x40) {
        int32_t diff = bitextract(n, 0, 1);
        int32_t same = (n >> 1) + 3;
        *dest++ = last + diff;
        nleft -= same;
        if (nleft <= 0)
          return -1;
        while (same--)
          *dest++ = last;
      } else {
        *dest++ = (last += decode(n));
      }
      nleft--;

    } else if (t & 0x40) {

      nleft -= 2;
      if (nleft < 0)
        return -1;
      {
        i = bitextract(t, 0, 3);
        *dest++ = last + decode(i);
        i = bitextract(t, 3, 3);
        *dest++ = (last += decode(i));
      }

    } else {

      nleft -= 3;
      if (nleft < 0)
        return -1;
      {
        i = bitextract(t, 0, 2);
        *dest++ = last + decode(i);
        i = bitextract(t, 2, 2);
        *dest++ = last + decode(i);
        i = bitextract(t, 4, 2);
        *dest++ = (last += decode(i));
      }
    }
  }

  return num;
}

uint32_t lc2_comprlinelenmax(uint32_t col) { return ((col * 5) + 3) & -4; }
