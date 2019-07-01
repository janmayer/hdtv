#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is the main HDTV application.
"""

from __future__ import print_function

import sys
import os
import glob
from pathlib import Path
import argparse

if __name__ == "__main__":
    project_dir = Path(__file__).absolute().parents[1]
    sys.path.remove(str(project_dir/"hdtv"))
    sys.path.insert(0, str(project_dir))


class App:
    def __init__(self):
        # Reset command line arguments so that ROOT does not stumble about them
        hdtv_args = sys.argv[1:]
        sys.argv = [sys.argv[0]]

        # Get config and data directory
        self.legacypath = Path.home()/".hdtv"
        self.configpath = os.getenv("HDTV_USER_PATH",
            self.legacypath if self.legacypath.is_dir() else
            Path(os.getenv("XDG_CONFIG_HOME",
                Path.home()/".config"))/"hdtv")
        self.datapath = os.getenv("HDTV_USER_PATH",
            self.legacypath if self.legacypath.is_dir() else
            Path(os.getenv("XDG_DATA_HOME",
                Path.home()/".local/share"))/"hdtv")

        for path in [self.datapath, self.configpath]:
            try:
                path.mkdir(parents=True)
            except OSError:
                pass

        if not os.access(self.datapath, os.W_OK):
            print("ERROR: data path {} is not writable".format(
                self.datapath), file=sys.stderr)

        if not os.access(self.configpath, os.R_OK):
            print("ERROR: Could not access config path " + configpath, file=sys.stderr)

        os.environ["HDTV_USER_PATH"] = str(self.configpath)
        sys.path.append(self.configpath)
        sys.path.append(self.configpath/"plugins")

        args = self.parse_args(hdtv_args)

        if args.rebuildusr:
            import hdtv.rootext.dlmgr
            hdtv.rootext.dlmgr.RebuildLibraries(hdtv.rootext.dlmgr.usrlibdir)
        if args.rebuildsys:
            import hdtv.rootext.dlmgr
            hdtv.rootext.dlmgr.RebuildLibraries(hdtv.rootext.dlmgr.syslibdir)

        if args.rebuildusr or args.rebuildsys:
            sys.exit(0)

        # Import core modules
        import hdtv.cmdline
        import hdtv.session
        import hdtv.ui


        hdtv.cmdline.SetHistory(self.datapath/"hdtv_history")
        hdtv.cmdline.SetInteractiveDict(locals())
        spectra = hdtv.session.Session()
        import __main__
        __main__.spectra = spectra

        # Import core plugins
        import hdtv.plugins.textInterface
        import hdtv.plugins.ls
        import hdtv.plugins.run
        import hdtv.plugins.specInterface
        import hdtv.plugins.fitInterface
        import hdtv.plugins.calInterface
        import hdtv.plugins.matInterface
        import hdtv.plugins.rootInterface
        import hdtv.plugins.config
        import hdtv.plugins.fitlist
        import hdtv.plugins.fittex
        import hdtv.plugins.fitmap
        import hdtv.plugins.dblookup
        import hdtv.plugins.peakfinder
        import hdtv.plugins.printing


        hdtv.ui.msg("HDTV - Nuclear Spectrum Analysis Tool")


        # Execute startup.py for user configuration in python
        try:
            import startup
        except ImportError:
            hdtv.ui.debug("No startup.py file")

        # Execute startup.hdtv and startup.hdtv.d/*.hdtv
        # for user configuration in "hdtv" language
        startup_d_hdtv = [self.configpath/"startup.hdtv"] + list(
            (self.configpath/"startup.hdtv.d").glob("*.hdtv"))

        for startup_hdtv in startup_d_hdtv:
            try:
                if os.path.exists(startup_hdtv):
                    hdtv.cmdline.command_line.ExecCmdfile(startup_hdtv)
            except IOError as msg:
                hdtv.ui.error("Error reading %s: %s" % (startup_hdtv, msg))

        self.run_batchfile(args)
        self.run_commands(args)

        hdtv.cmdline.MainLoop()
        hdtv.plugins.rootInterface.r.rootfile = None
        hdtv.cmdline.command_tree.SetDefaultLevel(1)

    def parse_args(self, args):
        import hdtv.version
        parser = argparse.ArgumentParser()
        parser.add_argument("-b", "--batch", dest="batchfile",
            help="Open and execute HDTV batchfile")
        parser.add_argument("-e", "--execute", dest="commands",
            help="Execute HDTV command(s)")
        parser.add_argument("-v", "--version", action="version",
            help="Show HDTV Version",
            version="HDTV {}".format(hdtv.version.__version__))
        parser.add_argument("--rebuild-usr", action='store_true', dest='rebuildusr',
            help='Rebuild ROOT-loadable libraries for the current user')
        parser.add_argument("--rebuild-sys", action='store_true', dest='rebuildsys',
            help='Rebuild ROOT-loadable libraries for all users')
        return parser.parse_args(args)

    def run_commands(self, args):
        """Execute commands given on command line"""
        import hdtv.cmdline

        if args.commands is not None:
            hdtv.cmdline.command_line.DoLine(args.commands)

    def run_batchfile(self, args):
        """Execute batchfile given on command line"""
        import hdtv.cmdline
        import hdtv.ui

        try:
            if args.batchfile is not None:
                hdtv.cmdline.command_line.ExecCmdfile(args.batchfile)
        except IOError as msg:
            hdtv.ui.msg("Error reading %s: %s" % (args.batchfile, msg))


if __name__ == "__main__":
    App()
