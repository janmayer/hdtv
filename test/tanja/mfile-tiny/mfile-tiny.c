/* 
 * mfile-tiny - simple routines to read lc2-compressed spectra
 *
 * Extracted from libmfile, Copyright (C) 1992 Stefan Esser
 *
 * WARNING: This file is *not* GPL-licensed.
 *
 */

#include "mfile-tiny.h"
#include <stdlib.h>
#include <unistd.h>

int read_lc_header(int fhand, lc_header *head)
{
  if(lseek(fhand, 0, SEEK_SET) < 0)
	return -1;

  if(read(fhand, (void *) head, sizeof(lc_header)) != sizeof(lc_header))
	return -1;
  
  return 0;
}

lc_header *alloc_lc_header(void)
{
	return (lc_header *)malloc(sizeof(lc_header));
}

void free_lc_header(lc_header *head)
{
	free(head);
}

int read_poslen_tbl(int fhand, lc_header *head, lc_poslen *poslen_tbl)
{
  int tbl_size = head->lines * head->levels * sizeof(lc_poslen);

  if(lseek(fhand, sizeof(lc_header), SEEK_SET) < 0)
	return -1;

  if(read(fhand, (void *)poslen_tbl, tbl_size) != tbl_size)
	return -1;

  return 0;
}

lc_poslen *alloc_poslen_tbl(lc_header *head)
{
  int tbl_size = head->lines * head->levels * sizeof(lc_poslen);

  return (lc_poslen *) malloc(tbl_size);
}

void free_poslen_tbl(lc_poslen *poslen_tbl)
{
  free(poslen_tbl);
}

lc_poslen *alloc_and_read_poslen_tbl(int fhand, lc_header *head)
{
  lc_poslen *poslen_tbl;

  if(!(poslen_tbl = alloc_poslen_tbl(head)))
	return NULL;

  if(read_poslen_tbl(fhand, head, poslen_tbl) < 0) {
	free_poslen_tbl(poslen_tbl);
	return NULL;
  }

  return poslen_tbl;
}

int read_cspec(int fhand, int idx, lc_poslen *poslen_tbl, char *cspec)
{
  if(lseek(fhand, poslen_tbl[idx].pos, SEEK_SET) < 0)
	return -1;

  if(read(fhand, cspec, poslen_tbl[idx].len) != poslen_tbl[idx].len)
	return -1;

  return 0;
}

char *alloc_cspec(int idx, lc_poslen *poslen_tbl)
{
  return (char *) malloc(poslen_tbl[idx].len);
}

void free_cspec(char *cspec)
{
  free(cspec);
}

char *alloc_and_read_cspec(int fhand, int idx, lc_poslen *poslen_tbl)
{
  char *cspec;

  if(!(cspec = alloc_cspec(idx, poslen_tbl)))
	return NULL;

  if(read_cspec(fhand, idx, poslen_tbl, cspec) < 0)
	return NULL;

  return cspec;
}

int *read_spec(int fhand, int idx, lc_header *head, lc_poslen *poslen_tbl)
{
  char *cspec;
  int *spec;

  cspec = alloc_and_read_cspec(fhand, idx, poslen_tbl);
  if(!cspec)
	return NULL;
  
  spec = alloc_spec(head->columns);
  if(!spec) {
	free_cspec(cspec);
	return NULL;
  }

  if(lc2_uncompress(spec, cspec, head->columns) != head->columns) {
	free_cspec(cspec);
	free_spec(spec);
	return NULL;
  }

  return spec;
}

int *alloc_spec(int cols)
{
  return (int *) malloc(cols * sizeof(int));
}

void free_spec(int *spec)
{
  free(spec);
}

int check_lc2(lc_header *head)
{
  return (head->magic == MAGIC_LC && head->version == 2);
}

#define decode(i)	( ((i) & 1) ? ~((unsigned int)(i) >> 1)		\
				    :  ((unsigned int)(i) >> 1) )

#define bitextract(i,p,l) (((i) >> p) & ((1 << (l)) -1))

int lc2_uncompress(int *dest, char *src, int num)
{
  int last = 0;
  int nleft = num;
  
  while (nleft) {
    unsigned int i;
    unsigned char t = *src++;

    if (t & 0x80) {

      int n = t & 0x3f;
      if (n > 59) {
	int bytes = n - 59;
	int i;
	n = 59;
	for (i = 0; i < bytes; i++) {
	  unsigned char b = *src++;
	  int s = i << 3;
	  n += (b + 1) << s;
	}
      }
      if (t & 0x40) {
        int diff = bitextract (n, 0, 1);
	int same = (n >> 1) +3;
	*dest++ = last + diff;
	nleft -= same;
	if (nleft <= 0) return -1;
	while (same--) *dest++ = last;
      } else {
        *dest++ = (last += decode(n));
      }
      nleft--;

    } else if (t & 0x40) {

      nleft -= 2;
      if (nleft < 0) return -1;
      {
	i = bitextract (t, 0, 3);
	*dest++ = last + decode (i);
	i = bitextract (t, 3, 3);
	*dest++ = (last += decode (i));
      }

    } else {

      nleft -= 3;
      if (nleft < 0) return -1;
      {
	i = bitextract (t, 0, 2);
	*dest++ = last + decode (i);
	i = bitextract (t, 2, 2);
	*dest++ = last + decode (i);
	i = bitextract (t, 4, 2);
	*dest++ = (last += decode (i));
      }
    }

  }
  return num;
}
