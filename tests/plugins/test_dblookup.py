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
import sys

import pytest

import hdtv.cmdline
import hdtv.options
import hdtv.plugins.dblookup
from tests.helpers.utils import hdtvcmd


@pytest.fixture(autouse=True)
def prepare():
    hdtv.options.Set("table", "classic")
    hdtv.options.Set("uncertainties", "short")
    hdtv.options.Set("database.db", "pgaalib_iki2000")


def test_cmd_db_info():
    f, ferr = hdtvcmd("db info")
    assert "Database" in f
    assert "Valid fields" in f
    assert ferr == ""


def test_cmd_db_list():
    f, ferr = hdtvcmd("db list")
    assert "promptgammas" in f
    assert "pgaalib_iki2000" in f
    assert ferr == ""


def test_cmd_db_lookup_base():
    f, ferr = hdtvcmd("db lookup")
    assert "usage" in f
    assert "arguments" in ferr

    f, ferr = hdtvcmd("db lookup 0")
    assert ferr == ""
    assert "Found 0 results" in f


@pytest.mark.parametrize("specs", ["Intensity=0.1", "Sigma=0.03", "Energy=510"])
def test_cmd_db_lookup_specs(specs):
    assert count_results(f"db lookup {specs}") > 0


@pytest.mark.parametrize("specs", ["Intensity=0.3", "Sigma=0.04", "Energy=139.940"])
def test_cmd_db_lookup_fuzziness(specs):
    results_narrow = count_results(f"db lookup {specs} -f 0.005")
    results_broad = count_results(f"db lookup {specs} --fuzziness 0.5")
    assert results_narrow > 0
    assert results_broad > 0
    assert results_broad > results_narrow


@pytest.mark.parametrize("specs", ["k0=2", "510", "a=40", "z=33"])
def test_cmd_db_lookup_sort_reverse(specs):
    test_cmd_db_lookup_sort_key(specs, reverse=True)


@pytest.mark.parametrize("specs", ["k0=3", "511", "a=20", "z=10"])
def test_cmd_db_lookup_sort_key(specs, reverse=False):
    if reverse:
        f, ferr = hdtvcmd(f"db lookup {specs} -k energy -r")
    else:
        f, ferr = hdtvcmd(f"db lookup {specs} -k energy")
    old_value = sys.float_info.max if reverse else sys.float_info.min
    for line in f.split("\n")[2:-3]:
        new_value = float(line.split("|")[3].split("(")[0].strip())
        if reverse:
            assert new_value < old_value
        else:
            assert new_value > old_value
        old_value = new_value


@pytest.mark.parametrize("db", ["promptgammas", "pgaalib_iki2000"])
def test_cmd_db_set(db):
    f, ferr = hdtvcmd(f"db set {db}")
    assert "loaded" in f
    assert hdtv.options.Get("database.db") == db


def count_results(query):
    f, ferr = hdtvcmd(query)
    return int(re.search(r"Found (\d+) results", f).groups()[0])
