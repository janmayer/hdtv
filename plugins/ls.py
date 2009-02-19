# -*- coding: utf-8 -*-

# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2009  The HDTV development team (see file AUTHORS)
#
# This file is part of HDTV.
#
# HDTV is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# HDTV is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with HDTV; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

#-------------------------------------------------------------------------------
# Plugin implementing an ls-like command for the HDTV command line, by special
# request from R. Schulze :)
#-------------------------------------------------------------------------------

import hdtv.tabformat
import hdtv.cmdline
import os
import stat
import glob

def ls(args):
	"This function prints an output similar to that of the ``ls'' program"
	if len(args) > 0:
		pattern = os.path.expanduser(args[0])
	else:
		pattern = "*"
	
	dirlist = []
	for fname in glob.glob(pattern):
		# For broken symlinks, os.stat may fail.
		# We simply add them to the list, without
		# knowing more about them.
		try:
			mode = os.stat(fname)[stat.ST_MODE]
			if stat.S_ISDIR(mode):
				dirlist.append(fname + "/")
			else:
				dirlist.append(fname)
		except OSError:
			dirlist.append(fname)
	
	dirlist.sort()
	hdtv.tabformat.tabformat(dirlist)
	
hdtv.cmdline.AddCommand("ls", ls, maxargs=1, dirargs=True)
