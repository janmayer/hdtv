#!/usr/bin/env python

import versioneer
from setuptools import setup
import glob

manpages = glob.glob('doc/guide/*.1')

KEYWORDS = '''\
analysis
data-analysis
gamma-spectroscopy
nuclear-physics
nuclear-spectrum-analysis
physics
python
root
root-cern
spectroscopy
'''
CLASSIFIERS = '''\
Development Status :: 5 - Production/Stable
Environment :: Console
Environment :: X11 Applications
Intended Audience :: Information Technology
Intended Audience :: Science/Research
License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)
Natural Language :: English
Operating System :: MacOS
Operating System :: POSIX
Operating System :: POSIX :: Linux
Operating System :: UNIX
Programming Language :: C
Programming Language :: C++
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Information Analysis
Topic :: Scientific/Engineering :: Physics
Topic :: Scientific/Engineering :: Visualization
'''

setup(
    name='hdtv',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='HDTV - Nuclear Spectrum Analysis Tool',
    url='https://github.com/janmayer/hdtv',
    maintainer='Jan Mayer',
    maintainer_email='jan.mayer@ikp.uni-koeln.de',
    license='GPL',
    classifiers=CLASSIFIERS.strip().split('\n'),
    keywords=KEYWORDS.strip().replace('\n', ' '),
    install_requires=[
        'scipy',
        'matplotlib',
        'numpy',
        'ipython',
        'prompt_toolkit',
        'traitlets',
        'uncertainties',
    ],
    extras_require={
        'dev': ['docutils'],
        'test': [
            'pytest',
            'pytest-cov'
        ],
    },
    entry_points={
        'console_scripts': [
            'hdtv=hdtv.app:App',
        ]
    },
    packages=[
        'hdtv',
        'hdtv.database',
        'hdtv.backgroundmodels',
        'hdtv.efficiency',
        'hdtv.peakmodels',
        'hdtv.plugins',
        'hdtv.rootext',
    ],
    package_data={
        'hdtv': ['share/*'],
        'hdtv.rootext': [
            'calibration/*', 'display/*', 'fit/*', 'mfile-root/*', 'mfile-root/*/*', 'mfile-root/*/*/*'
        ],
    },
    data_files=[
        ('share/man/man1', manpages),
        ('share/zsh/site-functions', ['data/completions/_hdtv']),
        ('share/bash-completion/completions', ['data/completions/hdtv']),
        ('share/applications', ['data/hdtv.desktop']),
    ],
)
