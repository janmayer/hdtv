from .eePeak import PeakModelEE
from .theuerkaufPeak import PeakModelTheuerkauf

# dictionary of available peak models
PeakModels = {}
PeakModels["theuerkauf"] = PeakModelTheuerkauf
PeakModels["ee"] = PeakModelEE
