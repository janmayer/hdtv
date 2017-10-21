# HDTV - Nuclear Spectrum Analysis Tool

HDTV tries to provide functionality similar to the old TV program 
on top of the ROOT data analysis toolkit developed at CERN. The use 
of Python gives HDTV much better scripting capabilities than TV. 
Also, since HDTV consists of a number of modules that can in principle 
be used independently of each other, HDTV is much easier to extend and 
customize. HDTV is written in a mixture of C++ and Python, glued 
together using PyROOT. 


## Install

0. To build and run HDTV, the following dependencies are required:

    * [ROOT](https://root.cern/) 6
    * [libmfile](https://gitlab.ikp.uni-koeln.de/jmayer/libmfile)
    * python2.7 *or* python3
    * python-scipy
    * python-matplotlib
    * python-docutils (*build, for the documentation*)
    * libx11 (*build*)

1. Run locally from source directory

	```
	make
	./bin/hdtv
	```

2. (Optionally) Generate man pages
	
    ```
	make doc
	```

3. Install into system for current user only

	`python setup.py install --user`

4. Install into system (requires superuser's rights)

	`python setup.py install`


## Documentation
For more information, including an overview of the available key
bindings, refer to the [documentation](doc/guide/hdtv.rst).


## HDTV development team

- Jan Mayer <jan.mayer@ikp.uni-koeln.de>
- Elena Hoemann <ehoemann@ikp.uni-koeln.de>

### Previous developers
- Norbert Braun <n.braun@ikp.uni-koeln.de>
- Tanja Kotthaus <t.kotthaus@ikp.uni-koeln.de>
- Ralf Schulze <r.schulze@ikp.uni-koeln.de>
