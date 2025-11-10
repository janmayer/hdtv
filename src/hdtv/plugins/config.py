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

import re

from prompt_toolkit.completion import WordCompleter

import hdtv.cmdline
import hdtv.options
import hdtv.util


def ConfigSet(args):
    try:
        hdtv.options.Set(args.variable, args.value)
    except KeyError:
        raise hdtv.cmdline.HDTVCommandAbort(args.variable + ": no such option")
    except ValueError as err:
        raise hdtv.cmdline.HDTVCommandAbort(
            f"Invalid value ({args.value}) for option {args.variable}. {err}"
        )


def ConfigShow(args):
    if args.variable:
        try:
            hdtv.ui.msg(html=hdtv.options.Show(args.variable))
        except KeyError:
            hdtv.ui.warning(args.variable + ": no such option")
    else:
        hdtv.ui.msg(html=hdtv.options.Str(), end="")


def ConfigReset(args):
    if args.variable:
        if args.variable == "all":
            hdtv.options.ResetAll()
            hdtv.ui.debug("All configuration variables were reset.")
        else:
            try:
                hdtv.options.Reset(args.variable)
                hdtv.ui.debug("Reset configuration variable " + args.variable)
            except KeyError:
                hdtv.ui.warning(args.variable + ": no such option")
    else:
        hdtv.ui.msg(hdtv.options.Str(), end="")


config_var_completer = WordCompleter(
    hdtv.options.OptionManager.__dict__.keys(),
    pattern=re.compile(r"^([^\s]+)"),
)

prog = "config set"
description = "Set a configuration variable"
parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
parser.add_argument("variable")
parser.add_argument("value")
hdtv.cmdline.AddCommand(
    prog, ConfigSet, level=2, parser=parser, completer=config_var_completer
)

prog = "config show"
description = "Show the configuration or a single configuration variable"
parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
parser.add_argument("variable", nargs="?", default=None)
hdtv.cmdline.AddCommand(
    prog, ConfigShow, level=1, parser=parser, completer=config_var_completer
)

prog = "config reset"
description = "Reset a single configuration variable"
parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
parser.add_argument(
    "variable",
    nargs="?",
    default=None,
    help="Name of the variable to reset. Use 'all' to reset all configuration variables.",
)
hdtv.cmdline.AddCommand(
    prog, ConfigReset, level=2, parser=parser, completer=config_var_completer
)

hdtv.ui.debug("Loaded user interface for configuration variables")
