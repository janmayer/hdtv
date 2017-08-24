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
# Function for energy calibration
# 
#-------------------------------------------------------------------------------

import json
import hdtv.util
from hdtv.database import IAEALibraries
from hdtv.database import DDEPLibraries


def SearchNuclide(nuclide, database): 
	"""
	Searches for information about the nuclide in different databases.
	"""
	if database == "IAEA":
		Data = IAEALibraries.SearchNuclide(nuclide)
	elif database == "DDEP":
		Data = DDEPLibraries.SearchNuclide(nuclide)
	else:
		try:
			Data = IAEALibraries.SearchNuclide(nuclide)
		except:
			Data = DDEPLibraries.SearchNuclide(nuclide)

	return Data

def TabelOfNuclide(nuclide, Energies, EnergiesError, Intensities, IntensitiesError, Halflive, HalfliveError, source):
	"""
	Creates a table of the given data.
	"""
	tabledata = list() 
	Data = [[],[]]
	data = hdtv.errvalue.ErrValue(Halflive)
	data.SetError(HalfliveError)

	for j in range(0,len(Energies)):
		Data[0].append(hdtv.errvalue.ErrValue(Energies[j]))
		Data[0][j].SetError(EnergiesError[j])
		Data[1].append(hdtv.errvalue.ErrValue(Intensities[j]))
		Data[1][j].SetError(IntensitiesError[j])

        #for table option values are saved
		tableline = dict()
		tableline["Energy"] = Data[0][j]
		tableline["Intensity"] = Data[1][j]
		tabledata.append(tableline)

	result_header = "Data of the nuclide " + str(nuclide) + " of the data source " + str(source) + "." + "\n" + "Halflife: " +str(data)
	print() 
	table = hdtv.util.Table(data=tabledata, keys=["Energy", "Intensity"],extra_header = result_header, sortBy=None, ignoreEmptyCols=False)
	hdtv.ui.msg(str(table))        

def MatchPeaksAndEnergies(Peaks, Energies, sigma): 
	"""
	Combines Peaks with the right Energies from the table (with searchEnergie). 
	"""
	gradient = [] #list of all gradients Energy/PeakPosition
	pair = [] #list of all possible pairs Energy, Peak
	accordanceCount = [] 

	#error message if there are no given peaks
	if Peaks == []:
		raise hdtv.cmdline.HDTVCommandError("You must fit at least one peak.")

	#saves all pairs and gradients in lists
	for i in range(0,len(Peaks)):
		for j in range(0,len(Energies)):
			gradient.append(1.0*Energies[j]/Peaks[i]) 
			pair.append([Peaks[i],Energies[j]])
			accordanceCount.append(0)

	NumberHighestAccordance = 0 
	bestAccordance = 0 #gradient with best accordance to the others

	#compare all gradients with each other to find the most frequently one (within sigma)
	for i in range(0,len(gradient)): 
		for j in range(0,len(gradient)): 
			if gradient[j]>gradient[i]-sigma and gradient[j]<gradient[i]+sigma:
				accordanceCount[i] = accordanceCount[i] + 1 
				if accordanceCount[i] > NumberHighestAccordance:
					NumberHighestAccordance = accordanceCount[i]
					bestAccordance = gradient[i]

	accordance = [] #all pairs with the right gradient will be saved in this list

	for i in range(0,len(gradient)):
		if gradient[i]>bestAccordance-sigma and gradient[i]<bestAccordance+sigma:
			for a in accordance:
				if a[0] == pair[i][0] or a[1] == pair[i][1]: #Warning
					print(a, pair[i])
					hdtv.ui.warn("Some peaks/energies are used more than one time.")
			accordance.append(pair[i])

	#warning when only few pairs are found
	if len(accordance)<4:
		print(accordance)
		hdtv.ui.warn("Only a few (peak,energy) pairs are found.")

	return(accordance)

def MatchPeaksAndIntensities(Peaks, peakID, Energies, Intensities, IntensitiesError, sigma=0.5): #Peak is the Energy of the fitted Peak, Vol its volume 
#and Intensity and Energy the data from the chart
	"""
	Combines peaks with the right intensities from the table (with searchEnergie). 
	"""
	Match = [[],[],[]]

	count = 0
	for i in range(0,len(Energies)):
		for j in range(0,len(Peaks)):
			if abs(Energies[i]-Peaks[j]) <= sigma:
				Match[0].append(Peaks[j])
				Match[1].append(hdtv.errvalue.ErrValue(Intensities[i]))
				Match[1][count].SetError(IntensitiesError[i])
				Match[2].append(peakID[j])
				count = count + 1

	return Match