# HDTV - Nuclear Spectrum Analysis Tool

HDTV tries to provide functionality similar to the old TV program 
on top of the ROOT data analysis toolkit developed at CERN. The use 
of Python gives HDTV much better scripting capabilities than TV. 
Also, since HDTV consists of a number of modules that can in principle 
be used independently of each other, HDTV is much easier to extend and 
customize. HDTV is written in a mixture of C++ and Python, glued 
together using PyROOT. 


## Hotkeys

Note: Hotkeys are case sensitive.

### Window
* <kbd>u</kbd>, Update Viewport
* <kbd>l</kbd>, Toggle Log Scale
* <kbd>A</kbd>, Toggle Y Auto Scale
* <kbd>Exclam</kbd>, Toggle Use Norm

#### x directions
* <kbd>Space</kbd>, Set X Zoom Marker
* <kbd>x</kbd>, Expand X
* <kbd>Right</kbd>, Shift X Offset Right
* <kbd>Left</kbd>, Shift X Offset Left
* <kbd>Greater</kbd>, Shift X Offset Right
* <kbd>Less</kbd>, Shift X Offset Left
* <kbd>Return</kbd>, Update
* <kbd>Enter</kbd>, Update
* <kbd>Bar</kbd>, Set X Center at Cursor
* <kbd>1</kbd>, X Zoom In Around Cursor
* <kbd>0</kbd>, X Zoom Out Around Cursor

#### y direction
* <kbd>h</kbd>, Set Y Zoom Marker
* <kbd>y</kbd>, Expand Y
* <kbd>Up</kbd>, Shift Y Offset Up
* <kbd>Down</kbd>, Shift Y Offset Down
* <kbd>Z</kbd>, Y Zoom In Around Cursor
* <kbd>X</kbd>, Y Zoom Out Around Cursor

#### all directions
* <kbd>e</kbd>, Expand
* <kbd>i</kbd>, Enter Edit Mode: Go To Position

### Spec Interface
* <kbd>PageUp</kbd>, Show Prev
* <kbd>PageDown</kbd>, Show Next
* [<kbd>N</kbd>, <kbd>p</kbd>], Show Prev
* [<kbd>N</kbd>, <kbd>n</kbd>], Show Next
* <kbd>Equal</kbd>, Refresh All
* <kbd>t</kbd>, Refresh Visible
* <kbd>n</kbd>, Enter Edit Mode: Show spectrum
* <kbd>a</kbd>, Enter Edit Mode: Activate spectrum

### Fit Interface
* <kbd>b</kbd>, Set Marker bg
* [<kbd>Minus</kbd>, <kbd>b</kbd>], Remove Marker bg
* <kbd>r</kbd>, Set Marker region
* [<kbd>Minus</kbd>, <kbd>r</kbd>], Remove Marker region
* <kbd>p</kbd>, Set Marker peak
* [<kbd>Minus</kbd>, <kbd>p</kbd>], Remove Marker peak
* <kbd>B</kbd>, Execute Fit (Background only)
* <kbd>F</kbd>, Execute Fit 
* <kbd>Q</kbd>, QuickF it
* [<kbd>Minus</kbd>, <kbd>B</kbd>], Clear Fit (Background only)
* [<kbd>Minus</kbd>, <kbd>F</kbd>], Clear Fit
* [<kbd>Plus</kbd>, <kbd>F</kbd>], Store Fit
* <kbd>D</kbd>, Show Decomposition
* [<kbd>Minus</kbd>, <kbd>D</kbd>], Hide Decomposition
* [<kbd>f</kbd>, <kbd>s</kbd>], Enter Edit Mode: Show Fit
* [<kbd>f</kbd>, <kbd>a</kbd>], Enter Edit Mode: Activate Fit
* [<kbd>f</kbd>, <kbd>p</kbd>], Show Prev
* [<kbd>f</kbd>, <kbd>n</kbd>], Show Next
* <kbd>I</kbd>, Execute Integral

### Matrix Interface
* <kbd>g</kbd>, Set Marker cut
* [<kbd>c</kbd>, <kbd>g</kbd>], Set Marker cutregion
* [<kbd>c</kbd>, <kbd>b</kbd>], Set Marker cutbg
* [<kbd>Minus</kbd>, <kbd>c</kbd>, <kbd>g</kbd>], Remove Marker cutregion
* [<kbd>Minus</kbd>, <kbd>c</kbd>, <kbd>b</kbd>], Remove Marker cutbg
* [<kbd>Minus</kbd>, <kbd>C</kbd>], Clear Cut
* [<kbd>Plus</kbd>, <kbd>C</kbd>], Store Cut
* <kbd>C</kbd>, Execute Cut
* [<kbd>c</kbd>, <kbd>s</kbd>], Enter Edit Mode: Show Cut
* [<kbd>c</kbd>, <kbd>a</kbd>], Enter Edit Mode: Activate Cut
* [<kbd>c</kbd>, <kbd>p</kbd>], Show Prev
* [<kbd>c</kbd>, <kbd>n</kbd>], Show Next
* <kbd>Tab</kbd>, Switch



## Install

1.) Install locally and run from source directory

	Execute "make" in the src subdirectory

2.) Install into system (requires superuser's rights)

	Run "python setup.py install"



## HDTV development team

- Jan Mayer <jan.mayer@ikp.uni-koeln.de>
- Elena Hoemann <ehoemann@ikp.uni-koeln.de>

### Previous developers
- Norbert Braun <n.braun@ikp.uni-koeln.de>
- Tanja Kotthaus <t.kotthaus@ikp.uni-koeln.de>
- Ralf Schulze <r.schulze@ikp.uni-koeln.de>
