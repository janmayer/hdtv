#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include "mfile-tiny.h"

int main()
{
  int f;
  struct stat stat;
  lc_header head;
  lc_poslen *poslen_tbl;
  int *spec;
  
  int i;

  f = open("ge9.0073", O_RDONLY);
  if(f < 0) {
	fprintf(stderr, "Error: open() failed.\n");
	return -1;
  }

  if(read_lc_header(f, &head) < 0 || !check_lc2(&head)) {
	fprintf(stderr, "Error: Not an LC2-compressed spectrum.\n");
	close(f);
	return -1;
  }

  poslen_tbl = alloc_and_read_poslen_tbl(f, &head);
  if(!poslen_tbl) {
	fprintf(stderr, "Error: could not read index table.\n");
	close(f);
	return -1;
  }

  spec = read_spec(f, 0, &head, poslen_tbl);
  if(!spec) {
	fprintf(stderr, "Error: count not read spectrum.\n");
	free_poslen_tbl(poslen_tbl);
	close(f);
	return -1;
  }

  close(f);
  free_poslen_tbl(poslen_tbl);
  
  for(i=0; i<head.columns; i++) {
	printf("%d\n", spec[i]);
  }

  free_spec(spec);

  return 0;
}
