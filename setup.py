#!/usr/bin/env python

import versioneer
from setuptools import setup


setup(
    name='hdtv',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='HDTV - Nuclear Spectrum Analysis Tool',
    url='https://github.com/janmayer/hdtv',
    maintainer='Jan Mayer',
    maintainer_email='jan.mayer@ikp.uni-koeln.de',
    license='GPL',
    install_requires=['scipy', 'matplotlib', 'uncertainties'],
    extras_require={
        'dev': ['docutils'],
        'test': ['pytest', 'pytest-cov'],
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
    package_data={
        'hdtv': ['share/*'],
        'hdtv.rootext': [
            'display/*', 'fit/*', 'mfile-root/*', 'mfile-root/*/*', 'mfile-root/*/*/*'
        ],
    },
    data_files=[
        ('share/zsh/site-functions', ['data/completions/_hdtv']),
        ('share/bash-completion/completions', ['data/completions/hdtv']),
        ('share/applications', ['data/hdtv.desktop']),
    ],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
