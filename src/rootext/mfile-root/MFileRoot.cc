/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2010  The HDTV development team (see file AUTHORS)
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

#include "MFileRoot.hh"
#include <iostream>

MFile::MFile(const char *fname, const char *mode) : fZombie(false), fFile(nullptr) {
  if (fname) {
    fFile = mopen(const_cast<char *>(fname), const_cast<char *>(mode));
    if (fFile == nullptr) {
      fZombie = true;
    }
  }
}

MFile::~MFile() {
  if (IsZombie() || IsNull()) {
    return;
  }

  if (mclose(fFile) != 0) {
    std::cerr << "WARNING: mclose() failed" << std::endl;
  }
}
