# -*- coding: utf-8 -*-

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

import re
import os
from itertools import count
from html import escape

from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.keys import Keys

import hdtv.options
import hdtv.ui
import hdtv.dummy

def Indent(s, indent=" "):
    """
    Re-format a (possibly multi-line) string such that each line is indented.
    """
    return indent + ("\n" + indent).join(s.splitlines()) + "\n"


def GetCompleteOptions(begin, options):
    l = len(begin)
    return [o + " " for o in options if o[0:l] == begin]


class TxtFile(object):
    """
    Handle txt files, ignoring commented lines
    """

    def __init__(self, filename, mode="r"):

        self.lines = list()
        self.linos = list()
        self.mode = mode
        # TODO: this has to be handled properly (escaped whitespaces, etc...)
        filename = filename.rstrip()
        self.filename = os.path.expanduser(filename)
        self.fd = None

    def read(self, verbose=False):
        """
        Read text file to self.lines

        Comments are stripped and lines seperated by '\' are automatically
        concatenated
        """
        try:
            self.fd = open(self.filename, self.mode)
            prev_line = ""
            number = 0
            for line in self.fd:
                number += 1
                line = line.rstrip('\r\n ')
                # line is continued on next line
                if len(line) > 0 and line[-1] == '\\':
                    prev_line += line.rstrip('\\')
                    continue
                else:
                    if prev_line != "":
                        line = prev_line + " " + line
                    prev_line = ""
                if verbose:
                    hdtv.ui.msg('file> ' + str(line))

                # Strip comments
                line = remove_comments(line)
                if line.strip() == "":
                    continue
                self.lines.append(line)
                self.linos.append(number)

        except IOError as msg:
            raise IOError("Error opening file:" + str(msg))
        #except BaseException:  # Let MainLoop handle other exceptions
        #    raise
        finally:
            if self.fd is not None:
                self.fd.close()

    def write(self):
        """
        Write lines stored in self.lines to text file

        Newlines are automatically appended if necessary
        """
        try:
            self.fd = open(self.filename, self.mode)
            for line in self.lines:
                line.rstrip('\r\n ')
                line += os.linesep
                self.fd.write(line)
        except IOError as msg:
            raise IOError("Error opening file: %s" % msg)
        except BaseException:
            raise
        finally:
            if self.fd is not None:
                self.fd.close()


class Pairs(list):
    """
    List of pair values

    conv_func: conversion function to be called before storage of pair
    """

    # default conversion is "identity" -> No conversion
    def __init__(self, conv_func=lambda x: x):

        super(Pairs, self).__init__()
        self.conv_func = conv_func  # Conversion function, e.g. float

    def add(self, x, y):
        """
        Add a pair
        """
        self.append([self.conv_func(x), self.conv_func(y)])

    def remove(self, pair):
        """
        TODO
        """
        pass

    def fromFile(self, fname, sep=None):
        """
        Read pairs from file
        """
        file = TxtFile(fname)
        file.read()
        for line in file.lines:
            pair = line.split(sep)
            try:
                self.add(pair[0], pair[1])
            except (ValueError, IndexError):
                hdtv.ui.error("Invalid Line in", fname, ":", line)

    def fromLists(self, list1, list2):
        """
        Create pairs from to lists by assigning corresponding indices
        """
        if len(list1) != len(list2):
            hdtv.ui.error(
                "Lists for Pairs.fromLists() are of different length")
            return False

        for item1, item2 in zip(list1, list2):
            self.add(item1, item2)


opt_table = hdtv.options.Option(
    default="modern",
    parse=hdtv.options.parse_choices(["classic", "simple", "grid", "modern"]))
hdtv.options.RegisterOption("table", opt_table)

opt_uncertainties = hdtv.options.Option(
    default="short",
    parse=hdtv.options.parse_choices(["short", "pretty", "long"]))
hdtv.options.RegisterOption("uncertainties", opt_uncertainties)

