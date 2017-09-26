# -*- coding: utf-8 -*-
# IAEA database, International Atomic Energy Agency

import json
import hdtv.util
import urllib.request
import urllib.parse
import urllib.error
import hdtv.ui
from hdtv.database.common import *

# TODO: integrate this in a class?


def SearchNuclide(nuclide):
    """
    Opens table of nuclides with peak energies, gives back the peak energies of the nuclide and its intensities.
    """
    # opens json File with a list of nuclieds and their energies
    tableOfEnergiesFile = open(os.path.join(hdtv.datadir, "IAEA.json"))
    tableOfEnergiesStr = tableOfEnergiesFile.read()  # Sting oft the json file
    Energies = []  # the energies of the right nuclide will be saved in this list
    EnergiesError = []
    Intensities = []
    IntensitiesError = []
    Halflive = 0
    HalfliveError = 0
    source = "IAEA"

    # compares the name of every nuclide with the given one and saves the
    # energies in the list
    for tableOfEnergiesData in json.loads(tableOfEnergiesStr):
        if tableOfEnergiesData['nuclide'] == nuclide:
            Halflive = float(tableOfEnergiesData['halflife'])
            HalfliveError = float(tableOfEnergiesData['halflife_uncertainty'])
            Energies = [float(data['energy'])
                        for data in tableOfEnergiesData['transitions']]
            EnergiesError = [float(data['energy_uncertainty'])
                             for data in tableOfEnergiesData['transitions']]
            Intensities = [float(data['intensity'])
                           for data in tableOfEnergiesData['transitions']]
            IntensitiesError = [float(data['intensity_uncertainty'])
                                for data in tableOfEnergiesData['transitions']]
            return Energies, EnergiesError, Intensities, IntensitiesError, Halflive, HalfliveError, source
            break

    # error message if nuclide is not in the table
    if Energies == []:
        errorText = "There is no nuclide called " + nuclide + " in the table."
        raise hdtv.cmdline.HDTVCommandError(errorText)
