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
Write and Read Fitlist saved in xml format
"""

import os
import glob
import hdtv.cmdline
import hdtv.options
import hdtv.fitxml
import hdtv.ui
import hdtv.util


class FitlistManager(object):
    def __init__(self, spectra):
        hdtv.ui.debug("Loaded fitlist plugin")

        self.spectra = spectra
        self.xml = hdtv.fitxml.FitXml(spectra)
        self.list = dict()

        self.tv = FitlistHDTVInterface(self)

    def WriteXML(self, sid, fname=None):
        name = self.spectra.dict[sid].name
        # remember absolut pathname for later use
        fname = os.path.abspath(fname)
        self.list[name] = fname
        with hdtv.util.open_compressed(fname, mode='wb') as f:
            self.xml.WriteFitlist(f, sid)

    def ReadXML(self, sid, fname, refit=False, interactive=True):
        spec = self.spectra.dict[sid]
        # remember absolut pathname for later use
        fname = os.path.abspath(fname)
        self.list[spec.name] = fname
        with hdtv.util.open_compressed(fname, mode='rb') as f:
            self.xml.ReadFitlist(f, sid, refit, interactive, fname=fname)

    def WriteList(self, fname):
        lines = list()
        listpath = os.path.abspath(fname)
        for (spec, xml) in self.list.items():
            # create relativ path name
            common = os.path.commonprefix([listpath, xml])
            xml = xml.replace(common, "")
            xml = xml.strip("/")
            lines.append(spec + ": " + xml)
        text = "\n".join(lines)
        with open(fname, "w") as f:
            f.write(text)

    def ReadList(self, fname):
        with open(fname, "r") as f:
            dirname = os.path.dirname(fname)
            for linenum, l in enumerate(f):
                # Remove comments and whitespace; ignore empty lines
                l = l.split('#', 1)[0].strip()
                if l == "":
                    continue
                try:
                    (k, v) = l.split(':', 1)
                    name = k.strip()
                    xmlfile = v.strip()
                    # create valid path from relative pathnames
                    xmlfile = os.path.join(dirname, xmlfile)
                    if not os.path.exists(xmlfile):
                        hdtv.ui.warn("No such file %s" % xmlfile)
                        continue
                    sid = None
                    for ID in self.spectra.ids:
                        if self.spectra.dict[ID].name == name:
                            sid = ID
                            break
                    if sid is not None:
                        self.ReadXML(sid, xmlfile)
                    else:
                        hdtv.ui.warn("Spectrum %s is not loaded. " % name)
                except ValueError:
                    hdtv.ui.warn(
                        "Could not parse line %d of file %s: ignored." %
                        (linenum + 1, fname))


class FitlistHDTVInterface(object):
    def __init__(self, FitlistIf):
        self.FitlistIf = FitlistIf
        self.spectra = FitlistIf.spectra

        prog = "fit write"
        description = "write fits to xml file"
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default="active",
            help="for which the fits should be saved (default=active)")
        parser.add_argument("-F", "--force", action="store_true", default=False,
            help="overwrite existing files without asking")
        parser.add_argument(
            "filename",
            nargs='?',
            default=None,
            help='''may contain %%s, %%d, %%02d (or other python
            format specifier) as placeholder for spectrum id''')
        hdtv.cmdline.AddCommand(prog, self.FitWrite,
                                fileargs=True, parser=parser)

        prog = "fit read"
        description = "read fits from xml file"
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description)
        parser.add_argument(
            "-s",
            "--spectrum",
            action="store",
            default="active",
            help="spectra to which the fits should be added (default=active)")
        parser.add_argument("-r", "--refit", action="store_true", default=False,
            help="Force refitting during load")
        parser.add_argument(
            "filename",
            nargs='+',
            help='''may contain %%s, %%d, %%02d (or other python
            format specifier) as placeholder for spectrum id''')
        hdtv.cmdline.AddCommand(
            prog, self.FitRead, fileargs=True, parser=parser)

        prog = "fit getlists"
        description = "reads fitlists according to the list saved in a file"
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description)
        parser.add_argument(
            "filename",
            default=None)
        hdtv.cmdline.AddCommand(prog, self.FitGetlists,
                                fileargs=True, parser=parser)

        prog = "fit savelists"
        description = "saves a list of spectrum names and corresponding fitlist files to file"
        parser = hdtv.cmdline.HDTVOptionParser(
            prog=prog, description=description)
        parser.add_argument("-F", "--force", action="store_true", default=False,
            help="overwrite existing files without asking")
        parser.add_argument(
            "filename",
            metavar='output-file',
            default=None)
        hdtv.cmdline.AddCommand(prog, self.FitSavelists,
                                fileargs=True, parser=parser)

    def FitWrite(self, args):
        """
        Saving a fitlist as xml
        """
        # TODO: this need urgent cleanup and testing, especially for the saving
        # of fitlists from multiple spectra, but I'm really in a hurry now. Sorry. Ralf
        # get spectrum
        sids = hdtv.util.ID.ParseIds(args.spectrum, __main__.spectra)
        if len(sids) == 0:
            raise hdtv.cmdline.HDTVCommandError("There is no active spectrum")
        if len(sids) > 1:
            # TODO: Check if placeholder character is present in filename and
            # warn if not
            pass
#            raise hdtv.cmdline.HDTVCommandError("Can only save fitlist of one spectrum")
        for sid in sids:
            #            sid = sids[0]
            # get filename
            if args.filename is None:
                name = self.spectra.dict[sid].name
                try:
                    fname = self.FitlistIf.list[name]
                except KeyError:
                    (base, ext) = os.path.splitext(name)
                    fname = base + "." + hdtv.options.Get("fit.list.default_extension")
            else:
                fname = os.path.expanduser(args.filename)
                # Try to replace placeholder "%s" in filename with specid
                try:
                    fname = fname % sid
                except TypeError:  # No placeholder found
                    # TODO: do something sensible here... Luckily hdtv will not
                    # overwrite spectra without asking...
                    pass
            hdtv.ui.msg("Saving fits of spectrum %d to %s" % (sid, fname))
        
            if hdtv.util.user_save_file(fname, args.force):
                self.FitlistIf.WriteXML(sid, fname)

    def FitRead(self, args):
        """
        reading a fitlist from xml
        """
        fnames = dict()  # Filenames for each spectrum ID
        sids = hdtv.util.ID.ParseIds(args.spectrum, __main__.spectra)
        if len(sids) == 0:
            raise hdtv.cmdline.HDTVCommandError("There is no active spectrum")

        # Build list of files to load for each spectrum
        for sid in sids:
            fnames[sid] = list()  # Filenames for this spectrum ID
            for fname_raw in args.filename:
                try:
                    # Try to replace format placeholder (e.g. %s) with spectrum
                    # ID
                    fname = fname_raw % sid
                except TypeError:  # No placeholder found
                    fname = fname_raw

                fname = os.path.expanduser(fname)
                more = glob.glob(fname)
                if len(more) == 0:
                    hdtv.ui.warn("No such file %s" % fname)
                fnames[sid].extend(more)

        # Load files
        for sid in sids:
            for fname in fnames[sid]:
                hdtv.ui.msg("Reading fitlist %s to spectrum %s" % (fname, sid))
                self.FitlistIf.ReadXML(sid, fname, refit=args.refit)

    def FitSavelists(self, args):
        if hdtv.util.user_save_file(args.filename, args.force):
            self.FitlistIf.WriteList(args.filename)

    def FitGetlists(self, args):
        fname = glob.glob(os.path.expanduser(args.filename))
        if len(fname) > 1:
            raise hdtv.cmdline.HDTVCommandError("More than 1 files match the pattern")
        fname = fname[0]
        if not os.path.exists(fname):
            raise hdtv.cmdline.HDTVCommandError("No such file %s" % fname)
        self.FitlistIf.ReadList(fname)

hdtv.options.RegisterOption('fit.list.default_extension',
                            hdtv.options.Option(default="xfl"))

import __main__
fitxml = FitlistManager(__main__.spectra)
hdtv.cmdline.RegisterInteractive("fitxml", fitxml)
