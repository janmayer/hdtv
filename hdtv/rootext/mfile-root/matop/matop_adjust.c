/*
 * Copyright (c) 1992-2008, Stefan Esser <se@ikp.uni-koeln.de>
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *      * Redistributions of source code must retain the above copyright notice,
 *        this list of conditions and the following disclaimer.
 *      * Redistributions in binary form must reproduce the above copyright
 *        notice, this list of conditions and the following disclaimer in the
 *        documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.
 * IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/*
 * This code was derived from the matop package, the license of which is
 * reproduced above.
 *
 * Adapted for HDTV by Norbert Braun, 2010.
 */

#include "matop_adjust.h"

int matop_adjustfmts(MFILE *matw, MFILE *matr) {

  minfo infor;
  minfo infow;

  mgetinfo(matr, &infor);
  mgetinfo(matw, &infow);

  if (infow.levels && infow.lines && infow.columns) {
    infor.levels = infow.levels;
    infor.lines = infow.lines;
    infor.columns = infow.columns;
    return msetinfo(matr, &infor);
  } else {
    infow.levels = infor.levels;
    infow.lines = infor.lines;
    infow.columns = infor.columns;
    return msetinfo(matw, &infow);
  }
}

int matop_adjustfmts_trans(MFILE *matw, MFILE *matr) {

  minfo infor;
  minfo infow;

  mgetinfo(matr, &infor);
  mgetinfo(matw, &infow);

  if (infow.levels && infow.lines && infow.columns) {
    infor.levels = infow.levels;
    infor.lines = infow.columns;
    infor.columns = infow.lines;
    return msetinfo(matr, &infor);
  } else {
    infow.levels = infor.levels;
    infow.lines = infor.columns;
    infow.columns = infor.lines;
    return msetinfo(matw, &infow);
  }
}

int matop_adjustfmts_prx(MFILE *matw, MFILE *matr) {

  minfo infor;
  minfo infow;

  mgetinfo(matr, &infor);
  mgetinfo(matw, &infow);

  if (infor.levels > 2)
    return -1; // FIXME

  infow.levels = infor.levels;
  infow.lines = 1;
  infow.columns = infor.columns;

  return msetinfo(matw, &infow);
}

int matop_adjustfmts_pry(MFILE *matw, MFILE *matr) {

  minfo infor;
  minfo infow;

  mgetinfo(matr, &infor);
  mgetinfo(matw, &infow);

  if (infor.levels > 2)
    return -1; // FIXME

  infow.levels = infor.levels;
  infow.lines = 1;
  infow.columns = infor.lines;

  return msetinfo(matw, &infow);
}
