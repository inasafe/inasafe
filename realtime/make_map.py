# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Functionality related to shake data files.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '30/07/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import sys
import logging
from urllib2 import URLError
from zipfile import BadZipfile

from realtime.sftp_client import SFtpClient
from realtime.utilities import data_dir, is_event_id, realtime_logger_name
from realtime.shake_event import ShakeEvent
from realtime.exceptions import SFTPEmptyError

# Initialised in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


def process_event(event_id=None, locale='en'):
    """Launcher that actually runs the event processing.

    :param event_id: The event id to process. If None the latest event will
       be downloaded and processed.
    :type event_id: str

    :param locale: The locale that will be used. Default to en.
    :type locale: str
    """
    population_path = os.path.join(
        data_dir(),
        'exposure',
        'population.tif')

    # Use cached data where available
    # Whether we should always regenerate the products
    force_flag = False
    if 'INASAFE_FORCE' in os.environ:
        force_string = os.environ['INASAFE_FORCE']
        if str(force_string).capitalize() == 'Y':
            force_flag = True

    # We always want to generate en products too so we manipulate the locale
    # list and loop through them:
    locale_list = [locale]
    if 'en' not in locale_list:
        locale_list.append('en')

    # Now generate the products
    for locale in locale_list:
        # Extract the event
        # noinspection PyBroadException
        try:
            if os.path.exists(population_path):
                shake_event = ShakeEvent(
                    event_id=event_id,
                    locale=locale,
                    force_flag=force_flag,
                    population_raster_path=population_path)
            else:
                shake_event = ShakeEvent(
                    event_id=event_id,
                    locale=locale,
                    force_flag=force_flag)
        except (BadZipfile, URLError):
            # retry with force flag true
            if os.path.exists(population_path):
                shake_event = ShakeEvent(
                    event_id=event_id,
                    locale=locale,
                    force_flag=True,
                    population_raster_path=population_path)
            else:
                shake_event = ShakeEvent(
                    event_id=event_id,
                    locale=locale,
                    force_flag=True)
        except SFTPEmptyError as ex:
            LOGGER.info(ex)
            return
        except:
            LOGGER.exception('An error occurred setting up the shake event.')
            return

        LOGGER.info('Event Id: %s', shake_event)
        LOGGER.info('-------------------------------------------')

        shake_event.render_map(force_flag)

if __name__ == '__main__':
    LOGGER.info('-------------------------------------------')

    if 'INASAFE_LOCALE' in os.environ:
        locale_option = os.environ['INASAFE_LOCALE']
    else:
        locale_option = 'en'

    if len(sys.argv) > 2:
        sys.exit(
            'Usage:\n%s [optional shakeid]\nor\n%s --list\nor%s --run-all' % (
                sys.argv[0], sys.argv[0], sys.argv[0]))
    elif len(sys.argv) == 2:
        print('Processing shakemap %s' % sys.argv[1])

        event_option = sys.argv[1]
        if event_option in '--list':
            sftp_client = SFtpClient()
            dir_listing = sftp_client.get_listing(function=is_event_id)
            for event in dir_listing:
                print event
            sys.exit(0)
        elif event_option in '--run-all':
            #
            # Caution, this code path gets memory leaks, use the
            # batch file approach rather!
            #
            sftp_client = SFtpClient()
            dir_listing = sftp_client.get_listing()
            for event in dir_listing:
                print 'Processing %s' % event
                # noinspection PyBroadException
                try:
                    process_event(event, locale_option)
                except:  # pylint: disable=W0702
                    LOGGER.exception('Failed to process %s' % event)
            sys.exit(0)
        else:
            process_event(event_option, locale_option)

    else:
        event_option = None
        print('Processing latest shakemap')
        # noinspection PyBroadException
        try:
            process_event(locale=locale_option)
        except:  # pylint: disable=W0702
            LOGGER.exception('Process event failed')
