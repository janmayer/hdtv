from .theuerkaufPeak import PeakModelTheuerkauf
from .eePeak import PeakModelEE

# dictionary of available peak models
PeakModels = dict()
PeakModels["theuerkauf"] = PeakModelTheuerkauf
PeakModels["ee"] = PeakModelEE
