#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include "mfile-tiny.h"

const int sumChannels = 16384;

double Ch2E(double ch, double *shift, double *cal)
{
  double s_ch;
  s_ch = shift[0] + shift[1] * ch;
  return cal[0] + (cal[1] + (cal[2] + (cal[3]) * s_ch) * s_ch) * s_ch;
}

double *allocSum(void)
{
  double *sum;
  int i;
  
  sum = (double *)malloc(sumChannels * sizeof(double));
  for(i=0; i<sumChannels; i++) {
    sum[i] = 0;
  }
  
  return sum;
}
void freeSum(double *sum)
{
  free(sum);
}

int readCal(double *cal, char *fname)
{
  FILE *calFile;
  double value;
  int i=0;
  
  calFile = fopen(fname, "r");
  if(!calFile) {
    fprintf(stderr, "Error opening calibration file\n");
    return -1;
  }
  
  while(fscanf(calFile, "%lf", &value) != EOF) {
    if(i < 4) {
      cal[i++] = value;
    } else {
      i = 1000;
      break;
    }
  }
  
  if(i != 4) {
    fprintf(stderr, "Format error while reading calibration\n");
    fclose(calFile);
    return -1;
  }
  
  if(fclose(calFile) < 0) {
    fprintf(stderr, "Error closing calibration file\n");
    return -1;
  }
  
  return 0;
}

int readShift(double *cal, char *fname)
{
  FILE *calFile;
  double value[6];
  int i=0;
  
  calFile = fopen(fname, "r");
  if(!calFile) {
    fprintf(stderr, "Error opening shift file\n");
    return -1;
  }
  
  while(fscanf(calFile, "%lf %lf", &value[i], &value[i+1]) != EOF) {
    i += 2;
    if(i > 4)
      break;
  }
  
  if(i != 4) {
    fprintf(stderr, "Format error while reading shifts\n");
    fclose(calFile);
    return -1;
  }
  
  if(fclose(calFile) < 0) {
    fprintf(stderr, "Error closing shift file\n");
    return -1;
  }
  
  cal[1] = (value[3] - value[1]) / (value[2] - value[0]);
  cal[0] = value[1] - cal[1] * value[0];
  
  return 0;
}

int main(int argc, char **argv)
{
  double *sum;
  double cal[4];
  double shift[2];
  FILE *runFile;
  int run;
  char fileName[256];
  
  if(argc != 4) {
    fprintf(stderr, "Usage: %s <det> <pr_det> <runs>\n", argv[0]);
    return -1;
  }
  
  sum = allocSum();
  
  runFile = fopen(argv[3], "r");
  if(!runFile) {
    fprintf(stderr, "Error: failed to open runs file\n");
    freeSum(sum);
    return -1;
  }
  
  snprintf(fileName, 256, "/home/braun/Diplom/shiftfiles/%s.cal", argv[2]);
  if(readCal(cal, fileName) < 0) {
    freeSum(sum);
    fclose(runFile);
    return -1;
  }
  
  while(fscanf(runFile, "%d", &run) != EOF) {
    //printf("Info: processing run %d\n", run);
    
    snprintf(fileName, 256, "/home/braun/Diplom/shiftfiles/%04d/%s.%04d_shd", run, argv[2], run);
    if(readShift(shift, fileName) < 0) {
      freeSum(sum);
      fclose(runFile);
      return -1;
    }
  
    snprintf(fileName, 256, "/home/braun/Diplom/88Zr_angle_singles/%04d/%s.%04d", run, argv[1], run);
    if(readAndAddSpec(sum, fileName, shift, cal) < 0) {
      fclose(runFile);
      freeSum(sum);
      return -1;
    }
  }
  
  snprintf(fileName, 256, "%s.sum", argv[1]);
  if(writeSpec(sum, fileName) < 0) {
    fclose(runFile);
    freeSum(sum);
    return -1;
  }
  
  freeSum(sum);
  
  if(fclose(runFile) < 0) {
    fprintf(stderr, "Error: failed to close runs file\n");
    return -1;
  }
  
  return 0;
}

int writeSpec(double *spec, char *fname)
{
  FILE *sFile;
  int i;
  
  sFile = fopen(fname, "w");
  if(!sFile) {
    fprintf(stderr, "Error: Failed to open output file.\n");
    return -1;
  }
  
  for(i=0; i<sumChannels; i++) {
    fprintf(sFile, "%f\n", spec[i]);
  }
  
  if(fclose(sFile) != 0) {
    fprintf(stderr, "Error: fclose() failed for output file.\n");
    return -1;
  }
}

void addSpec(double *sum, int *spec, int len, double *shift, double *cal)
{
  int i,j;
  double Elow, Ehigh, counts, fac;
  int Elow_bin, Ehigh_bin;
  
  for(i=0; i<len; i++) {
    Elow = Ch2E((double) i - 0.5, shift, cal);
    Ehigh = Ch2E((double) i + 0.5, shift, cal);
    
    Elow_bin = (int) (Elow * 2.0 + 0.5);
    Ehigh_bin = (int) (Ehigh * 2.0 + 0.5);
    
    counts = (double) spec[i];
    
    if(Elow_bin < sumChannels && Ehigh_bin > 0) {
      if(Elow_bin == Ehigh_bin) {
        sum[Elow_bin] += counts;
      } else {
        if(Elow_bin >= 0) {
          fac = (((double) Elow_bin / 2.0 + 0.25) - Elow) / (Ehigh - Elow);
          sum[Elow_bin] += counts * fac;
        } else {
          Elow_bin = -1;
        }
      
        if(Ehigh_bin < sumChannels) {
          fac = (Ehigh - ((double) Ehigh_bin / 2.0 - 0.25)) / (Ehigh - Elow);
          sum[Ehigh_bin] += counts * fac;
        } else {
          Ehigh_bin = sumChannels;
        }
    
        fac = 0.5 / (Ehigh - Elow);
        for(j=Elow_bin+1; j<Ehigh_bin; j++)
          sum[j] += counts * fac;
      }
    }
  }
}

int readAndAddSpec(double *sum, char *fname, double *shift, double *cal)
{
  int f;
  struct stat stat;
  lc_header head;
  lc_poslen *poslen_tbl;
  int *spec;
  
  int i;

  f = open(fname, O_RDONLY);
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
  
  addSpec(sum, spec, head.columns, shift, cal);
  
  free_spec(spec);

  return 0;
}
