#!/usr/bin/env python3


from hdtv.ui import *
import hdtv.database

db = hdtv.database.PGAALibraries.PGAAlib_IKI2000()

output = db.find(energy=511, sort_key="k0", fuzziness=2)

table = Table(
    output,
    header=["ID", "Energy / (keV)", "Intensity / (%)", "Sigma / (b)"],
    attrs=["id", "energy", "intensity", "sigma"],
    sortBy="intensity",
    reverseSort=True,
)

table.out()


table2 = Table(output, attrs=["id", "energy", "intensity", "sigma"])
print(table2)
