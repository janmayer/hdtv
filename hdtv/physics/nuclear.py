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


# nuclear physics functions

def weizsaecker(A, Z):
    '''
    Calculate the Energy in MeV off a given atom using the Weizsaecker equation
    '''
    if A % 2 == 1 and Z % 2 == 1:
        sign = 1
    elif A % 2 == 0 and Z % 2 == 0:
        sign = -1
    else:
        sign = 0
 
    return ((A - Z) * 939.5445995 +
            Z * 938.762158 +
            Z * 0.510998910 - 15.85 * A +
            18.34 * A**(2.0 / 3.0) +
            92.86 / A * (A * 0.5 - Z)**2 +
            0.75 * Z**2 / A**(1.0 / 3.0) +
            sign * 35 * A**(-3.0 / 4.0))
