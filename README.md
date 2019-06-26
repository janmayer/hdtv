# HDTV - Nuclear Spectrum Analysis Tool

[![PyPI version](https://badge.fury.io/py/hdtv.svg)](https://badge.fury.io/py/hdtv)
[![Build Status](https://travis-ci.org/janmayer/hdtv.svg?branch=master)](https://travis-ci.org/janmayer/hdtv)
[![codecov](https://codecov.io/gh/janmayer/hdtv/branch/master/graph/badge.svg)](https://codecov.io/gh/janmayer/hdtv)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/d54b84b35f834cb9a73a89a5ea67a8bf)](https://app.codacy.com/manual/janmayer/hdtv/dashboard)

HDTV tries to provide functionality similar to the old TV program
on top of the ROOT data analysis toolkit developed at CERN. The use
of Python gives HDTV much better scripting capabilities than TV.
Also, since HDTV consists of a number of modules that can in principle
be used independently of each other, HDTV is much easier to extend and
customize. HDTV is written in a mixture of C++ and Python, glued
together using PyROOT.


## Installation

```sh
pip install hdtv
```

Please note that the python package (wheel) does currently not include the compiled libraries required to run, as these depend on the root version, the python version, the compiler, and the moon phases.
Instead, these are compiled automatically at first start, which requires certain build tools (see below).

Alternatively, the compilation can be triggered with
```sh
hdtv --rebuild-usr
```
for the current user; or with
```sh
hdtv --rebuild-sys
```
for all user (requires superuser privileges).


### Requirements
To build and run HDTV, the following dependencies are required:

* Python
	- Tested with 2.7, 3.6, 3.7, 3.8
	- Packages: scipy matplotlib uncertainties (docutils)
* [Cern ROOT](https://root.cern/) 6
    - Needs to be compiled against the correct python version.
    - In python, **`import ROOT` must succeed.**
    - System packages may be available on some systems, e.g. `<tool> install root python3-root`
* cmake, gcc, g++ (or similar, in a somewhat modern version)
* libx11-dev `<tool> install libx11-6 libx11-dev`


## Documentation
For more information, including an overview of the available key
bindings, refer to the [documentation](doc/guide/hdtv.rst).
A [tutorial](doc/guide/hdtv-tutorial.rst) giving an introduction
to HDTV and its basic features is also available.


## Further installation topics

### Run locally from source directory without installation

```
git clone https://gitlab.ikp.uni-koeln.de/staging/hdtv.git
cd hdtv
./hdtv/app.py
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
version will be chosen.



### Example installation on Ubuntu 20.04

Note that we use a precompiled ROOT, which unfortunately is linked against python2.
For python2, python-pip is not available as package, thus we use an installer script.

```sh
sudo apt install -y python2 python2-dev python-is-python2 cmake make gcc g++ libx11-dev
wget https://root.cern/download/root_v6.20.04.Linux-ubuntu19-x86_64-gcc9.2.tar.gz
tar xf root_v6.20.04.Linux-ubuntu19-x86_64-gcc9.2.tar.gz
echo 'source ~/root/bin/thisroot.sh' >> ~/.bashrc
echo 'export PATH=~/.local/bin/:$PATH' >> ~/.bashrc
source ~/.bashrc
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
pip install hdtv
hdtv --rebuild-usr
```
