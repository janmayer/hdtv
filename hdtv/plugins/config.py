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

import hdtv.options
import hdtv.cmdline
import hdtv.util

def ConfigVarCompleter(text, args=None):
    return hdtv.util.GetCompleteOptions(text, hdtv.options.variables.iterkeys())

def ConfigSet(args):
    try:       
        hdtv.options.Set(args[0], args[1])
    except KeyError:
        print "%s: no such option" % args[0]
    except ValueError:
        print "Invalid value (%s) for option %s" % (args[1], args[0])

def ConfigShow(args):
    if len(args) == 0:
        print hdtv.options.Str(),
    else:
        try:
            print hdtv.options.Show(args[0])
        except KeyError:
            print "%s: no such option" % args[0]
    
def ConfigReset(args):
    if len(args) == 0:
        print hdtv.options.Str(),
    else:
        try:
            hdtv.options.Reset(args[0])
        except KeyError:
            print "%s: no such option" % args[0]


hdtv.cmdline.AddCommand("config set", ConfigSet, nargs=2, level=2,
                        usage="%prog <variable> <value>",
                        completer=ConfigVarCompleter)
hdtv.cmdline.AddCommand("config show", ConfigShow, maxargs=1, level=2,
                        usage="%prog [variable]",
                        completer=ConfigVarCompleter)
hdtv.cmdline.AddCommand("config reset", ConfigReset, maxargs=1, level=2,
                        usage="%prog [variable]",
                        completer=ConfigVarCompleter)
                        
print "Loaded user interface for configuration variables"
