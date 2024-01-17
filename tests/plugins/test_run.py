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

import pytest

from tests.helpers.utils import hdtvcmd


@pytest.mark.parametrize(
    "script, contains",
    [("tests/share/hdtvscript.py", ["Successfully loaded script.", "7625597484987"])],
)
def test_cmd_run(script, contains):
    f, ferr = hdtvcmd("run " + script)
    assert "Running script" in f
    assert "Finished" in f
    for fragment in contains:
        assert fragment in f


@pytest.mark.parametrize("script", ["tests/share/invalid.py"])
def test_cmd_run_fail(script):
    f, ferr = hdtvcmd("run " + script)
    assert "No such file" in ferr
