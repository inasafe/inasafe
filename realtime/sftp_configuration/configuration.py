# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Wrapper for SFTP Configuration.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__version__ = '2.1'
__date__ = '18/07/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os

from realtime.sftp_configuration.base_config import (
    BASE_URL,
    PORT,
    USERNAME,
    PASSWORD,
    BASE_PATH,
    GRID_SOURCE)


def get_sftp_base_url():
    """Get base url of the sftp.

    If set, the environment variable EQ_SFTP_BASE_URL will be used, otherwise
    the url will be taken from the configuration file.

    :return: The base URL of the sftp.
    :rtype: str
    """
    if 'EQ_SFTP_BASE_URL' in os.environ:
        return os.environ['EQ_SFTP_BASE_URL']
    else:
        return BASE_URL


def get_sftp_port():
    """Get the sftp port.

    If set, the environment variable EQ_SFTP_PORT will be used, otherwise
    the sftp port will be taken from the configuration file.

    :return: The port of the sftp.
    :rtype: int
    """
    if 'EQ_SFTP_PORT' in os.environ:
        return int(os.environ['EQ_SFTP_PORT'])
    else:
        return int(PORT)


def get_sftp_user_name():
    """Get the username allowed to login.

    If set, the environment variable EQ_SFTP_USER_NAME will be used, otherwise
    the username will be taken from the configuration file.

    :return: The username allowed to login.
    :rtype: str
    """
    if 'EQ_SFTP_USER_NAME' in os.environ:
        return os.environ['EQ_SFTP_USER_NAME']
    else:
        return USERNAME


def get_sftp_user_password():
    """Get the password of the allowed username to log in.

    If set, the environment variable EQ_SFTP_USER_PASSWORD will be used,
    otherwise the password for the username will be taken from the
    configuration file.

    :return: The password for the username specified in get_sftp_user_name().
    :rtype: str
    """
    if 'EQ_SFTP_USER_PASSWORD' in os.environ:
        return os.environ['EQ_SFTP_USER_PASSWORD']
    else:
        return PASSWORD


def get_sftp_base_path():
    """Get the base path where the shakemaps are placed.

    If set, the environment variable EQ_SFTP_BASE_PATH will be used, otherwise
    the base path will be taken from the configuration file.

    :return: The base path where the shakemaps are placed.
    :rtype: str
    """
    if 'EQ_SFTP_BASE_PATH' in os.environ:
        return os.environ['EQ_SFTP_BASE_PATH']
    else:
        return BASE_PATH


def get_grid_source():
    """Get the grid source where the grid.xml is obtained from.

    If set, the environment variable EQ_GRID_SOURCE will be used, otherwise
    the grid source will be taken from the configuration file.

    :return: The source of the grid.xml.
    :rtype: str
    """
    if 'EQ_GRID_SOURCE' in os.environ:
        return os.environ['EQ_GRID_SOURCE']
    else:
        return GRID_SOURCE
