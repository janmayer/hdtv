#!/usr/bin/env python

import hdtv.version
from setuptools import setup
from distutils.command.build import build
import glob
import subprocess
import os

class CustomBuild(build):
    def run(self):
        # run original install code
        build.run(self)

        # Build libraries for this system
        # run hdtv --rebuild-sys after installation or any root version change
        # or reinstall from scratch
        for module in ['mfile-root', 'fit', 'display']:
            dir = os.path.join(self.build_lib, 'hdtv/rootext/', module)
            print("Building library in %s" % dir)
            subprocess.check_call(['make', '-j', '--silent'], cwd=dir)

manpages = glob.glob('doc/guide/*.1')

setup(
    name='hdtv',
    version=hdtv.version.VERSION,
    description='HDTV - Nuclear Spectrum Analysis Tool',
    url='https://gitlab.ikp.uni-koeln.de/staging/hdtv',
    maintainer='Jan Mayer',
    maintainer_email='jan.mayer@ikp.uni-koeln.de',
    license='GPL',
    install_requires=['scipy', 'matplotlib', 'uncertainties'],
    extras_require={
        'dev': ['docutils'],
        'test': ['pytest'],
    },
    scripts=['bin/hdtv'],
    packages=[
        'hdtv',
        'hdtv.plugins',
        'hdtv.peakmodels',
        'hdtv.efficiency',
        'hdtv.database',
        'hdtv.rootext',
    ],
    package_data={
        'hdtv': ['share/*'],
        'hdtv.rootext': [
            'Makefile', 'Makefile.def', 'Makefile.body',
            'mfile-root/*.hh', 'mfile-root/*.cc', 'mfile-root/Makefile', 'mfile-root/LinkDef.h',
            'mfile-root/libmfile-root.so', 'mfile-root/libmfile-root_rdict.pcm', 'mfile-root/libmfile-root.rootmap',
            'mfile-root/matop/*.h', 'mfile-root/matop/*.c',
            'fit/*.hh', 'fit/*.cc', 'fit/Makefile', 'fit/LinkDef.h',
            'fit/libfit.so', 'fit/libfit_rdict.pcm', 'fit/libfit.rootmap',
            'display/*.hh', 'display/*.cc', 'display/Makefile', 'display/LinkDef.h',
            'display/libdisplay.so', 'display/libdisplay_rdict.pcm', 'display/libdisplay.rootmap',
        ],
    },
    data_files=[
        ('share/man/man1', manpages),
        ('share/zsh/site-functions', ['data/completions/_hdtv']),
        ('share/bash-completion/completions', ['data/completions/hdtv']),
        ('share/applications', ['data/hdtv.desktop']),
    ],
    cmdclass={
        'build': CustomBuild,
    }
)
