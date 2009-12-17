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

# ------------------------------------------------------------------------------
# Classes implementing the well-known error propagation with
# first-order-truncated Taylor series.
# ------------------------------------------------------------------------------

# Each instance of ErrValue is a user-supplied value and error. By default, the
# different instances are considered to be statistically independant, but the
# user can specify covariances between them (via ErrValue.SetCov()).
#
# An arithmetic operation on one or two ErrValues produces a DepErrValue
# instance. DepErrValue instances keep track of the ErrValues they are dependant
# on. For each dependance, a weighting factor, equal to the partial derivative
# of the DepErrValue instance with respect to the ErrValue instance, is stored.
# Arithmetic operations on DepErrValue instances yield DepErrValue instances as
# well. Even then, however, dependencies are stored in terms of ErrValue
# instances, with the weighting factors suitably propagated. This prevents
# large tree structures in memory.
#
# When requested, the error of each DepErrValue instance can be calculated to
# first order, with covariances taken into account. A slight subtlety is that
# the error of the DepErrValue instance is only calculated on request, whereas
# its value is calculated immediately. This means that the user can specify
# errors and covariances of the ErrValues *after* using them in calculations
# (whereas the values have to be specified beforehand). For example, the
# following code fragment will correctly add (1 ± .1) and (2 ± .1):
#
#    a = ErrValue(1)
#    b = ErrValue(2)
#    c = a + b
#    a.SetError(.1)
#    b.SetError(.1)
#    print c.value, c.error  ## Prints 3, 0.141421...
#
# Note, however, that ErrValues can become inaccesible (e.g. by using b += a in
# the above code), so it is recommended to set the error immediately after
# creation of the ErrValue instance.
#
# For technical reasons, equality between ErrValue instances refers to equality
# as instances (in the sense of id(a) == id(b)), not to equality of value and
# error. For example, if a = ErrValue(1, .1) and b = ErrValue(1, .1), a == a,
# but a != b. This makes sense insofar as (a + b) gives a result different from
# (a + a) (because a and b are considered to be statistically independant).
# (Note that you generally cannot use == to test for statistical independance.)

# NOTES ON THE IMPLEMENTATION:
# 1. In pratice, ErrValue inherits from DepErrValue, and is dependant on self
# with a weighting factor of 1.
#
# 2. DepErrValue should not have a __float__ method. It might seem tempting to
# have DepErrValue.__float__ return the value. Then, however, code like
#    c = a * math.sin(a) ,
# with a an ErrValue instance, will silently give wrong results, rather than
# (visibly) throwing an exception.
# (At the moment, DepErrValue does have a __float__ method, which prints a
# warning message and returns the value. It is deprecated and should be removed
# in the future.)
#
# 3. The implementation is optimized such that successive additions, along the
# lines of
#
#    s = 0
#    for v in values:
#        s += ErrValue(v, math.sqrt(v))
#
# take linear time. Replacing the += with e.g. *= will however cause the loop to
# take quadratic time. (Also note that, after the loop has finished, s will keep
# a lot of ErrValue instances alive, so s should be disposed of as soon as
# possible.)

from __future__ import division
import math
import sys
import re
import copy
import traceback
import hdtv.ui

