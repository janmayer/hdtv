#!/usr/bin/env python

import hdtv.version
from setuptools import setup
from distutils.command.build import build
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
            subprocess.check_call(['make', '-j'], cwd=dir)


setup(
    name='hdtv',
    version=hdtv.version.VERSION,
    description='HDTV - Nuclear Spectrum Analysis Tool',
    url='https://github.com/janmayer/hdtv',
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
        'hdtv.database',
        'hdtv.efficiency',
        'hdtv.peakmodels',
        'hdtv.physics',
        'hdtv.plugins',
        'hdtv.rootext',
    ],
    data_files=[
        ('share/zsh/site-functions', ['data/completions/_hdtv']),
        ('share/bash-completion/completions', ['data/completions/hdtv']),
        ('share/applications', ['data/hdtv.desktop']),
    ],
    # cmdclass={
    #     'build': CustomBuild,
    # }
)
