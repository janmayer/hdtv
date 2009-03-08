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
import hdtv.dlmgr
import array
import os

class SpecReaderError(Exception):
	pass

class TextSpecReader:
	"""
	Configurable formatted text file import
	"""
	def __init__(self):
		pass
		
	def GetSpectrum(self, fname, histname, histtitle):
		# Preliminary!!!
		data = []
		f = open(fname, "r")
		try:
			for line in f:
				line = line.strip()
				if line != '' and line[0] != '#':
					vals = line.split()
					if len(vals) != 2:
						f.close()
						raise SpecReaderError, "Found row with more or less than two columns"
					else:
						data.append(map(lambda s: float(s), vals))
		
		except ValueError:
			f.close()
			raise SpecReaderError, "Non-numeric value found in text file"
		f.close()
			
		# Sort by increasing x value
		data.sort(lambda x,y: cmp(x[0], y[0]))
		
		# Generate array containing bin centers
		# xbins = array.array('d', map(lambda x: x[0], data))
		
		# Create and fill ROOT histogram object
		hist = ROOT.TH1D(histname, histtitle, len(data), -0.5, len(data)-0.5)
		for b in range(0, len(data)):
			hist.SetBinContent(b+1, data[b][1])
			
		return hist

class SpecReader:
	def __init__(self):
		self.fDefaultFormat = "mfile"
		
	def GetSpectrum(self, fname, fmt=None, histname=None, histtitle=None):
		"""
		Reads a histogram from a non-ROOT file. fmt specifies the format.
		The following formats are recognized:
		  * cracow  (Cracow from GSI)
		  * mfile   (use libmfile and attempt autodetection)
		  * any format specifier understood by libmfile
		"""
		if not fmt:
			fmt = self.fDefaultFormat
		if histname == None:
			histname = os.path.basename(fname)
		if histtitle == None:
			histtitle = os.path.basename(fname)
	
		if fmt.lower() == 'cracow':
			hdtv.dlmgr.LoadLibrary("cracowio")
			cio = ROOT.CracowIO()
			hist = cio.GetCracowSpectrum(fname, histname, histtitle)
			if not hist:
				raise SpecReaderError, cio.GetErrorMsg()
			return hist
		elif fmt.lower() == 'xy':
			txtio = TextSpecReader()
			# The following line may raise a SpecReaderError exception
			return txtio.GetSpectrum(fname, histname, histtitle)
		else:
			hdtv.dlmgr.LoadLibrary("mfile-root")
			mhist = ROOT.MFileHist()

			if not fmt or fmt.lower() == 'mfile':
				result = mhist.Open(fname)
			else:
				result = mhist.Open(fname, fmt)
			
			if result != ROOT.MFileHist.ERR_SUCCESS:
				raise SpecReaderError, mhist.GetErrorMsg()
			hist = mhist.ToTH1D(histname, histtitle, 0, 0)
			if not hist:
				raise SpecReaderError, mhist.GetErrorMsg()
			return hist
		
	def GetMatrix(self, filename, fmt, histname, histtitle):
		hdtv.dlmgr.LoadLibrary("mfile-root")
		mhist = ROOT.MFileHist()
		mhist.Open(filename)
		return mhist.ToTH2D(histname, histtitle, 0)
		
	def WriteSpectrum(self, hist, fname, fmt):
		hdtv.dlmgr.LoadLibrary("mfile-root")
		result = ROOT.MFileHist.WriteTH1(hist, fname, fmt)
		if result != ROOT.MFileHist.ERR_SUCCESS:
			raise SpecReaderError, ROOT.MFileHist.GetErrorMsg(result)
