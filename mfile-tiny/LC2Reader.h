#include <TH1.h>
#include "mfile-tiny.h"

enum EReadError {
	kSuccess = 0,
	kRuntimeError = -1,
	kIOError = -2,
	kMemError = -3
};

class LC2Reader {
 public:
  LC2Reader();
  ~LC2Reader();
  int Open(char *filename);
  int Close(void);
  int Probe(void);
  int GetNumBins(void);
  int Fill(TH1 *hist, int idx=0);
  
 private:
  int handle;
  lc_header *header;
  lc_poslen *poslen_tbl;
};
