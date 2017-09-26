#!/usr/bin/python
# -*- coding: utf-8 -*-

# Unit tests for the ErrValue class

from __future__ import print_function, division

import hdtv.errvalue
from hdtv.errvalue import ErrValue, sqrt, exp, log, sin, cos, tan, asin, acos, atan, sinh, cosh, tanh
import math
import time
import traceback

tests_passed = 0
tests_failed = 0


def _Assert(cond):
    global tests_passed, tests_failed

    if not cond:
        tb = traceback.extract_stack()[-3]
        print("FAIL: assertion %s" % tb[3])
        print("      in file \"%s\", line %d, in %s" % (tb[0], tb[1], tb[2]))
        tests_failed += 1
        return False

    tests_passed += 1
    return True


def Assert(cond):
    """
    Test if cond is true
    """
    return _Assert(cond)


def AssertEqual(x, y, eps=1e-10):
    """
    Test two numbers for equality, in a way that ignores small (rounding) errors
    """
    return _Assert(abs(x - y) <= eps * abs(x))


def AssertEqual_Bool(x, y):
    """
    Test two booleans for equality
    """
    return _Assert(x == y)


def SimpleTest():
    x = ErrValue(2, .1)
    y = ErrValue(10, .3)

    AssertEqual(x.value, 2)
    AssertEqual(x.error, .1)
    AssertEqual(x.rel_error, .1 / 2)
    AssertEqual(x.rel_error_percent, .1 / 2 * 100)

    z = x + y
    AssertEqual(z.value, 12)
    AssertEqual(z.error, math.sqrt(.1**2 + .3**2))

    z = (x + x + y - y) / 2
    AssertEqual(z.value, 2)
    AssertEqual(z.error, .1)

    z = (1 * x + 2 * x - x * 2 + x * 3) / 4
    AssertEqual(z.value, 2)
    AssertEqual(z.error, .1)

    z = 1 / (1 / x + 1 / y) - (x * y) / (x + y) + x / 1000
    AssertEqual(z.value, .002)
    AssertEqual(z.error, .0001)

    z = x**y / x**(y - 1) - y**x / y**(x + 1) + y**(-1)
    AssertEqual(z.value, 2)
    AssertEqual(z.error, .1)

    z = 0
    for i in range(0, 10):
        z += ErrValue(i, i / 10)
    AssertEqual(z.value, 45)
    AssertEqual(z.error, math.sqrt(2.85))


def CompareTest():
    a = ErrValue(9.9, 1)
    b = ErrValue(10, 1)

    AssertEqual_Bool(a < b, True)
    AssertEqual_Bool(a.equal(b), True)
    AssertEqual_Bool(a > b, False)

    AssertEqual_Bool(a < 9.95, True)
    AssertEqual_Bool(b > 9.95, True)


