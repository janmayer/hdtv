"""IAEA database, International Atomic Energy Agency"""

import json
import os

from uncertainties import ufloat

import hdtv.ui
import hdtv.util

# from hdtv.database.common import *

# TODO: integrate this in a class?


def SearchNuclide(nuclide):
    # Get all data as dict from json file
    alldata = json.loads(open(os.path.join(hdtv.datadir, "IAEA.json")).read())

    # Select nuclide
    data = next(x for x in alldata if x["nuclide"] == nuclide)
    if not data:
        errorText = "There is no nuclide called " + nuclide + " in the table."
        raise hdtv.cmdline.HDTVCommandError(errorText)

    # Use ufloat to represent values with uncertainties
    transitions = [
        {
            "energy": ufloat(t["energy"], t["energy_uncertainty"]),
            "intensity": ufloat(t["intensity"], t["intensity_uncertainty"]),
        }
        for t in data["transitions"]
    ]
    data["transitions"] = transitions
    data["halflife"] = ufloat(data["halflife"], data["halflife_uncertainty"])
    del data["halflife_uncertainty"]

    return data