class Table(object):
    """
    Class to store tables

    data: iterable that contains 'keys' as attributes or dict entries
    """

    def __init__(
            self,
            data,
            keys,
            header=None,
            ignoreEmptyCols=True,
            sortBy=None,
            reverseSort=False,
            extra_header=None,
            extra_footer=None):
        self.extra_header = extra_header
        self.extra_footer = extra_footer
        self.sortBy = sortBy
        self.keys = keys
        self.data = list()

        self.style = style = hdtv.options.Get("table")

        if style == "classic":
            self.col_sep_char = "|"
            self.empty_field = "-"
            self.header_sep_char = "-"
            self.header_sep_char_sorted = "~"
            self.crossing_char = "+"
        elif style == "simple":
            self.col_sep_char = "\t"
            self.empty_field = ""
            self.header_sep_char = ""
            self.header_sep_char_sorted = ""
            self.crossing_char = ""
        elif style == "grid":
            self.col_sep_char =   '│'  
            self.empty_field = ''
            self.header_sep_char =   '─'  
            self.header_sep_char_sorted =   '╌'  
            self.crossing_char =   '┼'  
        else: # default style 'modern'
            self.col_sep_char = ''
            self.empty_field = ''
            self.header_sep_char =   '─'  
            self.header_sep_char_sorted =   '━'  
            self.crossing_char = ''


        self._width = 0  # Width of table
        self._col_width = list()  # width of columns

        # One additional "border column"
        self._ignore_col = [ignoreEmptyCols for i in range(0, len(keys) + 1)]

        self.read_data(data, keys, header)
        if sortBy is not None:
            self.sort_data(sortBy, reverseSort)

    @property
    def num_columns(self):
        return len(self.keys)

    @property
    def num_rows(self):
        return len(self.data)

    def read_data(self, data, keys, header=None):
        self.data = list()
        for d in data:
            tmp = dict()
            for k in keys:
                try:
                    tmp[k] = d[k]
                except KeyError:
                    # there is a missing value in the data
                    tmp[k] = None
                except TypeError:
                    # Data is no dict so we try to read attribute
                    tmp[k] = getattr(d, k)
            self.data.append(tmp)
        # header
        if header is None:
            self.header = keys
        else:
            self.header = header
        # initial width of columns
        for header in self.header:
            # TODO: len fails on unicode characters (e.g. σ) ->
            # str.decode(encoding)
            self._col_width.append(len(str(header)) + 2)

    def build_lines(self):
        lines = list()
        for d in self.data:
            line = list()
            for i, key in enumerate(self.keys):
                try:
                    value = d[key]
                    # deal with ufloats
                    try:
                        if value.value is None:
                            value = ""
                    except BaseException:
                        pass
                    if value is None:
                        value = ""
                    else:
                        try:
                            if hdtv.options.Get("uncertainties") == "short":
                                value = "{:S}".format(value)
                            elif hdtv.options.Get("uncertainties") == "pretty":
                                value = "{:P}".format(value)
                            else:
                                value = "{:.4u}".format(value).replace("+/-", " ")
                        except BaseException:
                            value = str(value)
                    if not value is "":  # We have values in this columns -> don't ignore it
                        self._ignore_col[i] = False

                    line.append(value)
                    # TODO: len fails on unicode characters (e.g. σ) -> str.decode(encoding)
                    # Store maximum col width
                    self._col_width[i] = max(
                        self._col_width[i], len(value) + 2)
                except KeyError:
                    line.append(self.empty_field)
            lines.append(line)
        return lines

    def sort_data(self, sortBy, reverseSort=False):
        self.data.sort(key=lambda x: x[sortBy], reverse=reverseSort)

    def calc_width(self):
        # Determine table widths
        for w in self._col_width:
            self._width += w
            # TODO: for unicode awareness we have to do something
            #       like len(col_sep_char.decode('utf-8')
            self._width += len(self.col_sep_char)

    def build_header(self):
        headerline = str()
        for col in range(0, len(self.header)):
            if not self._ignore_col[col]:
                headerline += "<b>" + escape(str(" " + self.header[col] +
                                  " ").center(self._col_width[col])) + "</b>"
            if not self._ignore_col[col + 1]:
                headerline += escape(self.col_sep_char)
        return headerline

    def build_sep(self):
        # Seperator between header and data
        header_sep_line = str()
        for i in range(0, len(self._col_width)):
            if not self._ignore_col[i]:
                for j in range(0, self._col_width[i]):
                    if self.header[i] == self.sortBy:
                        header_sep_line += self.header_sep_char_sorted
                    else:
                        header_sep_line += self.header_sep_char
                if not self._ignore_col[i + 1]:
                    header_sep_line += self.crossing_char
        return header_sep_line

    def __str__(self):
        text = str()
        if self.extra_header is not None:
            text += str(self.extra_header) + os.linesep

        # this must be before the header, because of self._ignore_col
        lines = self.build_lines()

        headerline = self.build_header()
        text += headerline + os.linesep

        header_sep_line = self.build_sep()
        text += header_sep_line + os.linesep

        for line in lines:
            line_str = ""
            for col in range(0, len(line)):
                if not self._ignore_col[col]:
                    line_str += str(" " + line[col] +
                                    " ").rjust(self._col_width[col])
                if not self._ignore_col[col + 1]:
                    line_str += self.col_sep_char

            text += escape(line_str) + os.linesep

        if self.extra_footer is not None:
            text += escape(str(self.extra_footer)) + os.linesep

        return text


