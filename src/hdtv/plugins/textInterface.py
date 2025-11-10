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

"""
TextInterface functions
"""

import fcntl
import pydoc
import struct
import termios
from html import escape

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.filters import to_filter
from prompt_toolkit.formatted_text import HTML, fragment_list_to_text, to_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import BufferControl
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.processors import Processor, Transformation

import hdtv.options
import hdtv.ui


class FormatText(Processor):
    def apply_transformation(self, ti):
        fragments = to_formatted_text(HTML(fragment_list_to_text(ti.fragments)))
        return Transformation(fragments)


class TextInterface(hdtv.ui.SimpleUI):
    def __init__(self, height=25, width=80):
        hdtv.ui.debug("Loaded TextInterface")

        super().__init__()
        # Set options
        self.opt = {}
        self.opt["ui.pager.cmd"] = hdtv.options.Option(default="less")  # default pager
        self.opt["ui.pager.args"] = hdtv.options.Option(
            default="-F -X -R -S"
        )  # default pager cmd line options
        self.opt["ui.pager.builtin"] = hdtv.options.Option(
            default=True, parse=hdtv.options.parse_bool
        )  # use built-in pager instead of external program
        self.opt["ui.pager.disable_pager"] = hdtv.options.Option(
            default=False, parse=hdtv.options.parse_bool
        )  # whether to not use pager at all

        for key, opt in list(self.opt.items()):
            hdtv.options.RegisterOption(key, opt)

        self._fallback_canvasheight = height
        self._fallback_canvaswidth = width
        self._updateTerminalSize()

    def page(self, html, end="\n"):
        """
        Print text by pages
        """
        # TODO: Convert HTML to ANSI?
        if not hdtv.options.Get("ui.pager.builtin"):
            cmd = hdtv.options.Get("ui.pager.cmd")
            args = hdtv.options.Get("ui.pager.args")

            pydoc.tempfilepager(html, str(cmd) + " " + str(args))
        else:
            self.pager(html, end)

    def pager(self, html, end="\n"):
        """
        Construct pager using prompt_toolkit
        """

        my_buffer = Buffer()
        my_window = Window(
            BufferControl(
                buffer=my_buffer,
                focusable=True,
                preview_search=True,
                input_processors=[FormatText()],
            )
        )

        my_buffer.text = html
        my_buffer.read_only = to_filter(True)

        root_container = HSplit(
            [
                my_window,
            ]
        )

        bindings = KeyBindings()

        @bindings.add("c-c")
        @bindings.add("q")
        def _(event):
            "Quit."
            event.app.exit()

        application = Application(
            layout=Layout(
                root_container,
                focused_element=my_window,
            ),
            key_bindings=bindings,
            enable_page_navigation_bindings=True,
            mouse_support=True,
            full_screen=True,
        )

        application.run()
        super().msg(html=html, end=end)

    def msg(self, text=None, *, html=None, end="\n"):
        """
        Message output
        """
        self._updateTerminalSize()
        if not html:
            html = escape(text)
        lines = len(html.splitlines())

        if lines > self.canvasheight and not hdtv.options.Get("ui.pager.disable_pager"):
            self.page(html, end)
        else:
            super().msg(html=html, end=end)

    def _updateTerminalSize(self):
        try:
            h, w, hp, wp = struct.unpack(
                "HHHH",
                fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack("HHHH", 0, 0, 0, 0)),
            )
            self.canvasheight = h
            self.canvaswidth = w
        except:
            self.canvasheight = 30
            self.canvaswidth = 1050


# initialization
hdtv.ui.ui = TextInterface()
hdtv.ui.msg = hdtv.ui.ui.msg