def ParseTest():
    x = ErrValue("0123")
    AssertEqual(x.value, 123)
    AssertEqual(x.error, 0)
    AssertEqual_Bool(x.has_error, False)

    x = ErrValue("1.234(0010)e5")
    AssertEqual(x.value, 1.234e5)
    AssertEqual(x.error, 0.01e5)
    AssertEqual_Bool(x.has_error, True)

    x = ErrValue("1.234(1000)e5")
    AssertEqual(x.value, 1.234e5)
    AssertEqual(x.error, 1e5)
    AssertEqual_Bool(x.has_error, True)

    x = ErrValue("1.234(2)e5")
    AssertEqual(x.value, 1.234e5)
    AssertEqual(x.error, 0.002e5)
    AssertEqual_Bool(x.has_error, True)

    x = ErrValue("1234(2)e5")
    AssertEqual(x.value, 1234e5)
    AssertEqual(x.error, 2e5)
    AssertEqual_Bool(x.has_error, True)

    x = ErrValue("     2.345	( 11 )   e-6")
    AssertEqual(x.value, 2.345e-6)
    AssertEqual(x.error, 0.011e-6)
    AssertEqual_Bool(x.has_error, True)

    x = ErrValue(" 3.1415 e+8   ")
    AssertEqual(x.value, 3.1415e8)
    AssertEqual(x.error, 0)
    AssertEqual_Bool(x.has_error, False)

    x = ErrValue(" 3.1415E-8   ")
    AssertEqual(x.value, 3.1415e-8)
    AssertEqual(x.error, 0)
    AssertEqual_Bool(x.has_error, False)

    had_exception = False
    try:
        x = ErrValue("")
    except ValueError:
        had_exception = True
    Assert(had_exception)

    had_exception = False
    try:
        x = ErrValue("1.234 ( 23) e+6 f")
    except ValueError:
        had_exception = True
    Assert(had_exception)

    had_exception = False
    try:
        x = ErrValue("0x123")
    except ValueError:
        had_exception = True
    Assert(had_exception)

    had_exception = False
    try:
        # No space allowed between "e" and exponent (mimics behavior of Pythons
        # float() method)
        x = ErrValue("1.234 ( 23) e +6")
    except ValueError:
        had_exception = True
    Assert(had_exception)

    had_exception = False
    try:
        # No decimal point allowed in error
        x = ErrValue("123(.4)")
    except ValueError:
        had_exception = True
    Assert(had_exception)

    x = ErrValue(23)
    y = ErrValue(str(x))
    AssertEqual(x.value, y.value)
    AssertEqual(x.error, y.error)

    x = ErrValue(23e15)
    y = ErrValue(str(x))
    AssertEqual(x.value, y.value)
    AssertEqual(x.error, y.error)

    x = ErrValue(23e15, 4e10)
    y = ErrValue(str(x))
    AssertEqual(x.value, y.value)
    AssertEqual(x.error, y.error)

    x = ErrValue(23e-2, 4e-7)
    y = ErrValue(str(x))
    AssertEqual(x.value, y.value)
    AssertEqual(x.error, y.error)

    x = ErrValue(23e-15, 4e-18)
    y = ErrValue(str(x))
    AssertEqual(x.value, y.value)
    AssertEqual(x.error, y.error)


def EqTest():
    a = ErrValue(1, .1)
    b = ErrValue(1, .1)
    AssertEqual((a + b).error, .1 * math.sqrt(2))
    AssertEqual((2 * a).error, .2)
    c = a
    AssertEqual((a + c).error, .2)

    x = ErrValue(1, .1)
    y = ErrValue(1.14, .1)
    z = ErrValue(1.15, .1)

    Assert(x.equal(y))
    Assert(y.equal(z))
    Assert(not x.equal(z))


def CovTest():
    x = ErrValue(1, .1)
    y = ErrValue(1, .1)
    x.SetCov(y, 0.)

    z = x + y

    AssertEqual(z.value, 2)
    AssertEqual(z.error, .1 * math.sqrt(2))

    x = ErrValue(2, 1)
    y = ErrValue(3, 2)

    f = 3 * x + 2 * y - 10
    g = x - 3 * y + 4

    AssertEqual((f + g + 45).cov(f - 2 * g - 100), -28)

    x = ErrValue(10, 5)
    y = ErrValue(20, 6)
    x.SetCov(y, -21)

    AssertEqual(x.cov(y), -21)
    AssertEqual(y.cov(x), -21)

    a = x + y
    b = x - 2 * y

    AssertEqual(a.cov(b), -26)
    AssertEqual(b.cov(a), -26)

    a = 2 * x + 3 * y + 15
    b = (2 + 3) * x + 2 * (y + 2)

    AssertEqual(x.cov(a), 2 * 25 - 3 * 21)
    AssertEqual(a.cov(x), 2 * 25 - 3 * 21)
    AssertEqual(y.cov(b), 2 * 36 - 5 * 21)

    AssertEqual(a.cov(b), 10 * 25 - 19 * 21 + 6 * 36)
    AssertEqual(b.cov(a), a.cov(b))

    x.SetCov(y, -10)
    x.SetError(4)
    AssertEqual(a.cov(b), 10 * 16 - 19 * 10 + 6 * 36)
    AssertEqual(b.cov(a), a.cov(b))

    AssertEqual(x.cov(a), 2 * 16 - 3 * 10)


