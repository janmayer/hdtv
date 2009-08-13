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
# Gamma database integration for HDTV
#-------------------------------------------------------------------------------


import hdtv.cmdline
import hdtv.options
import hdtv.database
import re

class Database(object):
    
    def __init__(self):
        
        print "loaded Database Lookup plugin"
        
        
        self.opt = dict()
        # Register configuration variables for fit peakfind
        self.opt["db"] = hdtv.options.Option(default = "PGAAlib_IKI2000") # default database
        hdtv.options.RegisterOption("database.db", self.opt["db"])    
        
        self.opt["fuzziness"] = hdtv.options.Option(default = 1.0)
        hdtv.options.RegisterOption("database.fuzziness", self.opt["fuzziness"]) # Lookup fuzziness
        
        self.opt["sort_key"] = hdtv.options.Option(default = None)
        hdtv.options.RegisterOption("database.sort_key", self.opt["sort_key"])
        
        self.opt["sort_reverse"] = hdtv.options.Option(default = False)
        hdtv.options.RegisterOption("database.sort_reverse", self.opt["sort_reverse"])
        
        # TODO: proper help
        prog = "db lookup"
        description = "Lookup database entry"
        usage = "%prog <specs>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        parser.add_option("-f", "--fuzziness", action = "store", default = None, # Default is handled via hdtv.options.Option
                        help = "Fuzziness for database lookup")
        parser.add_option("-k", "--sort-key", action = "store", default = None, # Default is handled via hdtv.options.Option
                        help = "Sort by key")
        parser.add_option("-r", "--sort-reverse", action = "store_true", default = None,
                        help = "Reverse sorting")
 
        hdtv.cmdline.AddCommand(prog, self.Lookup, parser = parser, minargs = 1, fileargs = False)
        
        prog = "db list"
        description = "Show available databases"
        usage = "%prog"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.List, parser = parser, nargs = 0, fileargs = False)
        
        prog = "db set"
        description = "Set database"
        usage = "%prog <db>"
        parser = hdtv.cmdline.HDTVOptionParser(prog = prog, description = description, usage = usage)
        hdtv.cmdline.AddCommand(prog, self.Open, parser = parser, nargs = 1, fileargs = False)
        
        self.database = self.opt["db"]
        
    def Open(self, args = None, options = None):
        """ 
        open database
        """
        
        if args is None:
            dbname = hdtv.options.Get("database.db")
        else:    
            dbname = args[0]
        
        try:
            # Check if it has already been opened
            dbname = dbname
            if self.database != getattr(hdtv.database, dbname): 
                print "opening database", dbname
                self.database = getattr(hdtv.database, dbname)
                self.database.open()
                hdtv.options.Set("database.db", dbname)
                print "\"" + self.database.description + "\" loaded\n"
        except AttributeError:
            print "No such database", dbname
            return False               
        return True
    
    def List(self, args, options):
        
        for (db, desc) in hdtv.database.databases.items():
            print  db + ": " + str(desc)
        
        
    def Lookup(self, args, options):
        """
        Lookup entry in database
        
        args should be something like "<fieldname>=value"
        if <fieldname> is omitted it is assumed to be energy
        """
        if not self.Open():
            return False

        try:
            lookupargs = dict()
#            print self.database.fields
            # Valid arguments
            vargs = list()
            for v in self.database.fields:
                vargs.append(v.lower())
            
            # parse arguments
            for a in args:
                m = re.match(r"(.*)=(.*)", a)
                if not m is None:
                    if m.group(1).lower() in vargs:
                        lookupargs[m.group(1)] = m.group(2)
                    else:
                        print "Valid fields: ",
                        for key in self.database.fields.keys():
                            print "\'" + str(key) + "\'",
                else:
                    try: # default
                        lookupargs['energy'] = float(a)
                        continue
                    except ValueError:
                        return "USAGE"

            if options.sort_key is None:
                lookupargs['sort_key'] = hdtv.options.Get("database.sort_key")
            else:
                lookupargs['sort_key'] = options.sort_key
                
            if options.sort_reverse is None:
                lookupargs['sort_reverse'] = hdtv.options.Get("database.sort_reverse") 
            else:
                lookupargs['sort_reverse'] = options.sort_reverse
            
            if options.fuzziness is None:
                fuzziness = hdtv.options.Get("database.fuzziness")
            else:
                fuzziness = options.fuzziness
                
            try:
                results = self.database.find(float(fuzziness), **lookupargs)
            except AttributeError:
                return False
            
            for r in results:
                print r
                
            print "Found", len(results), "results" 

        except ValueError:           
            return "USAGE"
        
# plugin initialisation
import __main__
__main__.database = Database()
