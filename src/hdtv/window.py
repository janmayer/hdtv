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

import traceback

import ROOT

import hdtv.cmdline
import hdtv.color
import hdtv.options
import hdtv.rootext.display
import hdtv.ui
from hdtv.marker import MarkerCollection


class HotkeyList:
    "Class to handle multi-key hotkeys."

    def __init__(self):
        self.fKeyCmds = {}
        self.fCurNode = self.fKeyCmds

    def AddHotkey(self, key, cmd):
        """
        Adds a hotkey to the hotkey table. If key is a list,
        it is taken as a multi-key hotkey. The function refuses
        to overwrite definitions that do not match exactly, i.e.
        once you have defined hotkey x, you can no longer define
        the multi-key combination xy (since that would have to
        overwrite x). You can overwrite matching combinations,
        though (i.e. redefine x in the example above).
        """
        curNode = self.fKeyCmds
        if isinstance(key, list):
            for k in key[0:-1]:
                try:
                    curNode = curNode[k]
                    if not isinstance(curNode, dict):
                        raise RuntimeError("Refusing to overwrite non-matching hotkey")
                except KeyError:
                    curNode[k] = {}
                    curNode = curNode[k]

            key = key[-1]

        curNode[key] = wrap_cmd(cmd)

    def HandleHotkey(self, key):
        """
        Handles a key press. Returns True if the input was a
        valid hotkey, False if it was not, and None if further
        input is needed (i.e. if the input could be part of a
        multi-key hotkey)
        """
        try:
            node = self.fCurNode[key]
        except KeyError:
            self.ResetHotkeyState()
            return False

        if isinstance(node, dict):
            self.fCurNode = node
            return None
        else:
            node()
            self.ResetHotkeyState()
            return True

    def ResetHotkeyState(self):
        """
        Reset possible waiting state for a multi-key hotkey.
        """
        self.fCurNode = self.fKeyCmds


class KeyHandler(HotkeyList):
    """
    Hotkey handler, adding support for a status line (that can be (ab)used as
    a text entry)
    """

    def __init__(self):
        super().__init__()

        self.fEditMode = False  # Status bar currently used as text entry
        # Modifier keys
        self.MODIFIER_KEYS = (
            ROOT.kKey_Shift,
            ROOT.kKey_Control,
            ROOT.kKey_Meta,
            ROOT.kKey_Alt,
            ROOT.kKey_CapsLock,
            ROOT.kKey_NumLock,
            ROOT.kKey_ScrollLock,
        )

        # Parent class must provide self.viewer and self.viewport!

    def EnterEditMode(self, prompt, handler):
        """
        Enter edit mode (mode where the status line is used as a text entry)
        """
        self.fEditMode = True
        self.fEditStr = ""
        self.fEditPrompt = prompt
        self.fEditHandler = wrap_cmd(handler)
        self.viewport.SetStatusText(self.fEditPrompt)

    def EditKeyHandler(self):
        """
        Key handler in edit mode
        """
        try:
            keyStr = self.viewer.fKeyStr.as_string()
        except AttributeError:
            # Older versions of cppyy already convert to string
            keyStr = self.viewer.fKeyStr
        except UnicodeDecodeError as err:
            keyStr = err.args[1].split(b"\x00")[0].decode("utf-8")

        if self.viewer.fKeySym == ROOT.kKey_Backspace:
            self.fEditStr = self.fEditStr[0:-1]
            self.viewport.SetStatusText(self.fEditPrompt + self.fEditStr)
        elif (
            self.viewer.fKeySym == ROOT.kKey_Return
            or self.viewer.fKeySym == ROOT.kKey_Enter
        ):
            self.fEditMode = False
            self.viewport.SetStatusText("")
            self.fEditHandler(self.fEditStr)
        elif keyStr != "":
            self.fEditStr += keyStr[0]
            self.viewport.SetStatusText(self.fEditPrompt + self.fEditStr)
        else:
            return False

        return True

    def KeyHandler(self):
        """
        Key handler (handles hotkeys and calls EditKeyHandler in edit mode)
        """
        # Filter unknown and modifier keys
        if (
            self.viewer.fKeySym in self.MODIFIER_KEYS
            or self.viewer.fKeySym == ROOT.kKey_Unknown
        ):
            return

        # ESC aborts
        if self.viewer.fKeySym == ROOT.kKey_Escape:
            self.ResetHotkeyState()
            self.fEditMode = False
            self.keyString = ""
            self.viewport.SetStatusText("")
            return True

        # There are two modes: the ``edit'' mode, in which the status
        # bar is abused as a text entry, and the normal mode, in which
        # the keys act as hotkeys.
        if self.fEditMode:
            handled = self.EditKeyHandler()
        else:
            try:
                keyStr = self.viewer.fKeyStr.as_string()
            except AttributeError:
                # Older versions of cppyy already convert to string
                keyStr = self.viewer.fKeyStr
            except UnicodeDecodeError as err:
                keyStr = err.args[1].split(b"\x00")[0].decode("utf-8")

            if not keyStr:
                keyStr = "<?>"

            handled = self.HandleHotkey(self.viewer.fKeySym)

            if handled is None:
                self.keyString += keyStr
                self.viewport.SetStatusText("Command: %s" % self.keyString)
            elif not handled:
                self.keyString += keyStr
                self.viewport.SetStatusText("Invalid hotkey %s" % self.keyString)
                self.keyString = ""
            else:
                if not self.fEditMode:
                    self.viewport.SetStatusText("")
                self.keyString = ""

        return handled