def ImmutableTest():
    x = ErrValue(2, .1)
    y = x
    x += ErrValue(1, .1)

    AssertEqual(y.value, 2)
    AssertEqual(y.error, .1)
    AssertEqual(x.value, 3)
    AssertEqual(x.error, .1 * math.sqrt(2))


def PropTest():
    x = ErrValue(1, .1)
    y = ErrValue(2, .2)
    z = x
    w = x + y

    AssertEqual(x.var, .01)
    AssertEqual(y.var, .04)
    AssertEqual(x.cov(y), 0)
    AssertEqual(y.cov(x), 0)

    x.SetCov(y, .2)
    AssertEqual(x.cov(y), .2)
    AssertEqual(y.cov(x), .2)
    AssertEqual(z.cov(x), .01)
    AssertEqual(z.cov(y), .2)
    AssertEqual(x.cov(z), .01)
    AssertEqual(y.cov(z), .2)

    x.SetError(.5)
    AssertEqual(z.error, .5)

    AssertEqual(w.value, 3)
    AssertEqual(w.error, math.sqrt(.25 + .4 + .04))

    y.SetCov(x, .3)
    AssertEqual(w.error, math.sqrt(.25 + .6 + .04))


def GetRuntime(func):
    t0 = time.clock()
    func()
    t1 = time.clock()

    return t1 - t0


def TimeTest():
    def LongLoop(n):
        s = ErrValue(0, 0)
        b = s

        for i in range(0, n):
            s += ErrValue(i, math.sqrt(i)) * ErrValue(.1, 0)

        AssertEqual(b.value, 0)
        AssertEqual(b.error, 0)
        s2 = sum(range(0, n))
        AssertEqual(s.value, s2 / 10)
        AssertEqual(s.var, s2 / 100)

    for n in (1000, 2000, 3000, 4000):
        t = GetRuntime(lambda: LongLoop(n))
        print("Info: %d iterations take %f seconds." % (n, t))


def OverloadTest():
    AssertEqual(sqrt(10), math.sqrt(10))
    AssertEqual(exp(10), math.exp(10))
    AssertEqual(log(10), math.log(10))

    AssertEqual(sin(10), math.sin(10))
    AssertEqual(cos(10), math.cos(10))
    AssertEqual(tan(10), math.tan(10))

    AssertEqual(asin(.1), math.asin(.1))
    AssertEqual(acos(.1), math.acos(.1))
    AssertEqual(atan(.1), math.atan(.1))

    AssertEqual(sinh(10), math.sinh(10))
    AssertEqual(cosh(10), math.cosh(10))
    AssertEqual(tanh(10), math.tanh(10))


def SpecFuncTest():
    x = ErrValue(2, .1)
    y = ErrValue(10, .3)
    x.SetCov(y, 1)

    z = sqrt(x)**2 + sqrt(y) * sqrt(y) - y
    AssertEqual(z.value, 2)
    AssertEqual(z.error, .1)

    z = exp(log(x)) + exp(log(y) - log(y))
    AssertEqual(z.value, 3)
    AssertEqual(z.error, .1)

    z = sinh(x) + cosh(x) - exp(x) + 5
    AssertEqual(z.value, 5)
    AssertEqual(z.error, 0)

    z = tanh(x) + tanh(y) - sinh(y) / cosh(y)
    w = .5 * log((1 + z) / (1 - z))  # Inverse tanh
    AssertEqual(w.value, 2)
    AssertEqual(w.error, .1)

    x = ErrValue(.5, .1)
    y = ErrValue(.2, .03)

    z = asin(sin(x)) + acos(cos(y))
    AssertEqual(z.value, .5 + .2)
    AssertEqual(z.error, math.sqrt(.1**2 + .03**2))

    z = asin(sin(x)) + sin(x) / cos(x) - tan(x) + sin(y) / cos(y) - tan(y)
    AssertEqual(z.value, .5)
    AssertEqual(z.error, .1)

    z = atan(sin(y) / cos(y))
    AssertEqual(z.value, .2)
    AssertEqual(z.error, .03)

    z = sin(x)**2 + cos(x)**2
    AssertEqual(z.value, 1)
    AssertEqual(z.error, 0)


