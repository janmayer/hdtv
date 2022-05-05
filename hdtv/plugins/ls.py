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

"""
Plugin implementing some useful hdtv commands for navigation the file system
his includes a ls-like command, by special request from R. Schulze :)
"""

import os
import stat
import glob

import hdtv.tabformat
import hdtv.cmdline
import hdtv.ui
import hdtv.util


def ls(args):
    """
    this function prints an output similar to that of the ``ls'' program
    """
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

    dirlist = sorted(dirlist, key=hdtv.util.natural_sort_key)
    hdtv.tabformat.tabformat(dirlist)


def cd(args):
    """
    change current working directory
    """
    if len(args) == 0:
        path = os.path.expanduser("~")
    elif args[0] == "-":
        path = os.environ["OLDPWD"]
    else:
        path = os.path.expanduser(args[0])
    try:
        os.environ["OLDPWD"] = os.getcwd()
        os.chdir(path)
        hdtv.ui.msg(path)
    except OSError as msg:
        hdtv.ui.msg(msg)


def pwd(args):
    """
    print name of current/working directory
    """
    hdtv.ui.msg(os.getcwd())


hdtv.cmdline.AddCommand("ls", ls, level=2, maxargs=1, dirargs=True)
hdtv.cmdline.AddCommand("cd", cd, level=2, maxargs=1, dirargs=True)
hdtv.cmdline.AddCommand("pwd", pwd, level=2, nargs=0)

hdtv.ui.debug("Loaded ls plugin")
