/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2009  The HDTV development team (see file AUTHORS)
 *
 * This file is part of HDTV.
 *
 * HDTV is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * HDTV is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
 * for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with HDTV; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
 *
 */
#include "MFileHist.hh"

#include <iostream>

#include <TArrayD.h>
#include <TH1.h>
#include <TH2.h>

const int MFileHist::ERR_SUCCESS = 0;
const int MFileHist::ERR_READ_OPEN = 1;
const int MFileHist::ERR_READ_INFO = 2;
const int MFileHist::ERR_READ_NOTOPEN = 3;
const int MFileHist::ERR_READ_BADIDX = 4;
const int MFileHist::ERR_READ_GET = 5;
const int MFileHist::ERR_READ_CLOSE = 6;
const int MFileHist::ERR_WRITE_OPEN = 7;
const int MFileHist::ERR_WRITE_INFO = 8;
const int MFileHist::ERR_WRITE_PUT = 9;
const int MFileHist::ERR_WRITE_CLOSE = 10;
const int MFileHist::ERR_INVALID_FORMAT = 11;
const int MFileHist::ERR_UNKNOWN = 12;

const char *MFileHist::GetErrorMsg(int error_nr) {
  static const char *errorDesc[] = {"No error",
                                    "Failed to open file for reading",
                                    "Failed to get info from file",
                                    "File is not open",
                                    "Bad index (level/line)",
                                    "Failed to get data from file",
                                    "Failed to close file after reading",
                                    "Failed to open file for writing",
                                    "Failed to put info into file",
                                    "Failed to put data into file",
                                    "Failed to close file after writing",
                                    "Invalid format specified",
                                    "Unknown error"};

  if (error_nr < 0 || error_nr > ERR_UNKNOWN) {
    error_nr = ERR_UNKNOWN;
  }

  return errorDesc[error_nr];
}

MFileHist::MFileHist() {
  fHist = nullptr;
  fInfo = nullptr;
  fErrno = ERR_SUCCESS;
}

MFileHist::~MFileHist() {
  delete fInfo;

  if (fHist) {
    mclose(fHist);
  }
}

int MFileHist::WriteTH1(const TH1 *hist, char *fname, char *fmt) {
  MFILE *mf;
  minfo info;
  int nbins = hist->GetNbinsX();

  mf = mopen(fname, const_cast<char *>("w"));
  if (!mf) {
    return ERR_WRITE_OPEN;
  }

  if (msetfmt(mf, fmt) != 0) {
    mclose(mf);
    return ERR_INVALID_FORMAT;
  }

  mgetinfo(mf, &info);
  info.levels = 1;
  info.lines = 1;
  info.columns = nbins;
  if (msetinfo(mf, &info) != 0) {
    mclose(mf);
    return ERR_WRITE_INFO;
  }

  TArrayD buf(nbins);
  for (int i = 0; i < nbins; i++) {
    buf[i] = hist->GetBinContent(i + 1);
  }

  if (mputdbl(mf, buf.GetArray(), 0, 0, 0, nbins) != nbins) {
    mclose(mf);
    return ERR_WRITE_PUT;
  }

  if (mclose(mf) != 0) {
    return ERR_WRITE_CLOSE;
  }

  return ERR_SUCCESS;
}

int MFileHist::WriteTH2(const TH2 *hist, char *fname, char *fmt) {
  MFILE *mf;
  minfo info;
  int nbinsx = hist->GetNbinsX();
  int nbinsy = hist->GetNbinsY();
  int col, line;

  mf = mopen(fname, const_cast<char *>("w"));
  if (!mf) {
    return ERR_WRITE_OPEN;
  }

  if (msetfmt(mf, fmt) != 0) {
    mclose(mf);
    return ERR_INVALID_FORMAT;
  }

  mgetinfo(mf, &info);
  info.levels = 1;
  info.lines = nbinsy;
  info.columns = nbinsx;
  if (msetinfo(mf, &info) != 0) {
    mclose(mf);
    return ERR_WRITE_INFO;
  }

  TArrayD buf(nbinsx);

  for (line = 0; line < nbinsy; line++) {
    for (col = 0; col < nbinsx; col++) {
      buf[col] = hist->GetBinContent(col + 1, line + 1);
    }

    if (mputdbl(mf, buf.GetArray(), 0, line, 0, nbinsx) != nbinsx) {
      break;
    }
  }

  if (line != nbinsy) {
    mclose(mf);
    return ERR_WRITE_PUT;
  }

  if (mclose(mf) != 0) {
    return ERR_WRITE_CLOSE;
  }

  return ERR_SUCCESS;
}

int MFileHist::Open(char *fname, char *fmt) {
  /* If a format is specified, we first test if the specification is valid, and
   * return an error otherwise. We then set the format for the real matrix with
   * no further error checking. This mirrors how it is done in the matconv
   * program. */
  if (fmt && msetfmt(nullptr, fmt) != 0) {
    fErrno = ERR_INVALID_FORMAT;
    return fErrno;
  }

  fHist = mopen(fname, const_cast<char *>("r"));
  if (!fHist) {
    fErrno = ERR_READ_OPEN;
    return fErrno;
  }

  if (fmt) {
    msetfmt(fHist, fmt);
  }

  fInfo = new minfo;

  if (mgetinfo(fHist, fInfo) != 0) {
    delete fInfo;
    fInfo = nullptr;

    mclose(fHist);
    fHist = nullptr;

    fErrno = ERR_READ_INFO;
    return fErrno;
  }

  fErrno = ERR_SUCCESS;
  return fErrno;
}