class Window(KeyHandler):
    """
    Base class of a window object

    This class provides basic key handling for zooming and scrolling.
    """

    def __init__(self):
        super().__init__()

        self.viewer = ROOT.HDTV.Display.Viewer()
        self.viewport = self.viewer.GetViewport()
        self._dispatchers = []

        # Handle closing of the main window (with an application exit)
        disp = ROOT.TPyDispatcher(hdtv.cmdline.AsyncExit)
        self.viewer.Connect("CloseWindow()", "TPyDispatcher", disp, "Dispatch()")
        self._dispatchers.append(disp)

        self.XZoomMarkers = MarkerCollection(
            "X", paired=True, maxnum=1, color=hdtv.color.zoom
        )
        self.XZoomMarkers.Draw(self.viewport)
        self.YZoomMarkers = MarkerCollection(
            "Y", paired=True, maxnum=1, color=hdtv.color.zoom
        )
        self.YZoomMarkers.Draw(self.viewport)

        # Key Handling
        disp = ROOT.TPyDispatcher(self.KeyHandler)
        self.viewer.Connect("KeyPressed()", "TPyDispatcher", disp, "Dispatch()")
        self._dispatchers.append(disp)

        self.keyString = ""
        self.AddHotkey(ROOT.kKey_u, lambda: self.viewport.Update())
        # toggle spectrum display
        self.AddHotkey(ROOT.kKey_l, self.viewport.ToggleLogScale)
        self.AddHotkey(ROOT.kKey_A, self.viewport.ToggleYAutoScale)
        self.AddHotkey(ROOT.kKey_Exclam, self.viewport.ToggleUseNorm)
        # x directions
        self.AddHotkey(ROOT.kKey_Space, self.SetXZoomMarker)
        self.AddHotkey(ROOT.kKey_x, self.ExpandX)
        self.AddHotkey(ROOT.kKey_Right, lambda: self.viewport.ShiftXOffset(0.1))
        self.AddHotkey(ROOT.kKey_Left, lambda: self.viewport.ShiftXOffset(-0.1))
        self.AddHotkey(ROOT.kKey_Greater, lambda: self.viewport.ShiftXOffset(0.1))
        self.AddHotkey(ROOT.kKey_Less, lambda: self.viewport.ShiftXOffset(-0.1))
        self.AddHotkey(ROOT.kKey_Return, lambda: self.viewport.Update(True))
        self.AddHotkey(ROOT.kKey_Enter, lambda: self.viewport.Update(True))
        self.AddHotkey(
            ROOT.kKey_Bar, lambda: self.viewport.SetXCenter(self.viewport.GetCursorX())
        )
        self.AddHotkey(ROOT.kKey_1, lambda: self.viewport.XZoomAroundCursor(2.0))
        self.AddHotkey(ROOT.kKey_0, lambda: self.viewport.XZoomAroundCursor(0.5))
        # y direction
        self.AddHotkey(ROOT.kKey_h, self.SetYZoomMarker)
        self.AddHotkey(ROOT.kKey_y, self.ExpandY)
        self.AddHotkey(ROOT.kKey_Up, lambda: self.viewport.ShiftYOffset(0.1))
        self.AddHotkey(ROOT.kKey_Down, lambda: self.viewport.ShiftYOffset(-0.1))
        self.AddHotkey(ROOT.kKey_Z, lambda: self.viewport.YZoomAroundCursor(2.0))
        self.AddHotkey(ROOT.kKey_X, lambda: self.viewport.YZoomAroundCursor(0.5))
        # expand in all directions
        self.AddHotkey(ROOT.kKey_e, self.Expand)

        self.AddHotkey(
            ROOT.kKey_i,
            lambda: self.EnterEditMode(prompt="Position: ", handler=self.GoToPosition),
        )

        # Register configuration variables
        opt = hdtv.options.Option(
            default=self.viewport.GetYMinVisibleRegion(),
            parse=lambda x: float(x),
            changeCallback=self.YMinVisibleRegionChanged,
        )
        hdtv.options.RegisterOption("display.YMinVisibleRegion", opt)

        opt = hdtv.options.Option(
            default=self.viewport.GetDarkMode(),
            parse=hdtv.options.parse_bool,
            changeCallback=self.SetDarkMode,
        )
        hdtv.options.RegisterOption("display.mode.dark", opt)

        prog = "window view center"
        description = "center window to position"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-w", "--width", type=float, help="width of window", default=100.0
        )
        parser.add_argument("position", type=float)
        hdtv.cmdline.AddCommand(prog, self.GoToPosition, parser=parser)

        prog = "window view region"
        description = "show region in window"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument("start", type=float)
        parser.add_argument("end", type=float)
        hdtv.cmdline.AddCommand(prog, self.ViewRegion, parser=parser)

    def YMinVisibleRegionChanged(self, opt):
        self.viewport.SetYMinVisibleRegion(opt.Get())

    def SetDarkMode(self, opt):
        """
        Switch between dark and light mode.
        """
        self.viewport.SetDarkMode(opt.Get())
        try:
            from hdtv.plugins.matInterface import matrix_interface

            for viewport in matrix_interface.matviews:
                viewport.SetDarkMode(opt.Get())
        except:
            pass

    def ViewRegion(self, args):
        """
        Zoom and move viewport to show a region
        """
        width = abs(args.end - args.start)
        center = args.start + width / 2.0
        self.viewport.SetXVisibleRegion(width)
        self.viewport.SetXCenter(center)

    def GoToPosition(self, args):
        """
        Move viewport to be centered around a position
        """
        try:
            width = args.width
        except AttributeError:
            width = 100.0
        try:
            center = float(args)
        except TypeError:
            center = float(args.position)
        self.viewport.SetXVisibleRegion(width)
        self.viewport.SetXCenter(center)

    def FocusObjects(self, objs):
        """
        Move and stretch viewport to show multiple objs
        """
        xdimensions = ()
        # Get dimensions of objects
        for obj in objs:
            try:
                if obj.xdimensions is not None:
                    xdimensions += obj.xdimensions
            except BaseException:
                # ignore objects without xdimensions
                pass
        # calulate
        if len(xdimensions) > 0:
            view_width = max(xdimensions) - min(xdimensions)
            view_width *= 1.2
            if view_width < 50.0:
                view_width = 50.0  # TODO: make this configurable
            view_center = (max(xdimensions) + min(xdimensions)) / 2.0
            # change viewport
            self.viewport.SetXVisibleRegion(view_width)
            self.viewport.SetXCenter(view_center)

    def IsInVisibleRegion(self, obj, part=False):
        """
        Check if obj is in the visible region of the viewport
        """
        try:
            xdim = obj.xdimensions
        except BaseException:
            xdim = None
        if xdim is None:  # Object has no dimensions
            return True
        # get viewport limits
        viewport_start = self.viewport.GetXOffset()
        viewport_end = viewport_start + self.viewport.GetXVisibleRegion()
        # check if the full object is visible
        if not part:
            if (xdim[0] > viewport_start) and (xdim[1] < viewport_end):
                return True
            else:
                return False
        # check if a part of the object is visible
        if part:
            if (xdim[0] < viewport_start) and (xdim[1] < viewport_start):
                return False
            elif (xdim[0] > viewport_end) and (xdim[1] > viewport_end):
                return False
            else:
                return True

    def ExpandX(self):
        """
        expand in X direction
        """
        self._Expand("X")

    def ExpandY(self):
        """
        expand in Y direction
        """
        self._Expand("Y")

    def Expand(self):
        """
        expand in X and in Y direction
        """
        self._Expand("X")
        self._Expand("Y")

    def _Expand(self, xytype):
        """
        expand the display to show the region between the zoom markers (X or Y),
        or the full spectrum if not zoom markers are set.
        """
        # check the input
        if xytype not in ["X", "Y"]:
            hdtv.ui.error(
                "invalid parameter %s to the private function _Expand" % xytype
            )
            return

        zoomMarkers = getattr(self, "%sZoomMarkers" % xytype)
        if len(zoomMarkers) == 1:
            zm = zoomMarkers[0]
            p1 = zm.p1.pos_cal
            if zm.p2 is None:
                p2 = 0.0
            else:
                p2 = zm.p2.pos_cal
            setOffset = getattr(self.viewport, "Set%sOffset" % xytype)
            setOffset(min(p1, p2))
            setVisibleRegion = getattr(self.viewport, "Set%sVisibleRegion" % xytype)
            setVisibleRegion(abs(p2 - p1))
            getattr(self, "%sZoomMarkers" % xytype).pop()
        else:
            if xytype == "X":
                self.viewport.ShowAll()
            elif xytype == "Y":
                self.viewport.YAutoScaleOnce()

    def SetXZoomMarker(self, pos=None):
        """
        set a X zoom marker
        """
        if pos is None:
            pos = self.viewport.GetCursorX()
        self.XZoomMarkers.SetMarker(pos)

    def SetYZoomMarker(self, pos=None):
        """
        set a Y zoom marker
        """
        if pos is None:
            pos = self.viewport.GetCursorY()
        self.YZoomMarkers.SetMarker(pos)


def wrap_cmd(cmd):
    def _wrapper(*args, **kwargs):
        try:
            cmd(*args, **kwargs)
        except hdtv.cmdline.HDTVCommandAbort as msg:
            if msg.value:
                hdtv.ui.error(msg.value)
        except (hdtv.cmdline.HDTVCommandError, Exception) as msg:
            try:
                if msg.value:
                    hdtv.ui.error(msg.value)
            except AttributeError:
                hdtv.ui.error(str(msg))
            hdtv.ui.debug(traceback.format_exc())

    return _wrapper
