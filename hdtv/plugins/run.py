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
Plugin for executing a python script from the command line
"""

import os

import hdtv.cmdline
import hdtv.ui


def run(args):
    """
    Executes a python script from the hdtv command line (via execfile)
    """
    fname = os.path.expanduser(args[0])
    try:
        with open(fname) as f:
            hdtv.ui.msg("Running script %s" % fname)
            exec(compile(f.read(), fname, "exec"))
            hdtv.ui.msg("Finished!")
    except OSError as err:
        hdtv.ui.error(str(err))


hdtv.cmdline.AddCommand("run", run, nargs=1, fileargs=True)

hdtv.ui.debug("Loaded run plugin")
