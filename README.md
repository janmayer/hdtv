# HDTV - Nuclear Spectrum Analysis Tool

[![Build Status](https://travis-ci.org/janmayer/hdtv.svg?branch=master)](https://travis-ci.org/janmayer/hdtv)

HDTV tries to provide functionality similar to the old TV program
on top of the ROOT data analysis toolkit developed at CERN. The use
of Python gives HDTV much better scripting capabilities than TV.
Also, since HDTV consists of a number of modules that can in principle
be used independently of each other, HDTV is much easier to extend and
customize. HDTV is written in a mixture of C++ and Python, glued
together using PyROOT.


## Installation

### Requirements
To build and run HDTV, the following dependencies are required:

* libx11 (*build*)
* python2.7 *or* python3
* python-scipy
* python-matplotlib
* python-uncertainties
* python-docutils (*build, for the documentation*)
* [ROOT](https://root.cern/) 6
    - Needs to be compiled against the correct python version.
    - In python, `import ROOT` must succeed.
    - System packages may be available, e.g. `root python2-root`
* [libmfile](https://gitlab.ikp.uni-koeln.de/jmayer/libmfile)


### Installation via pip

If you use pip to you manage your python packages (recommended):
```
pip install --egg https://gitlab.ikp.uni-koeln.de/staging/hdtv/repository/master/archive.zip
```

It is also possible to create a pip-installable package with 
`python setup.py sdist`.


### Installation without pip
- Clone repository

    ```
    git clone https://gitlab.ikp.uni-koeln.de/staging/hdtv.git
    cd hdtv
    ```

- Install into system for current user only

    `python setup.py install --user`

-  Install into system (requires superuser's rights)

	`python setup.py install`


### Run locally from source directory without installation

```
git clone https://gitlab.ikp.uni-koeln.de/staging/hdtv.git
cd hdtv
./bin/hdtv
```

Generate man pages:

```
cd doc/guide
make doc
```


### Handling different ROOT versions

HDTV uses `ROOT.gSystem.Load(libary)` to load some critical
components. These need to be compiled against the *exact* ROOT
version imported in python. HDTV will try to automatically recompile
the libraries for the current ROOT if the available ones cannot
be loaded. This can also be forced with:

`hdtv --rebuild-usr`  

When installed system-wide, the libraries can be recompiled once for
all users with:
 
`hdtv --rebuild-sys`

This eliminates the need to reinstall HDTV after changes to the root
installation.  

Multiple Versions of ROOT can be used alongside, the correct library 
version will be choosen.


## Documentation
For more information, including an overview of the available key
bindings, refer to the [documentation](doc/guide/hdtv.rst).
A [tutorial](doc/guide/hdtv-tutorial.rst) giving an introduction
to HDTV and its basic features is also available.
