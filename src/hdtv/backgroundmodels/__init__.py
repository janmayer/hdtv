from .exponential import BackgroundModelExponential
from .interpolation import BackgroundModelInterpolation
from .polynomial import BackgroundModelPolynomial

# dictionary of available background models
BackgroundModels = {}
BackgroundModels["exponential"] = BackgroundModelExponential
BackgroundModels["polynomial"] = BackgroundModelPolynomial
BackgroundModels["interpolation"] = BackgroundModelInterpolation
