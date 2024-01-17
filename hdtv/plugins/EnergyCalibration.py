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

"""
Function for energy calibration
"""


import hdtv.ui
import hdtv.util
from hdtv.database import DDEPLibraries, IAEALibraries


def SearchNuclide(nuclide, database):
    """
    Searches for information about the nuclide in different databases.
    """
    if database == "IAEA":
        data = IAEALibraries.SearchNuclide(nuclide)
    elif database == "DDEP":
        data = DDEPLibraries.SearchNuclide(nuclide)
    else:
        try:
            data = IAEALibraries.SearchNuclide(nuclide)
        except BaseException:
            data = DDEPLibraries.SearchNuclide(nuclide)
    return data


def TableOfNuclide(data):
    """
    Creates a table of the given data.
    """
    result_header = " ".join(
        [
            "\n",
            "Nuclide:",
            data["nuclide"],
            "\n",
            "Halflife:",
            str(data["halflife"]),
            "\n",
            "Reference:",
            data["reference"],
            "\n",
        ]
    )

    table = hdtv.util.Table(
        data=data["transitions"],
        keys=["energy", "intensity"],
        extra_header=result_header,
        sortBy=None,
        ignoreEmptyCols=False,
    )

    hdtv.ui.msg(html=str(table))


def MatchPeaksAndEnergies(peaks, energies, sigma):
    """
    Combines Peaks with the right energies from the table (with searchEnergie).
    """
    gradient = []  # list of all gradients energy/PeakPosition
    pair = []  # list of all possible pairs energy, Peak
    accordanceCount = []

    # error message if there are no given peaks
    if peaks == []:
        raise hdtv.cmdline.HDTVCommandError("You must fit at least one peak.")

    # saves all pairs and gradients in lists
    for peak in peaks:
        for energy in energies:
            gradient.append(1.0 * energy / peak)
            pair.append([peak, energy])
            accordanceCount.append(0)

    NumberHighestAccordance = 0
    bestAccordance = 0  # gradient with best accordance to the others

    # compare all gradients with each other to find the most frequently one
    # (within sigma)
    for i in range(len(gradient)):
        for j in range(len(gradient)):
            if gradient[j] > gradient[i] - sigma and gradient[j] < gradient[i] + sigma:
                accordanceCount[i] = accordanceCount[i] + 1
                if accordanceCount[i] > NumberHighestAccordance:
                    NumberHighestAccordance = accordanceCount[i]
                    bestAccordance = gradient[i]

    accordance = []  # all pairs with the right gradient will be saved in this list

    for i in range(len(gradient)):
        if (
            gradient[i] > bestAccordance - sigma
            and gradient[i] < bestAccordance + sigma
        ):
            for a in accordance:
                if a[0] == pair[i][0] or a[1] == pair[i][1]:
                    hdtv.ui.msg(f"{a} {pair[i]}")
                    hdtv.ui.warning("Some peaks/energies are used more than one time.")
            accordance.append(pair[i])

    if len(accordance) < 4:
        # hdtv.ui.msg(accordance)
        hdtv.ui.warning("Only few (peak,energy) pairs found. Try with a larger --sigma")

    return accordance


def MatchFitsAndTransitions(fits, transitions, sigma=0.5):
    """
    Combines peaks with the right intensities.
    """
    return [
        {"fit": fit, "transition": transition}
        for fit in fits
        for transition in transitions
        if abs(transition["energy"] - fit.ExtractParams()[0][0]["pos"]) <= sigma
    ]
