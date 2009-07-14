#!/usr/bin/env python

import os
import glob

from distutils.core import setup, Extension


display = Extension('display', 
					sources = glob.glob('src/display/*.cxx'), 
					include_dirs=['/usr/include/root'],
					language='c++',
					depends=''
					)
fit 	= Extension('fit', 
					sources=glob.glob('src/fit/*.cxx'), 
					include_dirs=['/usr/include/root'],
					language='c++',
					depends=''
					)
mfile_root = Extension('mfile-root', 
					sources=glob.glob('src/mfile-root/*.cxx'), 
					include_dirs=['/usr/include/root'],
					libraries=['mfile'],
					language='c++',
					depends =''
					)

setup(name='hdtv',
	version = '0.1',
	description='hdtv',
	author = open('./AUTHORS', 'r').read(),
	long_description=open('./README','r').read(),
	scripts = ['bin/hdtv'],
	packages=['hdtv', 'hdtv.plugins'],
	ext_package='hdtv/clib',
	ext_modules=[display, fit, mfile_root ]
	)
#gcc -pthread -fno-strict-aliasing -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -fPIC -I/usr/include/python2.5 -c src/display/View.cxx -o build/temp.linux-i686-2.5/src/display/View.o

#g++ -pthread -m32 -I/usr/include/root -g -Wall -fpic -c View.cxx

