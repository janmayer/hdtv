#!/usr/bin/env python

import os
import glob

from distutils.core import setup, Extension


display = Extension('display', 
                    sources = glob.glob('src/display/*.cxx'), 
                    include_dirs=['/usr/include/root'],
                    depends=''
                    )
fit     = Extension('fit', 
                    sources=glob.glob('src/fit/*.cxx'), 
                    include_dirs=['/usr/include/root'],
                    depends=''
                    )
mfile_root = Extension('mfile-root', 
                    sources=glob.glob('src/mfile-root/*.cxx'), 
                    include_dirs=['/usr/include/root'],
                    libraries=['mfile', 'stdc++'],
                    depends =''
                    )

data = glob.glob('hdtv/share/*')

setup(name='hdtv',
    version = '0.1',
    description='hdtv',
    author = open('./AUTHORS', 'r').read(),
    long_description=open('./README','r').read(),
    scripts = ['bin/hdtv'],
    packages=['hdtv', 'hdtv.plugins', 'hdtv.peakmodels', 'hdtv.efficiency', 'hdtv.database'],
    package_data={'hdtv':['share/*']},
    ext_package='hdtv/clib',
    ext_modules=[display, fit, mfile_root ]
    )

