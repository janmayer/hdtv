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

from __future__ import print_function

import hdtv.options
import hdtv.cmdline
import hdtv.util
from hdtv.color import tcolors


def ConfigVarCompleter(text, args=None):
    return hdtv.util.GetCompleteOptions(
        text, iter(hdtv.options.variables.keys()))


def ConfigSet(args):
    try:
        hdtv.options.Set(args.variable, args.value)
    except KeyError:
        raise hdtv.cmdline.HDTVCommandAbort(args.variable + ": no such option")
    except ValueError as err:
        raise hdtv.cmdline.HDTVCommandAbort("Invalid value (%s) for option %s. %s" % (args.value, args.variable, err))


def ConfigShow(args):
    if args.variable:
        try:
            hdtv.ui.msg(hdtv.options.Show(args.variable))
        except KeyError:
            hdtv.ui.warn(args.variable + ": no such option")
    else:
        print(hdtv.options.Str(), end='')


def ConfigReset(args):
    if args.variable:
        if args.variable == 'all':
            hdtv.options.ResetAll()
            hdtv.ui.debug("All configuration variables were reset.")
        else:
            try:
                hdtv.options.Reset(args.variable)
                hdtv.ui.debug("Reset configuration variable " + args.variable)
            except KeyError:
                hdtv.ui.warn(args.variable + ": no such option")
    else:
        hdtv.ui.msg(hdtv.options.Str(), newline=False)

prog = "config set"
description = "Set a configuration variable"
parser = hdtv.cmdline.HDTVOptionParser(
    prog=prog, description=description)
parser.add_argument("variable")
parser.add_argument("value")
hdtv.cmdline.AddCommand(prog, ConfigSet, level=2, parser=parser,
    completer=ConfigVarCompleter)

prog = "config show"
description = "Show the configuration or a single configuration variable"
parser = hdtv.cmdline.HDTVOptionParser(
    prog=prog, description=description)
parser.add_argument("variable", nargs='?', default=None)
hdtv.cmdline.AddCommand(prog, ConfigShow, level=1, parser=parser,
    completer=ConfigVarCompleter)

prog = "config reset"
description = "Reset a single configuration variable"
parser = hdtv.cmdline.HDTVOptionParser(
    prog=prog, description=description)
parser.add_argument(
    "variable",
    nargs='?',
    default=None,
    help='Name of the variable to reset. Use \'all\' to reset all configuration variables.')
hdtv.cmdline.AddCommand(prog, ConfigReset, level=2, parser=parser,
    completer=ConfigVarCompleter)

hdtv.ui.debug("Loaded user interface for configuration variables")
