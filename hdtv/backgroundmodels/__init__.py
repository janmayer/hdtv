from .polynomial import BackgroundModelPolynomial 
from .interpolation import BackgroundModelInterpolation

# dictionary of available background models
BackgroundModels = dict()
BackgroundModels["polynomial"] = BackgroundModelPolynomial 
BackgroundModels["interpolation"] = BackgroundModelInterpolation