class Position(object):
    """
    Class for storing postions that may be fixed in calibrated or uncalibrated space

    if self.pos_cal is set the position is fixed in calibrated space.
    if self.pos_uncal is set the position is fixed in uncalibrated space.
    """

    def __init__(self, pos, fixedInCal, cal=None):
        self.cal = cal
        self._fixedInCal = fixedInCal
        if fixedInCal:
            self._pos_cal = pos
            self._pos_uncal = None
        else:
            self._pos_cal = None
            self._pos_uncal = pos

    # pos_cal
    def _set_pos_cal(self, pos):
        if not self.fixedInCal:
            raise TypeError("Position is fixed in uncalibrated space")
        self._pos_cal = pos
        self._pos_uncal = None

    def _get_pos_cal(self):
        if self.fixedInCal:
            return self._pos_cal
        else:
            return self._Ch2E(self._pos_uncal)

    pos_cal = property(_get_pos_cal, _set_pos_cal)

    # pos_uncal
    def _set_pos_uncal(self, pos):
        if self._fixedInCal:
            raise TypeError("Position is fixed in calibrated space")
        self._pos_uncal = pos
        self._pos_cal = None

    def _get_pos_uncal(self):
        if self.fixedInCal:
            return self._E2Ch(self._pos_cal)
        else:
            return self._pos_uncal

    pos_uncal = property(_get_pos_uncal, _set_pos_uncal)

    # fixedInCal property
    def _set_fixedInCal(self, fixedInCal):
        if fixedInCal:
            self.FixInCal()
        else:
            self.FixInUncal()

    def _get_fixedInCal(self):
        return self._fixedInCal

    fixedInCal = property(_get_fixedInCal, _set_fixedInCal)

    # other functions
    def __str__(self):
        text = str()
        if self.fixedInCal:
            text += "Cal: %s" % self._pos_cal
        else:
            text += "Uncal: %s" % self._pos_uncal
        return text

    def _Ch2E(self, Ch):
        if self.cal is None:
            E = Ch
        else:
            E = self.cal.Ch2E(Ch)
        return E

    def _E2Ch(self, E):
        if self.cal is None:
            Ch = E
        else:
            Ch = self.cal.E2Ch(E)
        return Ch

    def FixInCal(self):
        """
        Fix position in calibrated space
        """
        if not self._fixedInCal:
            self._fixedInCal = True
            self.pos_cal = self._Ch2E(self._pos_uncal)

    def FixInUncal(self):
        """
        Fix position in uncalibrated space
        """
        if self._fixedInCal:
            self._fixedInCal = False
            self.pos_uncal = self._E2Ch(self._pos_cal)


