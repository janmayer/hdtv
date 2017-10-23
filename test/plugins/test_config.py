import io
import re

import pytest

from helpers.utils import redirect_stdout

import hdtv.cmdline
import hdtv.options
import hdtv.plugins.config

# populate with a few options
import hdtv.plugins.dblookup

@pytest.yield_fixture(autouse=True)
def prepare():
    for variable in [
        "table", 
        "database.db", 
        "database.auto_lookup", 
        "database.fuzziness", 
        "database.sort_key", 
        "database.sort_reverse"]:
        hdtv.options.Reset(variable)
    yield

def test_cmd_config_show():
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("config show")
    out = f.getvalue().strip().split("\n")
    assert len(out) > 2
    for line in out:
        assert ': ' in line 
    assert ferr.getvalue().strip() == ""

@pytest.mark.parametrize("variable, value", [
    ("table", "modern"),
    ("database.db", "PGAAlib_IKI2000"),
    ("database.auto_lookup", "False"),
    ("database.fuzziness", "1.0"),
    ("database.sort_key", "None"),
    ("database.sort_reverse", "False")])
def test_cmd_config_show_variable(variable, value):
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("config show " + variable)
    out = f.getvalue().strip().split("\n")
    assert len(out) == 1
    res_variable, res_value = re.search('(.*): (.*)', out[0]).groups()
    assert variable in res_variable
    assert res_value == value
    assert ferr.getvalue().strip() == ""

@pytest.mark.parametrize("variable, value", [
    ("database.db", "promptgammas"),
    ("database.auto_lookup", "True"),
    ("database.fuzziness", "5.0"),
    ("database.sort_key", "energy"),
    ("database.sort_reverse", "True")])
def test_cmd_config_set(variable, value):
    hdtv.cmdline.command_line.DoLine("config set {} {}".format(variable, value))
    assert str(hdtv.options.Get(variable)) == value

@pytest.mark.parametrize("variable, value, default", [
    ("database.db", "promptgammas", "PGAAlib_IKI2000"),
    ("database.auto_lookup", "True", "False"),
    ("database.fuzziness", "5.0", "1.0"),
    ("database.sort_key", "energy", "None"),
    ("database.sort_reverse", "True", "False")])
def test_cmd_config_reset(variable, value, default):
    hdtv.options.Set(variable, value)
    hdtv.cmdline.command_line.DoLine("config reset {}".format(variable))
    assert str(hdtv.options.Get(variable)) == default

@pytest.mark.parametrize("bool_str, bool_val", [
    ("true", True),
    ("True", True),
    ("tRuE", True),
    ("false", False),
    ("False", False),
    ("fAlSe", False)])
def test_parse_bool(bool_str, bool_val):
    assert hdtv.options.parse_bool(bool_str) == bool_val

def test_register_option():
    opt = hdtv.options.Option(default="default")
    hdtv.options.RegisterOption("test.option", opt)
    assert hdtv.options.Get("test.option") == "default"

def test_register_option_fail():
    opt = hdtv.options.Option(default="default")
    hdtv.options.RegisterOption("test.fail", opt)
    try:
        hdtv.options.RegisterOption("test.fail", opt)
    except RuntimeError:
        error_occurred = True
    assert error_occurred
    assert hdtv.options.Get("test.fail") == "default"
