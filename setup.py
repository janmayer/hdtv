#!/usr/bin/env python

import os
import glob
import subprocess

from distutils.core import setup

print('Building C++ libraries ...')
subprocess.call(['make'])

sys_includes = glob.glob('src/*/*.h')

# Remove rootcling LinkDef.h from list of headers to distribute
sys_includes.remove('src/display/LinkDef.h')
sys_includes.remove('src/fit/LinkDef.h')
sys_includes.remove('src/mfile-root/LinkDef.h')

manpages = glob.glob('doc/guide/*.1')


import hdtv.version
setup(
    name='hdtv',
    version=hdtv.version.VERSION,
    license='GPL',
    description='HDTV - Nuclear Spectrum Analysis Tool',
    scripts=['bin/hdtv'],
    packages=[
        'hdtv',
        'hdtv.plugins',
        'hdtv.peakmodels',
        'hdtv.efficiency',
        'hdtv.database',
    ],
    package_data={
        'hdtv': ['share/*', 'clib/*.pcm', 'clib/*.so']
    },
    ext_package='hdtv/clib',
    data_files=[
        ('share/hdtv/include', sys_includes),
        ('share/man/man1', manpages),
        ('share/zsh/site-functions', ['data/completions/_hdtv']),
        ('share/bash-completion/completions', ['data/completions/hdtv']),
        ('share/applications', ['data/hdtv.desktop']),
    ],
)
