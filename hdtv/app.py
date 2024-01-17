#!/usr/bin/env python3

# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2019  The HDTV development team (see file AUTHORS)
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
This is the main HDTV application.
"""

import argparse
import os
import sys
from pathlib import Path

if __name__ == "__main__":
    project_dir = Path(__file__).absolute().parents[1].resolve()
    project_path = str((project_dir / "hdtv").resolve())
    if project_path in sys.path:
        sys.path.remove(project_path)
    sys.path.insert(0, str(project_dir))


def check_root_version():
    import ROOT

    version = ROOT.gROOT.GetVersion()

    if version in ["6.22/00", "6.22/02"]:
        print(
            f"Error: Unsupported ROOT version {version} detected.\n"
            "ROOT 6.22/00 and 6.22/02 are not compatible with HDTV.\n"
            "Please upgrade to ROOT 6.22/04 or later "
            "or use a different major version.\n See README.md for more information.",
        )
        exit(1)


def get_path(env: str, default: str) -> Path:
    """
    Get path used for user config and data
    """
    if user_path := os.environ.get("HDTV_USER_PATH"):
        return Path(user_path)

    legacy_path = Path.home() / ".hdtv"
    if legacy_path.exists():
        return legacy_path

    if xdg_path := os.environ.get(env):
        return Path(xdg_path) / "hdtv"

    return Path.home() / default / "hdtv"


class App:
    def __init__(self):
        # Reset command line arguments so that ROOT does not stumble about them
        hdtv_args = sys.argv[1:]
        sys.argv = [sys.argv[0]]

        # Get config and data directory
        self.configpath = get_path("XDG_CONFIG_HOME", ".config")
        self.datapath = get_path("XDG_DATA_HOME", ".local/share")

        for path in [self.datapath, self.configpath]:
            try:
                path.mkdir(parents=True)
            except OSError:
                pass

        if not os.access(self.datapath, os.W_OK):
            print(
                f"ERROR: data path {self.datapath} is not writable",
                file=sys.stderr,
            )

        if not os.access(self.configpath, os.R_OK):
            print(
                "ERROR: Could not access config path " + self.configpath,
                file=sys.stderr,
            )

        os.environ["HDTV_USER_PATH"] = str(self.configpath)
        sys.path.append(str(self.configpath))
        sys.path.append(str(self.configpath / "plugins"))

        args = self.parse_args(hdtv_args)

        if args.rebuildusr is not None:
            import hdtv.rootext.dlmgr

            hdtv.rootext.dlmgr.RebuildLibraries(
                hdtv.rootext.dlmgr.usrdir, libraries=args.rebuildusr or None
            )
        if args.rebuildsys is not None:
            import hdtv.rootext.dlmgr

            hdtv.rootext.dlmgr.RebuildLibraries(
                hdtv.rootext.dlmgr.sysdir, libraries=args.rebuildsys or None
            )

        if args.rebuildusr or args.rebuildsys:
            sys.exit(0)

        check_root_version()

        # Import core modules
        import hdtv.cmdline
        import hdtv.session
        import hdtv.ui

        hdtv.cmdline.command_line.StartEventLoop()
        hdtv.cmdline.SetHistory(self.datapath / "hdtv_history")
        hdtv.cmdline.SetInteractiveDict(locals())
        spectra = hdtv.session.Session()
        import __main__

        __main__.spectra = spectra

        # Import core plugins
        import hdtv.plugins.calInterface
        import hdtv.plugins.config
        import hdtv.plugins.dblookup
        import hdtv.plugins.fitInterface
        import hdtv.plugins.fitlist
        import hdtv.plugins.fitmap
        import hdtv.plugins.fittex
        import hdtv.plugins.ls
        import hdtv.plugins.matInterface
        import hdtv.plugins.peakfinder
        import hdtv.plugins.printing
        import hdtv.plugins.rootInterface
        import hdtv.plugins.run
        import hdtv.plugins.specInterface
        import hdtv.plugins.textInterface

        hdtv.ui.msg("HDTV - Nuclear Spectrum Analysis Tool")

        # Execute startup.py for user configuration in python
        try:
            import startup  # noqa: F401
        except ImportError:
            hdtv.ui.debug("No startup.py file")

        # Execute startup.hdtv and startup.hdtv.d/*.hdtv
        # for user configuration in "hdtv" language
        startup_d_hdtv = [self.configpath / "startup.hdtv"] + list(
            (self.configpath / "startup.hdtv.d").glob("*.hdtv")
        )

        for startup_hdtv in startup_d_hdtv:
            try:
                if os.path.exists(startup_hdtv):
                    hdtv.cmdline.command_line.ExecCmdfile(startup_hdtv)
            except OSError as msg:
                hdtv.ui.error(f"Error reading {startup_hdtv}: {msg}")

        self.run_batchfile(args)
        self.run_commands(args)

        hdtv.cmdline.MainLoop()
        hdtv.plugins.rootInterface.r.rootfile = None
        hdtv.cmdline.command_tree.SetDefaultLevel(1)

    def parse_args(self, args):
        from hdtv._version import get_versions

        __version__ = get_versions()["version"]
        del get_versions
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-b", "--batch", dest="batchfile", help="Open and execute HDTV batchfile"
        )
        parser.add_argument(
            "-e", "--execute", dest="commands", help="Execute HDTV command(s)"
        )
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            help="Show HDTV Version",
            version=f"HDTV {__version__}",
        )
        parser.add_argument(
            "--rebuild-usr",
            nargs="*",
            dest="rebuildusr",
            help="Rebuild ROOT-loadable libraries for the current user",
        )
        parser.add_argument(
            "--rebuild-sys",
            nargs="*",
            dest="rebuildsys",
            help="Rebuild ROOT-loadable libraries for all users",
        )
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
        except OSError as msg:
            hdtv.ui.msg(f"Error reading {args.batchfile}: {msg}")


def run():
    App()


if __name__ == "__main__":
    run()