int MFileHist::Close() {
  delete fInfo;
  fInfo = nullptr;
  fErrno = ERR_SUCCESS;

  if (fHist && mclose(fHist) != 0) {
    fErrno = ERR_READ_CLOSE;
  }
  fHist = nullptr;

  return fErrno;
}

template <class histType>
histType *MFileHist::ToTH1(const char *name, const char *title, unsigned int level, unsigned int line) {
  histType *hist;

  if (!fHist || !fInfo) {
    fErrno = ERR_READ_NOTOPEN;
    return nullptr;
  }

  if (level >= fInfo->levels || line >= fInfo->lines) {
    fErrno = ERR_READ_BADIDX;
    return nullptr;
  }

  hist = new histType(name, title, fInfo->columns, -0.5, fInfo->columns - 0.5);

  // FillTH1 will set fErrno
  if (!FillTH1(hist, level, line)) {
    delete hist;
    return nullptr;
  }

  return hist;
}

TH1 *MFileHist::FillTH1(TH1 *hist, unsigned int level, unsigned int line) {
  if (!fHist || !fInfo) {
    fErrno = ERR_READ_NOTOPEN;
    return nullptr;
  }

  if (level >= fInfo->levels || line >= fInfo->lines) {
    fErrno = ERR_READ_BADIDX;
    return nullptr;
  }

  TArrayD buf(fInfo->columns);

  int rc = mgetdbl(fHist, buf.GetArray(), level, line, 0, fInfo->columns);
  if (rc < 0 || static_cast<unsigned int>(rc) != fInfo->columns) {
    fErrno = ERR_READ_GET;
    return nullptr;
  }

  for (unsigned int i = 0; i < fInfo->columns; i++) {
    hist->SetBinContent(i + 1, buf[i]);
  }

  fErrno = ERR_SUCCESS;
  return hist;
}

TH1D *MFileHist::ToTH1D(const char *name, const char *title, unsigned int level, unsigned int line) {
  return ToTH1<TH1D>(name, title, level, line);
}

TH1I *MFileHist::ToTH1I(const char *name, const char *title, unsigned int level, unsigned int line) {
  return ToTH1<TH1I>(name, title, level, line);
}

double *MFileHist::FillBuf1D(double *buf, unsigned int level, unsigned int line) {
  if (!fHist || !fInfo) {
    fErrno = ERR_READ_NOTOPEN;
    return nullptr;
  }

  if (level >= fInfo->levels || line >= fInfo->lines) {
    fErrno = ERR_READ_BADIDX;
    return nullptr;
  }

  int rc = mgetdbl(fHist, buf, level, line, 0, fInfo->columns);
  if (rc < 0 || static_cast<unsigned int>(rc) != fInfo->columns) {
    fErrno = ERR_READ_GET;
    return nullptr;
  }

  fErrno = ERR_SUCCESS;
  return buf;
}

TH2 *MFileHist::FillTH2(TH2 *hist, unsigned int level) {
  unsigned int line, col;

  if (!fHist || !fInfo) {
    fErrno = ERR_READ_NOTOPEN;
    return nullptr;
  }

  if (level >= fInfo->levels) {
    fErrno = ERR_READ_BADIDX;
    return nullptr;
  }

  TArrayD buf(fInfo->columns);

  for (line = 0; line < fInfo->lines; line++) {
    int rc = mgetdbl(fHist, buf.GetArray(), level, line, 0, fInfo->columns);
    if (rc < 0 || static_cast<unsigned int>(rc) != fInfo->columns) {
      break;
    }

    for (col = 0; col < fInfo->columns; col++) {
      hist->SetBinContent(col + 1, line + 1, buf[col]);
    }
  }

  if (line != fInfo->lines) {
    fErrno = ERR_READ_GET;
    return nullptr;
  }

  fErrno = ERR_SUCCESS;
  return hist;
}

template <class histType> histType *MFileHist::ToTH2(const char *name, const char *title, unsigned int level) {
  histType *hist;

  if (!fHist || !fInfo) {
    fErrno = ERR_READ_NOTOPEN;
    return nullptr;
  }

  if (level >= fInfo->levels) {
    fErrno = ERR_READ_BADIDX;
    return nullptr;
  }

  hist = new histType(name, title, fInfo->columns, -0.5, fInfo->columns - 0.5, fInfo->lines, -0.5, fInfo->lines - 0.5);

  // FillTH2 will set fErrno
  if (!FillTH2(hist, level)) {
    delete hist;
    return nullptr;
  }

  return hist;
}

TH2D *MFileHist::ToTH2D(const char *name, const char *title, unsigned int level) {
  return ToTH2<TH2D>(name, title, level);
}

TH2I *MFileHist::ToTH2I(const char *name, const char *title, unsigned int level) {
  return ToTH2<TH2I>(name, title, level);
}
