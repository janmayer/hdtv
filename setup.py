#!/usr/bin/env python

import os
import glob
import subprocess

from distutils.core import setup, Extension

root_incdir = subprocess.Popen(["root-config --incdir"], stdout=subprocess.PIPE, shell=True).communicate()[0].strip()
root_ldflags = subprocess.Popen(["root-config --glibs"], stdout=subprocess.PIPE, shell=True).communicate()[0].strip().split(' ')
root_compile_args = subprocess.Popen(["root-config --cflags"], stdout=subprocess.PIPE, shell=True).communicate()[0].strip().split(' ')

print(root_incdir)
print(root_ldflags)
print(root_compile_args)

subprocess.call(["make", "-C", "src/display", "rootdict-display.cxx"])
subprocess.call(["make", "-C", "src/fit", "rootdict-fit.cxx"])
subprocess.call(["make", "-C", "src/mfile-root", "rootdict-mfile-root.cxx"])

subprocess.call(['mkdir', '-p', 'hdtv/clib'])
subprocess.call(['cp', 'src/display/rootdict-display_rdict.pcm', 'hdtv/clib/'])
subprocess.call(['cp', 'src/fit/rootdict-fit_rdict.pcm', 'hdtv/clib/'])
subprocess.call(['cp', 'src/mfile-root/rootdict-mfile-root_rdict.pcm', 'hdtv/clib/'])

display = Extension('display',
                    sources = glob.glob('src/display/*.cxx'),
                    include_dirs = [root_incdir],
                    depends = '',
                    libraries = ['X11'],
		    extra_link_args = [] + root_ldflags,
		    extra_compile_args = [] + root_compile_args
                    )
fit     = Extension('fit',
                    sources=glob.glob('src/fit/*.cxx'),
                    include_dirs = [root_incdir],
                    depends='',
		    extra_link_args = [] + root_ldflags,
		    extra_compile_args = [] + root_compile_args
                    )
mfile_root = Extension('mfile-root',
                    sources=glob.glob('src/mfile-root/*.cxx'),
                    include_dirs = [root_incdir],
                    libraries=['mfile', 'stdc++'],
                    depends ='',
		    extra_link_args = [] + root_ldflags,
		    extra_compile_args = [] + root_compile_args
                    )

data = glob.glob('hdtv/share/*')
sys_includes = ['src/display/Calibration.h','src/display/DisplayBlock.h',
     'src/display/DisplayCut.h', 'src/display/DisplayFunc.h',
     'src/display/DisplayObj.h', 'src/display/DisplaySpec.h',
     'src/display/DisplayStack.h', 'src/display/Marker.h',
     'src/display/MTViewer.h', 'src/display/Painter.h',
     'src/display/View1D.h', 'src/display/View2D.h',
     'src/display/Viewer.h', 'src/display/View.h',
     'src/display/XMarker.h', 'src/display/YMarker.h',
     'src/fit/Background.h', 'src/fit/EEFitter.h',
     'src/fit/Fitter.h', 'src/fit/Integral.h',
     'src/fit/Param.h', 'src/fit/PolyBg.h',
     'src/fit/TheuerkaufFitter.h', 'src/mfile-root/MatOp.h',
     'src/mfile-root/MFileHist.h', 'src/mfile-root/VMatrix.h']

setup(name='hdtv',
    version = '0.1',
    description='hdtv',
    author = open('./AUTHORS', 'r').read(),
    long_description=open('./README','r').read(),
    scripts = ['bin/hdtv'],
    packages=['hdtv', 'hdtv.plugins', 'hdtv.peakmodels', 'hdtv.efficiency', 'hdtv.database'],
    package_data={'hdtv':['share/*', 'clib/*.pcm']},
    ext_package='hdtv/clib',
    ext_modules=[display, fit, mfile_root ],
    data_files=[('share/hdtv/include', sys_includes)]
    )

