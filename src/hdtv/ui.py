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
Basic user interface functions (Input/Output, etc)
"""

import sys
from html import escape

from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.patch_stdout import patch_stdout

import hdtv.cmdline
import hdtv.options


class SimpleUI:
    """
    Very simple UserInterface
    """

    def __init__(self):
        self.stdout = None
        self.stderr = None

    def print(self, html, end="\n", err=False):
        # Currently, patch_stdout and print_formatted_text don’t work
        # together. Therefore, we clear the current line manually
        # first, print the formatted text, and finally call print to
        # force a redraw of the prompt. This causes problems when the
        # prompt is multiple lines long (the prompt will overwrite
        # the last lines that were just drawn).
        if self.stderr and err:
            self.stderr.write(html)
            return
        if self.stdout:
            self.stdout.write(html)
            return
        sys.stdout.write("\r")
        hdtv.cmdline.command_line.loop.call_soon_threadsafe(
            self.print_patched, HTML(html), end
        )

    def print_patched(self, text, end):
        with patch_stdout(raw=False):
            print_formatted_text(text, end=end)
            print("", end="\r")

    def msg(self, text=None, *, html=None, end="\n"):
        """
        Print message
        """
        if not html:
            html = escape(text or "")
        self.print(html, end=end)

    def info(self, text=None, *, html=None, end="\n"):
        """
        Print informational message
        """
        if not html:
            html = escape(text)
        html = "INFO: " + html
        self.print(text, end=end)

    def warning(self, text=None, *, html=None, end="\n"):
        """
        Print warning message
        """
        if not html:
            html = escape(text)
        self.print(f"<ansiyellow>WARNING: {html}</ansiyellow>", end=end, err=True)

    def error(self, text=None, *, html=None, end="\n"):
        """
        Print error message
        """
        if not html:
            html = escape(text)
        self.print(f"<ansired>ERROR: {html}</ansired>", end=end, err=True)

    def debug(self, text=None, *, html=None, end="\n", level=1):
        """
        Debugging output. The higher the level, the more specific is
        the debug message.
        """
        if not html:
            html = escape(text)
        self.print(f"<ansiblue>DEBUG: {html}</ansiblue>", end=end, err=True)


# Initialization
ui = SimpleUI()

msg = ui.msg
info = ui.info
warning = ui.warning
error = ui.error


def debug(text, end="\n", level=1):
    if level > hdtv.options.Get("ui.out.level"):
        return
    else:
        ui.debug(text, end=end, level=level)


opt = hdtv.options.Option(default=0, parse=lambda x: int(x))
hdtv.options.RegisterOption("ui.out.level", opt)
