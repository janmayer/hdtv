import sys
import os
import contextlib

from hdtv.ui import ui

@contextlib.contextmanager
def redirect_stdout(target_out, target_err=None, target_debug=None):
    original_out = sys.stdout
    original_out_hdtv = ui.stdout
    sys.stdout = target_out
    ui.stdout = target_out
    if target_err:
        original_err = sys.stderr
        sys.stderr = target_err
        original_err_hdtv = ui.stderr
        ui.stderr = target_err
    if target_debug:
        original_debug_hdtv = ui.debugout
        ui.debugout = target_debug
    yield
    sys.stdout = original_out
    ui.stdout = original_out_hdtv
    if target_err:
        sys.stderr = original_err
        ui.stderr = original_err_hdtv
    if target_debug:
        ui.debugout = original_debug_hdtv
