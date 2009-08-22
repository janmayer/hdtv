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
# Write and Read Fitlist saved in xml format
# 
#-------------------------------------------------------------------------------

import __main__
import hdtv.cmdline
import hdtv.fitxml 
if not hasattr(__main__, "spectra"):
    import hdtv.drawable
    __main__.spectra = hdtv.drawable.DrawableCompound(__main__.window.viewport)
__main__.fitxml = hdtv.fitxml.FitXml(__main__.spectra)


def WriteFitlist(args, options):
    fname = os.path.expanduser(args[0])
    
    


prog = "fit write"
description = "write fits to xml file"
usage = "%prog filename"
parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
parser.add_option("-s", "--spectrum", action = "store", default = "all",
                        help = "for which the fits should be saved (default=all)")
hdtv.cmdline.AddCommand(prog, lambda args, options: __main__.fitxml.WriteFitlist(args[0]), 
                        nargs=1, fileargs=True, parser=parser)

prog = "fit read"
description = "read fits from xml file"
usage ="%prog filename"
parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
hdtv.cmdline.AddCommand("fit read", lambda args, options: __main__.fitxml.ReadFitlist(args[0]), 
                    nargs=1, fileargs=True, parser=parser)

print "loaded fitlist plugin"
