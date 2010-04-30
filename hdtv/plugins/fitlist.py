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

#-------------------------------------------------------------------------------
# Write and Read Fitlist saved in xml format
# 
#-------------------------------------------------------------------------------
import os
import glob
import hdtv.cmdline
import hdtv.fitxml 
import hdtv.ui
import hdtv.util


class FitlistManager(object):
    def __init__(self, spectra):
        hdtv.ui.msg("loaded fitlist plugin")
        self.spectra = spectra
        self.xml = hdtv.fitxml.FitXml(spectra)
        self.list = dict()
        
        self.tv = FitlistHDTVInterface(self)
        
    def WriteXML(self, sid, fname=None):
        name = self.spectra.dict[sid].name
        # remember absolut pathname for later use
        fname = os.path.abspath(fname)
        self.list[name] = fname
        self.xml.WriteFitlist(fname, sid)
        
    def ReadXML(self, sid, fname, refit=False):
        spec = self.spectra.dict[sid]
        # remember absolut pathname for later use
        fname = os.path.abspath(fname)
        self.list[spec.name] = fname
        self.xml.ReadFitlist(fname, sid)

    def WriteList(self, fname):
        lines = list()
        listpath = os.path.abspath(fname)
        for (spec, xml) in self.list.iteritems():
            # create relativ path name
            common = os.path.commonprefix([listpath,xml])
            xml=xml.replace(common,"")
            xml=xml.strip("/")
            lines.append(spec + ": "+xml)
        text = "\n".join(lines)
        f = file(fname, "w")
        f.write(text)
        f.close()
        
    def ReadList(self, fname):
        try:
            f = file(fname, "r")
        except IOError, msg:
            hdtv.ui.error("Error opening file: %s" % msg)
            return None
        dirname = os.path.dirname(fname)
        linenum = 0
        for l in f:
            linenum += 1
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
                    hdtv.ui.warn("No such file %s" %xmlfile)
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
                hdtv.ui.warn("Could not parse line %d of file %s: ignored." % (linenum, fname))
        f.close()


class FitlistHDTVInterface(object):
    def __init__(self, FitlistIf):
        self.FitlistIf = FitlistIf
        self.spectra = FitlistIf.spectra

        prog = "fit write"
        description = "write fits to xml file"
        usage = "%prog filename"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-s", "--spectrum", action = "store", default = "active",
                                help = "for which the fits should be saved (default=active)")
        parser.add_option("-F","--force",action = "store_true", default=False,
                            help = "overwrite existing files without asking")
        hdtv.cmdline.AddCommand(prog, self.FitWrite, fileargs=True, parser=parser)

        prog = "fit read"
        description = "read fits from xml file"
        usage ="%prog filename"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-s", "--spectrum", action = "store", default = "active",
                                help = "spectra to which the fits should be added (default=active)")
        parser.add_option("-r", "--refit", action = "store_true", default = False,
                                help = "Force refitting during load")
        hdtv.cmdline.AddCommand(prog, self.FitRead, nargs=1, fileargs=True, parser=parser)

        prog = "fit getlists"
        description = "reads fitlists according to the list saved in a file"
        usage = "%prog filename"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.FitGetlists, nargs=1, fileargs=True, parser=parser)
        
        prog = "fit savelists"
        description = "saves a list of spectrum names and corresponding fitlist files to file"
        usage = "%prog filename"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-F","--force",action = "store_true", default=False,
                        help = "overwrite existing files without asking")
        hdtv.cmdline.AddCommand(prog, self.FitSavelists, nargs=1, fileargs=True, parser=parser)
        

    def FitWrite(self, args, options):
        """
        Saving a fitlist as xml
        """
        # get spectrum
        sids = hdtv.util.ID.ParseIds(options.spectrum, __main__.spectra)
        if len(sids)==0:
            hdtv.ui.error("There is no active spectrum")
            return
        if len(sids)>1:
            hdtv.ui.error("Can only save fitlist of one spectrum")
            return
        sid = sids[0]
        # get filename 
        if len(args)==0:
            name = self.spectra.dict[sid].name
            try:
                fname = self.FitlistIf.list[name]
            except KeyError:
                (base, ext) = os.path.splitext(name)
                fname = base + ".xfl"
        else:
            fname = os.path.expanduser(args[0])
        hdtv.ui.msg("Saving fits to %s" %fname)
        if not options.force and os.path.exists(fname):
            hdtv.ui.warn("This file already exists:")
            overwrite = None
            while not overwrite in ["Y","y","N","n","","B","b"]:
                question = "Do you want to replace it [y,n] or backup it [B]:"
                overwrite = raw_input(question)
            if overwrite in ["b","B",""]:
                os.rename(fname,"%s.back" %fname)
            elif overwrite in ["n","N"]:
                return 
        # do the work
        self.FitlistIf.WriteXML(sid, fname)

    def FitRead(self, args, options):
        """
        reading a fitlist from xml 
        """
        fnames = list()
        for fname in args:
            fname = os.path.expanduser(fname)
            more = glob.glob(fname)
            if len(more)==0:
                hdtv.ui.warn("No such file %s" %fname)
            fnames.extend(more)
        sids = hdtv.util.ID.ParseIds(options.spectrum, __main__.spectra)
        if len(sids)==0:
            hdtv.ui.error("There is no active spectrum")
            return
        for fname in fnames:
            for sid in sids:
                hdtv.ui.msg("Reading fitlist %s to spectrum %s" %(fname, sid))
                self.FitlistIf.ReadXML(sid, fname, refit=options.refit)

    def FitSavelists(self, args, options):
        fname = os.path.expanduser(args[0])
        if not options.force and os.path.exists(fname):
            hdtv.ui.warn("This file already exists:")
            overwrite = None
            while not overwrite in ["Y","y","N","n","","B","b"]:
                question = "Do you want to replace it [y,n] or backup it [B]:"
                overwrite = raw_input(question)
            if overwrite in ["b","B",""]:
                os.rename(fname,"%s.back" %fname)
            elif overwrite in ["n","N"]:
                return 
        # do the work
        self.FitlistIf.WriteList(fname)
    
    def FitGetlists(self, args, options):
        fname = args[0]
        fname = os.path.expanduser(args[0])
        fname = glob.glob(fname)
        if len(fname)>1:
            return "USAGE"
        fname = fname[0]
        if not os.path.exists(fname):
            hdtv.ui.error("No such file %s" %fname)
            return
        self.FitlistIf.ReadList(fname)
        
import __main__
__main__.fitxml = FitlistManager(__main__.spectra)