class DepErrValue:
    def __init__(self, value, depends):
        self._value = value
        # NOTE: both self._depends and self._lazy_union should be considered
        # references to shared dictionaries. They may only be modified after
        # verifying that they are only used by the instance in question.
        self._depends = depends
        self._lazy_union = None
    
    
    @property
    def depends(self):
        # Returns a dictionary with the ErrValue instances this value is
        # dependant on, and the respective weighting factors.
        
        # NOTE: The call to sys.getrefcount creates a temporary reference
        # to an object, so the return value is higher by one than what one
        # might expect.
        if self._lazy_union:
            if sys.getrefcount(self._lazy_union) == 2 and \
              len(self._lazy_union) > len(self._depends):
                for (x, dfdx) in self._depends.iteritems():
                    self._lazy_union[x] = self._lazy_union.get(x, 0) + dfdx
                self._depends = self._lazy_union
                self._lazy_union = None
            elif sys.getrefcount(self._depends) == 2:
                for (x, dfdx) in self._lazy_union.iteritems():
                    self._depends[x] = self._depends.get(x, 0) + dfdx
                self._lazy_union = None
            else:
                depends = dict(self._depends)
                for (x, dfdx) in self._lazy_union.iteritems():
                    depends[x] = depends.get(x, 0) + dfdx
                self._depends = depends
                self._lazy_union = None
        
        return self._depends
    
    
    @property
    def value(self):
        # the value of this variable
        return self._value
    
    
    @property
    def var(self):
        # the variance of this variable
        return self.cov(self)
    
    
    def cov(self, y):
        """
        Returns the covariance between self and y.
        """
        # The covariance is calculated as
        # cov(f, g) = \sum_i \sum_j \frac{\partial f}{\partial x_i}
        #   \frac{\partial g}{\partial x_j} cov(x_i, x_j)
        cov = 0
        
        for (xi, dfdxi) in self.depends.iteritems():
            tmp = 0
            for(xj, cij) in xi._cov.iteritems():
                tmp += y.depends.get(xj, 0) * cij
            cov += dfdxi * tmp
        
        return cov
    
    
    @property
    def error(self):
        # the error of this variable
        return math.sqrt(self.var)
    
    
    @property
    def rel_error(self):
        # the relative error (error / value) of this variable
        try:
            return self.error / self.value
        except ZeroDivisionError:
            return None
    
    
    @property
    def rel_error_percent(self):
        # the relative error (error / value) of this variable, in percent
        try:
            return self.error / self.value * 100
        except ZeroDivisionError:
            return None
    
    
    def equal(self, y, f=1):
        """
        Checks if self and y are equal within errors, i.e. if
         abs((self - y).value) <= f * (self - y).error
        The optional parameter f can be used to set the desired confidence.
        
        Note that this is not a true equality, because it lacks transitivity
        (that is, if may be that equal(a,b) == True and equal(b,c) == True,
        but equal(a,c) == False).
        """
        return (abs((self - y).value) <= f * (self - y).error)
    
    
    def __float__(self):
        tb = traceback.extract_stack()[-2]
        hdtv.ui.warn("__float__() called on an ErrValue instance.\n"
                     "    This may mask a serious programming error!\n"
                     "    (Use x.value to avoid this warning.)\n"
                   + "    (called from file \"%s\", line %d, in %s)" % (tb[0], tb[1], tb[2]))

        return self.value
    
    
    def __hash__(self):
        return id(self)
    
    
    def __eq__(self, y):
        return id(self) == id(y)
    
    
    def __cmp__(self, y):
        tb = traceback.extract_stack()[-2]
        hdtv.ui.warn("__cmp__() called on an ErrValue instance.\n"
                     "    This function is deprecated and should not be used!\n"
                     "    (Use cmp(x.value, y.value) instead to avoid this warning.)\n"
                   + "    (called from file \"%s\", line %d, in %s)" % (tb[0], tb[1], tb[2]))
        
        try:
            return cmp(self.value, y.value)
        except AttributeError:
            return cmp(self.value, float(y))
    
    
    def __str__(self):
        return self.fmt()
    
    
    def __abs__(self):
        if self.value < 0:
            return (-1) * self
        else:
            return self
    
    
    def __pos__(self):
        return self
    
    
    def __neg__(self):
        return (-1) * self
    
    
    def __add__(self, other):
        if isinstance(other, DepErrValue):
            rv = DepErrValue(self.value + other.value, self.depends)
            rv._lazy_union = other.depends
            return rv
        else:
            return DepErrValue(self.value + other, self.depends)
            
    
    def __radd__(self, other):
        return self.__add__(other)
    
    
    def __sub__(self, other):
        return self + (-1) * other
    
    
    def __rsub__(self, other):
        return other + (-1) * self
    
    
    def __mul__(self, other):
        if isinstance(other, DepErrValue):
            depends = dict()
            for (x, dfdx) in self.depends.iteritems():
                depends[x] = dfdx * other.value
            for (x, dgdx) in other.depends.iteritems():
                depends[x] = depends.get(x, 0) + self.value * dgdx
            return DepErrValue(self.value * other.value, depends)
        else:
            depends = dict()
            for (x, dfdx) in self.depends.iteritems():
                depends[x] = dfdx * other
            return DepErrValue(self.value * other, depends)
    
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    
    def _div(self, f, g):
        depends = dict()
        for (x, dfdx) in f.depends.iteritems():
            depends[x] = dfdx / g.value
        for (x, dgdx) in g.depends.iteritems():
            depends[x] = depends.get(x, 0) - dgdx * f.value / (g.value**2)
        return DepErrValue(f.value / g.value, depends)
    
    
    def __truediv__(self, other):
        if isinstance(other, DepErrValue):
            return self._div(self, other)
        else:
            depends = dict()
            for (x, dfdx) in self.depends.iteritems():
                depends[x] = dfdx / other
            return DepErrValue(self.value / other, depends)
    
    
    def __rtruediv__(self, other):
        if isinstance(other, DepErrValue):
            return self._div(other, self)
        else:
            depends = dict()
            for (x, dgdx) in self.depends.iteritems():
                depends[x] = -dgdx * other / (self.value**2)
            return DepErrValue(other / self.value, depends)
    
    
    # We always use new-style (true) division (in the sense of PEP 238)
    def __div__(self, other):
        return self.__truediv__(other)
    
    
    def __rdiv__(self, other):
        return self.__rtruediv__(other)
    
    
    def _pow(self, f, g):
        fpowg = f.value ** g.value
        depends = dict()
        for (x, dfdx) in f.depends.iteritems():
            depends[x] = fpowg * g.value / f.value * dfdx
        for (x, dgdx) in g.depends.iteritems():
            depends[x] = depends.get(x, 0) + fpowg * math.log(f.value) * dgdx
        return DepErrValue(fpowg, depends)
    
    
    def __pow__(self, other):
        if isinstance(other, DepErrValue):
            return self._pow(self, other)
        else:
            fpowg = self.value ** other
            depends = dict()
            for (x, dfdx) in self.depends.iteritems():
                depends[x] = fpowg * other / self.value * dfdx
            return DepErrValue(fpowg, depends)
    
    
    def __rpow__(self, other):
        if isinstance(other, DepErrValue):
            return self._pow(other, self)
        else:
            fpowg = other ** self.value
            depends = dict()
            for (x, dgdx) in self.depends.iteritems():
                depends[x] = fpowg * math.log(other) * dgdx
            return DepErrValue(fpowg, depends)
    
    
    ### Functions for string output ###
    def fmt(self):
        """
        Return a string in the form "3.1415(92)e-6" giving this value and its
        error
        """
        # Call fmt_no_error() for values without error
        if self.error == 0:
            return self.fmt_no_error()
        
        # Check and store sign
        if self.value < 0:
            sgn = "-"
            value = -self.value
        else:
            sgn = ""
            value = self.value
            
        error = self.error
        
        # Check whether to switch to scientific notation
        # Catch the case where value is zero
        try:
            log10_val = math.floor(math.log(value) / math.log(10.))
        except (ValueError, OverflowError):
            log10_val = 0.
        
        if log10_val >= 6 or log10_val <= -2:
            # Use scientific notation
            suffix = "e%d" % int(log10_val)
            exp = 10 ** log10_val
            value /= exp
            error /= exp
        else:
            # Use normal notation
            suffix = ""
        
        # Find precision (number of digits after decimal point) needed such that the
        # error is given to at least two decimal places
        if error >= 10.:
            prec = 0
        else:
            # Catch the case where error is zero
            try:
                prec = -math.floor(math.log(error) / math.log(10.)) + 1
            except (ValueError, OverflowError):
                prec = 6
        
        # Limit precision to sensible values, and capture NaN
        #  (Note that NaN is by definition unequal to itself)
        if prec > 20:
            prec = 20
        elif prec != prec:
            prec = 3
        
        return "%s%.*f(%.0f)%s" % (sgn, int(prec), value, error * 10 ** prec, suffix)
    
    
    def fmt_full(self):
        """
        Print ErrValue with absolute and relative error
        """
        string = str(self.fmt()) + " [" + "%.*f" % (2, self.rel_error_percent) + "%]"
        return string
    
    
    def fmt_no_error(self, prec = 6):
        # Check and store sign
        if self.value < 0:
            sgn = "-"
            value = -self.value
        else:
            sgn = ""
            value = self.value
        
        # Check whether to switch to scientific notation
        # Catch the case where value is zero
        try:
            log10_val = math.floor(math.log(value) / math.log(10.))
        except (ValueError, OverflowError):
            log10_val = 0.
        
        if log10_val >= 6 or log10_val <= -2:
            # Use scientific notation
            suffix = "e%d" % int(log10_val)
            value /= 10 ** log10_val
        else:
            # Use normal notation
            suffix = ""
        
        return "%s%.*f%s" % (sgn, prec, value, suffix)
    
    ###

