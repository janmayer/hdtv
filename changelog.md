# HDTV Change Log

## 17.12
+ Proper Support for Integrals: If one wants to work exclusively with integrals, it is possible to work with peak less fits. (@opapst)
+ Support for Python3 (@warr, @opapst) (Fixes #12)
+ Switch from optparse to argparse (@opapst) (Fixes #15)
+ Switch from own implementation of error values to uncertainties libary (@opapst) (Fixes #14)
+ pytest based testing (@opapst)
- Improvements to calibration fitting procedure (@opapst)
- Improvements to tab completion and command line interface (@opapst)
- A bit of documentation (Fixes #6)
- Replace deprecated auto_ptr (@warr)
- Allow exiting the program from batch files and other operations (@opapst)
- Missing background markers: Unexpected behavior fixed (@opapst)
- Diverse other Fixes (@opapst, @warr, @jmayer)
- Change location for user settings/history (@opapst)

## 17.01
+ Relative efficiencies limited to energy range of absolute efficiency (@ehoemann)
+ Fix Printing (@warr)

## 16.12
+ Fixed cutting calibrated mfile matrices
+ Fixed wide tables errvalue

## 16.11
- Fixed spectrum subtract crashing
+ Added support to add/subtract calibrated spectra
+ Added command `spectrum calbin` to rebin spectra to calibration unit.
- Fixed rebinning sometimes not updating calibration

## 16.10
+ wide tables: `config set table wide` for easier Copy & Pasting of tabular data. Use `config set table classic` to change back
+ Nuclide Decay Databases: e.g., `nuclide Ra-226` (@ehoemann)
+ Efficiency Fitting `calibration efficiency fit` (@ehoemann)
+ Some Readme
- Fixed (TM) installation process
- Removed a lot of dead code
- Cleaner startup output

## 16.09
- Fixed Peakfinder not working sometimes
- Support negative calibrations
- Fixed spectrum integration not working if higher region markers was set first
- Fixed rebinning spectra causing integration to sometime return the wrong volume
- Changes to installation and loading path
