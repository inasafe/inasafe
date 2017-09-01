# coding=utf-8
"""Setup file for distutils / pypi."""
try:
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    pass

import os
from setuptools import setup, find_packages


def get_version(version=None):
    """Returns a PEP 386-compliant version number from VERSION.

    :param version: A tuple that represent a version.
    :type version: tuple

    :returns: a PEP 386-compliant version number.
    :rtype: str

    """
    if version is None:
        # Get location of application wide version info
        root_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__)))
        fid = open(os.path.join(root_dir, 'metadata.txt'))
        version_list = []
        status = ''
        for line in fid.readlines():
            if line.startswith('version'):
                version_string = line.strip().split('=')[1]
                version_list = version_string.split('.')

            if line.startswith('status'):
                status = line.strip().split('=')[1]
        fid.close()
        version = tuple(version_list + [status] + ['0'])

    if len(version) != 5:
        msg = 'Version must be a tuple of length 5. I got %s' % (version,)
        raise RuntimeError(msg)

    if version[3] not in ('alpha', 'beta', 'rc', 'final'):
        msg = 'Version tuple not as expected. I got %s' % (version,)
        raise RuntimeError(msg)

    # Now build the two parts of the version number:
    # main = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|c}N - for alpha, beta and rc releases
    parts = 2 if version[2] == 0 else 3
    main = '.'.join(str(x) for x in version[:parts])

    return main


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
        "inasafe-parameters==1.0.1",
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
