#!/usr/bin/env python

import hdtv.version
from setuptools import setup
import glob


manpages = glob.glob('doc/guide/*.1')

setup(
    name='hdtv',
    version=hdtv.version.VERSION,
    description='HDTV - Nuclear Spectrum Analysis Tool',
    url='https://gitlab.ikp.uni-koeln.de/staging/hdtv',
    maintainer='Jan Mayer',
    maintainer_email='jan.mayer@ikp.uni-koeln.de',
    license='GPL',
    install_requires=['scipy', 'matplotlib'],
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
            'mfile-root/*.h', 'mfile-root/*.cxx', 'mfile-root/Makefile',
            'mfile-root/matop/*.h', 'mfile-root/matop/*.c',
            'fit/*.h', 'fit/*.cxx', 'fit/Makefile',
            'display/*.h', 'display/*.cxx', 'display/Makefile',
        ],
    },
    data_files=[
        ('share/man/man1', manpages),
        ('share/zsh/site-functions', ['data/completions/_hdtv']),
        ('share/bash-completion/completions', ['data/completions/hdtv']),
        ('share/applications', ['data/hdtv.desktop']),
    ],
)
