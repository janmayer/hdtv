#!/usr/bin/python

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
