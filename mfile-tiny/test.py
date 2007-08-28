#!/usr/bin/python

import ROOT
import time
from specreader import *

def wait():
	try:
		while True:
			time.sleep(10)
	except KeyboardInterrupt:
		pass

sr = SpecReader()
hist = sr.Get("../test/t13", "hist1", "Test")
hist.Draw()

wait()
