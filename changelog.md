# HDTV Changelog

## Unreleased
- Add GUI-dummy for usage with unittests (@opapst)
- Add background model using spline interpolation (@ugayer)
- Add coverage to unittests (@opapst)
- Add keywords and classifiers to setup.py (@opapst)
- Add object-oriented background models (@ugayer)
- Add travis.yml build and tests (@opapst)
- Fix autocomplete of pathes with spaces (@opapst)
- Fix hdtv.rootext import order (@opapst)
- Fix negative uncertainties from ROOT fits (@opapst)
- Fix typedef (@jmayer)
- Fix wrong cut axis from mfile matrices (@mweinert)
- Move Calibration.hh into separate module (@opapst)
- Remove Python2.7 support due to upcoming EOL (@opapst)
- Remove dead code (@opapst)
- Remove usage of global variables and usage of `__main__` namespace (@opapst)
- Replace Compat.hh by ROOT/RMakeUnique.hh (@opapst)
- Replace bin/hdtv by hdtv.app:App() entrypoint (@opapst)
- Replace code.InteractiveConsole with IPython for Python REPL (@opapst)
- Replace readline with prompt_toolkit (@opapst)
- Other small fixes

## 18.04
- Use uncertainties library (@opapst)
- Large overhaul of compiled libraries (@nima) (Closes #21)
- Fix efficiency fit and nuclide data (@jmayer)
- Other small fixes

## 18.01
- Changed building process in setup.py to allow for package building

## 17.12
+ (Some) Support for Integrals: If one wants to work exclusively with integrals, it is possible to work with peak less fits. See e.g. `fit integral list`. (@opapst)
+ Support for Python3 (@warr, @opapst) (Closes #12)
+ Automatic recompilation on ROOT version changes (@jmayer)
+ Easier installation, e.g. via pip (@jmayer)
+ Switch from optparse to argparse (@opapst) (Closes #15)
+ Switch from own implementation of error values to uncertainties libary (@opapst) (Closes #14)
+ pytest based testing (@opapst)
- Changes to display of tables and uncertainties, see `config set table help`, and `config set uncertainties help` (@opapst)
- Improvements to calibration fitting procedure (@opapst)
- Improvements to tab completion and command line interface (@opapst)
- A bit of documentation (#6)
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
