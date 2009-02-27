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
import ROOT
import hdtv.util


def MakeCalibration(cal):
	""" 
	Create a ROOT.HDTV.Calibration object from a python list
	"""
	if not isinstance(cal, ROOT.HDTV.Calibration):
		if cal==None:
			cal = [0,1]
		calarray = ROOT.TArrayD(len(cal))
		for (i,c) in zip(range(0,len(cal)),cal):
			calarray[i] = c
		# create the calibration object
		cal = ROOT.HDTV.Calibration(calarray)
	return cal

def CalFromPairs(pairs):
	"""
	Create a calibration from two pairs of channel and corresponding energy
	"""
 	if not len(pairs)==2:
		# FIXME: more pairs would be great!
 		print "The number of pairs must be exactly two."
 		raise ValueError
 	cal = hdtv.util.Linear.FromXYPairs(pairs[0], pairs[1])
	return MakeCalibration([cal.p0, cal.p1])

def CalFromFile(fname):
	"""
	Read calibration polynom from file
	
	There should be one coefficient in each line, starting with p0
	"""
	fname = os.path.expanduser(fname)
	try:
		f = open(fname)
	except IOError, msg:
		print msg
		return []
	try:
		calpoly = []
		for line in f:
			l = line.strip()
			if l != "":
				calpoly.append(float(l))
	except ValueError:
		f.close()
		print "Malformed calibration parameter file."
		raise ValueError
	f.close()
	return MakeCalibration(calpoly)

