from .theuerkaufPeak import PeakModelTheuerkauf
from .eePeak import PeakModelEE
from hdtv.errvalue import ErrValue

# dictionary of available peak models
PeakModels = dict()
PeakModels["theuerkauf"] = PeakModelTheuerkauf
PeakModels["ee"] = PeakModelEE
