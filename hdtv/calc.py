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

import math


def Median(values):
    """
    Calculate Median of a list
    """
    values.sort()
    n = len(values)
    if not n:
        return None

    if n % 2 == 0:
        return (values[(n - 1) / 2] + values[n / 2]) * 0.5
    return values[n / 2]


def stdDeviation(values):
    ssum = .0
    for val in values:
        ssum += (val.value - wMean(values))**2
    return math.sqrt(1. / len(values) * ssum)


def wMean(values):
    """
    Calculates weighted mean of a list of ufloats
    """
    wsum = .0
    weights = .0
    for val in values:
        weights += 1 / (val.std_dev / val.nominal_value)
        wsum += (val.value * 1. / (val.std_dev / val.nominal_value))
    return wsum / weights


def gcd(a, b):
    """
    Calculate greatest common denomiator of two integers
    """
    while b != 0:
        (a, b) = (b, a % b)
    return a


class Linear:
    """
    A linear relationship, i.e. y = p1 * x + p0
    """

    def __init__(self, p0=0., p1=0.):
        self.p0 = p0
        self.p1 = p1

    def Y(self, x):
        """
        Get y corresponding to a certain x
        """
        return self.p1 * x + self.p0

    def X(self, y):
        """
        Get x corresponding to a certain y
        May raise a ZeroDivisionError
        """
        return (y - self.p0) / self.p1

    @classmethod
    def FromXYPairs(cls, a, b):
        """
        Construct a linear relationship from two (x,y) pairs
        """
        l = cls()
        l.p1 = (b[1] - a[1]) / (b[0] - a[0])
        l.p0 = a[1] - l.p1 * a[0]
        return l

    @classmethod
    def FromPointAndSlope(cls, point, p1):
        """
        Construct a linear relationship from a slope and a point ( (x,y) pair )
        """
        l = cls()
        l.p1 = p1
        l.p0 = point[1] - l.p1 * point[0]
        return l
