# -*- coding: utf-8 -*-
# DDEP database, Decay Data Evaluation Project

import json
import hdtv.util
import urllib.request, urllib.error
import hdtv.ui
from hdtv.database.common import *


def SearchNuclide(nuclide):
    """
    Opens table of nuclides with peak energies, gives back the peak energies of the nuclide and its intensities.
    """
    Energies = [] #the energies of the right nuclide will be saved in this list
    EnergiesError = []
    Intensities = []
    IntensitiesError = []
    Halflive = 0
    HalfliveError = 0
    source = "DDEP"

    if nuclide == "Ra-226":
        nuclide = "Ra-226D"

    try:
        with urllib.request.urlopen("http://www.nucleide.org/DDEP_WG/Nuclides/"+str(nuclide)+".lara.txt") as resource:
            data = resource.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        hdtv.ui.error("Error looking up nuclide: {}".format(e.msg))
        return

    for line in data.split("\r\n"):
        sep = line.split(" ; ")

        if str(sep[0]) == "Half-life (s)":
            Halflive = float(sep[1])
            HalfliveError = float(sep[2])

        if str(sep[0]) == "Reference":
            source = str(sep[1])
            source = source.replace(source[-1],"")
            source = source.replace(source[-1],"")

        try:
            if str(sep[4]) == "g":
                Energies.append(float(sep[0]))
                try:
                    EnergiesError.append(float(sep[1]))
                except:
                    EnergiesError.append(0)
                Intensities.append(float(sep[2])/100)#because it is given in %
                try:
                    IntensitiesError.append(float(sep[3])/100)#because it is given in %
                except:
                    IntensitiesError.append(0)
        except:
            pass

    return Energies, EnergiesError, Intensities, IntensitiesError, Halflive, HalfliveError, source
