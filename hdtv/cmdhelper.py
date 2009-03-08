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

def ParseRange(strings, special=["all", "none"]):
	"""
	Parse a list of strings specifying (possibly many) ranges and
	return all values from all ranges. Ranges are inclusive. Each
	value is returned at most once, but it is no error if it occurs
	more than once. If ["all"] or ["none"] are passed, "ALL" or "NONE"
	are returned. Further such keywords may be defined using the
	optional special parameter. If the string is malformed, a
	ValueError exception is raised.
	
	Example: "1 3 2-5 10 12" gives set([1 2 3 4 5 10 12]).
	"""
	# Test for special strings
	if len(strings) == 1:
		if strings[0].strip().lower() in special:
			return strings[0].strip().upper()
	
	# Parse ranges
	values = set()
	for part in strings:
		r = part.split("-")
		if len(r) == 1:
			values.add(int(r[0]))
		elif len(r) == 2:
			values |= set(range(int(r[0]), int(r[1])+1))
		else:
			raise ValueError, "Malformed range"
			
	return values
