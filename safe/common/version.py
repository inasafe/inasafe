# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Version getter.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import os
import sys
import subprocess
from exceptions import WindowsError


def current_git_hash():
    """Retrieve the current git hash number of the git repo (first 6 digit).

    :returns: 6 digit of hash number.
    :rtype: str
    """
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    git_show = subprocess.Popen(
        'git rev-parse --short HEAD',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=repo_dir,
        universal_newlines=True
    )
    hash_number = git_show.communicate()[0].partition('\n')[0]
    return hash_number


def release_status():
    """Returns the release status from plugin metadata file.

    :returns: The status of release - it could be alpha, beta, rc, or final.
    :rtype: basestring
    """
    status = ''
    # Get location of application wide version info
    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..'))
    fid = open(os.path.join(root_dir, 'metadata.txt'))
    for line in fid.readlines():
        if line.startswith('status'):
            status = line.strip().split('=')[1]
    fid.close()

    return status


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
            os.path.dirname(__file__), '..', '..'))
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

    sub = ''
    # This crashes on windows
    if version[3] == 'alpha' and version[4] == '0':
        # Currently failed on windows and mac
        if 'win32' in sys.platform or 'darwin' in sys.platform:
            sub = '.dev-master'
        else:
            try:
                git_hash = current_git_hash()
                if git_hash:
                    sub = '.dev-%s' % git_hash
            except WindowsError:
                sub = '.dev-master'

    elif version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[version[3]] + str(version[4])

    return main + sub
