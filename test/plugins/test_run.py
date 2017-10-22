import io

import pytest

from helpers.utils import redirect_stdout

import hdtv.cmdline
import hdtv.plugins.run
import hdtv.plugins.ls


@pytest.mark.parametrize("script, contains", [
    ("test/share/hdtvscript.py", ["Successfully loaded script.", "7625597484987"])])
def test_cmd_run(script, contains):
    f = io.StringIO()
    with redirect_stdout(f):
        hdtv.cmdline.command_line.DoLine("run " + script)
    assert "Running script" in f.getvalue()
    assert "Finished" in f.getvalue()
    for fragment in contains:
        assert fragment in f.getvalue()

@pytest.mark.parametrize("script", [
    "test/share/invalid.py"])
def test_cmd_run_fail(script):
    f = io.StringIO()
    ferr = io.StringIO()
    with redirect_stdout(f, ferr):
        hdtv.cmdline.command_line.DoLine("run " + script)
    assert "No such file" in ferr.getvalue()
