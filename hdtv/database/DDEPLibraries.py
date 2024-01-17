"""DDEP database, Decay Data Evaluation Project"""

import hdtv.util

try:
    import urllib.error
    import urllib.request
except ImportError:
    import urllib
from uncertainties import ufloat

import hdtv.ui

# from hdtv.database.common import *


def SearchNuclide(nuclide):
    """
    Opens table of nuclides with peak energies, gives back the peak energies of the nuclide and its intensities.
    """

    out = {"nuclide": nuclide, "transitions": []}

    if nuclide == "Ra-226":
        nuclide = "Ra-226D"

    try:
        with urllib.request.urlopen(
            "http://www.nucleide.org/DDEP_WG/Nuclides/" + str(nuclide) + ".lara.txt"
        ) as resource:
            data = resource.read().decode("utf-8")
    except Exception:
        raise hdtv.cmdline.HDTVCommandError(f"Error looking up nuclide {nuclide}")

    for line in data.split("\r\n"):
        sep = line.split(" ; ")

        if str(sep[0]) == "Half-life (s)":
            out["halflife"] = ufloat(float(sep[1]), float(sep[2]))

        if str(sep[0]) == "Reference":
            out["reference"] = str(sep[1])

        try:
            if str(sep[4]) == "g":
                energy = ufloat(float(sep[0]), 0)
                try:
                    energy.std_dev = float(sep[1])
                except Exception:
                    pass

                intensity = ufloat(float(sep[2]) / 100, 0)
                try:
                    intensity.std_dev = float(sep[3]) / 100
                except Exception:
                    pass

                out["transitions"].append({"energy": energy, "intensity": intensity})
        except Exception:
            pass

    return out
