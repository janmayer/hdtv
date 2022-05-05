======
 HDTV
======

------------------------------
Nuclear Spectrum Analysis Tool
------------------------------

:Manual section: 1

SYNOPSIS
========

| **hdtv** [ **-h** ] [ **-b** *batchfile* ] [ **-e** *commands* ] [ **-v** ]

DESCRIPTION
===========

HDTV tries to provide functionality similar to the old TV program on top
of the ``ROOT``\(1) data analysis toolkit developed at CERN. The use of Python
gives HDTV much better scripting capabilities than TV. Also, since HDTV
consists of a number of modules that can in principle be used independently
of each other, HDTV is much easier to extend and customize. HDTV is written
in a mixture of C++ and Python, glued together using PyROOT.

OPTIONS
=======

--help, -h
    Show help message and exit

--batch *batchfile*, -b *batchfile*
    Open and execute hdtv batchfile

--execute *commands*, -e *commands*
    Execute hdtv command(s)

--version, -v
    Show HDTV Version

HDTV COMMAND LINE
=================

HDTV features an extensive command line interface. Besides a wide set of
HDTV commands, it is possible to use special prefixes:

:
    Execute a single Python command.

@
    Execute an HDTV batch file (or use the ``exec`` command).

!
    Execute a single shell command.

The command line is implemented using ``prompt_toolkit``. Common features,
such as tab-completion, history and history-search (using ``Ctrl-R``) are
available.

KEY BINDINGS
============

Note: Key bindings are case sensitive.

Window
------

u
    Update Viewport

l
    Toggle Log Scale

A
    Toggle Y Auto Scale

!
    Toggle Use Norm


x directions
^^^^^^^^^^^^

Space
    Set X Zoom Marker

x
    Expand X

Right, >
    Shift X Offset Right

Left, <
    Shift X Offset Left

Return, Enter
    Update

\|
    Set X Center at Cursor

1
    X Zoom In Around Cursor

0
    X Zoom Out Around Cursor

y direction
^^^^^^^^^^^

h
    Set Y Zoom Marker

y
    Expand Y

Up
    Shift Y Offset Up

Down
    Shift Y Offset Down

Z
    Y Zoom In Around Cursor

X
    Y Zoom Out Around Cursor


all directions
^^^^^^^^^^^^^^

e
    Expand

i
    Enter Edit Mode: Go To Position


Spec Interface
--------------

PageUp, N + p
    Show Prev

PageDown, N + n
    Show Next

=
    Refresh All

t
    Refresh Visible

n
    Enter Edit Mode: Show spectrum

a
    Enter Edit Mode: Activate spectrum


Fit Interface
-------------

b
    Set Marker bg

Minus + b
    Remove Marker bg

r
    Set Marker region

Minus + r
    Remove Marker region

p
    Set Marker peak

Minus + p
    Remove Marker peak

B
    Execute Fit (Background only)

F
    Execute Fit

Q
    QuickFit

Minus + B
    Clear Fit (Background only)

Minus + F
    Clear Fit

Plus + F
    Store Fit

D
    Show Decomposition

Minus + D
    Hide Decomposition

f + s
    Enter Edit Mode: Show Fit

f + a
    Enter Edit Mode: Activate Fit

f + p
    Show Prev

f + n
    Show Next

I
    Execute Integral


Matrix Interface
----------------

g
    Set Marker cut

c + g
    Set Marker cutregion

c + b
    Set Marker cutbg

Minus + c + g
    Remove Marker cutregion

Minus + c + b
    Remove Marker cutbg

Minus + C
    Clear Cut

Plus + C
    Store Cut

C
    Execute Cut

c + s
    Enter Edit Mode: Show Cut

c + a
    Enter Edit Mode: Activate Cut

c + p
    Show Prev

c + n
    Show Next

Tab
    Switch

FILES
=====

$HOME/.config/hdtv/startup.py
    Python script that gets executed during startup.

$HOME/.config/hdtv/startup.hdtv, $HOME/.config/hdtv/startup.hdtv.d/\*.hdtv
    Files containing HDTV commands that get executed during startup.

$HOME/.config/hdtv/plugins/
   Put plugins here.

$HOME/.local/share/hdtv/hdtv_history
    History of commands executed in HDTV.

HDTV supports the XDG Base Directory Specification, with the default paths
listed above. If the legacy directory ``$HOME/.hdtv`` exists, it is used
instead. It is also possible to manually set the directory using the
``$HDTV_USER_PATH`` environment variable.

BUGS
====

See https://gitlab.ikp.uni-koeln.de/staging/hdtv/issues/ for a list of all
currently open bugs and feature requests.

AUTHORS
=======

Jan Mayer (jan.mayer@ikp.uni-koeln.de),
Elena Hoemann (ehoemann@ikp.uni-koeln.de),
Oliver Papst (opapst@ikp.tu-darmstadt.de),
Nigel Warr (warr@ikp.uni-koeln.de),
Norbert Braun (n.braun@ikp.uni-koeln.de),
Tanja Kotthaus (t.kotthaus@ikp.uni-koeln.de),
Ralf Schulze (r.schulze@ikp.uni-koeln.de)

SEE ALSO
========

| ``hdtv-tutorial``\(1), ``root``\(1), ``python``\(1)
