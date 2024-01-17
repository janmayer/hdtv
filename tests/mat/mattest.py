#!/usr/bin/env python3

import os
import struct

f = open("mat.mtx", "wb")

for y in range(1024):
    for x in range(1024):
        z = 1
        if x >= 200 and y >= 200:
            z = 2

        f.write(struct.pack("l", z))

f.close()

os.system("/ikp/bin/matconv -I 1k.1k.le4 -D mat.mtx")
os.system("/ikp/bin/matproj mat.mtx")
