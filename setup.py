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
# locations.
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
        if dirname.startswith('.'):
            del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath,
                          [os.path.join(dirpath, f) for f in filenames]])

#FIXME(Ariel): There is a case where we are putting data in python packages:
# csv's in the plugins folder. While I do not think that's a good idea, let's
# work around it in a very specific way.
csv_files = ['itb_vulnerability_non_eng.csv', 'itb_vulnerability_eng.csv']
csv_dir = os.path.join('safe', 'impact_functions', 'earthquake')
data_files.append([csv_dir, [os.path.join(csv_dir, f) for f in csv_files]])


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='python-safe',
      version=safe.__full_version__,
      description='Spatial Analysis Functional Engine',
      license='GPL',
      keywords='gis vector feature raster data',
      author='Ole Nielsen, Tim Sutton, Ariel Núñez',
      author_email='ole.moller.nielsen@gmail.com',
      url='http://github.com/AIFDR/inasafe',
      long_description=read('README'),
      packages=packages,
      data_files=data_files,
      install_requires=['Numpy', ],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering :: GIS',
      ],
      zip_safe=False,)
