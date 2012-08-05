#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from distutils.core import setup
safe = __import__('safe')

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name          = 'python-safe',
      version       = safe.get_version(),
      description   = 'Spatial Analysis Functional Engine',
      license       = 'GPL',
      keywords      = 'gis vector feature raster data',
      author        = 'Ole Nielsen, Tim Sutton, Ariel Núñez',
      author_email  = 'ole.moller.nielsen@gmail.com',
      url   = 'http://github.com/AIFDR/inasafe',
      long_description = read('README'),
      packages = ['safe',
                  'safe.common',
                  'safe.storage',
                  'safe.engine',
                  'safe.engine.impact_functions_for_testing',
                  'safe.impact_functions'],
      package_data = {'safe': ['test/data/hazard/*',
                               'test/data/exposure/*',
                               'test/data/projects/*',
                               'i18n/id/*',
                               'i18n/af/*',
                               ]},
      install_requires = ['Numpy',
                          #documentation
                          'Sphinx',
                          'cloud-sptheme'],
      classifiers   = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
        ],
      zip_safe=False,
)
