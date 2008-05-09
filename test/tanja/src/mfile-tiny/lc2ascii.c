#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include "mfile-tiny.h"

#define ASCII_FNAME_MAX_LEN 1024

void print_usage(char *progname)
{
  fprintf(stderr, "%s -- Program to convert spectra from LC2 to ASCII\n", progname);
  fprintf(stderr, "This program contains code from the mfile library.\n\n");
  fprintf(stderr, "Usage: %s [-f] [-q] [-h] <specfile> [<specfile>, ...]\n", progname);
  fprintf(stderr, "<specfile> is a spectrum in LC2 format.\nThe ASCII spectrum is named <specfile>.asc\n\n");
  fprintf(stderr, "-f: Overwrite ASCII file if it already exists\n");
  fprintf(stderr, "-q: Quiet operation\n");
  fprintf(stderr, "-h: Help (this text)\n");
}

int main(int argc, char **argv)
{
  int overwrite_flag = 0, quiet_flag = 0, help_flag = 0;
  int c;
  int i;
  int channels;
  char ascii_fname[ASCII_FNAME_MAX_LEN];
  char *lc2_fname;
  int err_count = 0;
  
  if(argc == 0) {
    fprintf(stderr, "argc == 0 ?! This should not happen!\n");
    return -1;
  }
  
  while((c = getopt(argc, argv, "fqh")) != -1) {
    switch(c) {
      case 'f':
        overwrite_flag = 1;
        break;
      case 'q':
      	quiet_flag = 1;
      	break;
      case 'h':
        help_flag = 1;
        break;
    }
  }
  
  if(help_flag || optind >= argc) {
    print_usage(argv[0]);
    return 0;
  }
  
  for(i=optind; i<argc; i++) {
    lc2_fname = argv[i];
    if(snprintf(ascii_fname, ASCII_FNAME_MAX_LEN, "%s.asc", lc2_fname) >= ASCII_FNAME_MAX_LEN) {
      fprintf(stderr, "%s: Error: Destination filename too long (increase ASCII_FNAME_MAX_LEN in the program code)\n", lc2_fname);
      err_count ++;
    } else {
      channels = convert(lc2_fname, ascii_fname, overwrite_flag);
      if(channels < 0) {
        err_count ++;
      } else if(!quiet_flag) {
        printf("%s -> %s (%d channels)\n", lc2_fname, ascii_fname, channels);
      }
    }
  }
  
  if(err_count)
    fprintf(stderr, "WARNING: There were some errors!\n");
    
  return (err_count ? 0 : -1);
}

int convert(char *lc2_fname, char *ascii_fname, int overwrite)
{
  int lc2_fd;
  FILE *ascii_file;
  struct stat stat;
  lc_header head;
  lc_poslen *poslen_tbl;
  int *spec;
  
  int i;

  lc2_fd = open(lc2_fname, O_RDONLY);
  if(lc2_fd < 0) {
	fprintf(stderr, "%s: Error: open() failed on LC2 spectrum\n", lc2_fname);
	return -1;
  }

  if(read_lc_header(lc2_fd, &head) < 0 || !check_lc2(&head)) {
	fprintf(stderr, "%s: Error: Not an LC2-compressed spectrum.\n", lc2_fname);
	close(lc2_fd);
	return -1;
  }

  poslen_tbl = alloc_and_read_poslen_tbl(lc2_fd, &head);
  if(!poslen_tbl) {
	fprintf(stderr, "%s: Error: could not read index table.\n", lc2_fname);
	close(lc2_fd);
	return -1;
  }

  spec = read_spec(lc2_fd, 0, &head, poslen_tbl);
  if(!spec) {
	fprintf(stderr, "%s: Error: count not read spectrum.\n", lc2_fname);
	free_poslen_tbl(poslen_tbl);
	close(lc2_fd);
	return -1;
  }

  if(close(lc2_fd) != 0) {
    fprintf(stderr, "%s: Error: close() failed on LC2 spectrum\n", lc2_fname);
    free_poslen_tbl(poslen_tbl);
    return -1;
  }
  free_poslen_tbl(poslen_tbl);
  
  if(overwrite)
    ascii_file = fopen(ascii_fname, "w");
  else
    ascii_file = fopen(ascii_fname, "wx");
    
  if(!ascii_file) {
    if(overwrite)
      fprintf(stderr, "%s: Error: open() failed on ASCII spectrum\n", ascii_fname);
    else
      fprintf(stderr, "%s: Error: open() failed on ASCII spectrum (hint: use -f option to overwrite existing files)\n", ascii_fname);
    return -1;
  }
  
  for(i=0; i<head.columns; i++) {
	if(fprintf(ascii_file, "%d\n", spec[i]) < 0)
	  break;
  }
  
  if(i != head.columns) {
    fprintf(stderr, "%s: Error: fprintf() failed\n", ascii_fname);
    fclose(ascii_file);
    return -1;
  }
  
  if(fclose(ascii_file) != 0) {
    fprintf(stderr, "%s: Error: fclose() failed on ASCII spectrum\n");
    return -1;
  }

  free_spec(spec);

  return head.columns;
}
