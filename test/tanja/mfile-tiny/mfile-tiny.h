/* 
 * mfile-tiny - simple routines to read lc2-compressed spectra
 *
 * Extracted from libmfile, Copyright (C) 1992 Stefan Esser
 *
 * WARNING: This file is *not* GPL-licensed.
 *
 */

#ifndef __MFILE_TINY_H__
#define __MFILE_TINY_H__

#include <sys/types.h>

#define MAGIC_LC 0x80FFFF10

typedef unsigned int u_int;

typedef struct {
  u_int         magic;
  u_int         version;
  u_int         levels, lines, columns;
  u_int         poslentablepos;
  u_int         freepos, freelistpos;
  u_int         used, free;
  u_int         status;
} lc_header;

typedef struct {
  u_int         pos,len;
} lc_poslen;

extern int read_lc_header(int fhand, lc_header *head);
lc_header *alloc_lc_header(void);
void free_lc_header(lc_header *head);

extern lc_poslen *alloc_and_read_poslen_tbl(int fhand, lc_header *head);
extern int read_poslen_tbl(int fhand, lc_header *head, lc_poslen *poslen_tbl);
extern lc_poslen *alloc_poslen_tbl(lc_header *head);
extern void free_poslen_tbl(lc_poslen *poslen);

extern int check_lc2(lc_header *head);

extern int read_cspec(int fhand, int idx, lc_poslen *poslen_tbl, char *cspec);
extern char *alloc_and_read_cspec(int fhand, int idx, lc_poslen *poslen_tbl);
extern char *alloc_cspec(int idx, lc_poslen *poslen_tbl);
extern void free_cspec(char *cspec);

extern int *read_spec(int fhand, int idx, lc_header *head, lc_poslen *poslen_tbl);
extern int *alloc_spec(int cols);
extern void free_spec(int *spec);

extern int lc2_uncompress(int *dest, char *src, int num);

#endif
