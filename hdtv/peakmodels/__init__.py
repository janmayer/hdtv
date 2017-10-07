from .theuerkaufPeak import PeakModelTheuerkauf
from .eePeak import PeakModelEE
from .peak import FitValue

# dictionary of available peak models
PeakModels = dict()
PeakModels["theuerkauf"]=PeakModelTheuerkauf
PeakModels["ee"]=PeakModelEE
