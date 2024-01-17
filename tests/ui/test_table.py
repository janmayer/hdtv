#!/usr/bin/env python3


import hdtv.database
from hdtv.ui import Table

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