def WiedenhoeverTest():
    fVal = [5.072512500000000e+06, 1.914380073547363e+00, -
            2.576103271484375e+03, 5.575768750000000e+05, 2.690322510898113e-02]
    fCov = [[2.249871e+14, 4.650178e+06, -1.275365e+10, -3.515933e+10, -7.640853e+02],
            [4.650182e+06, 9.611798e-02, -2.635278e+02, -7.755506e+02, -1.618876e-05],
            [-1.275358e+10, -2.635262e+02, 7.242609e+05,
                7.009434e+05, 3.099347e-02],
            [-3.509266e+10, -7.741693e+02, 6.971664e+05,
                5.506305e+09, 4.921834e+01	],
            [-7.634589e+02, -1.617577e-05, 3.095811e-02, 4.921848e+01, 4.681867e-07	]]

    # NOTE: these numbers are chosen at random and carry no real significance.
    for E in (10., 25., 83., 100., 150., 413.,
              764., 1034., 2056., 5634., 10864.):
        (v0, e0) = WiedenhoeverManual(E, fVal, fCov)
        (v1, e1) = WiedenhoeverAuto(E, fVal, fCov)
        AssertEqual(v0, v1)
        AssertEqual(e0, e1)


def WiedenhoeverAuto(E, fVal, fCov):
    # Automatic error propagation

    fPars = [ErrValue(val) for val in fVal]
    # Note that the matrix provided is non-symmetric, so we symmetrize it
    for i in range(0, len(fVal)):
        for j in range(i, len(fVal)):
            fPars[i].SetCov(fPars[j], (fCov[i][j] + fCov[j][i]) / 2)

    eff = fPars[0] * pow((E - fPars[2] + fPars[3] *
                          hdtv.errvalue.exp(-fPars[4] * E)), -fPars[1])

    return (eff.value, eff.error)


def WiedenhoeverManual(E, fPars, fCov):
    # Manual error propagation

    norm = 1.0

    def _Eff(E, fPars): return norm * fPars[0] * math.pow(
        (E - fPars[2] + fPars[3] * math.exp(-fPars[4] * E)), -fPars[1])
    value = _Eff(E, fPars)

    # List of derivatives
    _dEff_dP = [None, None, None, None, None]
    _dEff_dP[0] = lambda E, fPars: norm * value / fPars[0]    # dEff/da
    _dEff_dP[1] = lambda E, fPars: norm * (- value) * math.log(
        E - fPars[2] + fPars[3] * math.exp(-fPars[4] * E))  # dEff/db
    _dEff_dP[2] = lambda E, fPars: norm * value * fPars[1] / \
        (E - fPars[2] + fPars[3] * math.exp(-fPars[4] * E))  # dEff/dc
    _dEff_dP[3] = lambda E, fPars: norm * (- value) * fPars[1] / (
        E - fPars[2] + fPars[3] * math.exp(-fPars[4] * E)) * math.exp(-fPars[4] * E)  # dEff/dd
    _dEff_dP[4] = lambda E, fPars: norm * value * fPars[1] / \
        (E - fPars[2] + fPars[3] * math.exp(-fPars[4] * E)) * \
        fPars[3] * math.exp(-fPars[4] * E) * E  # dEff/de

    # Do matrix multiplication
    res = 0.0
    for i in range(0, len(fPars)):
        tmp = 0.0
        for j in range(0, len(fPars)):
            tmp += (_dEff_dP[j](E, fPars) * fCov[i][j])

        res += (_dEff_dP[i](E, fPars) * tmp)

    error = math.sqrt(res)

    return (value, error)


