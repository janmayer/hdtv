# HDTV Change Log

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
