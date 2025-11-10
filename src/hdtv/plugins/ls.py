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

import glob
import os
from pathlib import Path

import hdtv.cmdline
import hdtv.tabformat
import hdtv.ui
import hdtv.util


def ls(args):
    """
    this function prints an output similar to that of the ``ls'' program
    """
    dirlist = []
    for pattern in args or ["."]:
        for arg in glob.glob(os.path.expanduser(pattern)):
            path = Path(arg)
            if path.is_dir():
                for fname in path.iterdir():
                    if fname.is_dir():
                        dirlist.append(f"{fname.name}/")
                    else:
                        dirlist.append(fname.name)
            else:
                dirlist.append(path.name)

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
