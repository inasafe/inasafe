# coding=utf-8
"""Setup file for distutils / pypi."""
try:
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    pass

import os
from setuptools import setup, find_packages


def get_version():
    """Obtain InaSAFE's version from version file.

    :returns: The current version number.
    :rtype: str

    """
    # Get location of application wide version info
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    version_file = os.path.join(root_dir, 'safe', 'definitions', 'versions.py')
    fid = open(version_file)
    version = ''
    for line in fid.readlines():
        if line.startswith('inasafe_version'):
            version = line.strip().split(' = ')[1]
            version = version.replace('\'', '')
            break
    fid.close()
    if version:
        return version
    else:
        raise Exception('Version is not found in %s' % version_file)


setup(
    name='inasafe-core',
    version=get_version(),
    packages=find_packages(include=['safe', 'safe.*']),
    include_package_data=True,
    license='GPL',
    author='InaSAFE Team',
    author_email='info@inasafe.org',
    url='http://inasafe.org/',
    description=('Realistic natural hazard impact scenarios for better '
                 'planning, preparedness and response activities.'),
    install_requires=[
        "inasafe-parameters==2.0.0",
        "PyDispatcher==2.0.5",
        "raven==6.1.0",  # This Raven doesn't use simplejson anymore
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
    ],
)