def _chain(f, dfdg, g):
    depends = dict()
    for (x, dgdx) in g.depends.iteritems():
        depends[x] = dfdg * dgdx
    return DepErrValue(f, depends)


def sqrt(x):
    if isinstance(x, DepErrValue):
        return _chain(math.sqrt(x.value), 1/(2*math.sqrt(x.value)), x)
    else:
        return math.sqrt(x)


def exp(x):
    if isinstance(x, DepErrValue):
        return _chain(math.exp(x.value), math.exp(x.value), x)
    else:
        return math.exp(x)


def log(x):
    if isinstance(x, DepErrValue):
        return _chain(math.log(x.value), 1/x.value, x)
    else:
        return math.log(x)


def sin(x):
    if isinstance(x, DepErrValue):
        return _chain(math.sin(x.value), math.cos(x.value), x)
    else:
        return math.sin(x)


def cos(x):
    if isinstance(x, DepErrValue):
        return _chain(math.cos(x.value), -math.sin(x.value), x)
    else:
        return math.cos(x)


def tan(x):
    if isinstance(x, DepErrValue):
        return _chain(math.tan(x.value), 1/(math.cos(x.value)**2), x)
    else:
        return math.tan(x)


def asin(x):
    if isinstance(x, DepErrValue):
        return _chain(math.asin(x.value), 1/math.sqrt(1-x.value**2), x)
    else:
        return math.asin(x)


