#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES

safe = __import__('safe')

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Tell distutils not to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
safe_dir = 'safe'

for dirpath, dirnames, filenames in os.walk(safe_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])


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
      packages = packages,
      data_files = data_files,
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
