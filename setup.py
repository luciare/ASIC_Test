#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 03 16:20:42 2020

@author: lucia
"""

#  Copyright 2017 Lucia Re Blanco <lucia.re@imb-cnm.csic.es>
#
#  This file is part of ASIC_Test.
#
#  ASIC_Test is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ASIC_Test is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.


from setuptools import setup, find_packages

_version = '0.0.1'

long_description = "Library for ASIC Test"

install_requires = ['numpy',
                    'matplotlib',
                    'pyqtgraph',
                    'scipy',]

console_scripts = []

entry_points = {'console_scripts': console_scripts, }

classifiers = ['Development Status :: 3 - Alpha',
               'Environment :: Console',
               'Environment :: X11 Applications :: Qt',
               'Environment :: Win32 (MS Windows)',
               'Intended Audience :: Science/Research',
               'License :: OSI Approved :: GNU General Public License (GPL)',
               'Operating System :: Microsoft :: Windows',
               'Operating System :: POSIX',
               'Operating System :: POSIX :: Linux',
               'Operating System :: Unix',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Programming Language :: Python :: 2.7',
               'Topic :: Scientific/Engineering',
               'Topic :: Software Development :: User Interfaces']

setup(name="ASIC_Test",
      version=_version,
      description="Library for ASIC Test",
      long_description=long_description,
      author="Lucia Re-Blanco",
      author_email="lucia.re@imb-cnm.csic.es",
      maintainer="Lucia Re-Blanco",
      maintainer_email="lucia.re@imb-cnm.csic.es",
      url="https://github.com/luciare/ASIC_Test",
      download_url="https://github.com/luciare/ASIC_Test",
      license="GPLv3",
      packages=find_packages(),
      classifiers=classifiers,
      entry_points=entry_points,
      install_requires=install_requires,
      include_package_data=True,
      )
