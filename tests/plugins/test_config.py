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

import pytest

import hdtv.cmdline
import hdtv.options
import hdtv.plugins.config

# populate with a few options
import hdtv.plugins.dblookup
from tests.helpers.utils import hdtvcmd


@pytest.fixture(autouse=True)
def prepare():
    for variable in [
        "table",
        "database.db",
        "database.auto_lookup",
        "database.fuzziness",
        "database.sort_key",
        "database.sort_reverse",
    ]:
        hdtv.options.Reset(variable)


def test_cmd_config_show():
    f, ferr = hdtvcmd("config show")
    out = f.split("\n")
    assert len(out) > 2
    for line in out:
        assert ": " in line
    assert ferr == ""


@pytest.mark.parametrize(
    "variable, value",
    [
        ("table", "modern"),
        ("database.db", "PGAAlib_IKI2000"),
        ("database.auto_lookup", "False"),
        ("database.fuzziness", "1.0"),
        ("database.sort_key", "None"),
        ("database.sort_reverse", "False"),
    ],
)
def test_cmd_config_show_variable(variable, value):
    f, ferr = hdtvcmd("config show " + variable)
    out = f.split("\n")
    assert len(out) == 1
    res_variable, res_value = re.search("<b>(.*)</b>: (.*)", out[0]).groups()
    assert variable in res_variable
    assert res_value == value
    assert ferr == ""


@pytest.mark.parametrize(
    "variable, value",
    [
        ("database.db", "promptgammas"),
        ("database.auto_lookup", "True"),
        ("database.fuzziness", "5.0"),
        ("database.sort_key", "energy"),
        ("database.sort_reverse", "True"),
    ],
)
def test_cmd_config_set(variable, value):
    hdtvcmd(f"config set {variable} {value}")
    assert str(hdtv.options.Get(variable)) == value


@pytest.mark.parametrize(
    "variable, value, default",
    [
        ("database.db", "promptgammas", "PGAAlib_IKI2000"),
        ("database.auto_lookup", "True", "False"),
        ("database.fuzziness", "5.0", "1.0"),
        ("database.sort_key", "energy", "None"),
        ("database.sort_reverse", "True", "False"),
    ],
)
def test_cmd_config_reset(variable, value, default):
    hdtv.options.Set(variable, value)
    hdtvcmd(f"config reset {variable}")
    assert str(hdtv.options.Get(variable)) == default


@pytest.mark.parametrize(
    "bool_str, bool_val",
    [
        ("true", True),
        ("True", True),
        ("tRuE", True),
        ("false", False),
        ("False", False),
        ("fAlSe", False),
    ],
)
def test_parse_bool(bool_str, bool_val):
    assert hdtv.options.parse_bool(bool_str) == bool_val


def test_register_option():
    opt = hdtv.options.Option(default="default")
    hdtv.options.RegisterOption("test.option", opt)
    assert hdtv.options.Get("test.option") == "default"


def test_register_option_fail():
    error_occurred = False
    opt = hdtv.options.Option(default="default")
    hdtv.options.RegisterOption("test.fail", opt)
    try:
        hdtv.options.RegisterOption("test.fail", opt)
    except RuntimeError:
        error_occurred = True
    assert error_occurred
    assert hdtv.options.Get("test.fail") == "default"
