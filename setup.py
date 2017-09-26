#!/usr/bin/env python

import os
import glob
import subprocess

from distutils.core import setup, Extension

sys_includes = []
print('Building C++ library display.so ...')
subprocess.call(['make', '-C', 'src/display'])
sys_includes += glob.glob('src/display/*.h')
print('Building C++ library fit.so ...')
subprocess.call(['make', '-C', 'src/fit'])
sys_includes += glob.glob('src/fit/*.h')
print('Building C++ library mfile-root.so ...')
subprocess.call(['make', '-C', 'src/mfile-root'])
sys_includes += glob.glob('src/mfile-root/*.h')

# Remove rootcling LinkDef.h from list of headers to
# distribute
sys_includes.remove('src/display/LinkDef.h')
sys_includes.remove('src/fit/LinkDef.h')
sys_includes.remove('src/mfile-root/LinkDef.h')


import hdtv.version
setup(name='hdtv',
      version=hdtv.version.VERSION,
      description='HDTV - Nuclear Spectrum Analysis Tool',
      scripts=['bin/hdtv'],
      packages=['hdtv', 'hdtv.plugins', 'hdtv.peakmodels',
                'hdtv.efficiency', 'hdtv.database'],
      package_data={'hdtv': ['share/*', 'clib/*.pcm', 'clib/*.so']},
      ext_package='hdtv/clib',
      data_files=[('share/hdtv/include', sys_includes)]
      )
