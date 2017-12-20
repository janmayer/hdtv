#!/usr/bin/env python

import hdtv.version
from setuptools import setup
from distutils.command.install import install
import glob
import os
import sys
import shutil

class CustomInstall(install):
    def run(self):
        # run original install code
        install.run(self)

        # Build libraries for all users
        # run hdtv --rebuild-sys after installation or any root version change
        # Fixme: This IS a very hacky solution
        # Sometimes ROOT will complain while loading the library that headers can't be found, even if those
        # are RIGHT THERE and all of them should have been inlined anyway.
        # This behavior depends on the specific Python+ROOT version / parameters / position of the moon
        #
        # Prepend final install location (.../site-packages) and load this specific dlmgr.
        sys.path.insert(1, os.path.join(self.install_lib, 'hdtv', 'rootext'))
        import dlmgr
        dlmgr.RebuildLibraries(dlmgr.syslibdir)


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
    cmdclass={
        'install': CustomInstall,
    }
)
