# -*- coding: utf-8 -*-

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

import hdtv.options
import hdtv.ui
import os
import pydoc
import sys
import signal
from html import escape

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import SearchToolbar, TextArea


class TextInterface(hdtv.ui.SimpleUI):

    def __init__(self, height=25, width=80):
        hdtv.ui.debug("Loaded TextInterface")

        super(TextInterface, self).__init__()
        # Set options
        self.opt = dict()
        self.opt["ui.pager.cmd"] = hdtv.options.Option(
            default="less")  # default pager
        self.opt["ui.pager.args"] = hdtv.options.Option(
            default="-F -X -R -S")  # default pager cmd line options
        self.opt["ui.pager.builtin"] = hdtv.options.Option(
            default=True, parse=hdtv.options.parse_bool)  # use built-in pager instead of external program

        for (key, opt) in list(self.opt.items()):
            hdtv.options.RegisterOption(key, opt)

        self._fallback_canvasheight = height
        self._fallback_canvaswidth = width
        self._updateTerminalSize(None, None)

        signal.signal(signal.SIGWINCH, self._updateTerminalSize)

    def page(self, html):
        """
        Print text by pages
        """
        # TODO: Convert HTML to ANSI?
        if not hdtv.options.Get("ui.pager.builtin"):
            cmd = hdtv.options.Get("ui.pager.cmd")
            args = hdtv.options.Get("ui.pager.args")

            pydoc.tempfilepager(html, str(cmd) + " " + str(args))
        else:
            self.pager(html)

    def pager(self, text):
        """
        Construct pager using prompt_toolkit
        """
        search_field = SearchToolbar(text_if_not_searching=[
            ('class:not-searching', "Press '/' to start searching.")])

        text_area = TextArea(
            text=text,
            read_only=True,
            wrap_lines=False,
            search_field=search_field)
        
        root_container = HSplit([
            text_area,
            search_field,
        ])

        bindings = KeyBindings()
        @bindings.add('c-c')
        @bindings.add('q')
        def _(event):
            " Quit. "
            event.app.exit()

        application = Application(
            layout=Layout(
                root_container,
                focused_element=text_area,
            ),
            key_bindings=bindings,
            enable_page_navigation_bindings=True,
            mouse_support=True,
            full_screen=True)

        application.run()
        super().msg(text)

    def msg(self, text=None, *, html=None, end='\n'):
        """
        Message output
        """
        if not html:
            html = escape(text)
        lines = len(html.splitlines())

        if lines > self.canvasheight:
            self.page(html)
        else:
            super().msg(html=html, end=end)

    # TODO: Make this work under windows
    def _updateTerminalSize(self, signal, frame):
        env = os.environ
        def ioctl_GWINSZ(fd):
            try:
                import fcntl
                import termios
                import struct
                import os
                cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
                                                     '1234'))
            except BaseException:
                return None
            return cr
        cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
        if not cr:
            try:
                fd = os.open(os.ctermid(), os.O_RDONLY)
                cr = ioctl_GWINSZ(fd)
                os.close(fd)
            except BaseException:
                pass
        if not cr:
            cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
        self.canvasheight = cr[0]
        self.canvaswidth = cr[1]

# initialization
hdtv.ui.ui = TextInterface()
hdtv.ui.msg = hdtv.ui.ui.msg
