# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Helpers, globals and general utilities for the realtime package**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '19/07/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import shutil
from datetime import datetime
from safe_qgis.utilities.custom_logging import setup_logger as setupLoggerSQ


def base_data_dir():
    """Create (if needed) and return the path to the base realtime data dir."""
    if 'INASAFE_WORK_DIR' in os.environ:
        base_data_directory = os.environ['INASAFE_WORK_DIR']
    else:
        # TODO: support env var setting here too
        base_data_directory = '/tmp/inasafe/realtime'
    mk_dir(base_data_directory)
    return base_data_directory


def data_dir():
    """Return the path to the standard data dir for e.g. geonames data."""
    dir_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'fixtures'))
    mk_dir(dir_path)
    return dir_path


def shakemap_zip_dir():
    """Create (if needed) and return the path to the base shakemap zip dir."""
    dir_path = os.path.join(base_data_dir(), 'shakemaps-zipped')
    mk_dir(dir_path)
    return dir_path


def shakemap_extract_dir():
    """Create (if needed) and return the path to the base shakemap extract dir.
    """
    dir_path = os.path.join(base_data_dir(), 'shakemaps-extracted')
    mk_dir(dir_path)
    return dir_path


def shakemap_data_dir():
    """Create (if needed) and return the path to the base shakemap post
    procesed (tifs and pickled events) data dir.
    """
    dir_path = os.path.join(base_data_dir(), 'shakemaps-processed')
    mk_dir(dir_path)
    return dir_path


def shakemap_cache_dir():
    """Create (if needed) and return the path to the base shakemap zip dir."""
    dir_path = os.path.join(base_data_dir(), 'shakemaps-cache')
    mk_dir(dir_path)
    return dir_path


def report_data_dir():
    """Create (if needed) and return the path to the base report data dir."""
    dir_path = os.path.join(base_data_dir(), 'reports')
    mk_dir(dir_path)
    return dir_path


def log_dir():
    """Create (if needed) and return the path to the log directory."""
    dir_path = os.path.join(base_data_dir(), 'logs')
    mk_dir(dir_path)
    return dir_path


def mk_dir(dir_path):
    """Make a directory, making sure it is world writable.

    :param dir_path: The directory path.
    """
    if not os.path.exists(dir_path):
        # Ensure that the dir is world writable
        # Umask sets the new mask and returns the old
        old_mask = os.umask(0000)
        os.makedirs(dir_path, 0777)
        # Resinstate the old mask for tmp
        os.umask(old_mask)


def purge_working_data():
    """Get rid of the shakemaps-* directories - mainly intended for
    invocation from unit tests to ensure there is a clean slate before
    testing."""
    shutil.rmtree(shakemap_extract_dir())
    shutil.rmtree(shakemap_data_dir())
    shutil.rmtree(shakemap_zip_dir())


def setup_logger():
    """Run once when the module is loaded and enable logging
    Borrowed heavily from this:
    http://docs.python.org/howto/logging-cookbook.html
    """
    log_file_path = os.path.join(log_dir(), 'realtime.log')
    sentry_url = (
        'http://fda607badbe440be9a2fa6b22e759c72'
        ':5e871adb47ac4da1a1114b912deb274a@sentry.linfiniti.com/2')
    setupLoggerSQ(log_file=log_file_path, sentry_url=sentry_url)


def is_event_id(event_id):
    """Check if an id is event id.

    :param event_id: The event id.

    Event id is in form of yyyymmddHHMMSS or '%Y%m%d%H%M%S'
    i.e. 20130110204706
    """
    if len(event_id) != 14:
        return False
    try:
        datetime.strptime(event_id, '%Y%m%d%H%M%S')
    except ValueError:
        return False
    return True