class ID(object):
    def __init__(self, major=None, minor=None):
        if major is None:
            self.major = None
        else:
            self.major = int(major)
            if self.major < 0:
                raise ValueError("Only positive major IDs allowed")
        if minor is None:
            self.minor = None
        else:
            self.minor = int(minor)
            if self.minor < 0:
                raise ValueError("Only positive minor IDs allowed")

    def __eq__(self, other):
        if other is None:
            return False
        return ((self.major, self.minor) == (other.major, other.minor))

    def __ne__(self, other):
        if other is None:
            return True
        return not ((self.major, self.minor) == (other.major, other.minor))

    def __gt__(self, other):
        try:
            if (self.major == other.major):
                return self.minor > other.minor
            return self.major > other.major
        except TypeError:
            return True

    def __lt__(self, other):
        try:
            if (self.major == other.major):
                return self.minor < other.minor
            return self.major < other.major
        except TypeError:
            return False

    def __ge__(self, other):
        return (self.__gt__(other) or self.__eq__(other))

    def __le__(self, other):
        return (self.__lt__(other) or self.__eq__(other))

    def __hash__(self):
        # this is needed to use IDs as keys in dicts and in sets
        return hash(self.major) ^ hash(self.minor)

    def __str__(self):
        if self.major is None and self.minor is None:
            return "-"
        if self.major is None:
            return "." + str(self.minor)
        if self.minor is None:
            return str(self.major)
        return str(self.major) + "." + str(self.minor)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    def __int__(self):
        return int(self.major)

    def __float__(self):
        if self.major is None:
            return int(self.minor) / 10.
        if self.minor is None:
            return int(self.major)
        return int(self.major) + int(self.minor) / 10.

    @classmethod
    def _parseSpecialID(cls, string, manager):
        if string.upper() == "NONE":
            return list()
        elif string.upper() == "NEXT":
            return [manager.nextID]
        elif string.upper() == "PREV":
            return [manager.prevID]
        elif string.upper() == "FIRST":
            return [manager.firstID]
        elif string.upper() == "LAST":
            return [manager.lastID]
        elif string.upper() == "ACTIVE":
            return [manager.activeID]
        elif string.upper() == "ALL":
            return manager.ids
        elif string.upper() == "VISIBLE":
            return list(manager.visible)
        else:
            raise ValueError

    @classmethod
    def _parseNormalID(cls, string):
        if "." in string:
            major_s, minor_s = [m for m in string.split(".")]
            major = int(major_s)
            # TODO
#            if minor_s.lower() in ("x", "y", "c"):
#                minor = minor_s
#            else:
            minor = int(minor_s)
        else:
            major = int(string)
            minor = None

        return ID(major, minor)

    @classmethod
    def ParseIds(cls, strings, manager, only_existent=True):
        # Normalize separators
        if not isinstance(strings, str):
            strings = ",".join(strings)
        strings = ",".join(strings.split())

        # Split string
        parts = [p for p in strings.split(",") if p]

        ids = list()
        for s in parts:
            # first deal with ranges
            if "-" in s:
                start, stop = s.split("-")
                # start
                try:
                    special = cls._parseSpecialID(start, manager)
                except ValueError:
                    start = cls._parseNormalID(start)
                except AttributeError:
                    hdtv.ui.error("Invalid key word %s" % start)
                    raise ValueError
                else:
                    if len(special) == 0:
                        start = special[0]
                    elif len(special) > 0:
                        hdtv.ui.error("Invalid ID %s" % start)
                        raise ValueError
                # stop
                try:
                    special = cls._parseSpecialID(stop, manager)
                except ValueError:
                    stop = cls._parseNormalID(stop)
                except AttributeError:
                    hdtv.ui.error("Invalid key word %s" % stop)
                    raise ValueError
                else:
                    if len(special) == 0:
                        stop = special[0]
                    elif len(special) > 0:
                        hdtv.ui.error("Invalid ID %s" % stop)
                        raise ValueError
                # fill the range
                ids.extend(
                    [i for i in manager.ids if (i >= start and i <= stop)])
            else:
                try:
                    special = cls._parseSpecialID(s, manager)
                    ids.extend(special)
                except ValueError:
                    ids.append(cls._parseNormalID(s))
                except AttributeError:
                    hdtv.ui.error("Invalid key word %s" % s)
                    raise ValueError

        # ID might be None, if e.g. activeID is None
        count = ids.count(None)
        for i in range(count):
            ids.remove(None)

        # filter non-existing ids
        valid_ids = list()
        if only_existent:
            for ID in ids:
                for mID in manager.ids:
                    if (mID.major == ID.major) and (mID.minor == ID.minor):
                        valid_ids.append(ID)
                        break  # break out of for mID in manager.ids loop

                if ID not in valid_ids:  # This only works because we appended IDs above, not mIDs, because they are different instances of the ID object
                    hdtv.ui.warn("Non-existent id %s" % ID)

        else:
            valid_ids = ids

        return valid_ids