def acos(x):
    if isinstance(x, DepErrValue):
        return _chain(math.acos(x.value), -1/math.sqrt(1-x.value**2), x)
    else:
        return math.acos(x)


def atan(x):
    if isinstance(x, DepErrValue):
        return _chain(math.atan(x.value), 1/(1+x.value**2), x)
    else:
        return math.atan(x)


def sinh(x):
    if isinstance(x, DepErrValue):
        return _chain(math.sinh(x.value), math.cosh(x.value), x)
    else:
        return math.sinh(x)


def cosh(x):
    if isinstance(x, DepErrValue):
        return _chain(math.cosh(x.value), math.sinh(x.value), x)
    else:
        return math.cosh(x)


def tanh(x):
    if isinstance(x, DepErrValue):
        return _chain(math.tanh(x.value), 1/(math.cosh(x.value)**2), x)
    else:
        return math.tanh(x)


class ErrValue(DepErrValue):
    def __init__(self, value, error = None):
        if isinstance(value, str):
            (value, error) = self._fromString(value)
        
        self._has_error = True
        if error == None:
            error = 0.
            self._has_error = False
        
        self._cov = { self: error**2 }
        DepErrValue.__init__(self, value, { self: 1 })
    
    
    @property
    def has_error(self):
        # Flag to indicate whether an error was specified for this ErrValue.
        # Note that in all calculations, no error is treated as error = 0., and 
        # this flag is not passed on.
        return self._has_error
    
    
    def SetError(self, error):
        """
        Sets the error of this variable.
        """
        self.SetVar(error**2)
    
    
    def SetVar(self, var):
        """
        Sets the variance (error squared) of this variable.
        """
        self._cov[self] = var
    
    
    def SetCov(self, y, cov):
        """
        Set covariance of self and y to cov.
        Note: this sets both cov(self, y) and cov(y, self), so also calling
        y.SetCov() is redundant.
        """
        if not isinstance(y, ErrValue):
            raise TypeError, "Can only set covariances between two ErrValue objects"
            
        if y == self:
            self.SetVar(cov)
        else:
            # One could consider to store only one of cov(self, y) and
            # cov(y, self), but that would make the covariance calculation
            # code above more complicated.
            self._cov[y] = cov
            y._cov[self] = cov
    
    
    ### Functions for string input ###
    @classmethod
    def _fromString(self, strvalue):
        """
        Convert values with error given as strings (e.g. "0.1234(56)") to
        a tuple (value, error). If no error was specified ("1.23"), error is
        returned as None.
        """
        
        if not strvalue:
            raise ValueError, "empty string for ErrValue()"
        
        # TODO: Handle decimal seperator properly, depending on locale
        expr_value = r"([+\-]?[0-9]*\.?(?:[0-9]*))"
        expr_error = r"\(\s*([0-9]+)\s*\)"
        expr_exp   = r"[eE]([+\-]?[0-9]+)"
        
        expr = "^\s*" + expr_value + "\s*(" + expr_error + ")?\s*(" + expr_exp + ")?\s*$"
        
        match = re.match(expr, strvalue)
        if match == None:
            raise ValueError, "invalid literal for ErrValue(): %s" % strvalue
        
        # Extract value
        value = float(match.group(1))
        
        # Extract error
        if match.group(2) != None:
            error = int(match.group(3))
            dec_split = match.group(1).split(".")
            if len(dec_split) > 1:
                error *= pow(0.1, len(dec_split[1]))
        else:
            error = None
        
        # Extract exponent
        if match.group(4) != None:
            exp = int(match.group(5))
            value *= pow(10, exp)
            if error is not None:
                error *= pow(10, exp)
        
        return (value, error)

