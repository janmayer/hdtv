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

def SearchEnergies(nuclide): 
	"""
	Opens table of nuclides with peakenergies, gives back the peakenergies of the nuclide 
	"""
	tableOfEnergiesFile = open("../hdtv/database/PeakEnergies.json") #opens jason File with a list of nuclieds and their energies
	tableOfEnergiesStr = tableOfEnergiesFile.read() #Sting oft the json file
	Energies = [] #the energies of the right nuclid will be saved in this list

	#compares the name of every nuclid with the given one and saves the energies in the list
	for tableOfEnergiesData in json.loads(tableOfEnergiesStr): 
		if tableOfEnergiesData['name'] == nuclide:
			Energies = [test['energy'] for test in tableOfEnergiesData['transitions']]
			return Energies
			break
	
	#error message if nuclid is not in the table
	if Energies == []:
		errorText = "There is no nuclide called "+nuclide+" in the table."
		raise hdtv.cmdline.HDTVCommandError(errorText)

def MatchPeaksAndEnergies(Peaks, Energies, sigma): 
	"""
	Combines Peaks wirth the right Energies from the table (with searchEnergie). 
	"""
	gradient = [] #list of all gradients Energy/PeakPosition
	pair = [] #list of all posibble pairs Energy, Peak
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

	#compare all gradients with each other to find the most fequently one (within sigma)
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
					print a, pair[i]
					hdtv.ui.warn("Some peaks/energies are used more than one time.")
			accordance.append(pair[i])

	#warning when ohnly few pairs are found
	if len(accordance)<4:
		print accordance
		hdtv.ui.warn("Only a few (peak,energy) pairs are found.")

	return(accordance)