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
Helper functions for access to ROOT files, treating them like POSIX
directories
"""

import os.path
import fnmatch
import ROOT

# Required for Get() to work (otherwise, histogram objects are automatically
# destroyed when the file containing them is closed).
ROOT.TH1.AddDirectory(False)


def GetRelDirectory(cur_posix_path, cur_root_dir, path):
    """
    Resolve the relative path path with respect to the current directory
    specified by cur_posix_path and cur_root_dir.

    cur_posix_path is a string specifying the current working directory. If
    cur_root_dir is not None, it is taken as a TDirectoryFile object specifying
    the working directory inside the ROOT file. The ROOT file is expected to
    reside inside the directory specified by cur_posix_path.

    Returns a triple (new_posix_path, new_root_file, new_root_dir).
    new_posix_path is the new posix path.
    new_root_file is the ROOT file in wich new_root_dir resides, or None if
    new_root_dir resides in the same file as cur_root_dir. If new_root_file is
    not None, the caller is expected to close the file after being done with it.
    (Note: a path moving out of a ROOT file and then back in
    is considered to refer to a different file, with the consequences mentioned
    above.)
    new_root_dir is the new ROOT TDirectory.

    If path is invalid, (None, None, None) is returned.
    """
    # Save the current ROOT directory

    # Annoyingly, ROOT automatically changes the ''current directory''
    # (ROOT.gDirectory) to that file if a ROOT file is opened. Obviously,
    # completion should *not* change the current directory, but we need to open
    # the file to see what is inside. Thus, we have to save the current
    # directory and restore it after we are done. Note that this trick is *not*
    # thread-safe!

    # Saving the current directory turns out to be tricky; see
    # http://root.cern.ch/phpBB2/viewtopic.php?t=6382

    prev_root_dir = ROOT.gDirectory.GetDirectory("")

    try:
        error = False
        rfile = None
        pcomp = path.split("/")

        # Handle absolute paths
        if len(pcomp) >= 2 and pcomp[0] == "":
            del pcomp[0]
            cur_posix_path = "/"
            cur_root_dir = None

        # Descend down the path
        for pc in pcomp:
            if cur_root_dir is not None:
                if pc == "" or pc == ".":
                    pass
                elif pc == "..":
                    cur_root_dir = cur_root_dir.GetMotherDir()
                    if cur_root_dir is None:
                        if rfile is not None:
                            # print "Info: closing %s" % str(rfile)
                            rfile.Close()
                else:
                    cur_root_dir = cur_root_dir.Get(pc)
                    if not isinstance(cur_root_dir, ROOT.TDirectoryFile):
                        error = True
                        break
            else:
                full_name = os.path.join(cur_posix_path, pc)
                if os.path.isdir(full_name):
                    cur_posix_path = full_name
                elif IsROOTFile(full_name):
                    # print("Info: Opening %s" % full_name)
                    # Disable warnings when opening files
                    ROOT.gErrorIgnoreLevel = ROOT.kError
                    rfile = ROOT.TFile(full_name)
                    ROOT.gErrorIgnoreLevel = ROOT.kInfo
                    if rfile.IsZombie():
                        error = True
                        break
                    cur_root_dir = rfile
                else:
                    error = True
                    break

        if error:
            if rfile:
                # print "Info: closing %s" % str(rfile)
                rfile.Close()
            return (None, None, None)

        return (cur_posix_path, rfile, cur_root_dir)

    finally:
        # Restore the saved ROOT directory
        if prev_root_dir:
            prev_root_dir.cd()


def PathComplete(cur_posix_path, cur_root_dir, path, pattern, dirs_only=False):
    """
    Suggest completions for paths to objects inside ROOT files

    cur_posix_path is a string specifying the current working directory. If
    cur_root_dir is not None, it is taken as a TDirectoryFile object specifying
    the working directory inside the ROOT file. The ROOT file is expected to
    reside inside the directory specified by cur_posix_path.

    path and pattern specify the path to be completed. path is taken as the
    fixed part. pattern in taken as the beginning of the part for which to
    suggest completions.

    dirs_only specifies whether to suggest directories only.
    """
    (posix_path, rfile, root_dir) = GetRelDirectory(cur_posix_path, cur_root_dir, path)
    if (posix_path, rfile, root_dir) == (None, None, None):
        return []

    # Suggest possible completions
    options = []
    l = len(pattern)

    if root_dir is not None:
        # Suggest completions from a ROOT directory
        keys = root_dir.GetListOfKeys()
        if keys is not None:
            for k in keys:
                name = k.GetName()
                if name[0:l] == pattern:
                    if k.GetClassName() == "TDirectoryFile":
                        options.append(name + "/")
                    elif not dirs_only:
                        options.append(name + " ")

    else:
        for name in os.listdir(posix_path):
            if name[0:l] == pattern:
                if os.path.isdir(os.path.join(posix_path, name)) or IsROOTFile(
                    os.path.join(posix_path, name)
                ):
                    options.append(name + "/")

    if rfile:
        # print "Info: closing %s" % str(rfile)
        rfile.Close()

    return options


def Get(cur_posix_path, cur_root_dir, pattern):
    """
    Function to load objects from ROOT files, treating them like POSIX
    directories.

    cur_posix_path specifies the current working directory.
    If cur_root_dir is a ROOT TDirectoryFile object, searching starts relative
    to that directory. If is is None, searching starts relative to
    cur_posix_path.    Pattern is a shell-style pattern, e.g. "*.root/spec/*".

    Returns a list of ROOT objects.
    """
    pcomp = pattern.split("/")

    if pcomp[0] == "":
        del pcomp[0]
        cur_root_dir = None
        cur_posix_path = "/"

    # Save the current ROOT directory (see comments in function PathComplete)
    prev_root_dir = ROOT.gDirectory.GetDirectory("")

    if cur_root_dir is None:
        objs = RecursivePathMatch(cur_posix_path, pcomp)
    else:
        objs = RecursiveROOTMatch(cur_posix_path, cur_root_dir, pcomp)

    # Restore the saved ROOT directory
    if prev_root_dir:
        prev_root_dir.cd()

    return objs


def RecursivePathMatch(cur_path, pcomp):
    if pcomp[0] in (".", ".."):
        if len(pcomp) > 1:
            return RecursivePathMatch(os.path.join(cur_path, pcomp[0]), pcomp[1:])
        else:
            return []

    matched_objects = []
    for name in os.listdir(cur_path):
        if fnmatch.fnmatch(name, pcomp[0]):
            full_name = os.path.join(cur_path, name)
            if os.path.isfile(full_name) and IsROOTFile(full_name):
                rfile = ROOT.TFile(full_name)
                matched_objects += RecursiveROOTMatch(cur_path, rfile, pcomp[1:])
                rfile.Close()
            elif os.path.isdir(full_name):
                matched_objects += RecursivePathMatch(full_name, pcomp[1:])
    return matched_objects


def RecursiveROOTMatch(rfile_path, rfile_dir, pcomp):
    """
    Recursively descend into ROOT file directory structure.
    rfile_path is a string specifying the POSIX directory of the ROOT file
    rfile_dir is a TDirectoryFile object specifying the current directory
     in the ROOT file
    """
    if pcomp[0] == ".":
        if len(pcomp) <= 1:
            return []
        else:
            return RecursiveROOTMatch(rfile_path, rfile_dir, pcomp[1:])
    elif pcomp[0] == "..":
        if len(pcomp) <= 1:
            return []
        else:
            mother_dir = rfile_dir.GetMotherDir()
            if mother_dir is not None:
                return RecursiveROOTMatch(rfile_path, mother_dir, pcomp[1:])
            else:
                return RecursivePathMatch(rfile_path, pcomp[1:])
    else:
        keys = rfile_dir.GetListOfKeys()
        if keys is None:
            return []

        matched_objects = []
        for k in keys:
            name = k.GetName()
            if fnmatch.fnmatch(name, pcomp[0]):
                if len(pcomp) == 1:
                    matched_objects.append(k.ReadObj())
                elif k.GetClassName() == "TDirectoryFile":
                    matched_objects += RecursiveROOTMatch(
                        rfile_path, k.ReadObj(), pcomp[1:]
                    )

    return matched_objects


def IsROOTFile(fname):
    """
    Tests if fname is a ROOT file
    """
    # Unfortunately, ROOT does not seem to provide a way to check if a given
    # file is a ROOT file, except for actually opening it. (TBrowser seems to
    # go by the filename extension.)

    try:
        if not os.path.isfile(fname):
            return False
        f = open(fname, "rb")
        ident = f.read(4).decode()
        f.close()
        return ident == "root"
    except (OSError, IOError):
        return False