def remove_comments(string):
    """
    Removes '#' comments at the end of a line
    """
    pattern = r"(\".*?\"|\'.*?\')|(#[^\r\n]*$)"
    regex = re.compile(pattern, re.MULTILINE|re.DOTALL)
    def _replacer(match):
        if match.group(2) is not None:
            return ""
        else:
            return match.group(1)
    return regex.sub(_replacer, string)

def split_line(line):
    """
    Splits multiple commands in a single line separated by ';'
    """
    split_pattern = re.compile(r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')
    return split_pattern.split(line)[1::2]

def user_save_file(filename, force=False):
    """
    Make sure filename is not in use. Offer to backup existing file
    unless force is True.
    Returns filename if successful or False if aborted.
    """
    filename = os.path.expanduser(filename)
    if not force and os.path.exists(filename):
        hdtv.ui.warn(f'This file already exists: {filename}')

        bindings = KeyBindings()

        @bindings.add('y')
        @bindings.add('Y')
        def yes(event):
            session.default_buffer.text = 'y'
            event.app.exit(result=filename)

        @bindings.add('n')
        @bindings.add('N')
        def no(event):
            session.default_buffer.text = 'n'
            event.app.exit(result=False)
        
        @bindings.add('b')
        @bindings.add('B')
        @bindings.add(Keys.Enter)
        def backup(event):
            session.default_buffer.text = 'b'
            backup_file(filename)
            event.app.exit(result=filename)

        @bindings.add(Keys.Any)
        def _(event):
            pass

        session = PromptSession("Replace [y/n] or backup [B] existing file? ",
            key_bindings=bindings)
        filename = session.prompt()
    return filename

def backup_file(filename, bak_ext='bak'):
    """
    Safely backup a file, using a new filename
    """
    backup_name_stem = backup_name = filename + '.' + bak_ext
    for i in count():
        if not os.path.isfile(backup_name):
            break
        backup_name = backup_name_stem + '.' + str(i)
    hdtv.ui.msg(f"Renamed file {filename} to {backup_name}")
    os.rename(filename, backup_name)

def open_compressed(fname, mode='rb', **kwargs):
    """
    Behaves like open(), but automatically handles compression,
    depending on the extension of the given filename.
    """
    ext = fname.split('.')[-1]
    try:
        if ext == 'gz':
            import gzip
            return gzip.open(fname, mode, **kwargs)
        elif ext == 'xz':
            import lzma
            return lzma.open(fname, mode, **kwargs)
        elif ext == 'bz2':
            import bz2
            return bz2.open(fname, mode, **kwargs)
        return open(fname, mode, **kwargs)
    except (ImportError, AttributeError):
        raise NotImplementedError(
            "{} files are not supported. Manually use '{}' instead.".format(
                ext, 'bzip2' if 'bz2' else ext))


class Singleton(type):
    """
    Permit no more than a single instance of a class.
    Use as a metaclass:

        class MyClass(metaclass=Singleton)
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class monkey_patch_ui():
    """Replace ROOT.HDTV.Display by a noop dummy version"""
    def __init__(self):
        import hdtv
        import hdtv.rootext.display
        import ROOT
        import hdtv.dummy
       
        self._orig = ROOT.HDTV.Display
        ROOT.HDTV.Display = hdtv.dummy
    
    def __enter__(self):
        pass

    def __exit__(self, *args, **kws):
        import ROOT
        ROOT.HDTV.Display = self._orig
