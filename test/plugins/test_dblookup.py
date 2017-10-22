import io
import re
import sys

import pytest

from helpers.utils import redirect_stdout

import hdtv.cmdline
import hdtv.options
import hdtv.plugins.dblookup

@pytest.yield_fixture(autouse=True)
def prepare():
    hdtv.options.Set("table", "classic")
    hdtv.options.Set("uncertainties", "short")
    hdtv.options.Set("database.db", "pgaalib_iki2000")
    yield

def test_cmd_db_info():
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("db info")
    out = f.getvalue()
    assert "Database" in out
    assert "Valid fields" in out
    assert ferr.getvalue().strip() == ""

def test_cmd_db_list():
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("db list")
    assert "promptgammas" in f.getvalue()
    assert "pgaalib_iki2000" in f.getvalue()
    assert ferr.getvalue().strip() == ""

def test_cmd_db_lookup_base():
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("db lookup")
    assert "usage" in f.getvalue().strip()
    assert "required" in ferr.getvalue()

    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("db lookup 0")
    assert ferr.getvalue().strip() == ""
    assert "Found 0 results" in f.getvalue()

@pytest.mark.parametrize("specs", [
    "Intensity=0.1", "Sigma=0.03", "Energy=510"])
def test_cmd_db_lookup_specs(specs):
    assert count_results("db lookup {}".format(specs)) > 0

@pytest.mark.parametrize("specs", [
    "Intensity=0.3", "Sigma=0.04", "Energy=139.940"])
def test_cmd_db_lookup_fuzziness(specs):
    results_narrow = count_results("db lookup {} -f 0.005".format(specs))
    results_broad = count_results("db lookup {} --fuzziness 0.5".format(specs))
    assert results_narrow > 0
    assert results_broad > 0
    assert results_broad > results_narrow

@pytest.mark.parametrize("specs", [
    "k0=2", "510", "a=40", "z=33"])
def test_cmd_db_lookup_sort_reverse(specs):
    test_cmd_db_lookup_sort_key(specs, reverse=True)

@pytest.mark.parametrize("specs", [
    "k0=3", "511", "a=20", "z=10"])
def test_cmd_db_lookup_sort_key(specs, reverse=False):
    f = io.StringIO()
    with redirect_stdout(f):
        if reverse:
            hdtv.cmdline.command_line.DoLine(
                "db lookup {} -k energy -r".format(specs))
        else:
            hdtv.cmdline.command_line.DoLine(
                "db lookup {} -k energy".format(specs))
    old_value = sys.float_info.max if reverse else sys.float_info.min
    for line in f.getvalue().split('\n')[2:-3]:
        new_value = float(line.split("|")[3].split("(")[0].strip())
        if reverse:
            assert new_value < old_value
        else:
            assert new_value > old_value
        old_value = new_value

@pytest.mark.parametrize("db", [
    "promptgammas", "pgaalib_iki2000"])
def test_cmd_db_set(db):
    f = io.StringIO()
    with redirect_stdout(f):
        hdtv.cmdline.command_line.DoLine("db set {}".format(db))
    assert "loaded" in f.getvalue()
    assert hdtv.options.Get("database.db") == db

def count_results(query):
    f = io.StringIO()
    with redirect_stdout(f):
        hdtv.cmdline.command_line.DoLine(query)
    return int(re.search('Found (\d+) results', f.getvalue()).groups()[0])