def WunderTest():
    fVal = [2.211263781646267e-04, 2.492647216796875e+03, -
            3.740219399333000e-04, -6.600070190429688e+02]
    fCov = [[8.177790e-09, 3.537367e-03, -4.079504e-09, -6.172973e-05],
            [3.537369e-03, 2.970566e+03, -1.781463e-03, -1.906571e+02],
            [-4.079504e-09, -1.781462e-03, 2.038979e-09, 3.218747e-05],
            [-6.173008e-05, -1.906572e+02, 3.218765e-05, 2.387957e+01]]

    # NOTE: these numbers are chosen at random and carry no real significance.
    for E in (10., 25., 83., 100., 150., 413.,
              764., 1034., 2056., 5634., 10864.):
        (v0, e0) = WunderManual(E, fVal, fCov)
        (v1, e1) = WunderAuto(E, fVal, fCov)
        AssertEqual(v0, v1)
        AssertEqual(e0, e1)


def WunderAuto(E, fVal, fCov):
    # Automatic error propagation

    fPars = [ErrValue(val) for val in fVal]
    # Note that the matrix provided is non-symmetric, so we symmetrize it
    for i in range(0, len(fVal)):
        for j in range(i, len(fVal)):
            fPars[i].SetCov(fPars[j], (fCov[i][j] + fCov[j][i]) / 2)

    eff = (fPars[0] * E + fPars[1] / E) * exp(fPars[2] * E + fPars[3] / E)

    return (eff.value, eff.error)


def WunderManual(E, fPars, fCov):
    # Manual error propagation

    norm = 1.0

    def _Eff(E, fPars): return norm * \
        (fPars[0] * E + fPars[1] / E) * math.exp(fPars[2] * E + fPars[3] / E)
    value = _Eff(E, fPars)

    # List of derivatives
    _dEff_dP = [None, None, None, None]

    _dEff_dP[0] = lambda E, fPars: norm * E * \
        math.exp(fPars[2] * E + fPars[3] / E)    # dEff/da
    _dEff_dP[1] = lambda E, fPars: norm * 1 / E * \
        math.exp(fPars[2] * E + fPars[3] / E)  # dEff/db
    _dEff_dP[2] = lambda E, fPars: norm * \
        (fPars[0] * E + fPars[1] / E) * E * \
        math.exp(fPars[2] * E + fPars[3] / E)  # dEff/dc
    _dEff_dP[3] = lambda E, fPars: norm * \
        (fPars[0] * E + fPars[1] / E) * 1 / E * \
        math.exp(fPars[2] * E + fPars[3] / E)  # dEff/dd

    # Do matrix multiplication
    res = 0.0
    for i in range(0, len(fPars)):
        tmp = 0.0
        for j in range(0, len(fPars)):
            tmp += (_dEff_dP[j](E, fPars) * fCov[i][j])

        res += (_dEff_dP[i](E, fPars) * tmp)

    error = math.sqrt(res)

    return (value, error)


# Test for sane division semantics
AssertEqual(1 / 2, .5)

# General tests
SimpleTest()
CompareTest()
ParseTest()
EqTest()
CovTest()
ImmutableTest()
PropTest()
TimeTest()
OverloadTest()
SpecFuncTest()

# Tests with hand-calculated derivatives
# (recycled from the old efficiency classes)
WiedenhoeverTest()
WunderTest()

# Print summary
if tests_failed == 0:
    print("SUCCESS: all %d tests passed" % tests_passed)
else:
    print("WARNING: %d tests failed (%d passed, %d total)" %
          (tests_failed, tests_passed, tests_failed + tests_passed))
