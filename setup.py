#!/usr/bin/env python

import os
import glob
import subprocess

from distutils.core import setup, Extension

root_incdir  = subprocess.Popen(["root-config", "--incdir"],stdout=subprocess.PIPE).communicate()[0].strip()
root_ldflags = subprocess.Popen(["root-config", "--glibs"],stdout=subprocess.PIPE).communicate()[0].strip().split(' ')

subprocess.call(["make", "-C", "src/display", "rootdict-display.cxx"])
subprocess.call(["make", "-C", "src/fit", "rootdict-fit.cxx"])
subprocess.call(["make", "-C", "src/mfile-root", "rootdict-mfile-root.cxx"])

display = Extension('display', 
                    sources = glob.glob('src/display/*.cxx'), 
                    include_dirs = [root_incdir],
                    depends = '',
		    extra_link_args = [] + root_ldflags
                    )
fit     = Extension('fit', 
                    sources=glob.glob('src/fit/*.cxx'), 
                    include_dirs = [root_incdir],
                    depends='',
		    extra_link_args = [] + root_ldflags
                    )
mfile_root = Extension('mfile-root', 
                    sources=glob.glob('src/mfile-root/*.cxx'), 
                    include_dirs = [root_incdir],
                    libraries=['mfile', 'stdc++'],
                    depends ='',
		    extra_link_args = [] + root_ldflags
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

