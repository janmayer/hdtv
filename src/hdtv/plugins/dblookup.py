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
Gamma database integration for HDTV
"""

import re
from html import escape

import hdtv.cmdline
import hdtv.database
import hdtv.fit
import hdtv.options
import hdtv.plugins
import hdtv.ui


class Database:
    def __init__(self):
        hdtv.ui.debug("Loaded Database Lookup plugin")

        self.opt = {}
        self.database = None

        # Register configuration variables for fit peakfind
        self.opt["db"] = hdtv.options.Option(
            default="PGAAlib_IKI2000",
            parse=hdtv.options.parse_choices(list(hdtv.database.databases.keys())),
            changeCallback=lambda x: self.Set(x),
        )  # default database
        hdtv.options.RegisterOption("database.db", self.opt["db"])

        # Automatically lookup fitted peaks in database
        self.opt["auto_lookup"] = hdtv.options.Option(
            default=False,
            parse=hdtv.options.parse_bool,
            changeCallback=lambda x: self.SetAutoLookup(x),
        )
        hdtv.options.RegisterOption("database.auto_lookup", self.opt["auto_lookup"])

        # Set default database
        #        hdtv.options.Reset("database.db")

        self.opt["fuzziness"] = hdtv.options.Option(
            default=1.0, parse=lambda x: float(x)
        )
        hdtv.options.RegisterOption(
            "database.fuzziness", self.opt["fuzziness"]
        )  # Lookup fuzziness

        self.opt["sort_key"] = hdtv.options.Option(default=None)
        hdtv.options.RegisterOption("database.sort_key", self.opt["sort_key"])

        self.opt["sort_reverse"] = hdtv.options.Option(
            default=False, parse=hdtv.options.parse_bool
        )
        hdtv.options.RegisterOption("database.sort_reverse", self.opt["sort_reverse"])

        # TODO: proper help
        prog = "db lookup"
        description = "Lookup database entry"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument(
            "-f",
            "--fuzziness",
            type=float,
            default=None,  # Default is handled via hdtv.options.Option
            help="Fuzziness for database lookup",
        )
        parser.add_argument(
            "-k",
            "--sort-key",
            action="store",
            default=None,  # Default is handled via hdtv.options.Option
            help="Sort by key",
        )
        parser.add_argument(
            "-r",
            "--sort-reverse",
            action="store_true",
            default=None,
            help="Reverse sorting",
        )
        parser.add_argument("specs", nargs="+")
        hdtv.cmdline.AddCommand(prog, self.Lookup, parser=parser, fileargs=False)

        prog = "db list"
        description = "Show available databases"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        hdtv.cmdline.AddCommand(prog, self.List, parser=parser, fileargs=False)

        prog = "db set"
        description = "Set database"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument("database")
        hdtv.cmdline.AddCommand(
            prog,
            lambda args: hdtv.options.Set("database.db", args.database),
            parser=parser,
            fileargs=False,
        )

        prog = "db info"
        description = "Show info about database"
        parser = hdtv.cmdline.HDTVOptionParser(prog=prog, description=description)
        parser.add_argument("database", default=None, nargs="*")
        hdtv.cmdline.AddCommand(prog, self.Info, parser=parser, fileargs=False)

    def FitPeakPostHook(self, fitclass):
        """
        Hook for hdtv.fit.Fit.FitPeakFunc function to automatically list matching
        database entries
        """
        for p in fitclass.peaks:
            self.Lookup(["energy=" + str(p.pos_cal.value)], defaults=True)

    def SetAutoLookup(self, autolookup_opt):
        """
        Activate/Deactivate automatic lookup of peaks
        """
        if autolookup_opt.Get():
            if self.FitPeakPostHook not in hdtv.fit.Fit.FitPeakPostHooks:
                hdtv.fit.Fit.FitPeakPostHooks.append(self.FitPeakPostHook)
                hdtv.ui.msg("Autolookup activated")
        else:
            try:
                hdtv.fit.Fit.FitPeakPostHooks.remove(self.FitPeakPostHook)
            except ValueError:  # Ignore error for trying to remove nonexistant element
                pass
            else:
                hdtv.ui.msg("Autolookup deactivated")

    def Set(self, dbname=None, open=False):
        """
        Set database Callback

        open: If true automatically opens and reads database
        """
        if dbname is None:
            dbname = hdtv.options.Get("database.db")
        else:
            try:
                dbname = dbname.Get()  # dbname may be an option
            except AttributeError:
                pass
        try:
            db = hdtv.database.databases[dbname.lower()]
            if self.database != db:
                self.database = db()
                if open:
                    self.database.open()
                hdtv.ui.msg('"' + self.database.description + '" loaded')
                return True
        except KeyError:
            raise hdtv.cmdline.HDTVCommandError("No such database: " + dbname)

    def Info(self, args):
        """
        Print info about database(s)
        """
        if not args.database:
            args.database = [hdtv.options.Get("database.db")]

        for dbs in args.database:
            db = hdtv.database.databases[dbs.lower()]()
            try:
                hdtv.ui.msg(html=f"<b>Database</b>: {escape(db.name)}")
                hdtv.ui.msg(html=f"<b>Description</b>: {escape(db.description)}")
                self.showDBfields(db)

            except KeyError:
                raise hdtv.cmdline.HDTVCommandError("No such database: " + db.name)

    def assureOpen(self):
        """
        assure that the database has been opened
        """
        try:
            if not self.database.opened:
                self.database.open()
        except AttributeError:
            self.Set(open=True)

    def List(self, args):
        """
        List available databases
        """
        for name, db in list(hdtv.database.databases.items()):
            hdtv.ui.msg(html=f"<b>{escape(name)}</b>: {escape(db().description)}")

    def showDBfields(self, db=None):
        """
        Show fields of database db. If db is None show field of current database
        """

        html = "<b>Valid fields</b>: "
        if db is None:
            db = self.database
        html += ", ".join([f"'{s!s}'" for s in db.fParamConv.keys()])
        hdtv.ui.msg(html=html)

    def Lookup(self, args, defaults=False):
        """
        Lookup entry in database

        args.specs should be something like "<fieldname>=value"
        if <fieldname> is omitted it is assumed to be energy
        """

        self.assureOpen()

        lookupargs = {}

        # Valid arguments
        vargs = []
        for v in self.database.fParamConv.keys():
            vargs.append(v.lower())

        # parse arguments
        for a in args.specs:
            m = re.match(r"(.*)=(.*)", a)
            if m is not None:
                if m.group(1).lower() in vargs:
                    lookupargs[m.group(1)] = m.group(2)
                else:
                    self.showDBfields()
                    return False
            else:
                lookupargs["energy"] = float(a)
                continue

        if defaults or args.sort_key is None:
            lookupargs["sort_key"] = hdtv.options.Get("database.sort_key")
        else:
            lookupargs["sort_key"] = args.sort_key

        if defaults or args.sort_reverse is None:
            lookupargs["sort_reverse"] = hdtv.options.Get("database.sort_reverse")
        else:
            lookupargs["sort_reverse"] = args.sort_reverse

        if defaults or args.fuzziness is None:
            fuzziness = hdtv.options.Get("database.fuzziness")
        else:
            fuzziness = args.fuzziness

        try:
            results = self.database.find(fuzziness, **lookupargs)
        except AttributeError:
            return False

        if len(results) > 0:
            table = hdtv.util.Table(
                results,
                header=self.database.fOrderedHeader,
                keys=self.database.fParamConv.keys(),
            )
            hdtv.ui.msg(html=str(table))

        hdtv.ui.msg("Found " + str(len(results)) + " results")


# plugin initialisation
database = Database()
hdtv.cmdline.RegisterInteractive("database", database)
