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

#ifndef __MFileRoot_h__
#define __MFileRoot_h__

#include <mfile.h>

class MFile {
public:
  explicit MFile(const char *fname = nullptr, const char *mode = "r");
  ~MFile();

  bool IsZombie() { return fZombie; }
  bool IsNull() { return fFile == nullptr; }
  MFILE *File() { return fFile; }
  explicit operator MFILE *() { return fFile; }

private:
  bool fZombie;
  MFILE *fFile;
};

#endif
