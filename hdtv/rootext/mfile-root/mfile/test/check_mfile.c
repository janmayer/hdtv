#include "mfile.h"

#define SIZE 1024
#define FAILURE -1
#define SUCCESS 0

int columns;

minfo info;

/* Compare two buffers */
int cmp_buffer(int *buffer, int *check_buffer, int size) {

  int i;

  for (i = 0; i < SIZE; i++) {
    if (buffer[i] != check_buffer[i]) {
      printf("Buffer[%d] = %d = %d\n", i, buffer[i], check_buffer[i]);
      printf("Comparing buffers failed\n");
      return FAILURE;
    }
  }
  return SUCCESS;
}

int write_test_spectra(char *name, int *buffer, minfo mat_info) {

  MFILE *dest = mopen(name, "w");
  int lin, lev;
  int ret = SUCCESS;
  printf("Writing spectrum %s\n", name);

  if (msetinfo(dest, &mat_info) != 0) {
    printf("msetinfo failed for:%s\n", name);
    return FAILURE;
  }
  for (lev = 0; lev < info.levels; lev++)
    for (lin = 0; lin < info.lines; lin++) {
      mputint(dest, buffer, lev, lin, 0, mat_info.columns);
    }
  mclose(dest);
  return ret;
}

int read_test_spectra(char *name, int *buffer) {

  MFILE *src = mopen(name, "r");
  int lin, lev;
  int ret = SUCCESS;
  minfo this_mat_info;

  if (mgetinfo(src, &this_mat_info) != 0) {
    printf("mgetinfo failed for:%s\n", name);
    return FAILURE;
  }
  for (lev = 0; lev < info.levels; lev++)
    for (lin = 0; lin < info.lines; lin++) {
      mgetint(src, buffer, lev, lin, 0, this_mat_info.columns);
    }

  mclose(src);

  return ret;
}

int test_spectra_rw(char *name, int *buffer, minfo mat_info) {

  int i;
  int ret = SUCCESS;
  int check_buffer[SIZE];

  for (i = 0; i < SIZE; i++)
    check_buffer[i] = 0;

  if (write_test_spectra(name, buffer, mat_info) != SUCCESS) {
    printf("Write of spectra %s failed\n", name);
    ret = FAILURE;
  }
  if (read_test_spectra(name, check_buffer) != SUCCESS) {
    printf("Read of spectra %s failed\n", name);
    ret = FAILURE;
  }
  if (cmp_buffer(buffer, check_buffer, SIZE) != SUCCESS) {
    printf("Read/Write of spectra %s failed\n", name);
    ret = FAILURE;
  }

  return ret;
}

int main(void) {
  int i;
  int return_code = SUCCESS;
  int buffer[SIZE];

  /* Make a buffer for test spectra */
  for (i = 0; i < SIZE; i++)
    buffer[i] = 2 * i;

  info.lines = 1;
  info.levels = 1;
  info.columns = SIZE;
  printf("lines= %d\n", info.lines);
  printf("levels= %d\n", info.levels);
  printf("columns= %d\n", info.columns);

  info.filetype = MAT_TXT;
  return_code += test_spectra_rw("test_txt.spe", buffer, info);
  info.filetype = MAT_LC;
  return_code += test_spectra_rw("test_lc.spe", buffer, info);
  info.filetype = MAT_GF2;
  return_code += test_spectra_rw("test_gf2.spe", buffer, info);
  info.filetype = MAT_HGF2;
  return_code += test_spectra_rw("test_hgf2.spe", buffer, info);
  info.filetype = MAT_LE4;
  return_code += test_spectra_rw("test_le4.spe", buffer, info);
  info.filetype = MAT_HE4;
  return_code += test_spectra_rw("test_he4.spe", buffer, info);
  info.filetype = MAT_LE2S;
  return_code += test_spectra_rw("test_le2s.spe", buffer, info);
  info.filetype = MAT_HE2S;
  return_code += test_spectra_rw("test_he2s.spe", buffer, info);
  /* These are not working yet */
  /*
  info.filetype = MAT_LE4T;
  return_code += test_spectra_rw("test_le4t.spe", buffer, info);
  info.filetype = MAT_HE4T;
  return_code += test_spectra_rw("test_he4t.spe", buffer, info);
  info.filetype = MAT_LE2T;
  return_code += test_spectra_rw("test_le2t.spe", buffer, info);
  */

  /* These have to be checked with float buffers */
  /*
  info.filetype = MAT_LF4;
  return_code += test_spectra_rw("test_lf4.spe", buffer, info);
  info.filetype = MAT_HF4;
  return_code += test_spectra_rw("test_hf4.spe", buffer, info);
  info.filetype = MAT_LF8;
  return_code += test_spectra_rw("test_lf8.spe", buffer, info);
  info.filetype = MAT_HF8;
  return_code += test_spectra_rw("test_hf8.spe", buffer, info);
  */
  printf("Returning %d\n", return_code);
  return return_code;
}
// END_TEST
//
//
// int
// main (void) {
//    return 0;
//}
