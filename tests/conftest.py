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

import os
import shutil
import sys
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), "helpers"))


pytest_plugins = ("tests.helpers.fixtures",)


def pytest_addoption(parser):
    parser.addoption(
        "--force-rebuild", action="store_true", help="Force library rebuild."
    )


def pytest_configure(config):
    print("Update Root Include Path ...")
    import hdtv.rootext

    hdtv.rootext.UpdateRootIncludePath()
    os.environ["XDG_CACHE_HOME"] = tempfile.mkdtemp()
    if config.getoption("force_rebuild"):
        print("Force Library Rebuild ...")
        import hdtv.rootext.dlmgr

        hdtv.rootext.dlmgr.RebuildLibraries(hdtv.rootext.dlmgr.usrlibdir)


def pytest_sessionfinish(session, exitstatus):
    tmpdir = os.getenv("XDG_CACHE_HOME")
    if tmpdir != "" and os.path.exists(tmpdir):
        # fingers crossed
        shutil.rmtree(tmpdir)
